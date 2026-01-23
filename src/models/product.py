from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    """Represents a product from any retailer."""

    name: str
    price: str
    url: str
    image_url: str
    retailer: str
    category: Optional[str] = None
    colors: list[str] = field(default_factory=list)
    sizes: list[str] = field(default_factory=list)
    description: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "price": self.price,
            "url": self.url,
            "image_url": self.image_url,
            "retailer": self.retailer,
            "category": self.category,
            "colors": self.colors,
            "sizes": self.sizes,
            "description": self.description,
        }
