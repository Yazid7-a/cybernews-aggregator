from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, Integer, Index

class Base(DeclarativeBase):
    pass

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    source: Mapped[str] = mapped_column(String(80), index=True)
    domain: Mapped[str] = mapped_column(String(120), index=True)

    title: Mapped[str] = mapped_column(String(400))
    url: Mapped[str] = mapped_column(String(1000), unique=True, index=True)
    canonical_url: Mapped[str | None] = mapped_column(String(1000), index=True, nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(DateTime, index=True, nullable=True)

    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    category: Mapped[str | None] = mapped_column(String(60), index=True, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(16), index=True, nullable=True)
    soc_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    dedupe_key: Mapped[str] = mapped_column(String(128), index=True)

Index("ix_articles_domain_published", Article.domain, Article.published_at)
