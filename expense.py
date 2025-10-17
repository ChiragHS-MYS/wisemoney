from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import SessionLocal
from models import Expense, User
from auth import get_db, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

# Pydantic schema
class ExpenseCreate(BaseModel):
    amount: float
    category: str
    date: datetime = datetime.utcnow()

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    date: datetime
    user_id: int

    class Config:
        orm_mode = True

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Get current user from JWT
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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

# Create expense
@router.post("/", response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_expense = Expense(
        amount=expense.amount,
        category=expense.category,
        date=expense.date,
        user_id=current_user.id
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

# Get all expenses for current user
@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    expenses = db.query(Expense).filter(Expense.user_id == current_user.id).all()
    return expenses
