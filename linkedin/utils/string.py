def name_from_email(email: str):
    return " ".join([e.capitalize() for e in email.split("@")[0].split(".")])
