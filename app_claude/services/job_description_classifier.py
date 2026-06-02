from typing import List
from pydantic import BaseModel, Field


# ============================================
# PYDANTIC SCHEMA
# ============================================

class IntersectedReality(BaseModel):

    connected_terms: List[str] = Field(
        description=(
            "The terms being linked together by the LLM. "
            "E.g., ['Java', 'CI/CD', 'Frequent Releases', 'Approachable']"
        )
    )

    operational_implication: str = Field(
        description=(
            "What this combination actually means for daily work "
            "(e.g., complex versioning, git controls, regression testing "
            "matrices, handling rollback strategies)."
        )
    )

    cross_functional_stakeholders: List[str] = Field(
        description=(
            "The teams or roles this candidate must collaborate with as a "
            "direct result of these linked terms (e.g., QA Testers, Release "
            "Managers, Devs, Operations staff)."
        )
    )

    probable_business_context: str = Field(
        description=(
            "The underlying business landscape or tension causing this "
            "(e.g., rolling out frequent patches in an emerging, highly "
            "auditable financial tech ecosystem)."
        )
    )


class TieredSoftwareEngineeringSchema(BaseModel):

    role_tier: str = Field(
        description=(
            "The classified segment of this tech role. Must be one of: "
            "'Application Development', 'DevOps & Infrastructure', "
            "'Engineering Management', 'Data Engineering'"
        )
    )

    company: str = Field(
        description="The organization advertising the role."
    )

    job_title: str = Field(
        description="The formal role title."
    )

    job_summary: str = Field(
        description=(
            "Concise high-level overview of the role's mission "
            "and core purpose."
        )
    )

    tech_stack: List[str] = Field(
        description=(
            "Explicit hard skills, frameworks, languages, cloud tools."
        )
    )

    methodologies: List[str] = Field(
        description=(
            "Delivery styles, testing practices, deployment cadences."
        )
    )

    soft_skills: List[str] = Field(
        description=(
            "Interpersonal, behavioral, and leadership traits requested."
        )
    )

    relational_synthesis: List[IntersectedReality] = Field(
        description=(
            "CRITICAL: Read between the lines of the entire JD. Intersect "
            "the tech stack, methodologies, and soft skills to deduce the "
            "real-world engineering realities, version control pressures, "
            "and cross-functional team dynamics."
        )
    )

    job_benefits: str = Field(
        description=(
            "Salary, perks, pension, and remote/hybrid policies."
        )
    )


# ============================================
# SYSTEM PROMPT
# ============================================

SYSTEM_PROMPT = """
You are an expert technical recruiter and systems architect specializing
in Software Engineering and Tech Leadership roles.

Your task is to parse messy job advertisements into a highly synthesized
JSON schema.

Instead of looking at terms in isolation, you must globally evaluate how
the technologies, working methods, and traits connect to form specific,
real-world operational realities.

Deduce what high-level corporate buzzwords like 'Technical Leadership'
or 'Frequent Releases' *actually* mean at a practical engineering level
for the specified stack.
"""


# ============================================
# CLASSIFIER
# ============================================

class JobDescriptionClassifier:

    def __init__(
        self,
        openai_service,
        model="gpt-5.4-mini"
    ):

        self.openai_service = openai_service
        self.model = model

    def classify(self, text):

        result = (
            self.openai_service
            .parse_structured_output(
                model=self.model,
                system_prompt=SYSTEM_PROMPT,
                user_text=text[:30000],
                response_schema=TieredSoftwareEngineeringSchema,
                temperature=0
            )
        )

        return result.model_dump()
