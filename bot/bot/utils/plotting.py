import warnings
from io import BytesIO

import pandas as pd
import seaborn as sns
from discord import Interaction

from bot.context import Context, buffer_to_embed_file

from . import to_async
from .dataframes import remove_outliers

warnings.filterwarnings("ignore", category=UserWarning)


async def histogram_2d(
    df: pd.DataFrame,
    *,
    title: str | None = "Value distribution",
    x_label: str | None = "value",
    y_label: str | None = "frequency",
    include_outliers: bool = False,
    ctx: Context | Interaction | None,
) -> BytesIO | None:
    @to_async
    def __build_histogram_2d(data: pd.DataFrame) -> BytesIO:
        sns.set_theme()
        svm = sns.histplot(data, x=x_label, kde=True)

        svm.set_title(title)

        if (x_l := x_label) is not None:
            svm.set_xlabel(x_l.capitalize())
        if (y_l := y_label) is not None:
            svm.set_ylabel(y_l.capitalize())

        buffer = BytesIO()
        svm.get_figure().savefig(buffer, format="png")
        buffer.seek(0)

        svm.figure.clf()

        return buffer

    if include_outliers and (x_l := x_label) is not None:
        df = remove_outliers(df, x_l)

    b = await __build_histogram_2d(df)

    if ctx is None:
        return b

    if isinstance(ctx, Interaction):
        embed, file = buffer_to_embed_file(b)

        interaction: Interaction = ctx

        await interaction.response.send_message(embed=embed, file=file)
    else:
        await ctx.send_image_buffer(b)

    return None


async def barplot_2d(
    df: pd.DataFrame,
    *,
    title: str | None = "Values",
    x_label: str | None = "percentiles",
    y_label: str | None = "amount",
    include_outliers: bool = False,
    ctx: Context | Interaction | None,
) -> BytesIO | None:
    @to_async
    def __build_barplot_2d(data: pd.DataFrame) -> BytesIO:
        sns.set_theme()
        svm = sns.barplot(data, x=x_label, y=y_label)

        svm.set_title(title)

        if (x_l := x_label) is not None:
            svm.set_xlabel(x_l.capitalize())
        if (y_l := y_label) is not None:
            svm.set_ylabel(y_l.capitalize())

        buffer = BytesIO()
        svm.get_figure().savefig(buffer, format="png")
        buffer.seek(0)

        svm.figure.clf()

        return buffer

    if include_outliers and (x_l := x_label) is not None:
        df = remove_outliers(df, x_l)

    b = await __build_barplot_2d(df)

    if ctx is None:
        return b

    if isinstance(ctx, Interaction):
        embed, file = buffer_to_embed_file(b)

        interaction: Interaction = ctx

        await interaction.response.send_message(embed=embed, file=file)
    else:
        await ctx.send_image_buffer(b)

    return None
