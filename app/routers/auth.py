# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.models.models import get_db, User
from app.controllers.user_controller import UserController
from app.schemas.user import UserCreate, UserResponse, UserUpdate, Token
from app.utils.auth import create_access_token, get_current_active_user, revoke_token
from app.config import settings

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={401: {"description": "Unauthorized"}},
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Tạo một tài khoản mới.
    - **email**: Nhập vào email của bạn
    - **username**: Nhập vào username
    - **password**: Nhập vào password
    """

    user_controller = UserController(db)

    # Kiểm tra xem username hoặc email đã tồn tại chưa
    if user_controller.get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    if user_controller.get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Tạo user mới
    return user_controller.create_user(user)


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Đăng nhập với username và password

    Args:
        - **username**: Tên tài khoản
        - **password**: Tên mật khẩu
    Returns:
        Access Token: access_token
    """

    user_controller = UserController(db)
    user = user_controller.authenticate(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.JWT_EXPIRES_MINUTES)
    token_data = create_access_token(
        db=db,
        user_id=user.id,
        expires_delta=access_token_expires
    )

    return token_data


@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_active_user)):
    # Lấy token từ header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        revoke_token(db, token)
        return {"message": "Successfully logged out"}

    raise HTTPException(status_code=400, detail="Invalid token")

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Lấy thông tin người dùng hiện tại.


    Returns:
        UserResponse: Thông tin người dùng
    """


    return current_user


# @router.put("/me", response_model=UserResponse)
# async def update_user_me(user_data: UserUpdate,
#                          current_user: User = Depends(get_current_active_user),
#                          db: Session = Depends(get_db)):
#     user_controller = UserController(db)
#
#     # Kiểm tra xem username mới đã tồn tại chưa (nếu có)
#     if user_data.username and user_data.username != current_user.username:
#         existing_user = user_controller.get_user_by_username(user_data.username)
#         if existing_user:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Username already exists"
#             )
#
#     # Kiểm tra xem email mới đã tồn tại chưa (nếu có)
#     if user_data.email and user_data.email != current_user.email:
#         existing_email = user_controller.get_user_by_email(user_data.email)
#         if existing_email:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Email already exists"
#             )
#
#     # Cập nhật thông tin người dùng
#     updated_user = user_controller.update_user(current_user.id, user_data)
#     return updated_user