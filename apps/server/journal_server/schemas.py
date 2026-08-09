"""Pydantic request/response schemas."""

from pydantic import BaseModel, Field


class AuthIn(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    # ASVS 6.2.1: passwords must be at least 8 characters.
    password: str = Field(min_length=8, max_length=128)


class AuthOut(BaseModel):
    token: str
    username: str


class EntryIn(BaseModel):
    id: str
    body: str = ""
    created_at: str
    updated_at: str
    deleted: bool = False


class EntryOut(BaseModel):
    id: str
    body: str
    created_at: str
    updated_at: str
    deleted: bool
