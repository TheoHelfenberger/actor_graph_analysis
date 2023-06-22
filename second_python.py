import pandas as pd

from feature_cleaning_1 import load_merged_data




def f1(filename, nrows=100, **kwargs):
    df_name = kwargs['df_name']

    print(filename, nrows, df_name)
    f2(nrows, **kwargs)

def f2(nrows, **kwargs):
    df_name = kwargs['df_name']
    print(nrows, df_name)





if __name__ == "__main__":
    #df_actors = load_merged_data()
    #print(df_actors.describe())
    f1('filename', 42, df_name='df_names')

    