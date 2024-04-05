import datetime
import decimal

from num2words import num2words  # type: ignore

from setech.constants import LATVIAN_MONTH_MAP_GEN, LATVIAN_MONTH_MAP_NOM


def convert_number_to_latvian_words(number: decimal.Decimal, with_currency: bool = True) -> str:
    """Convert a number into words in Latvian language."""
    if not number:
        return ""

    whole_part = int(number)
    fraction_part = round((number - whole_part) * 100)
    text = num2words(whole_part, lang="lv")

    if with_currency:
        text += f" eiro, {fraction_part:02d} centi"
    else:
        text += f", {fraction_part:02d}"

    if whole_part in [100, 1000]:
        text = "viens " + text

    return text


def convert_datetime_to_latvian_words(date: datetime.date | None = None, genitive: bool = False) -> str:
    """Convert a date into words in Latvian language."""
    if date is None:
        date = datetime.date.today()
    date_sign_contract = date.strftime("%Y. gada %d. ")
    date_sign_contract += (LATVIAN_MONTH_MAP_GEN if genitive else LATVIAN_MONTH_MAP_NOM)[date.month]
    return date_sign_contract
