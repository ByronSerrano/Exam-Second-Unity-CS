from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from db.database import Base

# Auth
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

# Trainings
class Training(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    date = Column(DateTime)
    members = relationship("Members", secondary="training_members", back_populates="trainings")

class TrainingMember(Base):
    __tablename__ = "training_members"

    training_id = Column(Integer, ForeignKey("trainings.id"), primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"), primary_key=True)

# Competitions
class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    date = Column(DateTime)
    members = relationship("Members", secondary="competition_members", back_populates="competitions")

class CompetitionMember(Base):
    __tablename__ = "competition_members"

    competition_id = Column(Integer, ForeignKey("competitions.id"), primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id"), primary_key=True)

# Members
class Members(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    edad = Column(Integer)
    trainings = relationship("Training", secondary="training_members", back_populates="members")
    competitions = relationship("Competition", secondary="competition_members", back_populates="members")
