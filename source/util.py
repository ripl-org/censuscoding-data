def upper(x):
    return "".join(c for c in x.upper() if c.isalpha() or c==" ")

def upper_alphanum(x):
    return "".join(c for c in x.upper() if c.isalnum() or c==" ")

