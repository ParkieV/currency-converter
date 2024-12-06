from datetime import date
from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), unique=True, primary_key=True, index=True, default=uuid4)

class Currencies(Base):
    __tablename__ = "currencies"

    site: Mapped[str] = mapped_column()
    cdr_id: Mapped[str | None] = mapped_column()
    name: Mapped[str] = mapped_column()
    char_code: Mapped[str] = mapped_column()
    value: Mapped[float] = mapped_column()
    nominal: Mapped[int] = mapped_column()
    unit_value: Mapped[float] = mapped_column()
    data_check: Mapped[date] = mapped_column()
