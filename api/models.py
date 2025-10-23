"""SQLAlchemy models."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CloudGuidelineSection(Base):
    __tablename__ = "cloud_guideline_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(12), default="en")

    matches: Mapped[list["Match"]] = relationship(back_populates="guideline")


class RegulationSection(Base):
    __tablename__ = "regulation_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(Text)
    region: Mapped[str] = mapped_column(String(64))
    regulation_type: Mapped[str] = mapped_column(String(64))
    language: Mapped[str] = mapped_column(String(12), default="en")

    matches: Mapped[list["Match"]] = relationship(back_populates="regulation")


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guideline_id: Mapped[int] = mapped_column(ForeignKey("cloud_guideline_sections.id"))
    regulation_id: Mapped[int] = mapped_column(ForeignKey("regulation_sections.id"))
    score: Mapped[float] = mapped_column()
    confidence: Mapped[float] = mapped_column()
    rationale: Mapped[str] = mapped_column(Text)
    guideline_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    regulation_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    guideline_span_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    guideline_span_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    regulation_span_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    regulation_span_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    reviewer: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    guideline: Mapped[CloudGuidelineSection] = relationship(back_populates="matches")
    regulation: Mapped[RegulationSection] = relationship(back_populates="matches")
