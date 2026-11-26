from typing import Optional
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimeStampMixin


class User(Base, TimeStampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="procurement_analyst", index=True) # admin, procurement_analyst, viewer
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
