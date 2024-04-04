from dataclasses import dataclass


@dataclass
class DateFormat:
    US = [
        "%Y/%d/%m",
        "%Y/%-d/%b",
        "%Y/%d/%b",
        "%m/%d/%Y",
        "%m/%-d/%Y",
        "%b/%d/%Y",
        "%B%d%Y",
        "%B/%d/%Y",
        "%m/%d/%y",
        "%m/%-d/%y",
        "%b/%d/%y",
        "%B%d%y",
        "%B/%d/%y",
    ]
    Standard = [
        "%Y/%m/%d",
        "%Y/%b/%-d",
        "%Y/%b/%d",
        "%d/%m/%Y",
        "%-d/%m/%Y",
        "%d/%b/%Y",
        "%d%B%Y",
        "%d/%B/%Y",
        "%d/%m/%y",
        "%-d/%m/%y",
        "%d/%b/%y",
        "%d%B%y",
        "%d/%B/%y",
    ]


class Cleaner:
    @staticmethod
    def replace_range(values, substitution, string):
        for v in values:
            string = string.replace(v, substitution)
        return string
