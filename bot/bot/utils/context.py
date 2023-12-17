from io import BytesIO
from uuid import UUID, uuid4

from discord import Embed, File, Interaction

from bot.context import Context


async def send_image_buffer(
    buffer: BytesIO,
    *,
    ctx: Context,
    embed: Embed | None = None,
    file_name: str | UUID | None = None,
) -> None:
    embed = embed or Embed()
    file_name = file_name or uuid4()

    embed.set_image(url=f"attachment://{file_name}.png")

    file = File(fp=buffer, filename=f"{file_name}.png")

    if isinstance(ctx, Context):
        await ctx.send(embed=embed, file=file)
    elif isinstance(ctx, Interaction):
        interaction: Interaction = ctx
        await interaction.response.send_message(embed=embed, file=file)
