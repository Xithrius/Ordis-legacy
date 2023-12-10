import asyncio
import warnings
from functools import partial
from io import BytesIO
from uuid import uuid4

import numpy as np
from discord import Embed, File
from discord.ext.commands import Context
from matplotlib import pyplot as plt

warnings.filterwarnings("ignore", category=UserWarning)
plt.style.use("dark_background")


async def send_plot_buffer(ctx: Context, buffer: BytesIO) -> None:
    embed = Embed()

    file_name = uuid4()

    embed.set_image(url=f"attachment://{file_name}.png")

    file = File(fp=buffer, filename=f"{file_name}.png")

    await ctx.send(embed=embed, file=file)


async def plot_histogram_2d(
    data: list[int | float],
    *,
    title: str | None = "Cost distribution",
    x_label: str | None = "Value",
    y_label: str | None = "Frequency",
    ctx: Context | None,
) -> BytesIO | None:
    def __build_histogram_2d() -> BytesIO:
        # Create a histogram
        plt.hist(data, bins=30, density=True, alpha=0.7, color="blue")

        # Fit a normal distribution to the data
        mu, sigma = np.mean(data), np.std(data)
        x = np.linspace(min(data), max(data), 100)
        y = (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)

        # Plot the fitted normal distribution
        plt.plot(x, y, color="orange")

        # Set labels and title
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        plt.clf()

        return buffer

    b = await asyncio.to_thread(partial(__build_histogram_2d))

    if ctx is None:
        return b

    return await send_plot_buffer(ctx, b)
