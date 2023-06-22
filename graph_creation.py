import pandas as pd
import networkx as nx
import os.path

import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
import sys


from networkx.algorithms import approximation

from feature_cleaning_1 import load_merged_data

def max_degree(G, filename):
    degrees = sorted([ (n,d) for n,d in G.degree()], key=lambda n_d: n_d[1], reverse=True)
    
    # for n_d in degrees[:20]:
    #     print(n_d[1], G.nodes[n_d[0]], f"https://www.imdb.com/name/{n_d[0]}")


    const_tag = 'const' # 'tconst' if degrees[0][0].startswith('tt') else 'nconst'

    degree_file = open(f"graph/{filename}_degree", mode='w')
    degree_writer = csv.writer(degree_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    degree_writer.writerow([const_tag, 'degree'])
    degree_writer.writerows(degrees)


def labeling(G, filename):
    labels = list(nx.algorithms.community.label_propagation_communities(G))
    labels = sorted(labels, key=len, reverse=True)

    labeling_file = open(f"graph/{filename}_labeling", mode='w')
    labeling_writer = csv.writer(labeling_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    labeling_writer.writerows(labels)

    # for index, lab in enumerate(labels[:20]):
    #     for actor in lab:
    #         print(G.nodes[actor])
    #     print("\n\n")

   
    
def show_neighbour_of_max_degress(G, filename):
    df_degree = pd.read_csv(f"graph/{filename}_degree")

    first_row = df_degree.iloc[0]
    node_id = first_row['const']

    print(f'Showing neighbour of {G.nodes[node_id]["name"]}')
    for neighbour in G.neighbors(node_id):
        print(G.nodes[neighbour]['name']) 
        

    nodes = list(G.neighbors(node_id))
    nodes.append(node_id)
    print(nodes)
    G_subgraph = G.subgraph(nodes)
    nx.write_gml(G_subgraph, f"graph/{filename}_subgraph.gml")  


def show_degree(G, filename):
    print("Showing calculated degrees")
    df_degree = pd.read_csv(f"graph/{filename}_degree")
    for index, row in df_degree.iterrows():
        print(row['degree'], G.nodes[row['const']]['name'])
        if index > 20:
            return

def show_labels(G, filename):
    print("Showing calculated labels")
    labeling_file = open(f"graph/{filename}_labeling", mode='r')
    csv_reader = csv.reader(labeling_file, delimiter=',', quotechar='"')

    for i, row in enumerate(csv_reader):
        names = [G.nodes[elem]['name'] for elem in row]
        print(f"{i}-> ", names)
        print("\n\n")    
        if i > 20:
            return    


def build_bi_graph(df):
    G = nx.Graph()    
    actors = set()
    movies = set()

    for index, row in df.iterrows():

        actor_node = row['nconst']
        movie_node = row['tconst']

        actors.add(actor_node)
        movies.add(movie_node)

        title_href = f'<a target="_blank" href="https://www.imdb.com/name/{actor_node}">{row["primaryName"]}</a>'
        movie_href = f'<a target="_blank" href="https://www.imdb.com/title/{movie_node}">{row["primaryTitle"]}</a>'
        
        
        #G.add_node(actor_node, name=row['primaryName'],  birthYear=row['birthYear'])
        #G.add_node(movie_node, name=row['primaryTitle'], year=row['startYear'])

        G.add_node(actor_node, name=row['primaryName'], title=title_href, birthYear=row['birthYear'], bipartite=0)
        G.add_node(movie_node, name=row['primaryTitle'], title=movie_href, year=row['startYear'], bipartite=1)

        # G.add_node(actor_node)
        # G.add_node(movie_node)


        G.add_edge(movie_node, actor_node, averageRating=row['averageRating'])
        #G.add_edge(movie_node, actor_node)
        if index % 10000 == 0:
            print(f"Building graph {index}")

    return G, (actors, movies)

def my_weight(G, u, v, weight="weight"):
    print(u,v)
    return 1


def build_graphs(df, filename):
    if not os.path.exists(f"graph/{filename}_bi.gml"):
        G, (actors, movies) = build_bi_graph(df)

        G_actors = nx.bipartite.collaboration_weighted_projected_graph(G, list(actors)) #, weight_function=my_weight)
        G_movies = nx.bipartite.collaboration_weighted_projected_graph(G, list(movies)) #, weight_function=my_weight)

        nx.write_gml(G, f"graph/{filename}_bi.gml")  
        nx.write_gml(G_actors, f"graph/{filename}_actors.gml")  
        nx.write_gml(G_movies, f"graph/{filename}_movies.gml")  

    return G, G_actors, G_movies



def iterate_dataframe(df, graph):
    actors = set()

    for index, row in df.iterrows():

        actor_node = row['nconst']
        movie_node = row['tconst']

        actors.add(actor_node)
        
        graph.add_node(actor_node, label=row['primaryName'], name=row['primaryName'], birthYear=row['birthYear'])
        graph.add_node(movie_node, label=row['primaryTitle'], title=row['primaryTitle'], year=row['startYear'])
        graph.add_edge(movie_node, actor_node)
        if index % 10000 == 0:
            print(f"{index}")

    print(f"Len actors {len(actors)}")
    #for movie in actors:
    #    print(movie, graph.nodes[movie])

    G = nx.bipartite.projected_graph(graph, list(actors))
    nx.write_gexf(G, "actors.gexf", prettyprint=True)

    print(nx.info(G))
    for lab in nx.algorithms.community.label_propagation_communities(G):
        for actor in lab:
            print(G.nodes[actor])
        print("\n\n")

    

def filter_merged_by(df_merged, N = 1):
    df_nconst_important = df_merged.groupby('nconst').size().loc[lambda n: n >= N].to_frame().reset_index()[['nconst']]
    return df_merged[df_merged['nconst'].isin(df_nconst_important['nconst'])]


if __name__ == "__main__":
    graph_file = "full_actors"
    #graph_file = "bond_movies"
    #graph_file = "watched_movies"
    #graph_file = "superheroes_movies"
    #graph_file = "marvel_movies"

    if not os.path.exists(f"graph/{graph_file}_bi.gml"):
        df = load_merged_data() if graph_file.startswith("full_actors") else pd.read_csv(f"processed/{graph_file}.csv")
        # df = pd.read_csv(f"processed/{graph_file}.csv")
        # df = load_merged_data()

        df = filter_merged_by(df, 1)
        print(f'Number of lines in merged file {len(df)}')
        G, G_actors, G_movies= build_graphs(df, graph_file)
    
    loadme = f"graph/{graph_file}_movies.gml"
    print(f"Loading graph {loadme}")
    G_loaded = nx.read_gml(loadme)
    print(f"Loading graph {loadme} done!")

    nx.write_gexf(G_loaded, f"{graph_file}.gexf", prettyprint=True)
    #sys.exit(0)

    #G_actors = nx.bipartite.projected_graph(G, list(actors))
    #print(nx.info(G_actors))
    # max_degree(G_actors)

    #G_movies = nx.bipartite.projected_graph(G, list(movies))
    #print(nx.info(G_movies))

    print("Max degree")
    max_degree(G_loaded, graph_file)

    print("Max labeling")
    labeling(G_loaded, graph_file)

    show_degree(G_loaded, graph_file)

    show_neighbour_of_max_degress(G_loaded, graph_file)

    #show_labels(G_loaded, graph_file)
    #print(nx.info(G_movies))

    # degree_file = open(f"graph/{graph_file}_labeling", mode='r')
    # degree_reader = csv.reader(degree_file)
    # for row in degree_reader:
    #     print(len(row))


    a = [len(c) for c in sorted(nx.connected_components(G_loaded), key=len, reverse=True)]
    print(a[0:10])


    #print(df_super_heroes.info())
    #print(df_super_heroes.describe())
    # G = nx.Graph()
    #iterate_dataframe(df_super_heroes, G)


