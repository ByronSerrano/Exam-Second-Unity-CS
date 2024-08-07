from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Auth
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# Members
class MemberBase(BaseModel):
    nombre: str
    edad: int

class MemberCreate(MemberBase):
    pass

class Member(MemberBase):
    id: int

    class Config:
        from_attributes = True

# Trainings
class TrainingBase(BaseModel):
    title: str
    description: str
    date: datetime

class TrainingCreate(TrainingBase):
    members: List[int]

class Training(TrainingBase):
    id: int
    members: List[Member]

    class Config:
        from_attributes = True

# Competitions
class CompetitionBase(BaseModel):
    name: str
    location: str
    date: datetime

class CompetitionCreate(CompetitionBase):
    members: List[int]

class Competition(CompetitionBase):
    id: int
    members: List[Member]

    class Config:
        from_attributes = True
