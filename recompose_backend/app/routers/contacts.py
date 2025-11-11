# --- Contacts Router ---
"""
Contacts management endpoints for storing and managing user contacts/prospects.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import List, Optional
from email_validator import validate_email, EmailNotValidError
from app.db import get_db
from app.models.user import User
from app.models.contact import Contact
from app.routers.auth import get_current_user
import logging

# --- Router Setup ---
router = APIRouter(prefix="/api/contacts", tags=["contacts"])

# --- Logger ---
logger = logging.getLogger(__name__)


# --- Pydantic Models ---
class ContactCreate(BaseModel):
    """Contact creation request model."""
    name: str = Field(..., min_length=1, max_length=255, description="Contact name")
    email: EmailStr = Field(..., description="Contact email address")
    company: Optional[str] = Field(None, max_length=255, description="Company name")
    notes: Optional[str] = Field(None, max_length=5000, description="Additional notes")
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        try:
            validation = validate_email(v, check_deliverability=False)
            return validation.email.lower()
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email address: {str(e)}")


class ContactUpdate(BaseModel):
    """Contact update request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    company: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=5000)


class ContactResponse(BaseModel):
    """Contact response model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: str
    company: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def serialize_datetime(cls, v):
        """Serialize datetime to ISO format."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class ContactListResponse(BaseModel):
    """Paginated contacts list response."""
    contacts: List[ContactResponse]
    total: int
    limit: int
    offset: int


class BatchContactCreate(BaseModel):
    """Batch contact creation request model."""
    contacts: List[ContactCreate] = Field(..., min_length=1, max_length=1000)


# --- Helper Functions ---
async def check_contact_ownership(contact_id: int, user_id: int, db: AsyncSession) -> Contact:
    """Check if contact exists and belongs to user."""
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id)
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


async def check_email_duplicate(user_id: int, email: str, db: AsyncSession, exclude_id: Optional[int] = None) -> bool:
    """Check if email already exists for user."""
    query = select(Contact).where(Contact.user_id == user_id, Contact.email == email.lower())
    if exclude_id:
        query = query.where(Contact.id != exclude_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


# --- Endpoints ---
@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    request: Request,
    contact_data: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new contact."""
    # Check for duplicate email
    if await check_email_duplicate(current_user.id, contact_data.email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contact with email {contact_data.email} already exists"
        )
    
    # Create contact
    contact = Contact(
        user_id=current_user.id,
        name=contact_data.name,
        email=contact_data.email.lower(),
        company=contact_data.company,
        notes=contact_data.notes
    )
    
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    
    logger.info(
        f"User {current_user.id} created contact {contact.id}",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return contact


@router.post("/batch", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_contacts_batch(
    request: Request,
    batch_data: BatchContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create multiple contacts in batch."""
    created = []
    skipped = []
    
    for contact_data in batch_data.contacts:
        # Check for duplicate
        if await check_email_duplicate(current_user.id, contact_data.email, db):
            skipped.append({"email": contact_data.email, "reason": "Duplicate email"})
            continue
        
        try:
            contact = Contact(
                user_id=current_user.id,
                name=contact_data.name,
                email=contact_data.email.lower(),
                company=contact_data.company,
                notes=contact_data.notes
            )
            db.add(contact)
            created.append(contact_data.email)
        except Exception as e:
            skipped.append({"email": contact_data.email, "reason": str(e)})
    
    await db.commit()
    
    logger.info(
        f"User {current_user.id} batch created {len(created)} contacts, skipped {len(skipped)}",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return {
        "created": len(created),
        "skipped": len(skipped),
        "created_emails": created,
        "skipped_details": skipped
    }


@router.get("", response_model=ContactListResponse)
async def list_contacts(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100, description="Number of contacts to return"),
    offset: int = Query(default=0, ge=0, description="Number of contacts to skip"),
    search: Optional[str] = Query(None, description="Search by name, email, or company")
):
    """List contacts with pagination and search."""
    # Build query
    query = select(Contact).where(Contact.user_id == current_user.id)
    
    # Add search filter
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            or_(
                Contact.name.ilike(search_term),
                Contact.email.ilike(search_term),
                Contact.company.ilike(search_term)
            )
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    query = query.order_by(Contact.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    contacts = result.scalars().all()
    
    return {
        "contacts": contacts,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    request: Request,
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific contact."""
    contact = await check_contact_ownership(contact_id, current_user.id, db)
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    request: Request,
    contact_id: int,
    contact_data: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a contact."""
    contact = await check_contact_ownership(contact_id, current_user.id, db)
    
    # Check for email duplicate if email is being updated
    if contact_data.email and contact_data.email.lower() != contact.email:
        if await check_email_duplicate(current_user.id, contact_data.email, db, exclude_id=contact_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact with email {contact_data.email} already exists"
            )
        contact.email = contact_data.email.lower()
    
    # Update fields
    if contact_data.name is not None:
        contact.name = contact_data.name
    if contact_data.company is not None:
        contact.company = contact_data.company
    if contact_data.notes is not None:
        contact.notes = contact_data.notes
    
    await db.commit()
    await db.refresh(contact)
    
    logger.info(
        f"User {current_user.id} updated contact {contact_id}",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    request: Request,
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a contact."""
    contact = await check_contact_ownership(contact_id, current_user.id, db)
    
    await db.delete(contact)
    await db.commit()
    
    logger.info(
        f"User {current_user.id} deleted contact {contact_id}",
        extra={"request_id": getattr(request.state, "request_id", "unknown")}
    )
    
    return None

