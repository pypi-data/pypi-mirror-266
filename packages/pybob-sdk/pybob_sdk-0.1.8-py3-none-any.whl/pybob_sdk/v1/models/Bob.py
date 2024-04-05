from pydantic import BaseModel, Field


class BobCreds(BaseModel):
    service_account_id: str = Field(description="A Bob HR service account ID")
    service_account_token: str = Field(description="A Bob HR service account token")
