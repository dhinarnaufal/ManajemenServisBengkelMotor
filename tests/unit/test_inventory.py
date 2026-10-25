import pytest

from app.core.errors import InsufficientStockError
from app.services.inventory import add_stock, take_stock


def make_part(stock=10):
    return {"id": 1, "name": "Kampas Rem", "price": 40000, "stock": stock}


def test_take_stock_reduces_stock():
    part = make_part(10)
    take_stock(part, 3)
    assert part["stock"] == 7


def test_take_stock_can_use_all_stock():
    part = make_part(5)
    take_stock(part, 5)
    assert part["stock"] == 0


def test_take_stock_insufficient_raises_and_keeps_stock():
    part = make_part(2)
    with pytest.raises(InsufficientStockError):
        take_stock(part, 3)
    assert part["stock"] == 2


def test_take_stock_rejects_non_positive_quantity():
    with pytest.raises(ValueError):
        take_stock(make_part(), 0)


def test_add_stock_increases_stock():
    part = make_part(1)
    add_stock(part, 4)
    assert part["stock"] == 5


def test_add_stock_rejects_non_positive_quantity():
    with pytest.raises(ValueError):
        add_stock(make_part(), -1)
