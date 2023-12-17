from io import BytesIO

import pandas as pd
from PIL import Image, ImageDraw

from bot.utils.decorators import to_async


@to_async
def dataframe_to_table_image(
    dataframe: pd.DataFrame,
    *,
    cell_width: int | None = 100,
    cell_height: int | None = 30,
) -> BytesIO:
    # Calculate image size based on dataframe size and cell dimensions
    img_width = cell_width * len(dataframe.columns)
    img_height = cell_height * (len(dataframe) + 1)  # +1 for header row

    # Create a new image with a white background
    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    # Draw header row
    for col_index, col_name in enumerate(dataframe.columns):
        draw.rectangle(
            [col_index * cell_width, 0, (col_index + 1) * cell_width, cell_height],
            outline="black",
            fill="lightgray",
        )
        draw.text(
            (col_index * cell_width + 5, 5),
            str(col_name),
            fill="black",
        )

    # Draw data rows
    for row_index in range(len(dataframe)):
        for col_index, col_name in enumerate(dataframe.columns):
            cell_value = str(dataframe.at[row_index, col_name])
            draw.rectangle(
                [
                    col_index * cell_width,
                    (row_index + 1) * cell_height,
                    (col_index + 1) * cell_width,
                    (row_index + 2) * cell_height,
                ],
                outline="black",
                fill="white",
            )
            draw.text(
                (col_index * cell_width + 5, (row_index + 1) * cell_height + 5),
                cell_value,
                fill="black",
            )

    # Save the image to a buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    # Rewind the buffer to the beginning
    buffer.seek(0)

    return buffer
