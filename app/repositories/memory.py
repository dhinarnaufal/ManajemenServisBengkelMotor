from collections import defaultdict
from itertools import count
from typing import Any, Dict, Iterator

customers: Dict[int, Dict[str, Any]] = {}
vehicles: Dict[int, Dict[str, Any]] = {}
mechanics: Dict[int, Dict[str, Any]] = {}
spareparts: Dict[int, Dict[str, Any]] = {}
orders: Dict[int, Dict[str, Any]] = {}

_counters: Dict[str, Iterator[int]] = defaultdict(lambda: count(1))


def next_id(entity: str) -> int:
    return next(_counters[entity])


def reset_store() -> None:
    """Dipakai test agar setiap tes mulai dari kondisi bersih."""
    for table in (customers, vehicles, mechanics, spareparts, orders):
        table.clear()
    _counters.clear()
