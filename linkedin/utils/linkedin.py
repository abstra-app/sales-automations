import re

def extract_linkedin_handle(txt: str) -> str:

    match = re.search(r"(https://)?(www.)?(linkedin.com/in/|linkedin.com/company/)[^/]+", txt)
    if match:
        return match.group().split("/")[-1]
    
    # raise exception if not linkedin url
    match = re.search(r"(https?://)?(www.)", txt)
    if match:
        raise ValueError("Invalid linkedin url")
    return txt
