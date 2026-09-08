from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from models.models import User, Meeting, ChatHistory
from auth.auth import get_current_user
from core.rag_engine import load_rag_chain, ask_questions

router = APIRouter(prefix="/meetings", tags=["Chat"])


class QuestionRequest(BaseModel):
    question: str


@router.post("/{meeting_id}/ask")
def ask_meeting(
    meeting_id: int,
    req: QuestionRequest,
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

    rag_chain = load_rag_chain(str(meeting_id))

    answer = ask_questions(
        rag_chain,
        req.question
    )

    chat = ChatHistory(
        meeting_id=meeting.id,
        user_id=current_user.id,
        question=req.question,
        answer=answer
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return {
        "id": chat.id,
        "meeting_id": meeting.id,
        "question": chat.question,
        "answer": chat.answer,
        "created_at": chat.created_at
    }


@router.get("/{meeting_id}/chats")
def get_meeting_chats(
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

    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.meeting_id == meeting_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )

    return [
        {
            "id": chat.id,
            "question": chat.question,
            "answer": chat.answer,
            "created_at": chat.created_at
        }
        for chat in chats
    ]