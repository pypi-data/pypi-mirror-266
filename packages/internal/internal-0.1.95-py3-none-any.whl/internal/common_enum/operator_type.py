from enum import Enum


class OperatorTypeEnum(str, Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    CUSTOMER = "CUSTOMER"
