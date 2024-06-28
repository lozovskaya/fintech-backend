from enum import Enum

class AgreementStatus(Enum):
    NEW = 1
    CLOSED = 2
    ACTIVE = 3
    
class ScoringStatus(Enum):
    APPROVED = 1
    REJECTED = 2

class SchedulePaymentStatus(Enum):
    FUTURE = 1
    PAID = 2
    OVERDUE = 3