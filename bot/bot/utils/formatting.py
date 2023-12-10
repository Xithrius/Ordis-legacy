def markdown_link(
    *,
    desc: str,
    link: str,
    desc_wrapper: str = "",
) -> str:
    if not (desc or link):
        raise ValueError("Description and link must exist")
    return f"[{desc_wrapper}{desc}{desc_wrapper}]({link})"


def codeblock(code: str | list[str], *, language: str | None = None) -> str:
    block = "\n".join(code) if isinstance(code, list) else code

    return f"```{'' if language is None else language}\n{block}\n```"


def bold(content: str) -> str:
    return f"**{content}**"
