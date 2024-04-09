from enum import Enum


class ContactTypeEnum(str, Enum):
    OWNER = "OWNER"
    DRIVER = "DRIVER"
    BUYER = "BUYER"
    CLIENT = "CLIENT"
