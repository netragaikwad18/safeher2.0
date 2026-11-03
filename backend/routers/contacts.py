from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import EmergencyContact, User
from backend.security import get_current_user

router = APIRouter(prefix="/api/contacts", tags=["Emergency Contacts"])

class ContactCreateSchema(BaseModel):
    name: str
    phone: str
    relationship: str
    is_primary: Optional[bool] = False
    email: Optional[EmailStr] = None

class ContactUpdateSchema(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    relationship: Optional[str] = None
    is_primary: Optional[bool] = None
    email: Optional[EmailStr] = None

@router.get("")
def list_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.user_id == current_user.id
    ).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "relationship": c.relationship_type,
            "is_primary": c.is_primary,
            "email": c.email,
            "created_at": c.created_at
        }
        for c in contacts
    ]

@router.post("")
def add_contact(
    data: ContactCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.is_primary:
        db.query(EmergencyContact).filter(EmergencyContact.user_id == current_user.id).update({"is_primary": False})

    contact = EmergencyContact(
        user_id=current_user.id,
        name=data.name,
        phone=data.phone,
        relationship_type=data.relationship,
        is_primary=data.is_primary or False,
        email=data.email
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return {
        "id": contact.id,
        "name": contact.name,
        "phone": contact.phone,
        "relationship": contact.relationship_type,
        "is_primary": contact.is_primary,
        "email": contact.email
    }

@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.id == contact_id,
        EmergencyContact.user_id == current_user.id
    ).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}
