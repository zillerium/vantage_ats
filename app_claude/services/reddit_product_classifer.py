from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================
# PYDANTIC SCHEMA
# ============================================

class ProductMention(BaseModel):
    product_name: str = Field(
        description=(
            "The standard, formal name of the software product, platform, "
            "or library. Avoid conversational shorthand here (e.g., use 'Databricks' "
            "or 'Amazon EMR', not 'DBX' or 'EMR')."
        )
    )

    product_description: str = Field(
        description=(
            "CRITICAL: A factual, concise, objective summary defining exactly "
            "what the tool is and its core technical purpose (e.g., 'A unified, cloud-based platform "
            "for data analytics, data engineering, and artificial intelligence'). Do not "
            "include conversational opinions, pros/cons, or context specific to this post here."
        )
    )

    category: str = Field(
        description=(
            "The core industry market or architectural category this product belongs to. "
            "Examples: 'Analytics', 'DevOps & Infrastructure', 'Security', 'Database', "
            "'Data Integration', 'Containers & Orchestration'."
        )
    )
    
    context_of_mention: str = Field(
        description="A short summary of how or why this product was explicitly brought up in the discussion."
    )
    
    sentiment: str = Field(
        description="The general developer sentiment towards this product in the post. Must be one of: 'Positive', 'Negative', 'Neutral', or 'Mixed'."
    )
    
    pros_mentioned: List[str] = Field(
        default=[],
        description="Specific advantages, features, or design choices praised by the user."
    )
    
    cons_mentioned: List[str] = Field(
        default=[],
        description="Specific limitations, cost issues, or functional complaints raised by the user."
    )


class RedditProductAnalysisSchema(BaseModel):
    subreddit: str = Field(
        description="The subreddit where the discussion took place (e.g., 'dataengineering')."
    )
    
    thread_topic: str = Field(
        description="The primary question or theme underlying the thread."
    )
    
    identified_products: List[ProductMention] = Field(
        description="A master collection of distinct products extracted to fuel database entity lookups."
    )
    
    key_operational_takeaway: str = Field(
        description="High level summary of the consensus reached by the engineers in the conversation."
    )


# ============================================
# SYSTEM PROMPT
# ============================================

SYSTEM_PROMPT = """
You are an expert technical data analyst and knowledge graph engineer specializing in cloud computing ecosystems, dev tools, and software products.

Your goal is to parse unstructured text (such as developer discussion forums) and extract entities for a data engineering knowledge graph. 

For each identified product, tool, framework, or cloud service, you must decouple its conversational context from its objective profile:
1. Provide its canonical product name.
2. Provide an accurate, dictionary-style technical description of what the tool actually is, drawing on your broad foundation knowledge of software ecosystems. 
3. Assign a clean market category (e.g., 'Analytics', 'DevOps & Infrastructure').

Ensure clean differentiation between these immutable global attributes and the specific user viewpoints or forum feedback.
"""


# ============================================
# CLASSIFIER
# ============================================

class RedditProductClassifier:

    def __init__(
        self,
        openai_service,
        model="gpt-5.4-mini"
    ):
        self.openai_service = openai_service
        self.model = model

    def classify(self, text: str) -> dict:
        """
        Parses raw forum text to isolate baseline product definitions alongside 
        sentiment telemetry, ensuring straightforward mapping into a downstream graph DB load asset.
        """
        result = (
            self.openai_service
            .parse_structured_output(
                model=self.model,
                system_prompt=SYSTEM_PROMPT,
                user_text=text[:30000],
                response_schema=RedditProductAnalysisSchema,
                temperature=0
            )
        )

        return result.model_dump()