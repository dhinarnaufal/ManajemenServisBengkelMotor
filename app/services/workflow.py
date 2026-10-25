from typing import Optional

from app.core.enums import ServiceStatus
from app.core.errors import InvalidStatusTransitionError

STATUS_FLOW = [
    ServiceStatus.ANTRI,
    ServiceStatus.DIKERJAKAN,
    ServiceStatus.SELESAI,
    ServiceStatus.DIBAYAR,
]

# Servis dianggap "aktif" (membebani mekanik) selama belum selesai dikerjakan.
ACTIVE_STATUSES = (ServiceStatus.ANTRI, ServiceStatus.DIKERJAKAN)


def next_status(current: ServiceStatus) -> Optional[ServiceStatus]:
    index = STATUS_FLOW.index(current)
    if index + 1 < len(STATUS_FLOW):
        return STATUS_FLOW[index + 1]
    return None


def ensure_valid_transition(current: ServiceStatus, target: ServiceStatus) -> None:
    expected = next_status(current)
    if expected is None:
        raise InvalidStatusTransitionError(
            "Servis sudah berstatus dibayar dan tidak bisa diubah lagi."
        )
    if target != expected:
        raise InvalidStatusTransitionError(
            "Transisi status tidak valid: dari '{}' hanya boleh ke '{}'.".format(
                current.value, expected.value
            )
        )


def is_active(status: ServiceStatus) -> bool:
    return status in ACTIVE_STATUSES


def can_modify_parts(status: ServiceStatus) -> bool:
    return is_active(status)
