def letters_to_number(letters):
    result = 0
    for char in letters:
        result = result * 26 + (ord(char.upper()) - ord('A')) + 1
    return result
