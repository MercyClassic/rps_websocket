from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class User(Base):
    __tablename__ = 'account'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[str] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[str] = mapped_column(Boolean, nullable=False, default=False)
    win_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lose_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
