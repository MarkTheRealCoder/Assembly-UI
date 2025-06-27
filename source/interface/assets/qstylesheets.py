import regex


def translateQSS(style: str):
    variables: dict[str: str] = {}
    index = style.find("variables")
    last_index = style.find("}", index)
    substring_variables = style[index:last_index]
    substring_variables = substring_variables.replace("variables", "").replace("{", "")
    raw = substring_variables.split(";")  # comments_free.split(";")
    for i in raw:
        try:
            k, v = i.split(":")
            variables[k.strip()] = v.strip()
        except Exception as e:
            del e
    style = style[last_index + 1:]
    matches: list[regex.Match] = regex.findall(r"(var\s*\((.*)\))", style)
    for s, r in matches:
        style = style.replace(s, variables.get(r))
    return style