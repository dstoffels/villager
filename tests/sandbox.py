def trunc(text: str) -> str:
    return text[:-2] if len(text) > 4 else text


print(trunc("Saint Kitts and Nevis"))
