import sys
import os.path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from timeit import default_timer as timer
from datetime import timedelta

MAX_LINE = sys.maxsize - 1

def load_title_basics(nrows):
    print("Loading title.basics.tsv.gz")
    dftitlebasics = pd.read_csv('data/title.basics.tsv.gz', sep='\t', nrows=nrows)
    
    # Setting missing start year and is adult to -1
    dftitlebasics['startYear'][dftitlebasics['startYear'] == '\\N'] = -1
    dftitlebasics['isAdult'][dftitlebasics['isAdult'] == '\\N'] = 0
    # Only use movies will reduce the size drastically
    moviecondition = dftitlebasics['titleType'] == 'movie'
    isAdultFalse = dftitlebasics['isAdult'].astype(int) == 0
    # Only movies newer than 1950
    movie_age_ondition = dftitlebasics['startYear'].astype(int) > 1950
    dftitle_only_movies = dftitlebasics[moviecondition & movie_age_ondition & isAdultFalse]

    print("Only non adult movies after 1950")
    # drop columns not used
    return dftitle_only_movies.drop(columns=['titleType', 'originalTitle', 'isAdult', 'endYear', 'runtimeMinutes'])

def load_and_clean_names(nrows):
    print("Loading name.basics.tsv.gz")
    dfnamebasics = pd.read_csv('data/name.basics.tsv.gz', sep='\t' , nrows=nrows)

    actorCondition = dfnamebasics['primaryProfession'].str.contains('actor|actress', regex=True)
    dfnamebasics['birthYear'][dfnamebasics['birthYear'] == '\\N'] = -1
    birthYearCondition = dfnamebasics['birthYear'].astype(int) > 1900

    dfnamebasics = dfnamebasics[actorCondition & birthYearCondition]
    df_t_r = dfnamebasics
    # Enrich with know for titles
    # df_t_r = enrich_with_known_4(dfnamebasics)
    return df_t_r.drop(columns=['deathYear', 'primaryProfession', 'knownForTitles'])


def enrich_with_known_4(dfnamebasics):
    df_titles = dfnamebasics['knownForTitles'].str.split(',', expand=True).rename(columns={0: 't0', 1: 't1', 2: 't2', 3: 't3'})
    df_res = dfnamebasics.join(df_titles)

    df_t_0 = df_res[['nconst', 'primaryName', 'birthYear', 't0']].rename(columns={'t0':'tconst'})
    df_t_1 = df_res[['nconst', 'primaryName', 'birthYear', 't1']].rename(columns={'t1':'tconst'})
    df_t_2 = df_res[['nconst', 'primaryName', 'birthYear', 't2']].rename(columns={'t2':'tconst'})
    df_t_3 = df_res[['nconst', 'primaryName', 'birthYear', 't3']].rename(columns={'t3':'tconst'})


    df_t_r = df_t_0.append([df_t_1, df_t_2, df_t_3])
    df_t_r.dropna(axis=0, inplace=True)  
    return df_t_r  

def load_and_clean_actors(nrows):
    print("Loading title.principals.tsv.gz")
    dftitleprincipals = pd.read_csv('data/title.principals.tsv.gz', sep='\t', nrows=nrows)
    actorCondition = dftitleprincipals['category'].str.contains('actor|actress', regex=True)

    dftitlePrincipalActor = dftitleprincipals[actorCondition]
    return dftitlePrincipalActor.drop(columns=['ordering', 'job', 'characters', 'category'])
    

def loadProcessAndStore(filename, loadFn, nrows=MAX_LINE, clean=False):
    if clean and os.path.exists(filename):
        os.remove(filename)

    if not os.path.exists(filename):
        print(f"Pickle file {filename} does not exist - loading and processing it")
        df_loaded_and_processed = loadFn(nrows)
        df_loaded_and_processed.to_pickle(filename)

    return pd.read_pickle(filename)



def merge_and_store_data(filename, df_title_basics, df_actors,df_names, clean=False):
    if clean and os.path.exists(filename):
        _ = os.remove(filename)

    if not os.path.exists(filename):
        print("Merging dataframes")

        dfActorInMoviesWithNames = df_title_basics.merge(df_actors, on='tconst')
        dfActorInMoviesWithNames =dfActorInMoviesWithNames.merge(df_names, on='nconst')
        dfActorInMoviesWithNames.to_pickle(filename)

    return pd.read_pickle(filename)


def main(clean=False, nrows=MAX_LINE):
    df_title_basics = loadProcessAndStore('processed/title.basics.pkl.gz', load_title_basics, nrows=nrows, clean=clean)
    print(df_title_basics.info())

    df_actors = loadProcessAndStore('processed/title.principals.pkl.gz', load_and_clean_actors, nrows=nrows, clean=clean)
    print(df_actors.info())

    df_names = loadProcessAndStore('processed/name.basics.pkl.gz', load_and_clean_names, nrows=nrows, clean=clean)
    print(df_names.info())

    df_merged = merge_and_store_data('processed/merged_actors.pkl.gz', df_title_basics, df_actors, df_names,clean=clean)
    print(df_merged.info())
    return df_merged


def load_merged_data(clean=False):
    filename = 'processed/merged_actors.pkl.gz'
    if clean and os.path.exists(filename):
        _ = os.remove(filename)
        main(clean)
    
    return pd.read_pickle(filename)



def load_exported_list(filename):
    df_exported_list = pd.read_csv(f"data/{filename}")
    df_exported_list = df_exported_list.rename(columns={'Const': 'tconst'})
    return df_exported_list[['tconst']] 


if __name__ == "__main__":
    # df_exported_super = load_exported_list("Top 111+ Superhero Movies.csv")
    df_exported_super = load_exported_list("The James Bond Films.csv")
    print(df_exported_super.info())

    
    df_merged = main(clean=False, nrows=MAX_LINE)

    # condition = df_merged['nconst'] == 'nm0000125'
    # print(df_merged [condition].head())

    df_super = df_merged.merge(df_exported_super, on='tconst')
    print(df_super.info())
    df_super.to_csv("processed/super_heroes.csv")

    print(df_super['primaryTitle'].unique())


    # for index, row in df_exported_super.iterrows():
    #     condition = df_merged['tconst'] == row['tconst']
    #     print(f"https://www.imdb.com/title/{row['tconst']}")
    #     print(df_merged[condition].head(30))



    #df_merged = main()
    #print(df_merged.describe())

    #df_merged_after_2000 = df_merged[df_merged['startYear'].astype(int) > 2010]
    #print(df_merged_after_2000.describe())

    #df_merged_after_2000.to_csv("merged.cvs")
       