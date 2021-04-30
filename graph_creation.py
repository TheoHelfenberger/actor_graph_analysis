import pandas as pd
import networkx as nx
import os.path

import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv


from networkx.algorithms import approximation

from feature_cleaning_1 import load_merged_data

def max_degree(G, filename):
    degrees = sorted([ (n,d) for n,d in G.degree()], key=lambda n_d: n_d[1], reverse=True)
    
    for n_d in degrees[:20]:
        print(n_d[1], G.nodes[n_d[0]], f"https://www.imdb.com/name/{n_d[0]}")

    degree_file = open(f"graph/{filename}_degree", mode='w')
    degree_writer = csv.writer(degree_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    degree_writer.writerow(['nconst', 'degree'])
    degree_writer.writerows(degrees)


def labeling(G, filename):
    labels = list(nx.algorithms.community.label_propagation_communities(G))
    labels = sorted(labels, key=len, reverse=True)

    labeling_file = open(f"graph/{filename}_labeling", mode='w')
    labeling_writer = csv.writer(labeling_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    labeling_writer.writerows(labels)

    for index, lab in enumerate(labels[:20]):
        for actor in lab:
            print(G.nodes[actor])
        print("\n\n")

   
    



def max_degree2(G):
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)
    dmax = max(degree_sequence)
    print(f"Max degree {dmax}")

    plt.loglog(degree_sequence, "b-", marker="o")
    plt.title("Degree rank plot")
    plt.ylabel("degree")
    plt.xlabel("rank")

    # draw graph in inset
    plt.axes([0.45, 0.45, 0.45, 0.45])
    Gcc = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])
    pos = nx.spring_layout(Gcc)
    plt.axis("off")
    nx.draw_networkx_nodes(Gcc, pos, node_size=20)
    nx.draw_networkx_edges(Gcc, pos, alpha=0.4)
    plt.show()

def build_bi_graph(df):
    G = nx.Graph()    
    actors = set()
    movies = set()

    for index, row in df.iterrows():

        actor_node = row['nconst']
        movie_node = row['tconst']

        actors.add(actor_node)
        movies.add(movie_node)
        
        G.add_node(actor_node, name=row['primaryName'], birthYear=row['birthYear'])
        G.add_node(movie_node, title=row['primaryTitle'], year=row['startYear'])
        G.add_edge(movie_node, actor_node)
        if index % 10000 == 0:
            print(f"Building graph {index}")

    return G, (actors, movies)

def build_graphs(df, filename):
    if not os.path.exists(f"graph/{filename}_bi.gml"):
        G, (actors, movies) = build_bi_graph(df)

        G_actors = nx.bipartite.projected_graph(G, list(actors))
        G_movies = nx.bipartite.projected_graph(G, list(movies))

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
        
        graph.add_node(actor_node, name=row['primaryName'], birthYear=row['birthYear'])
        graph.add_node(movie_node, title=row['primaryTitle'], year=row['startYear'])
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

    



if __name__ == "__main__":
    graph_file = "full_actors"
    # graph_file = "bond_movies"

    if not os.path.exists(f"graph/{graph_file}_bi.gml"):
        df = pd.read_csv("processed/super_heroes.csv")
        #df = load_merged_data()
        G, G_actors, G_movies= build_graphs(df, graph_file)
    
    loadme = f"graph/{graph_file}_actors.gml"
    print(f"Loading graph {loadme}")
    G_loaded = nx.read_gml(loadme)


    #G_actors = nx.bipartite.projected_graph(G, list(actors))
    #print(nx.info(G_actors))
    # max_degree(G_actors)

    #G_movies = nx.bipartite.projected_graph(G, list(movies))
    #print(nx.info(G_movies))

    print("Plotting")

    max_degree(G_loaded, graph_file)
    labeling(G_loaded, graph_file)

    #print(nx.info(G_movies))

    # degree_file = open(f"graph/{graph_file}_labeling", mode='r')
    # degree_reader = csv.reader(degree_file)
    # for row in degree_reader:
    #     print(len(row))



    #print(df_super_heroes.info())
    #print(df_super_heroes.describe())
    # G = nx.Graph()
    #iterate_dataframe(df_super_heroes, G)


