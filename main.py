from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, String, Enum, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from enum import Enum as PyEnum
import uuid
import os







DATABASE_UR = os.environ.get("DATABASE_UR")


engine = create_engine(DATABASE_UR)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI()
templates = Jinja2Templates(directory="templates")







class LeadStage(str, PyEnum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    TRANSFERRED = "transferred"
    LOST = "lost"


class SaleStage(str, PyEnum):
    NEW = "new"
    KYC = "kyc"
    AGREEMENT = "agreement"
    PAID = "paid"
    LOST = "lost"







class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stage = Column(Enum(LeadStage), nullable=True)
    ai_score = Column(Float, nullable=True)
    ai_recommendation = Column(String, nullable=True)

    sales = relationship("Sale", back_populates="lead")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(String, ForeignKey("leads.id"))
    stage = Column(Enum(SaleStage), default=SaleStage.NEW)

    lead = relationship("Lead", back_populates="sales")
Base.metadata.create_all(engine)





def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()







LEAD_TRANSITIONS = {
    LeadStage.NEW: LeadStage.CONTACTED,
    LeadStage.CONTACTED: LeadStage.QUALIFIED,
}

SALE_TRANSITIONS = {
    SaleStage.NEW: SaleStage.KYC,
    SaleStage.KYC: SaleStage.AGREEMENT,
    SaleStage.AGREEMENT: SaleStage.PAID,
}







@app.get("/", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/leads")
def create_lead(db: Session = Depends(get_db)):
    lead = Lead()
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead.__dict__


@app.post("/leads/{lead_id}/start")
def start_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")

    lead.stage = LeadStage.NEW
    db.commit()
    db.refresh(lead)
    return lead.__dict__


@app.post("/leads/{lead_id}/next")
def next_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")

    if lead.stage not in LEAD_TRANSITIONS:
        raise HTTPException(400, "Invalid transition")

    lead.stage = LEAD_TRANSITIONS[lead.stage]
    db.commit()
    db.refresh(lead)
    return lead.__dict__


@app.post("/leads/{lead_id}/analyze")
def analyze_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")

    if lead.stage != LeadStage.QUALIFIED:
        raise HTTPException(400, "Must be QUALIFIED")

    lead.ai_score = 0.8
    lead.ai_recommendation = "transfer"
    db.commit()
    db.refresh(lead)

    return {
        "score": lead.ai_score,
        "recommendation": lead.ai_recommendation
    }


@app.post("/leads/{lead_id}/transfer")
def transfer(lead_id: str, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(404, "Lead not found")

    if lead.ai_score is None or lead.ai_score < 0.6:
        raise HTTPException(400, "Analyze first")

    sale = Sale(lead_id=lead.id)
    db.add(sale)

    lead.stage = LeadStage.TRANSFERRED

    db.commit()
    db.refresh(sale)

    return sale.__dict__


@app.post("/sales/{sale_id}/next")
def next_sale(sale_id: str, db: Session = Depends(get_db)):
    sale = db.get(Sale, sale_id)
    if not sale:
        raise HTTPException(404, "Sale not found")

    if sale.stage not in SALE_TRANSITIONS:
        raise HTTPException(400, "Invalid transition")

    sale.stage = SALE_TRANSITIONS[sale.stage]
    db.commit()
    db.refresh(sale)
    return sale.__dict__