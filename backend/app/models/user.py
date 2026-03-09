from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import TimeStampedModel


class User(TimeStampedModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relaciones
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.email}>"
