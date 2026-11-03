from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, AdminUser
from backend.security import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class RegisterSchema(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    emergency_pin: Optional[str] = "1234"
    blood_group: Optional[str] = "O+"
    medical_notes: Optional[str] = None
    address: Optional[str] = None

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordSchema(BaseModel):
    email: EmailStr
    emergency_pin: str
    new_password: str

class UpdateProfileSchema(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    emergency_pin: Optional[str] = None
    blood_group: Optional[str] = None
    medical_notes: Optional[str] = None
    address: Optional[str] = None

@router.post("/register")
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(status_code=400, detail="An account with this phone number already exists.")

    new_user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
        emergency_pin=data.emergency_pin,
        blood_group=data.blood_group,
        medical_notes=data.medical_notes,
        address=data.address,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.email, "role": new_user.role, "id": new_user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "full_name": new_user.full_name,
            "email": new_user.email,
            "phone": new_user.phone,
            "role": new_user.role
        }
    }

@router.post("/login")
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        admin = db.query(AdminUser).filter(AdminUser.email == data.email).first()
        if admin and verify_password(data.password, admin.password_hash):
            token = create_access_token({"sub": admin.email, "role": "admin", "id": admin.id})
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": admin.id,
                    "full_name": admin.username,
                    "email": admin.email,
                    "phone": "Admin Hotline",
                    "role": "admin"
                }
            }
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role
        }
    }

@router.get("/profile")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": current_user.phone,
        "blood_group": current_user.blood_group,
        "medical_notes": current_user.medical_notes,
        "address": current_user.address,
        "emergency_pin": current_user.emergency_pin,
        "role": current_user.role,
        "created_at": current_user.created_at
    }

@router.put("/profile")
def update_profile(data: UpdateProfileSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.full_name: current_user.full_name = data.full_name
    if data.phone: current_user.phone = data.phone
    if data.emergency_pin: current_user.emergency_pin = data.emergency_pin
    if data.blood_group: current_user.blood_group = data.blood_group
    if data.medical_notes is not None: current_user.medical_notes = data.medical_notes
    if data.address is not None: current_user.address = data.address

    db.commit()
    return {"message": "Profile updated successfully"}

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found with this email.")
    if user.emergency_pin != data.emergency_pin:
        raise HTTPException(status_code=400, detail="Security verification failed: Incorrect emergency PIN.")

    user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password has been reset successfully. Please log in with your new password."}
