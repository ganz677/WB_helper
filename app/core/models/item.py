import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Enum as SAEnum, Boolean, Text, Index, DateTime, func

from .base import Base
from .enums import SourceType

if TYPE_CHECKING:
    from .answer import Answer

class Item(Base):
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    source: Mapped[SourceType] = mapped_column(
        SAEnum(SourceType, name='sourcetype'),
        default=SourceType.review,
        nullable=False,
    )
    nm_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        index=True,
        nullable=True
    )
    answered: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    payload: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    answers: Mapped[List['Answer']] = relationship(
        back_populates='item',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_items_created_answered", "created_at", "answered"),
    )