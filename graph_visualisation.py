from pyvis.network import Network
import networkx as nx
import csv
import os.path
import json
import pandas as pd



options_json_str = \
"""
{
	"configure": {
		"enabled": true,
		"filter": [
			"physics"
		]
	},
	"edges": {
		"color": {
			"inherit": false
		},
		"smooth": {
			"enabled": false,
			"type": "continuous"
		}
	},
    "nodes": {
		"color": {
			"background": "yellow",
            "highlight": "red"
		}
	},
	"interaction": {
		"dragNodes": true,
		"hideEdgesOnDrag": false,
		"hideNodesOnDrag": false
	},
 "physics": {
    "repulsion": {
      "nodeDistance": 205,
      "damping": 0.63
    },
    "minVelocity": 0.75,
    "solver": "repulsion"
  }

}
"""



if __name__ == "__main__":

    options = options_json_str.replace("\n", "").replace(" ", "")
    first_bracket = options.find("{")
    options = options[first_bracket:]
    print(options)
    options = json.loads(options)

    graph_file = "full_actors"
    #graph_file = "superheroes_movies"
    #graph_file = "watched_movies"
    #graph_file = "bond_movies"
    #graph_file = "marvel_movies"



    if not os.path.exists(f"graph/{graph_file}_bi.gml"):
        df = pd.read_csv(f"processed/{graph_file}.csv")
        # df = load_merged_data()
        G, G_actors, G_movies= build_graphs(df, graph_file)
    
    #loadme = f"graph/{graph_file}_actors.gml"
    loadme = f"graph/{graph_file}_subgraph.gml"
    print(f"Loading graph {loadme}")
    G_loaded = nx.read_gml(loadme,)
    print(f"Loading graph {loadme} done!")
    
    nt = Network('1024px', '2048px')
    nt.set_template("graph_template.html")
    
    

    nt.from_nx(G_loaded)

    for node in nt.nodes:
        node['label'] = node['name']

    print(f'Number of nodes = {len(nt.nodes)}')


    nt.set_options((options_json_str))
    #nt.show_buttons(filter_=['physics'])
    #nt.show_buttons(filter_=['edges', 'nodes'])
    nt.show('nx.html')