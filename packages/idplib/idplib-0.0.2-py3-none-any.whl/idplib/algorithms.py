import operator
import re


class CreditCard:
    @staticmethod
    def luhn(card_number):
        n_digits = len(card_number)
        n_sum = 0
        is_second = False

        for i in range(n_digits - 1, -1, -1):
            d = ord(card_number[i]) - ord("0")

            if is_second == True:
                d = d * 2

            # We add two digits to handle
            # cases that make two digits after
            # doubling
            n_sum += d // 10
            n_sum += d % 10

            is_second = not is_second

        if n_sum % 10 == 0:
            return True
        else:
            return False

    @staticmethod
    def is_visa(card_number):
        ## is Visa
        pattern = r"^4[0-9]"
        match = re.search(pattern, card_number)
        if match:
            return True
        return False

    @staticmethod
    def is_mastercard(card_number):
        ## is Visa
        pattern = r"^5[1-5][0-9]"
        match = re.search(pattern, card_number)
        if match:
            return True
        return False

    @staticmethod
    def is_discover(card_number):
        if (
            card_number.startswith("6011")
            or card_number.startswith("644")
            or card_number.startswith("65")
        ):
            return True
        return False

    @staticmethod
    def is_amex(card_number):
        if card_number.startswith("34") or card_number.startswith("37"):
            return True
        return False

        # if len(cc_num) == 16 and cc_num.isdigit():
        #     digits = list(map(int, cc_num))
        #     doubled_digits = [
        #         2 * digit if index % 2 else digit
        #         for index, digit in enumerate(digits[::-1])
        #     ]
        #     summed_digits = sum(
        #         digit - 9 if digit > 9 else digit for digit in doubled_digits
        #     )

        #     if summed_digits % 10 == 0:
        #         return True


class AusGov:
    @staticmethod
    def abn(abn):
        """
        Checks if a given string meets the requirements of a valid abn number
        """

        weighting = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        modulus = 89

        temp_abn = [int(c) for c in abn if c.isdigit()]
        temp_abn[0] -= 1

        check_sum = sum(map(operator.mul, temp_abn, weighting)) % modulus
        if check_sum != 0:
            return False
        return True

    @staticmethod
    def tfn(tfn):
        weighting = [1, 4, 3, 7, 5, 8, 6, 9, 10]
        check_sum = sum(int(tfn[i]) * weighting[i] for i in range(9))
        return check_sum % 11 == 0
