def parse_year_val(raw):
    if raw is None or raw == '':
        return None, 'Year is required'
    try:
        y = int(raw)
    except (TypeError, ValueError):
        return None, 'Year must be a number not text'
    if y < 1 or y > 4:
        return None, 'Year should be between 1 and 4'
    return y, None


def parse_cgpa_val(raw):
    if raw is None or raw == '':
        return None, 'CGPA is required'
    try:
        c = float(raw)
    except (TypeError, ValueError):
        return None, 'CGPA must be a number not text'
    if c < 0 or c > 10:
        return None, 'Invalid CGPA. Enter a value between 0 and 10.'
    return c, None


def parse_min_cgpa_val(raw):
    if raw is None or raw == '':
        return None, 'Minimum CGPA is required'
    try:
        c = float(raw)
    except (TypeError, ValueError):
        return None, 'Minimum CGPA must be a number'
    if c < 0 or c > 10:
        return None, 'Invalid CGPA. Enter a value between 0 and 10.'
    return c, None


def phone_ok(phone):
    if not phone:
        return True, None
    s = str(phone).strip()
    if not s.isdigit() or len(s) != 10:
        return False, 'Phone must be exactly 10 digits'
    return True, None
