def number_to_letters(number):
    result = ''
    while number > 0:
        number, remainder = divmod(number - 1, 26)
        result = chr(remainder + ord('A')) + result
    return result
