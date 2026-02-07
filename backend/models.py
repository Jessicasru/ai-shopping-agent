"""Database models and helpers for the AI Shopping Agent."""

import os
from datetime import datetime

from sqlalchemy import String, Text, Float, DateTime, create_engine, ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.dialects.postgresql import JSONB


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(500))
    price: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(Text, unique=True)
    image_url: Mapped[str] = mapped_column(Text)
    retailer: Mapped[str] = mapped_column(String(200))
    category: Mapped[str | None] = mapped_column(String(200), nullable=True)
    colors: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    sizes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "url": self.url,
            "image_url": self.image_url,
            "retailer": self.retailer,
            "category": self.category,
            "colors": self.colors or [],
            "sizes": self.sizes or [],
            "description": self.description,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }


def get_engine():
    """Create a SQLAlchemy engine from DATABASE_URL."""
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    # Railway uses postgres:// but SQLAlchemy 2.0 requires postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    return create_engine(database_url)


def init_db() -> None:
    """Create all tables if they don't exist."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def save_products(products: list[dict], scraped_at: str | None = None) -> int:
    """Upsert products into the database. Returns count of saved products."""
    engine = get_engine()
    ts = datetime.fromisoformat(scraped_at) if scraped_at else datetime.utcnow()
    saved = 0

    with Session(engine) as session:
        for p in products:
            existing = session.query(Product).filter_by(url=p["url"]).first()
            if existing:
                existing.name = p["name"]
                existing.price = p["price"]
                existing.image_url = p["image_url"]
                existing.retailer = p["retailer"]
                existing.category = p.get("category")
                existing.colors = p.get("colors", [])
                existing.sizes = p.get("sizes", [])
                existing.description = p.get("description")
                existing.scraped_at = ts
            else:
                session.add(Product(
                    name=p["name"],
                    price=p["price"],
                    url=p["url"],
                    image_url=p["image_url"],
                    retailer=p["retailer"],
                    category=p.get("category"),
                    colors=p.get("colors", []),
                    sizes=p.get("sizes", []),
                    description=p.get("description"),
                    scraped_at=ts,
                ))
            saved += 1
        session.commit()

    return saved


def get_all_products() -> list[dict]:
    """Fetch all products ordered by most recently scraped."""
    engine = get_engine()
    with Session(engine) as session:
        products = (
            session.query(Product)
            .order_by(Product.scraped_at.desc())
            .all()
        )
        return [p.to_dict() for p in products]
