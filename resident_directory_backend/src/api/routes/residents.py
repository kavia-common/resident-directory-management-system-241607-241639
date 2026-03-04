from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.api.core.auth import require_admin_user
from src.api.core.db import get_db
from src.api.models.resident import Resident
from src.api.schemas.resident import ResidentCreate, ResidentOut, ResidentUpdate

router = APIRouter(prefix="/residents", tags=["Residents"])


@router.get(
    "",
    response_model=list[ResidentOut],
    summary="List residents (public)",
    description=(
        "Public endpoint to list residents, optionally filtered by search query and status.\n\n"
        "Compatibility:\n"
        "- Accepts `q` (new) or `query` (frontend)\n"
        "- Accepts `active` (new) or `include_inactive` (frontend)\n"
    ),
    operation_id="list_residents",
)
def list_residents(
    q: str | None = Query(
        default=None,
        description="Search query matched against name, unit, email, phone, notes",
        max_length=100,
    ),
    # Frontend compatibility
    query: str | None = Query(default=None, description="Alias of `q` (deprecated; frontend compatibility)"),
    active: bool | None = Query(default=None, description="Filter by active status (True=active, False=inactive)"),
    include_inactive: bool | None = Query(
        default=None,
        description="If true, include inactive residents (frontend compatibility)",
    ),
    limit: int = Query(default=50, ge=1, le=200, description="Max results to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
):
    """List residents (public). Returns residents ordered by last_name then first_name then unit_number."""
    effective_q = q if (q is not None and q.strip()) else (query if (query is not None and query.strip()) else None)

    stmt = select(Resident)

    # Determine status filtering
    if active is not None:
        stmt = stmt.where(Resident.status == ("active" if active else "inactive"))
    elif include_inactive is None or include_inactive is False:
        # Default public behavior: show active only
        stmt = stmt.where(Resident.status == "active")

    if effective_q is not None:
        like = f"%{effective_q.strip()}%"
        stmt = stmt.where(
            or_(
                Resident.first_name.ilike(like),
                Resident.last_name.ilike(like),
                (Resident.first_name + " " + Resident.last_name).ilike(like),
                Resident.unit_number.ilike(like),
                Resident.email.ilike(like),
                Resident.phone.ilike(like),
                Resident.notes.ilike(like),
            )
        )

    stmt = (
        stmt.order_by(Resident.last_name.asc(), Resident.first_name.asc(), Resident.unit_number.asc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.execute(stmt).scalars().all())


@router.get(
    "/{resident_id}",
    response_model=ResidentOut,
    summary="Get resident (public)",
    description="Fetch a resident by UUID.",
    operation_id="get_resident",
)
def get_resident(
    resident_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a resident by id (public)."""
    resident = db.get(Resident, resident_id)
    if resident is None:
        raise HTTPException(status_code=404, detail="Resident not found")
    return resident


@router.post(
    "",
    response_model=ResidentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create resident (admin)",
    description="Create a resident (admin only).",
    operation_id="create_resident",
)
def create_resident(
    payload: ResidentCreate,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin_user),
):
    """Create a new resident (admin-only)."""
    resident = Resident(
        first_name=payload.first_name,
        last_name=payload.last_name,
        unit_number=payload.unit_number,
        email=payload.email,
        phone=payload.phone,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(resident)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        # Common cause: unique constraint on unit_number
        raise HTTPException(status_code=400, detail="Could not create resident") from exc
    db.refresh(resident)
    return resident


@router.put(
    "/{resident_id}",
    response_model=ResidentOut,
    summary="Update resident (admin)",
    description="Update a resident by UUID (admin only).",
    operation_id="update_resident",
)
def update_resident(
    resident_id: UUID,
    payload: ResidentUpdate,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin_user),
):
    """Update resident (admin-only). Partial update via PUT payload with optional fields."""
    resident = db.get(Resident, resident_id)
    if resident is None:
        raise HTTPException(status_code=404, detail="Resident not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(resident, k, v)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not update resident") from exc
    db.refresh(resident)
    return resident


@router.delete(
    "/{resident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete resident (admin)",
    description="Delete a resident by UUID (admin only).",
    operation_id="delete_resident",
)
def delete_resident(
    resident_id: UUID,
    db: Session = Depends(get_db),
    _admin: str = Depends(require_admin_user),
):
    """Delete resident (admin-only)."""
    resident = db.get(Resident, resident_id)
    if resident is None:
        raise HTTPException(status_code=404, detail="Resident not found")
    db.delete(resident)
    db.commit()
    return None
