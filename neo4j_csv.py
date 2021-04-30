import csv
from feature_cleaning_1 import load_merged_data


employee_file = open('employee_file.csv', mode='w')
employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
employee_writer.writerow(['John Smith', 'Accounting', 'November'])

employee_file.close()


def write_neo4j_files(df_actors):
    actors_file = open('neo4j/import/actors_file.csv', mode='w')
    movies_file = open('neo4j/import/movies_file.csv', mode='w')
    acted_in_writer = open('neo4j/import/acted_in_file.csv', mode='w')
    already_written = set()

    # personId:ID,name,:LABEL
    actors_writer = csv.writer(actors_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    actors_writer.writerow(['personId:ID', 'primaryName', 'birthYear:int', ':LABEL'])

    movies_writer = csv.writer(movies_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    movies_writer.writerow(['movieId:ID', 'primaryTitle', 'startYear:int','genres',':LABEL'])

    acted_in_writer = csv.writer(acted_in_writer, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    acted_in_writer.writerow([':START_ID', ':END_ID', ':TYPE'])


    for index, row in df_actors.iterrows():
        if index % 99 == -1:
            return

        if not row['nconst'] in already_written:
            actors_writer.writerow([row['nconst'], row['primaryName'], row['birthYear'], 'Actor'])
            already_written.add(row['nconst'])

        if not row['tconst'] in already_written:
            movies_writer.writerow([row['tconst'], row['primaryTitle'], row['startYear'], row['genres'], 'Movie'])
            already_written.add(row['tconst'])

        acted_in_writer.writerow([row['nconst'], row['tconst'], 'ACTED_IN'])


if __name__ == "__main__":
    df_actors = load_merged_data()
    after_2010 = df_actors['startYear'].astype(int) > 2010
    before_2012 = df_actors['startYear'].astype(int) < 2012
    df_actors = df_actors[after_2010 & before_2012]
    print(df_actors.info())
    print(df_actors.describe())
    
    write_neo4j_files(df_actors)