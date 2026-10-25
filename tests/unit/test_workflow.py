import pytest

from app.core.enums import ServiceStatus as S
from app.core.errors import InvalidStatusTransitionError
from app.services.workflow import (
    can_modify_parts,
    ensure_valid_transition,
    is_active,
    next_status,
)


def test_next_status_follows_the_flow():
    assert next_status(S.ANTRI) == S.DIKERJAKAN
    assert next_status(S.DIKERJAKAN) == S.SELESAI
    assert next_status(S.SELESAI) == S.DIBAYAR


def test_final_status_has_no_next():
    assert next_status(S.DIBAYAR) is None


def test_valid_transition_does_not_raise():
    ensure_valid_transition(S.ANTRI, S.DIKERJAKAN)


@pytest.mark.parametrize(
    "current,target",
    [
        (S.ANTRI, S.SELESAI),       # melompat
        (S.ANTRI, S.DIBAYAR),       # melompat
        (S.DIKERJAKAN, S.ANTRI),    # mundur
        (S.SELESAI, S.DIKERJAKAN),  # mundur
        (S.ANTRI, S.ANTRI),         # sama
    ],
)
def test_invalid_transitions_raise(current, target):
    with pytest.raises(InvalidStatusTransitionError):
        ensure_valid_transition(current, target)


def test_paid_service_cannot_change():
    with pytest.raises(InvalidStatusTransitionError):
        ensure_valid_transition(S.DIBAYAR, S.ANTRI)


def test_only_antri_and_dikerjakan_are_active():
    assert is_active(S.ANTRI) and is_active(S.DIKERJAKAN)
    assert not is_active(S.SELESAI) and not is_active(S.DIBAYAR)


def test_parts_can_only_change_while_active():
    assert can_modify_parts(S.ANTRI)
    assert can_modify_parts(S.DIKERJAKAN)
    assert not can_modify_parts(S.SELESAI)
    assert not can_modify_parts(S.DIBAYAR)
