from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from core.rag_engine import get_llm


def extract_meeting_insights(transcript: str) -> dict:
    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are an expert meeting and video analyst.

Analyze the transcript and return ONLY valid JSON in the following format:

{{
  "title": "short meeting title",
  "summary": "detailed summary",
  "action_items": ["item1", "item2"],
  "key_decisions": ["decision1", "decision2"],
  "open_questions": ["question1", "question2"]
}}

Requirements for the summary:

Your task is to create a comprehensive, information-dense summary of the transcript.

The summary should be detailed enough that a user who never watched the video can fully understand:

- What was discussed
- Why it was discussed
- The key concepts explained
- Important examples mentioned
- Arguments, reasoning, and conclusions
- Any recommendations, action items, or decisions

Instructions:

1. Capture ALL major topics discussed in chronological order.
2. Explain important concepts in simple language.
3. Include examples, case studies, stories, analogies, and demonstrations mentioned by the speaker.
4. Preserve technical details when they are important.
5. Do not omit important explanations for the sake of brevity.
6. If multiple topics are discussed, create separate sections for each topic.
7. Mention key takeaways at the end.
8. The summary should be approximately 20–40% of the transcript length while remaining highly informative.
9. Use clear headings and bullet points.
10. Avoid generic statements such as "the speaker discussed several topics."
11. Focus on delivering maximum information value.
12. If the transcript contains educational content, explain the concepts as if teaching a student.
13. If the transcript contains a tutorial, include the step-by-step process explained.
14. If the transcript contains a meeting, include decisions, action items, concerns, blockers, and next steps.

Output format for the summary field:

# Executive Summary

(2-3 paragraph overview)

# Detailed Discussion

## Topic 1
- Detailed explanation
- Important examples
- Key insights

## Topic 2
- Detailed explanation
- Important examples
- Key insights

(Continue for all major topics)

# Key Takeaways

- Takeaway 1
- Takeaway 2
- Takeaway 3
- ...

Requirements for action_items:
- Include only concrete actions that someone needs to perform.
- Return an empty list if no action items exist.

Requirements for key_decisions:
- Include important conclusions, decisions, recommendations, or final outcomes.
- Return an empty list if none exist.

Requirements for open_questions:
- Include unanswered questions, concerns, blockers, or discussion points.
- Return an empty list if none exist.

Return JSON only.
Do not return markdown outside the JSON.
Do not return explanations outside the JSON.
"""
        ),
        ("human", "Transcript:\n\n{transcript}")
    ])

    chain = prompt | llm | JsonOutputParser()

    return chain.invoke({"transcript": transcript})


    