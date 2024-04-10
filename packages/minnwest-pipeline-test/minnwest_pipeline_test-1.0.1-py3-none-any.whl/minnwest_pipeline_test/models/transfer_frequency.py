from enum import Enum


class TransferFrequency(str, Enum):
    EVERYTWOMONTHS = "EveryTwoMonths"
    EVERYTWOWEEKS = "EveryTwoWeeks"
    HALFYEAR = "HalfYear"
    MONTHLY = "Monthly"
    ONCE = "Once"
    QUARTERLY = "Quarterly"
    TWICEMONTHLY = "TwiceMonthly"
    VARIABLE = "Variable"
    WEEKLY = "Weekly"
    YEARLY = "Yearly"

    def __str__(self) -> str:
        return str(self.value)
