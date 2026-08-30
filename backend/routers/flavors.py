from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..dependencies import get_db, require_admin
from ..models import Flavor, User
from ..schemas import FlavorCreate, FlavorListResponse, FlavorResponse, FlavorUpdate


router = APIRouter(prefix="/api/flavors", tags=["flavors"])


@router.get("", response_model=FlavorListResponse)
def get_flavors(
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=5, ge=1, le=100),
):
    offset = (page - 1) * page_size
    flavors = (
        db.query(Flavor)
        .filter(Flavor.available.is_(True))
        .order_by(Flavor.id.asc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total = db.query(func.count(Flavor.id)).filter(Flavor.available.is_(True)).scalar()
    return {"items": flavors, "page": page, "page_size": page_size, "total": total}


@router.post("", response_model=FlavorResponse, status_code=201)
def create_flavor(
    flavor_data: FlavorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    flavor = Flavor(**flavor_data.model_dump())
    try:
        db.add(flavor)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Flavor name already exists")
    db.refresh(flavor)
    return flavor


@router.get("/{flavor_id}", response_model=FlavorResponse)
def get_flavor(flavor_id: int, db: Session = Depends(get_db)):
    flavor = db.query(Flavor).filter(Flavor.id == flavor_id).first()
    if flavor is None:
        raise HTTPException(status_code=404, detail="Flavor not found")
    return flavor


@router.patch("/{flavor_id}", response_model=FlavorResponse)
def update_flavor(
    flavor_id: int,
    flavor_data: FlavorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    flavor = db.query(Flavor).filter(Flavor.id == flavor_id).first()
    if flavor is None:
        raise HTTPException(status_code=404, detail="Flavor not found")
    for field, value in flavor_data.model_dump(exclude_unset=True).items():
        setattr(flavor, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Flavor name already exists")
    db.refresh(flavor)
    return flavor


@router.delete("/{flavor_id}", status_code=204)
def delete_flavor(
    flavor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    flavor = db.query(Flavor).filter(Flavor.id == flavor_id).first()
    if flavor is None:
        raise HTTPException(status_code=404, detail="Flavor not found")
    try:
        db.delete(flavor)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Flavor is referenced and cannot be deleted; mark it as unavailable instead",
        )
