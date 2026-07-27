from dataclasses import dataclass

@dataclass
class Product:
    id: int
    name: str
    base_cost: float
    elasticity: float = 1.0
