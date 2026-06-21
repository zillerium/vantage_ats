from typing import List
from pydantic import BaseModel, Field

class ICOComplianceSchema(BaseModel):
    organization: str = Field(description="Name of the entity under audit observation.")
    governance_risk_score: str = Field(description="Assessed risk level: High, Medium, or Low.")
    critical_breaches: List[str] = Field(description="Explicit violations of data principles or governance gaps.")
    remediation_steps: List[str] = Field(description="Actionable steps recommended to align with ICO guidelines.")

SYSTEM_PROMPT = """
You are an expert technical data compliance auditor and legal knowledge engineer specializing in ICO (Information Commissioner's Office) data governance standards and privacy laws.
Your goal is to parse unstructured text inputs and extract explicit regulatory compliance entities and risks.
"""

class ICOClassifier:
    def __init__(self, openai_service, model="gpt-5.4-mini"):
        self.openai_service = openai_service
        self.model = model

    def classify(self, text: str) -> dict:
        result = self.openai_service.parse_structured_output(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            user_text=text[:30000],
            response_schema=ICOComplianceSchema,
            temperature=0
        )
        return result.model_dump()