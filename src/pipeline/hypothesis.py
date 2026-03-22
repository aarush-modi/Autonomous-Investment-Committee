from pydantic import BaseModel, field_validator


class InvestmentHypothesis(BaseModel):
    ticker: str
    thesis: str

    @field_validator("ticker")
    @classmethod
    def ticker_must_be_uppercase(cls, v):
        return v.upper().strip()

    @field_validator("thesis")
    @classmethod
    def thesis_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Thesis cannot be empty")
        return v.strip()
