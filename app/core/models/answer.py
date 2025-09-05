import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Enum, Boolean, Text, Index, String, ForeignKey, DateTime, func

from .base import Base

if TYPE_CHECKING:
    from .item import Item


class Answer(Base):
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('items.id', ondelete='CASCADE'),
        index=True,
        nullable=False,
    )
    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    edited_once: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    sent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    item: Mapped['Item'] = relationship(
        back_populates='answers'
    )