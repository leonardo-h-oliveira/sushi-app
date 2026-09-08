from fastapi import APIRouter

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

products = [
    {
        "id": 1,
        "name": "Hot Roll",
        "description": "8 unidades de hot roll",
        "price": 24.90,
        "category": "Hot Rolls",
        "active": True
    },
    {
        "id": 2,
        "name": "Combo 30 peças",
        "description": "Seleção especial com 30 peças",
        "price": 59.90,
        "category": "Combos",
        "active": True
    },
    {
        "id": 3,
        "name": "Temaki Salmão",
        "description": "Temaki de salmão com cream cheese",
        "price": 29.90,
        "category": "Temakis",
        "active": True
    }
]


@router.get("")
def list_products():
    return products