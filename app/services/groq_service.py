from groq import Groq
from app.core.config import settings
from typing import List, Dict, Any
import json

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # Using llama-3.3-70b-versatile

    async def generate_interview_questions(self, job_description: str, num_questions: int = 5) -> List[Dict[str, Any]]:
        prompt = f"""
        Based on the following job description, generate {num_questions} relevant interview questions.
        For each question, provide:
        1. The question text
        2. The expected answer criteria
        3. The skill/competency being assessed
        4. The difficulty level (1-5)

        Job Description:
        {job_description}

        Format the response as a JSON array of objects with the following structure:
        [
            {{
                "question": "question text",
                "criteria": "expected answer criteria",
                "skill": "skill being assessed",
                "difficulty": difficulty_level
            }}
        ]
        """

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.7,
            max_tokens=1000
        )

        try:
            questions = json.loads(response.choices[0].message.content)
            return questions
        except json.JSONDecodeError:
            # Fallback in case the response isn't valid JSON
            return []

    async def analyze_response(self, question: str, criteria: str, response: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze the candidate's response to the following interview question.
        
        Question: {question}
        Expected Criteria: {criteria}
        Candidate's Response: {response}

        Provide an analysis in the following JSON format:
        {{
            "score": score_out_of_10,
            "strengths": ["list", "of", "strengths"],
            "weaknesses": ["list", "of", "weaknesses"],
            "analysis": "detailed analysis of the response",
            "suggestions": "suggestions for improvement"
        }}
        """

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.3,
            max_tokens=1000
        )

        try:
            analysis = json.loads(response.choices[0].message.content)
            return analysis
        except json.JSONDecodeError:
            return {
                "score": 0,
                "strengths": [],
                "weaknesses": ["Unable to analyze response"],
                "analysis": "Error in analysis",
                "suggestions": "Please try again"
            }

    async def generate_final_report(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        Generate a comprehensive interview report based on the following interview data:
        
        {json.dumps(interview_data, indent=2)}

        Provide the report in the following JSON format:
        {{
            "overall_score": score_out_of_100,
            "strengths": ["list", "of", "key", "strengths"],
            "weaknesses": ["list", "of", "areas", "for", "improvement"],
            "detailed_analysis": "comprehensive analysis of the interview",
            "recommendations": "specific recommendations for the candidate",
            "hiring_decision": "recommended hiring decision with justification"
        }}
        """

        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0.3,
            max_tokens=2000
        )

        try:
            report = json.loads(response.choices[0].message.content)
            return report
        except json.JSONDecodeError:
            return {
                "overall_score": 0,
                "strengths": [],
                "weaknesses": ["Unable to generate report"],
                "detailed_analysis": "Error in report generation",
                "recommendations": "Please try again",
                "hiring_decision": "Unable to make a decision"
            } 