def format_float(n):
    s = format(n, 'f')
    return s.rstrip('0').rstrip('.') if '.' in s else s