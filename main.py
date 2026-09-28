import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from analysis import group_mood_by_sleep, calculate_correlation, describe_correlation
from database import Base, SessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the tables in the real database when the server starts
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Sleep & Mood Tracker", lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class EntryCreate(BaseModel):
    date: datetime.date
    sleep_hours: float = Field(ge=0, le=24)
    mood: int = Field(ge=1, le=10)


class EntryOut(EntryCreate):
    id: int

    model_config = {"from_attributes": True}


@app.get("/")
def home():
    return {"message": "Sleep & Mood Tracker API. See /docs for the interactive docs."}


@app.post("/entries", response_model=EntryOut, status_code=201)
def create_entry(entry: EntryCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Entry).filter(models.Entry.date == entry.date).first()
    if existing:
        raise HTTPException(status_code=409, detail="An entry for this date already exists")

    db_entry = models.Entry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


@app.get("/entries", response_model=list[EntryOut])
def list_entries(db: Session = Depends(get_db)):
    return db.query(models.Entry).order_by(models.Entry.date).all()


@app.delete("/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(models.Entry).filter(models.Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return Response(status_code=204)


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    rows = db.query(models.Entry).all()
    entries = [{"sleep_hours": r.sleep_hours, "mood": r.mood} for r in rows]
    corr = calculate_correlation(entries)

    return {
        "total_entries": len(entries),
        "average_mood_by_sleep": group_mood_by_sleep(entries),
        "correlation": corr,
        "interpretation": describe_correlation(corr),
    }
