def generate_codes(previous_code: str = None):
    if not previous_code:
        previous_code = "AAA-0000"
    prefix, num = previous_code.split("-")
    num = int(num)
    num += 1
    if num > 999999:
        prefix = "".join(
            [chr(ord(char) + 1) if char != "Z" else "A" for char in reversed(prefix)]
        )[::-1]
        num = 1
    return f"{prefix}-{str(num).zfill(4)}"
