import pandas as pd

from feature_cleaning_1 import load_merged_data



if __name__ == "__main__":
    df_actors = load_merged_data()
    print(df_actors.describe())