import sys
import os.path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from timeit import default_timer as timer
from datetime import timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MAX_LINE = sys.maxsize - 1

def load_title_basics(nrows):
    logger.info("Loading title.basics.tsv.gz")
    dftitlebasics = pd.read_csv('data/title.basics.tsv.gz', sep='\t', nrows=nrows)
    logger.info(f"Read {len(dftitlebasics)} lines")

    
    # Setting missing start year and is adult to -1
    dftitlebasics.loc[dftitlebasics['startYear'] == '\\N', 'startYear'] = -1
    dftitlebasics.loc[dftitlebasics['isAdult'] == '\\N', 'isAdult'] = 0
    # Only use movies will reduce the size drastically
    moviecondition = dftitlebasics['titleType'] == 'movie'
    isAdultFalse = dftitlebasics['isAdult'].astype(int) == 0
    # Only movies newer than 1950
    movie_age_ondition = dftitlebasics['startYear'].astype(int) > 1950
    dftitle_only_movies = dftitlebasics[moviecondition & movie_age_ondition & isAdultFalse]

    logger.debug("Only non adult movies after 1950")
    logger.info(f"After cleaning {len(dftitle_only_movies)} lines  remain")
    # drop columns not used
    return dftitle_only_movies.drop(columns=['titleType', 'originalTitle', 'isAdult', 'endYear', 'runtimeMinutes'])

def load_and_clean_names(nrows):
    logger.info("Loading name.basics.tsv.gz")
    dfnamebasics = pd.read_csv('data/name.basics.tsv.gz', sep='\t' , nrows=nrows)
    logger.info(f"Read {len(dfnamebasics)} lines")
    dfnamebasics.loc[dfnamebasics['birthYear'] == '\\N', 'birthYear'] = 1899
    
    df_t_r = dfnamebasics
    logger.info(f"After cleaning {len(df_t_r)} lines  remain")
    return df_t_r.drop(columns=['deathYear', 'primaryProfession'])


def load_and_clean_actors(nrows):
    logger.info("Loading title.principals.tsv.gz")
    dftitleprincipals = pd.read_csv('data/title.principals.tsv.gz', sep='\t', nrows=nrows)
    logger.info(f"Read {len(dftitleprincipals)} lines")
    actorCondition = dftitleprincipals['category'].str.contains('actor|actress', regex=True)

    dftitlePrincipalActor = dftitleprincipals[actorCondition]

    actors_with_N_or_more_movies = dftitlePrincipalActor.groupby(['nconst']).size().loc[lambda n: n >= 30]
    df_nconst_actors_with_N_or_more_movies = actors_with_N_or_more_movies.to_frame().reset_index()[['nconst']]
    dftitlePrincipalActor = dftitlePrincipalActor.merge(df_nconst_actors_with_N_or_more_movies, on='nconst')

    logger.info(f"After cleaning {len(dftitlePrincipalActor)} lines  remain")
    return dftitlePrincipalActor.drop(columns=['ordering', 'job', 'characters', 'category'])
    
def load_and_clean_ratings(nrows,  **kwargs):
    minvotes = kwargs['minvotes'] if 'minvotes' in kwargs  else 90000
    logger.info("Loading title.ratings.tsv.gz")
    df_ratings = pd.read_csv('data/title.ratings.tsv.gz', sep='\t', nrows=nrows)
    logger.info(f"Read {len(df_ratings)} lines")
    logger.info(f"Using minvotes={minvotes}")
    voteCond = df_ratings['numVotes'] > minvotes
    
    df_ratings = df_ratings[voteCond]
    logger.info(f"After cleaning {len(df_ratings)} lines  remain")
    return df_ratings

def loadProcessAndStore(filename, loadFn, nrows=MAX_LINE, clean=False, **kwargs):
    if clean and os.path.exists(filename):
        os.remove(filename)

    if not os.path.exists(filename):
        logger.debug(f"Pickle file {filename} does not exist - loading and processing it")
        df_loaded_and_processed = loadFn(nrows, **kwargs)
        df_loaded_and_processed.to_pickle(filename)

    return pd.read_pickle(filename)



def merge_and_store_data(filename, df_title_basics, df_actors,df_names, df_ratings, clean=False):
    if clean and os.path.exists(filename):
        _ = os.remove(filename)

    if not os.path.exists(filename):
        logger.info("Merging dataframes")

        dfActorInMoviesWithNames = df_title_basics.merge(df_actors, on='tconst')
        dfActorInMoviesWithNames =dfActorInMoviesWithNames.merge(df_names, on='nconst')
        dfActorInMoviesWithNamesAndRatings =dfActorInMoviesWithNames.merge(df_ratings, on='tconst')
        dfActorInMoviesWithNamesAndRatings.to_pickle(filename)
        logger.info(f"After merging {len(dfActorInMoviesWithNamesAndRatings)} lines  remain")
    return pd.read_pickle(filename)


