def to_camel_case(value: str):
    components = value.split("_")
    return components[0] + "".join(x.title() for x in components[1:])
