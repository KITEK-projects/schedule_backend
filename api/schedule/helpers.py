import re
from unidecode import unidecode

def make_topic_name(name: str) -> str:
    ascii_name = unidecode(name)
    return re.sub(r'[^a-zA-Z0-9-_.~%]', '_', ascii_name)
