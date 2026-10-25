from enum import Enum


class ServiceStatus(str, Enum):
    ANTRI = "antri"
    DIKERJAKAN = "dikerjakan"
    SELESAI = "selesai"
    DIBAYAR = "dibayar"
