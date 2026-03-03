import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

# Initialize Gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

class QuestionList(BaseModel):
    questions: List[str] = Field(description="A list of 5 mock interview questions")

class QuestionFeedback(BaseModel):
    question: str = Field(description="The original question")
    user_answer: str = Field(description="The user's answer")
    feedback: str = Field(description="Detailed feedback")
    ideal_answer: str = Field(description="Sample ideal answer")

class Feedback(BaseModel):
    overall_preparedness_score: int = Field(description="Score from 1 to 10")
    overall_answer_score: int = Field(description="Score from 1 to 10")
    feedbacks: List[QuestionFeedback] = Field(description="Feedback for each question")

def research_company(company_name: str, job_description: str):
    """Researches the company and context for the interview."""
    prompt = ChatPromptTemplate.from_template(
        "You are an expert recruiter researching {company_name} for an interview for a role described as: {job_description}. "
        "Summarize the company's core values, recent projects, and likely interview culture. "
        "Provide a concise summary of what this company looks for in candidates."
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"company_name": company_name, "job_description": job_description})

def generate_questions(company_research: str, job_description: str):
    """Generates 5 mock interview questions."""
    parser = JsonOutputParser(pydantic_object=QuestionList)
    prompt = ChatPromptTemplate.from_template(
        "Based on the company research: {company_research} and the job description: {job_description}, "
        "generate 5 mock interview questions that are likely to be asked. "
        "Mix behavioral and technical questions relevant to the role. "
        "Return the questions in JSON format with a 'questions' key. {format_instructions}"
    )
    chain = prompt | llm | parser
    result = chain.invoke({
        "company_research": company_research,
        "job_description": job_description,
        "format_instructions": parser.get_format_instructions()
    })
    return result["questions"]

def analyze_interview(questions: List[str], answers: List[str]):
    """Analyzes the complete interview."""
    parser = JsonOutputParser(pydantic_object=Feedback)
    
    interview_data = ""
    for q, a in zip(questions, answers):
        interview_data += f"Question: {q}\nAnswer: {a}\n\n"

    prompt = ChatPromptTemplate.from_template(
        "You are an interview coach. Here is the transcript of a mock interview:\n{interview_data}\n\n"
        "Analyze the interview and provide:\n"
        "1. Overall interview preparedness score (1-10)\n"
        "2. Overall answer score (1-10)\n"
        "3. For each question, provide: the original question, user's answer, detailed feedback, and an ideal sample answer.\n"
        "Return the response in JSON format. {format_instructions}"
    )
    chain = prompt | llm | parser
    return chain.invoke({
        "interview_data": interview_data,
        "format_instructions": parser.get_format_instructions()
    })
