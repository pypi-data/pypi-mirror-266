import datetime
import functools
import re
import operator
from decimal import ROUND_HALF_UP, Decimal
from defaults import DateFormat, Cleaner
from algorithms import CreditCard, AusGov
from fuzzywuzzy import fuzz # type: ignore


def replace_newline(func):
    def wrapper(*args, **kwargs):
        # first convert any None type args or kwargs to empty strings
        args = ["" if isinstance(arg, type(None)) else arg for arg in args]
        kwargs = {
            key: "" if isinstance(value, type(None)) else value
            for key, value in kwargs.items()
        }

        args = [arg.replace("\n", " ") if isinstance(arg, str) else arg for arg in args]
        kwargs = {
            key: value.replace("\n", " ") if isinstance(value, str) else value
            for key, value in kwargs.items()
        }
        return func(*args, **kwargs)

    return wrapper


class Normalise:
    @staticmethod
    def digit(value: str, pattern: str = r"[ -\$,]") -> str:
        """
        Removes spaces and dashes from a given string.
        """
        return re.sub(pattern, "", value)

    @staticmethod
    def safe_round(value: float, decimal_places: int = 2) -> float:
        # Convert the float to a Decimal object
        decimal_value = Decimal(str(value))

        # Round the Decimal object to n decimal places using proper rounding
        rounded_decimal = decimal_value.quantize(
            Decimal("1e-{}".format(decimal_places)), rounding=ROUND_HALF_UP
        )

        # Convert the rounded Decimal back to a float
        rounded_float = float(rounded_decimal)

        return rounded_float

    class Date:
        @staticmethod
        @replace_newline
        def from_string(value: str, eagle_mode:bool=False):
            """
            Converts a string date into a datetime object by trying different date formats and
            returning a default date if none of the formats work.

            :param value: a string representing a date in various formats, such as '2022-01-01', 'Jan. 1, 2022',
            '1/1/22', etc
            :param eagle_mode: a boolean defaulted to False which if set to True will utalise US formats for dates


            :return: a datetime object representing the input date string in one of the specified formats, or a
            datetime object representing the date '31/12/2999' if none of the formats match the input string.
            """
            symbols = ["-", ".", "_", " "]
            appendix = ["nd", "th", ","]

            try:
                value_lower = value.lower()

                value_no_symbols = Cleaner.replace_range(
                    values=symbols, 
                    substitution="/", 
                    string=value_lower
                    )

                value_no_appendix = Cleaner.replace_range(
                    values=appendix, 
                    substitution="", 
                    string=value_no_symbols
                    )

                # replace all occurences of 'st' in date
                # but not in the special case of 'august'
                value_no_st = re.sub(r"(?<!augu)st", "", value_no_appendix)

                if eagle_mode:
                    formats = DateFormat.US
                else:
                    formats = DateFormat.Standard

                for date_format in formats:
                    try:
                        dt = datetime.datetime.strptime(value_no_st, date_format)
                        return dt
                    except ValueError:
                        pass
            except:
                pass

            return datetime.datetime.strptime("31/12/2999", "%d/%m/%Y")

        @staticmethod
        def tax_year(value):
            """
            Takes a date as either string or datetime and returns the tax year
            """
            if isinstance(value, str):
                value = Normalise.Date.from_string(value)
            if value.month >= 7:
                return value.year + 1
            else:
                return value.year


class Compare:
    @staticmethod
    def digits(value1: str, value2: str) -> bool:
        """
        The function `digits` compares two string values after normalizing
        them as digits and returns a
        boolean indicating if they are equal.

        :param value1: The function normalizes the input strings using a method
        `Normalise.digit` and then compares the normalized values to check
        if they are equal
        :type value1: str
        :type value2: str
        :return: a boolean value indicating whether the normalised versions
        of the two input values are
        equal.
        """
        normalised1 = Normalise.digit(value=value1)
        normalised2 = Normalise.digit(value=value2)
        return normalised1 == normalised2

    @staticmethod
    @functools.lru_cache(maxsize=128)
    @replace_newline
    def string_with_percent(
        value1: str, value2: str, threshold: int = 88,ignore_order:bool=False,  token_ratio: int = 89
    ):
        value = fuzz.WRatio(value1, value2)
        if value < threshold:
            if ignore_order:
                value = fuzz.token_sort_ratio(value1, value2)
                if value > token_ratio:
                    return True, value
                else:
                    return False, value
            else:
                return False, value
        return True, value

    @staticmethod
    @functools.lru_cache(maxsize=128)
    @replace_newline
    def string(
        value1: str, value2: str, threshold: int = 88, ignore_order:bool=False, token_ratio: int = 89
    ) -> bool:
        result, _ = Compare.string_with_percent(value1, value2, threshold,ignore_order, token_ratio)
        return result


class Identify:
    @staticmethod
    def credit_card_number(value):
        """
        Attempts to identify if the value presented is a credit card
        Note, this isnt 100% but it is reasonably successful. If you dont like
        the outcome you are welcome to submit a patch
        """
        # Normalise the value
        try:
            cc_num = "".join(filter(str.isdigit, value))
            if CreditCard.luhn(cc_num):
                return True

        except:
            pass
        finally:
            # Check if card is likely one of the below
            return CreditCard.is_visa(value) or \
                CreditCard.is_mastercard(value) or \
                CreditCard.is_discover(value) or \
                CreditCard.is_amex(value)



    @staticmethod
    def abn(value):
        """
        Checks if a given string meets the requirements of a valid abn number
        """
        abn = Cleaner.replace_range(
            values=[" ", "-"], 
            substitution="", 
            string=str(value)
            )
        
        if not abn.isdigit() or len(abn) != 11:
            return False
        
        return AusGov.abn(abn=abn)


    @staticmethod
    def tfn(value):
        """
        Checks if a given string meets the requirements of a valid tfn number
        """
        tfn = str(value).replace(" ", "")
        if not tfn.isdigit() or len(tfn) != 9:
            return False
        return AusGov.tfn(tfn=tfn)

    @staticmethod
    def tfn_in_string(value, max_gap=6):
        """
        Checks if a given string contains a substring which meets the requirements
        of a valid tfn number
        max gap is the maximum amount of non digit characters between digit values
        """
        pattern = r"\d{3}\s?\d{3}\s?\d{3}"
        match = re.search(pattern, value)
        if match:
            tfn = match.group(0)
            if tfn:
                return True

        def full_shift_check(string):
            """
            The function checks for valid tfn's in a given string and returns a list of valid tfn's.

            :param string: The input string that contains one or more potential tfn's to be
            checked
            :return: a list of valid tfn's found in the input string. If no valid
            tfn's are found, an empty list is returned.
            """
            pattern = r"\d+"
            digits = re.findall(pattern, string)
            stream = "".join(digits)
            if len(stream) < 9:
                return False
            groups = []
            for i in range(len(stream) - 8):
                group = stream[i : i + 9]
                if not group.startswith("0"):
                    groups.append(group)

            found_tfns = []
            for item in groups:
                if Identify.tfn(item):
                    found_tfns.append(item)
            return found_tfns

        pattern = rf"(?:(?:\ |\-){{0,{max_gap}}}(?:\d)){{8,}}"
        matches = re.findall(pattern, value)  # Search for potential TFNs
        cleansed_matches = []
        for match in matches:
            cleansed_matches.append(match.replace("-", "").replace(" ", ""))

        for match in cleansed_matches:
            if full_shift_check(match):
                return True
        return False
