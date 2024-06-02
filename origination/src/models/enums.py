from enum import Enum

class ApplicationStatus(Enum):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3
    CANCELLED = 4
    CREATED = 5
    DECLINED = 6