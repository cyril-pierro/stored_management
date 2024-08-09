def generate_codes(previous_code="YYY-9999"):
    prefix, num = previous_code.split("-")
    num = int(num)
    num += 1
    if num > 9999:
        prefix = "".join(
            [chr(ord(char) + 1) if char != "Z" else "A" for char in reversed(prefix)]
        )[::-1]
        num = 1
    return f"{prefix}-{str(num).zfill(4)}"


print(generate_codes())
