from pydantic import BaseModel, Field

class Score(BaseModel):
    """Model for evaluating search result quality"""
    
    relevant_score: float = Field(
        default=0.0,
        title="Relevance Score",
        description="relevance of the context to the question(minor 0, max 5)",
        ge=0.0,
        le=5.0,
    )
    keyward_matching_score: float = Field(
        default=0.0,
        title="Matching Score",
        description="keyword matches between the context and the question(minor 0, max 5)",
        ge=0.0,
        le=5.0
    )
    specific_score: float = Field(
        default=0.0,
        title="Specific Score",
        description="specific examples or detailed data provided in the context(minor 0, max 5)",
        ge=0.0,
        le=5.0
    )
    irrelevant_score: float = Field(
        default=0.0,
        title="Irrelevant Score",
        description="irrelevant content or minor inconsistencies(minor -5, max 0)",
        ge=-5.0,
        le=0.0
    )
    logical_error_score: float = Field(
        default=0.0,
        title="Logical Error Score",
        description="major logical errors or lack of structure(minor -5, max 0)",
        ge=-5.0,
        le=0.0
    )