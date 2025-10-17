from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Income, Expense, Wallet, User
from auth import get_db, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException

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

# Total income, total expense, total balance across wallets
@router.get("/summary")
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_income = db.query(Income).filter(Income.user_id == current_user.id).with_entities(Income.amount).all()
    total_income = sum([i[0] for i in total_income])

    total_expense = db.query(Expense).filter(Expense.user_id == current_user.id).with_entities(Expense.amount).all()
    total_expense = sum([e[0] for e in total_expense])

    total_wallet_balance = db.query(Wallet).filter(Wallet.user_id == current_user.id).with_entities(Wallet.balance).all()
    total_wallet_balance = sum([w[0] for w in total_wallet_balance])

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_wallet_balance": total_wallet_balance,
        "net_balance": total_wallet_balance + total_income - total_expense
    }
