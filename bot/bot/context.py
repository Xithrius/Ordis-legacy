from io import BytesIO
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from discord import Embed, File
from discord.ext.commands import Context as BaseContext
from discord.ext.commands import Group

if TYPE_CHECKING:
    from bot.bot import Ordis


def buffer_to_embed_file(
    buffer: BytesIO,
    embed: Embed | None = None,
    file_name: str | UUID | None = None,
) -> tuple[Embed, File]:
    embed = embed or Embed()
    file_name = file_name or uuid4()

    embed.set_image(url=f"attachment://{file_name}.png")

    file = File(fp=buffer, filename=f"{file_name}.png")

    return (embed, file)


class Context(BaseContext):
    """Definition of a custom context."""

    bot: "Ordis"

    async def check_subcommands(self) -> None:
        if self.invoked_subcommand is not None:
            return

        if not isinstance(self.command, Group):
            raise AttributeError("command is not a group command")

        group: Group = self.command

        subcommands = "\n".join(
            [f"`{cmd.name} ({', '.join(cmd.aliases)})`" if cmd.aliases else f"`{cmd.name}`" for cmd in group.commands],
        )

        await self.send(
            embed=Embed(
                title="Subcommand not found, try one of these:",
                description=subcommands,
            ),
        )

    async def send_image_buffer(
        self,
        buffer: BytesIO,
        *,
        embed: Embed | None = None,
        file_name: str | UUID | None = None,
    ) -> None:
        embed, file = buffer_to_embed_file(buffer, embed, file_name)

        await self.send(embed=embed, file=file)
