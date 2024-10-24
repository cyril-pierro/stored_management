def generate_codes(previous_code: str = None, category: str = None):
    if not previous_code:
        previous_code = f"SK{category.upper()[0]}-0"
    prefix, num = previous_code.split("-")
    num = int(num) + 1
    return f"{prefix}-{str(num)}"