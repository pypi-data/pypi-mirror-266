class CronExpressionGenerator:
    """
    Generates cron expressions for cron job scheduling
    """

    def __init__(self):
        self._second = "*"
        self._minute = "*"
        self._hour = "*"
        self._day_of_month = "*"
        self._month = "*"
        self._day_of_week = "*"

    @property
    def cron_expression(self) -> str:
        return f"{self._second} {self._minute} {self._hour} {self._day_of_month} {self._month} {self._day_of_week}"

    def seconds(self, seconds: int, every: bool = False):
        if seconds not in range(0, 60):
            raise ValueError("Seconds must be between 0 and 60")

        value = f"{seconds}"
        if every:
            value = f"*/{seconds}"
        self._second = value
        return self

    def minutes(self, minutes: int, every: bool = False):
        if minutes not in range(0, 60):
            raise ValueError("Minutes must be between 0 and 60")

        value = f"{minutes}"
        if every:
            value = f"*/{minutes}"
        self._minute = value
        return self

    def hours(self, hours: int, every: bool = False):
        if hours not in range(0, 24):
            raise ValueError("Hours must be between 0 and 24")

        value = f"{hours}"
        if every:
            value = f"*/{hours}"
        self._hour = value
        return self

    def day_of_month(self, day_of_month: int, every: bool = False):
        if day_of_month not in range(1, 32):
            raise ValueError("Day of month must be between 1 and 32")

        value = f"{day_of_month}"
        if every:
            value = f"*/{day_of_month}"
        self._day_of_month = value
        return self

    def month(self, month: int, every: bool = False):
        if month not in range(1, 13):
            raise ValueError("Month must be between 1 and 12")

        value = f"{month}"
        if every:
            value = f"*/{month}"
        self._month = value
        return self

    def day_of_week(self, day_of_week: int, every: bool = False):
        if day_of_week not in range(0, 7):
            raise ValueError("Day of week must be between 0 and 7")

        value = f"{day_of_week}"
        if every:
            value = f"*/{day_of_week}"
        self._day_of_week = value
        return self

    def __str__(self) -> str:
        return self.cron_expression
