from pydantic import BaseModel, Field


class ToRecommendationsAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle generating recommendations for the user's trip."""
    
    #TODO: what is this?
    request: str = Field(
        description="Any necessary followup questions the recommendations assistant should clarify before proceeding."
    )

class ToServicesAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle user queries related to specific services and providers."""

    request: str = Field(
        description="Any necessary followup questions the services assistant should clarify before proceeding."
    )

class ToAccomodationAssistant(BaseModel):
    """Transfers work to a specialized assistant to handle user queries related to accomodation providers at destination."""

    request: str = Field(
        description="Any necessary followup questions the accomodation assistant should clarify before proceeding."
    )




class CompleteOrEscalate(BaseModel):
    """A tool to mark the current task as completed and/or to escalate control of the dialog to the main assistant,
    who can re-route the dialog based on the user's needs."""

    cancel: bool = True
    reason: str

    class Config:
        schema_extra = {
            "example": {
                "cancel": True,
                "reason": "User changed their mind about the current task.",
            },
            "example 2": {
                "cancel": True,
                "reason": "I have fully completed the task.",
            },
            "example 3": {
                "cancel": False,
                "reason": "I need to search the user's emails or calendar for more information.",
            },
        }
