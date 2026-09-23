import os
from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from core.vector_store import build_vector_store, load_vector_store, get_retriever

_llm = None
_llm_json = None

def get_llm():
    global _llm

    if _llm is None:
        _llm = ChatGroq(
            model="openai/gpt-oss-20b",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3,
        )


    return _llm

def get_llm_json():
    """JSON-mode LLM — used wherever structured JSON output is required."""
    global _llm_json
    if _llm_json is None:
        _llm_json = ChatGroq(
            model="openai/gpt-oss-20b",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3,
            model_kwargs={"response_format": {"type": "json_object"}},
        )
    return _llm_json


def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

def build_rag_chain(transcript:str, meeting_id: str):

    vector_store = build_vector_store(transcript, meeting_id)

    retriever = get_retriever(vector_store, k = 4)

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(

        [(
            "system",
            """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ]
    )

    #full LCEL Rag pipeline 

    rag_chain = (

        {"context" : retriever | RunnableLambda(format_docs),
         "question": RunnablePassthrough()
         }
         |prompt|llm|StrOutputParser()
    )

    return rag_chain


def load_rag_chain(meeting_id: str):
    vector_store = load_vector_store(meeting_id)
    retriever = get_retriever(vector_store)

    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are an expert meeting assistant. Answer the user's question 
based ONLY on the meeting transcript context provided below.

If the answer is not found in the context, say: 
"I could not find this information in the meeting transcript."

Always be concise and precise. If quoting someone, mention it clearly.

Context from meeting transcript:
{context}""",
        ),
        ("human", "{question}"),
    ])

    rag_chain = (
        {
            "context":  retriever| RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def ask_questions(rag_chain, question:str) -> str:
    print(f"Question : {question}")
    answer = rag_chain.invoke(question)
    print(f"answer :{answer}")
    return answer