def tconst_nconst_known_4(nrows, **kwargs):
    logger.debug("tconst_nconst_known_4")
    df_names = kwargs['df_names']
    df_actors = kwargs['df_actors']


    df_nconst_actors = df_actors[['nconst']].drop_duplicates(keep='first', ignore_index=True)
    df_names = df_names.merge(df_nconst_actors, on='nconst')

    logger.debug(df_names.head())

    df_know_4 = df_names[0:nrows]['knownForTitles'].str.split(',', expand=True)
    df_know_4 = df_know_4.join(df_names['nconst'])

    dfs = []
    nconst_idx = len(df_know_4.columns) -1
    logger.debug(nconst_idx)

    for i in range(0,5):
        df = df_know_4.iloc[:,[i,nconst_idx]]
        df.columns= ['tconst', 'nconst']
        df = df[df['tconst'].notna()]
        df = df[df['tconst'] != '\\N']
        logger.debug(df.head())
        dfs.append(df)
            

    df_known4_concat = pd.concat(dfs)
    logger.debug(df_known4_concat.describe())
    return df_known4_concat
    


def main(clean=False, nrows=MAX_LINE):
    df_title_basics = loadProcessAndStore('processed/title.basics.pkl.gz', load_title_basics, nrows=nrows, clean=clean)
    #df_title_basics.info()

    df_actors = loadProcessAndStore('processed/title.principals.pkl.gz', load_and_clean_actors, nrows=nrows, clean=clean)
    #df_actors.info()

    df_names = loadProcessAndStore('processed/name.basics.pkl.gz', load_and_clean_names, nrows=nrows, clean=clean)
    #df_names.info()

    df_tconst_nconst_known_4 = loadProcessAndStore('processed/tconst_nconst_know4.pkl.gz', tconst_nconst_known_4, nrows=nrows, clean=clean, df_names=df_names, df_actors=df_actors)
    #df_tconst_nconst_known_4.info()

    logger.debug("Merge actors with known 4")
    df_actors = pd.concat([df_actors, df_tconst_nconst_known_4]).drop_duplicates(keep='first', ignore_index=True)

    df_names = df_names.drop(columns=['knownForTitles'])

    df_ratings = loadProcessAndStore('processed/title.ratings.pkl.gz', load_and_clean_ratings, nrows=nrows, clean=clean, minvotes=1000)
    #df_ratings.info()

    df_merged = merge_and_store_data('processed/merged_actors.pkl.gz', df_title_basics, df_actors, df_names, df_ratings, clean=clean)
    df_merged.info()
    return df_merged


def load_merged_data(clean=False):
    filename = 'processed/merged_actors.pkl.gz'
    if clean and os.path.exists(filename):
        _ = os.remove(filename)
        main(clean)
    
    return pd.read_pickle(filename)



def export_bond(df_merged):
    df_exported_super = load_exported_list("The James Bond Films.csv")
    df_super = df_merged.merge(df_exported_super, on='tconst')
    df_super.to_csv("processed/bond_movies.csv")
    logger.info(f"James Bond contains {len(df_super)} lines")


def export_watched(df_merged):
    df_exported_super = load_exported_list("Watched Movies.csv")
    df_super = df_merged.merge(df_exported_super, on='tconst')
    df_super.to_csv("processed/watched_movies.csv")
    logger.info(f"Watched contains {len(df_super)} lines")

def export_superheroes(df_merged):
    df_exported_super = load_exported_list("Top 111+ Superhero Movies.csv")
    df_super = df_merged.merge(df_exported_super, on='tconst')
    df_super.to_csv("processed/superheroes_movies.csv")
    logger.info(f"Top 111+ Superhero Movies. contains {len(df_super)} lines")

def export_marvel(df_merged): 
    df_exported_super = load_exported_list("Marvel.csv")
    df_super = df_merged.merge(df_exported_super, on='tconst')
    df_super.to_csv("processed/marvel_movies.csv")
    logger.info(f"Marvel contains {len(df_super)} lines")


def load_exported_list(filename):
    df_exported_list = pd.read_csv(f"data/{filename}")
    df_exported_list = df_exported_list.rename(columns={'Const': 'tconst'})
    return df_exported_list[['tconst']] 


if __name__ == "__main__": 
    df_merged = main(clean=False, nrows=MAX_LINE)
    #df_merged = main(clean=True, nrows=10000)
    logger.debug("\n\nMerged!")

    logger.debug("\n\n")


    q = df_merged[df_merged['nconst'].str.contains('nm0005155')]
    logger.debug(q.head())
    
    export_bond(df_merged)
    export_watched(df_merged)
    export_superheroes(df_merged)
    export_marvel(df_merged)

    # for index, row in df_exported_super.iterrows():
    #     condition = df_merged['tconst'] == row['tconst']
    #     logger.debug(f"https://www.imdb.com/title/{row['tconst']}")
    #     logger.debug(df_merged[condition].head(30))



    #df_merged = main()
    # logger.debug(df_merged.describe())

    #df_merged_after_2000 = df_merged[df_merged['startYear'].astype(int) > 2010]
    #logger.debug(df_merged_after_2000.describe())

    #df_merged_after_2000.to_csv("merged.cvs")
       