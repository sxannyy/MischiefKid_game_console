from pydantic import BaseModel, constr, Field

class TokenCheck(BaseModel):
    username: constr(strip_whitespace=True, min_length=1) = Field(..., example="myuser")
    token: constr(strip_whitespace=True, min_length=6, max_length=6) = Field(..., example="123456")

class SaveLinkResponse(BaseModel):
    save_link: str = Field(..., example="https://supabase.co/...")