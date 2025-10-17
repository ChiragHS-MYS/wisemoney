from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import SessionLocal
from models import Income, User
from auth import get_db, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from pydantic import BaseModel

# Pydantic schema
class IncomeCreate(BaseModel):
    amount: float
    source: str
    date: datetime = datetime.utcnow()

class IncomeResponse(BaseModel):
    id: int
    amount: float
    source: str
    date: datetime
    user_id: int

    class Config:
        orm_mode = True

router = APIRouter()

# Dependency: get current user from JWT
def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    from fastapi import Request
    from fastapi.security import OAuth2PasswordBearer

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
    token = oauth2_scheme(Request)
    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Create new income
@router.post("/", response_model=IncomeResponse)
def create_income(income: IncomeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_income = Income(
        amount=income.amount,
        source=income.source,
        date=income.date,
        user_id=current_user.id
    )
    db.add(new_income)
    db.commit()
    db.refresh(new_income)
    return new_income

# Get all incomes for current user
@router.get("/", response_model=List[IncomeResponse])
def get_incomes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incomes = db.query(Income).filter(Income.user_id == current_user.id).all()
    return incomes
