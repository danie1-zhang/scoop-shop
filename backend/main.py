from fastapi import FastAPI, Depends, HTTPException, Query
from .models import Flavor, User, CartItem, OrderItem, Order
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func
from .dependencies import get_db, get_current_user, require_admin
from .schemas import FlavorResponse, FlavorListResponse, FlavorCreate, FlavorUpdate, UserCreate, UserResponse, LoginRequest, TokenResponse, CartItemResponse, CartItemRequest, CartItemUpdate, OrderResponse, OrderListResponse
from .auth import hash_password, verify_password, create_access_token
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from collections import deque
from datetime import datetime, timedelta, timezone
from threading import Lock
from sqlalchemy.dialects.postgresql import insert

app = FastAPI()

order_attempts: dict[int, deque[datetime]] = {}
order_attempts_lock = Lock()


@app.get("/api/health")
def get_health():
    return {
        "status": "ok"
    }


@app.get("/api/flavors", response_model=FlavorListResponse)
def get_flavors(db: Session = Depends(get_db), page: int = Query(default=1, ge=1), page_size: int = Query(default=5, ge=1, le=100)):
    offset = (page - 1) * page_size
    flavors = (
        db.query(Flavor)
        .filter(Flavor.available.is_(True))
        .order_by(Flavor.id.asc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    total = (
        db.query(func.count(Flavor.id))
        .filter(Flavor.available.is_(True))
        .scalar()
    )
    return {
        "items": flavors,
        "page": page,
        "page_size": page_size,
        "total": total
    }


@app.post("/api/flavors", response_model=FlavorResponse, status_code=201)
def create_flavor(flavor_data: FlavorCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    flavor = Flavor(
        name=flavor_data.name,
        description=flavor_data.description,
        price=flavor_data.price,
        available=flavor_data.available
    )
    try:
        db.add(flavor)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Flavor name already exists")
    db.refresh(flavor)
    return flavor


@app.get("/api/flavors/{flavor_id}", response_model=FlavorResponse)
def get_flavor(flavor_id: int, db: Session = Depends(get_db)):
    flavor = db.query(Flavor).filter(Flavor.id == flavor_id).first()
    if flavor:
        return flavor
    raise HTTPException(status_code=404, detail="Flavor not found")


@app.patch("/api/flavors/{flavor_id}", response_model=FlavorResponse)
def update_flavor(flavor_id: int, flavor_data: FlavorUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    flavor = db.query(Flavor).filter(Flavor.id == flavor_id).first()
    if flavor:
        updates = flavor_data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(flavor, field, value)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Flavor name already exists")
        db.refresh(flavor)
        return flavor
    raise HTTPException(status_code=404, detail="Flavor not found")


@app.delete("/api/flavors/{flavor_id}", response_model=None, status_code=204)
def delete_flavor(flavor_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    flavor = db.query(Flavor).filter(Flavor.id == flavor_id).first()
    if flavor:
        try:
            db.delete(flavor)
            db.commit()
            return
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Flavor is referenced and cannot be deleted; mark it as unavailable instead")
    raise HTTPException(status_code=404, detail="Flavor not found")


@app.post("/api/auth/register", response_model=UserResponse, status_code=201)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(func.lower(User.email) == user_data.email).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    user = User(
        email = user_data.email,
        password_hash = hash_password(user_data.password)
    )

    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")

    db.refresh(user)
    return user


@app.post("/api/auth/login", response_model=TokenResponse)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == login_data.email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    stored_hash = user.password_hash
    if not verify_password(login_data.password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get("/api/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/api/cart", response_model=list[CartItemResponse])
def get_cart_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = (
        db.query(CartItem)
        .options(joinedload(CartItem.flavor))
        .filter(CartItem.user_id == current_user.id)
        .all()
    )
    return items


@app.post("/api/cart/items", response_model=CartItemResponse)
def add_cart_item(item_data: CartItemRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
            set_={
                "quantity": CartItem.quantity + item_data.quantity,
            },
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

    item = (
        db.query(CartItem)
        .options(joinedload(CartItem.flavor))
        .filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == current_user.id,
        )
        .one()
    )

    return item


@app.patch("/api/cart/items/{cart_item_id}", response_model=CartItemResponse)
def update_cart_item(cart_item_id: int, item_data: CartItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = (
        db.query(CartItem)
        .options(joinedload(CartItem.flavor))
        .filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == current_user.id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(status_code=404, detail="Item not in cart")

    item.quantity = item_data.quantity
    db.commit()
    db.refresh(item)
    return item


@app.delete("/api/cart/items/{cart_item_id}", status_code=204)
def delete_cart_item(cart_item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.query(CartItem).filter(CartItem.user_id == current_user.id, CartItem.id == cart_item_id).first()

    if item is None:
        raise HTTPException(status_code=404, detail="Item not in cart")

    db.delete(item)
    db.commit()
    return None


@app.post("/api/orders", response_model=OrderResponse, status_code=201)
def create_order(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

    order = Order(
        user_id=current_user.id,
        total_price=total,
    )

    db.add(order)
    db.flush()

    for cart_item in cart_items:
        flavor = cart_item.flavor

        order_item = OrderItem(
            order_id=order.id,
            flavor_id=cart_item.flavor_id,
            quantity=cart_item.quantity,
            price_at_purchase=flavor.price
        )

        db.add(order_item)

    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()
    db.refresh(order)

    return order


@app.get("/api/orders", response_model=OrderListResponse)
def get_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user), page: int = Query(default=1, ge=1), page_size: int = Query(default=5, ge=1, le=100)):
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
    return {
        "items": orders,
        "page": page,
        "page_size": page_size,
        "total": total
    }


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).options(joinedload(Order.items)).filter(Order.user_id == current_user.id, Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="order does not exist")
    return order
    

def check_order_rate_limit(user_id: int) -> None:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=1)

    with order_attempts_lock:
        deq = order_attempts.setdefault(user_id, deque())

        while deq and deq[0] <= window_start:
            deq.popleft()

        if len(deq) >= 5:
            raise HTTPException(status_code=429, detail="too many requests")

        deq.append(now)
