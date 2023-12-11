import warnings
from io import BytesIO

import numpy as np
import pandas as pd
import seaborn as sns
from discord.ext.commands import Context
from scipy import stats

from bot.utils import send_image_buffer, to_async

warnings.filterwarnings("ignore", category=UserWarning)


def remove_outliers(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """
    Removes outliers from a dataframe.

    Source: https://stackoverflow.com/a/23202269
    """
    return df[np.abs(stats.zscore(df[key])) < 3]


async def plot_histogram_2d(
    df: pd.DataFrame,
    *,
    title: str | None = "Value distribution",
    x_label: str | None = "value",
    y_label: str | None = "frequency",
    include_outliers: bool | None = False,
    ctx: Context | None,
) -> BytesIO | None:
    @to_async
    def __build_histogram_2d(data: pd.DataFrame) -> BytesIO:
        sns.set_theme()
        svm = sns.histplot(data, kde=True, x=x_label)

        svm.set_title(title)

        svm.set_xlabel(x_label.capitalize())
        svm.set_ylabel(y_label.capitalize())

        buffer = BytesIO()
        svm.get_figure().savefig(buffer, format="png")
        buffer.seek(0)

        svm.figure.clf()

        return buffer

    if not include_outliers:
        df = remove_outliers(df, x_label)

    b = await __build_histogram_2d(df)

    if ctx is None:
        return b

    return await send_image_buffer(ctx, b)
