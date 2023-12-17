import warnings
from io import BytesIO

import pandas as pd
import seaborn as sns
from discord import Interaction
from discord.ext.commands import Context
from loguru import logger as log

from . import send_image_buffer, to_async
from .dataframes import remove_outliers
from .dataframes.calculate_bins import freedman_diaconis_rule

warnings.filterwarnings("ignore", category=UserWarning)


async def plot_histogram_2d(
    df: pd.DataFrame,
    *,
    title: str | None = "Value distribution",
    x_label: str | None = "value",
    y_label: str | None = "frequency",
    include_outliers: bool | None = False,
    ctx: Context | Interaction | None,
) -> BytesIO | None:
    @to_async
    def __build_histogram_2d(data: pd.DataFrame) -> BytesIO:
        sns.set_theme()
        svm = sns.histplot(data, x=x_label, kde=True, bins=freedman_diaconis_rule(data[x_label]))

        svm.set_title(title)

        svm.set_xlabel(x_label.capitalize())
        svm.set_ylabel(y_label.capitalize())

        buffer = BytesIO()
        svm.get_figure().savefig(buffer, format="png")
        buffer.seek(0)

        svm.figure.clf()

        return buffer

    log.info(len(df))

    if not include_outliers:
        df = remove_outliers(df, x_label)

    log.info(len(df))

    b = await __build_histogram_2d(df)

    if ctx is None:
        return b

    return await send_image_buffer(b, ctx=ctx)
