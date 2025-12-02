def shorten_name(name: str, max_chars: int = 80) -> str:
    if not name:
        return ""
    name = name.strip()
    if len(name) <= max_chars:
        return name
    cut = name[:max_chars]
    last_space = cut.rfind(" ")
    if last_space > max_chars // 2:
        return cut[:last_space].rstrip() + "..."
    return cut.rstrip() + "..."
