from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.extractor import extract_meeting_insights
from core.rag_engine import build_rag_chain, ask_questions

load_dotenv()


def run_pipeline(source: str, language: str = "english", meeting_id: str = None) -> dict:
    print("Starting AI Video Assistant")

    chunks = process_input(source)

    transcript = transcribe_all(chunks, language)
    print(f"Raw transcription first 300 characters: {transcript[:300]}")

    insights = extract_meeting_insights(transcript)

    title = insights["title"]
    summary = insights["summary"]
    action_items = insights["action_items"]
    key_decisions = insights["key_decisions"]
    open_questions = insights["open_questions"]

    build_rag_chain(transcript, meeting_id)

    return {
        "meeting_id": meeting_id,
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": key_decisions,
        "open_questions": open_questions,
    }


if __name__ == "__main__":
    source = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"
    meeting_id = input("Meeting ID optional: ").strip() or "cli-test-meeting"

    result = run_pipeline(source, language, meeting_id)

    print("\n" + "=" * 60)
    print(f"📌 Meeting ID: {result['meeting_id']}")
    print(f"📌 Title: {result['title']}")
    print(f"\n📋 Summary:\n{result['summary']}")
    print(f"\n✅ Action Items:\n{result['action_items']}")
    print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
    print(f"\n❓ Open Questions:\n{result['open_questions']}")
    print("=" * 60)

    print("\n💬 Chat with your meeting (type 'exit' to quit)\n")

    from core.rag_engine import load_rag_chain

    rag_chain = load_rag_chain(meeting_id)

    while True:
        question = input("You: ").strip()

        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break

        if not question:
            continue

        answer = ask_questions(rag_chain, question)
        print(f"\n🤖 Assistant: {answer}\n")