"""
Phase 8, Step 1: SQLite persistence for AI decisions and human
feedback. Kept as two separate tables so we never overwrite the
AI's original output when a human responds to it.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload

DB_PATH = "sqlite:///data/processed/agent.db"
engine = create_engine(DB_PATH, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True)
    case_id = Column(String, nullable=False)
    root_cause_service = Column(String, nullable=False)
    confidence = Column(String, nullable=False)
    explanation = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    evidence_gaps = Column(Text)
    combined_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    feedback = relationship("Feedback", back_populates="decision")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=False)
    verdict = Column(String, nullable=False)  # "confirmed" or "corrected"
    corrected_service = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    decision = relationship("Decision", back_populates="feedback")


def init_db():
    Base.metadata.create_all(engine)


def save_decision(case_id: str, llm_result: dict, top_combined_score: float) -> int:
    """Save an AI decision, return its new id."""
    session = Session()
    decision = Decision(
        case_id=case_id,
        root_cause_service=llm_result.get("root_cause_service"),
        confidence=llm_result.get("confidence"),
        explanation=llm_result.get("explanation"),
        recommended_action=llm_result.get("recommended_action"),
        evidence_gaps=llm_result.get("evidence_gaps"),
        combined_score=top_combined_score,
    )
    session.add(decision)
    session.commit()
    decision_id = decision.id
    session.close()
    return decision_id


def save_feedback(decision_id: int, verdict: str, corrected_service: str = None, notes: str = None):
    session = Session()
    fb = Feedback(
        decision_id=decision_id,
        verdict=verdict,
        corrected_service=corrected_service,
        notes=notes,
    )
    session.add(fb)
    session.commit()
    session.close()


def get_all_decisions():
    session = Session()
    decisions = (
        session.query(Decision)
        .options(joinedload(Decision.feedback))
        .order_by(Decision.created_at.desc())
        .all()
    )
    session.close()
    return decisions
