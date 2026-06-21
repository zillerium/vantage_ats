from typing import List
from pydantic import BaseModel, Field

# ============================================
# PYDANTIC SCHEMA
# ============================================

class ExplicitProduct(BaseModel):
    name: str = Field(
        description="The clean, definitive product name explicitly found in the text. E.g., 'Kubernetes', 'Docker', 'Spring Boot'."
    )
    classifications: List[str] = Field(
        description="Functional classifications. E.g., ['orchestration'], ['framework']."
    )

class ImplicitParadigm(BaseModel):
    term: str = Field(
        description="The compound skill or phrase from the text that implies a broader ecosystem. E.g., 'Java microservices', 'Infrastructure as Code'."
    )
    implied_ecosystem_anchors: List[str] = Field(
        description=(
            "The foundational technical pillars implied by this term. "
            "For 'Java microservices', this must be: ['enterprise-java-framework', 'containerization', 'container-orchestration', 'asynchronous-messaging']. "
            "For 'Infrastructure as Code', this must be: ['declarative-provisioning']."
        )
    )

class JobDescriptionProductSchema(BaseModel):
    explicit_products: List[ExplicitProduct] = Field(
        description="Products explicitly named within the job description."
    )
    implicit_paradigms: List[ImplicitParadigm] = Field(
        description="Compound terms that represent entire tech clusters, mapping them to their structural pillars."
    )

# ============================================
# SYSTEM PROMPT
# ============================================

SYSTEM_PROMPT = """
You are an expert technical taxonomy engine designed to build high-fidelity skills graphs. 
Your job is to look at a Job Description JSON and break it into two distinct matching layers:

1. EXPLICIT PRODUCTS: Extract only actual software products, languages, and frameworks explicitly mentioned (e.g., 'Java', 'Spring Boot', 'AWS', 'DynamoDB', 'Docker', 'Kubernetes', 'Gradle'). Classify them by their engineering function.

2. IMPLICIT PARADIGMS: Look for high-level ecosystem terms like 'Java microservices' or 'Infrastructure as Code'. 
Do NOT guess or hallucinate specific vendor products they might use (e.g., do not randomly assume they use Kafka or PostgreSQL unless written). 
Instead, map the term to its architectural pillars (e.g., 'Java microservices' maps to anchors like ['enterprise-java-framework', 'containerization', 'container-orchestration']).

Keep all classifications and anchors lowercase, utilizing kebab-case.
"""

class JobDescriptionProductClassifier:
    def __init__(self, openai_service, model="gpt-5.4-mini"):
        self.openai_service = openai_service
        self.model = model

    def classify(self, json_content_str: str) -> dict:
        result = self.openai_service.parse_structured_output(
            model=self.model,
            system_prompt=SYSTEM_PROMPT,
            user_text=json_content_str[:30000],
            response_schema=JobDescriptionProductSchema,
            temperature=0
        )
        return result.model_dump()