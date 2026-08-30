from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload

from ..dependencies import get_current_user, get_db
from ..models import CartItem, Flavor, User
from ..schemas import CartItemRequest, CartItemResponse, CartItemUpdate


router = APIRouter(prefix="/api/cart", tags=["cart"])


@router.get("", response_model=list[CartItemResponse])
def get_cart_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(CartItem)
        .options(joinedload(CartItem.flavor))
        .filter(CartItem.user_id == current_user.id)
        .all()
    )


@router.post("/items", response_model=CartItemResponse)
def add_cart_item(
    item_data: CartItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    flavor = db.query(Flavor).filter(Flavor.id == item_data.flavor_id).first()
    if flavor is None:
        raise HTTPException(status_code=404, detail="Flavor not found")
    if not flavor.available:
        raise HTTPException(status_code=409, detail="Flavor is unavailable")

    statement = (
        insert(CartItem)
        .values(
            user_id=current_user.id,
            flavor_id=item_data.flavor_id,
            quantity=item_data.quantity,
        )
        .on_conflict_do_update(
            constraint="uq_cart_item_user_flavor",
            set_={"quantity": CartItem.quantity + item_data.quantity},
            where=(CartItem.quantity + item_data.quantity <= 100),
        )
        .returning(CartItem.id)
    )
    cart_item_id = db.execute(statement).scalar_one_or_none()
    if cart_item_id is None:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cart item quantity cannot exceed 100",
        )
    db.commit()

    return (
        db.query(CartItem)
        .options(joinedload(CartItem.flavor))
        .filter(CartItem.id == cart_item_id, CartItem.user_id == current_user.id)
        .one()
    )


@router.patch("/items/{cart_item_id}", response_model=CartItemResponse)
def update_cart_item(
    cart_item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(CartItem)
        .options(joinedload(CartItem.flavor))
        .filter(CartItem.id == cart_item_id, CartItem.user_id == current_user.id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Item not in cart")
    item.quantity = item_data.quantity
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{cart_item_id}", status_code=204)
def delete_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(CartItem)
        .filter(CartItem.user_id == current_user.id, CartItem.id == cart_item_id)
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Item not in cart")
    db.delete(item)
    db.commit()
