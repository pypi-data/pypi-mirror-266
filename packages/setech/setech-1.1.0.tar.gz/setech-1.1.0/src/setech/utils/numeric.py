import decimal


def round_decimal(dec: decimal.Decimal, precision: int = 4) -> decimal.Decimal:
    """Round decimal value to a predefined precision from the start of the value. Examples:
        - dec=123.456, precision=7 -> 123.4560,
        - dec=123.456, precision=5 -> 123.46,
        - dec=123.456, precision=3 -> 123,
        - dec=123.456, precision=2 -> 120;
    :param dec: Decimal value to round
    :param precision: how many digits since the start of the value to keep
    :return: rounded Decimal
    """
    with decimal.localcontext() as ctx:
        ctx.rounding = decimal.ROUND_HALF_UP
        value = decimal.Decimal(dec)
        dec_tuple = dec.as_tuple()
        whole_numbers = len(dec_tuple.digits) + dec_tuple.exponent  # type: ignore
        ctx.prec = precision + whole_numbers
        value = value * 1
    return value
