import pandas as pd
from scipy.stats import zscore

# https://stackoverflow.com/a/23202269


def remove_outliers(df: pd.DataFrame, key: str) -> pd.DataFrame:
    desired_zscore_threshold = 4

    while True:
        # Calculate the z-scores
        z_scores = zscore(df[key])

        # Check if all z-scores are NaN
        if pd.notna(z_scores).any():
            # Identify outliers using the z-scores
            outliers_mask = abs(z_scores) <= desired_zscore_threshold

            # Filter the DataFrame to exclude outliers
            df_filtered = df[outliers_mask]

            # Check if no more outliers are found
            if len(df_filtered) == len(df):
                break

            df = df_filtered  # Update the DataFrame for the next iteration
        else:
            # If all z-scores are NaN, break out of the loop
            break

    return df_filtered
