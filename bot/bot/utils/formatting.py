def markdown_link(
    *,
    desc: str,
    link: str,
    desc_wrapper: str = "",
) -> str:
    if not desc or not link:
        raise ValueError("Description and link must exist")
    return f"[{desc_wrapper}{desc}{desc_wrapper}]({link})"


def codeblock(code: str | list[str], *, language: str | None = None) -> str:
    block = "\n".join(code) if isinstance(code, list) else code

    return f"```{"" if language is None else language}\n{block}\n```"


def bold(content: str) -> str:
    return f"**{content}**"


def final_join(
    items: list[str],
    *,
    sep: str = ", ",
    final_sep: str = "and",
) -> str:
    items_length = len(items)

    if items_length <= 1:
        return "" if items_length == 0 else items[0]
    return f"{sep.join(str(x) for x in items[:-1])}{sep}{final_sep} {items[-1]}"
