from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from ..dependencies import get_current_user, get_db
from ..models import CartItem, Order, OrderItem, User
from ..rate_limit import check_order_rate_limit
from ..schemas import OrderListResponse, OrderResponse


router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    check_order_rate_limit(current_user.id)
    cart_items = (
        db.query(CartItem)
        .options(selectinload(CartItem.flavor))
        .filter(CartItem.user_id == current_user.id)
        .with_for_update()
        .all()
    )
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = Decimal("0")
    for cart_item in cart_items:
        flavor = cart_item.flavor
        if flavor is None:
            raise HTTPException(status_code=404, detail="Flavor not found")
        if not flavor.available:
            raise HTTPException(status_code=409, detail="Flavor is unavailable")
        total += flavor.price * cart_item.quantity

    order = Order(user_id=current_user.id, total_price=total)
    db.add(order)
    db.flush()

    for cart_item in cart_items:
        flavor = cart_item.flavor
        db.add(
            OrderItem(
                order_id=order.id,
                flavor_id=cart_item.flavor_id,
                flavor_name_at_purchase=flavor.name,
                quantity=cart_item.quantity,
                price_at_purchase=flavor.price,
            )
        )
        db.delete(cart_item)

    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=OrderListResponse)
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=5, ge=1, le=100),
):
    offset = (page - 1) * page_size
    orders = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total = db.query(func.count(Order.id)).filter(Order.user_id == current_user.id).scalar()
    return {"items": orders, "page": page, "page_size": page_size, "total": total}


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.user_id == current_user.id, Order.id == order_id)
        .first()
    )
    if order is None:
        raise HTTPException(status_code=404, detail="order does not exist")
    return order
