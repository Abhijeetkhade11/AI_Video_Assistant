from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

from database.database import get_db
from models.models import User, Meeting
from auth.auth import get_current_user
from main import run_pipeline
from pydantic import BaseModel



router = APIRouter(prefix="/meetings", tags=["Meetings"])

class RenameMeetingRequest(BaseModel):
    title: str
class MeetingRequest(BaseModel):
    source: str
    language: str = "english"


@router.post("/process")
def process_meeting(
    req: MeetingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Step 1: create empty meeting first
    new_meeting = Meeting(
        user_id=current_user.id,
        source=req.source
    )

    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    meeting_id = str(new_meeting.id)

    # Step 2: run AI pipeline
    result = run_pipeline(
        source=req.source,
        language=req.language,
        meeting_id=meeting_id
    )

    # Step 3: save result in DB
    new_meeting.title = result["title"]
    new_meeting.transcript = result["transcript"]
    new_meeting.summary = result["summary"]
    new_meeting.action_items = json.dumps(result["action_items"])
    new_meeting.key_decisions = json.dumps(result["key_decisions"])
    new_meeting.open_questions = json.dumps(result["open_questions"])
    new_meeting.vector_path = f"vector_db/{meeting_id}"

    db.commit()
    db.refresh(new_meeting)

    return {
        "meeting_id": new_meeting.id,
        "title": new_meeting.title,
        "transcript": new_meeting.transcript,
        "summary": new_meeting.summary,
        "action_items": json.loads(new_meeting.action_items),
        "key_decisions": json.loads(new_meeting.key_decisions),
        "open_questions": json.loads(new_meeting.open_questions),
    }


@router.get("/")
def get_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meetings = (
        db.query(Meeting)
        .filter(Meeting.user_id == current_user.id)
        .order_by(Meeting.created_at.desc())
        .all()
    )

    return [
        {
            "id": meeting.id,
            "title": meeting.title,
            "source": meeting.source,
            "created_at": meeting.created_at,
            "chat_count": len(meeting.chats)
        }
        for meeting in meetings
    ]


@router.get("/{meeting_id}")
def get_single_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting = (
        db.query(Meeting)
        .filter(
            Meeting.id == meeting_id,
            Meeting.user_id == current_user.id
        )
        .first()
    )

    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meeting not found"
        )

    return {
        "id": meeting.id,
        "title": meeting.title,
        "source": meeting.source,
        "transcript": meeting.transcript,
        "summary": meeting.summary,
        "action_items": json.loads(meeting.action_items or "[]"),
        "key_decisions": json.loads(meeting.key_decisions or "[]"),
        "open_questions": json.loads(meeting.open_questions or "[]"),
        "created_at": meeting.created_at,
    }

@router.delete("/{meeting_id}")
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meeting = (
        db.query(Meeting)
        .filter(
            Meeting.id == meeting_id,
            Meeting.user_id == current_user.id
        )
        .first()
    )

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    db.delete(meeting)
    db.commit()

    return {"message": "Meeting deleted successfully"}

@router.patch("/{meeting_id}/rename")
def rename_meeting(
    meeting_id: int,
    data: RenameMeetingRequest,
    db: Session = Depends(get_db),
):
    meeting = (
        db.query(Meeting)
        .filter(Meeting.id == meeting_id)
        .first()
    )

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found"
        )

    meeting.title = data.title
    db.commit()

    return {
        "message": "Meeting renamed successfully"
    }