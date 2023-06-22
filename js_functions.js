
m = ["rgba(255,0,0, 1.0)", "rgba(200,0,0, 0.75)", "rgba(100,0,0, 0.75)", "rgba(50,0,0, 0.55)"]
a = ["rgba(0,255,0, 1.0)", "rgba(0, 200,0, 0.75)", "rgba(0, 100,0, 0.75)", "rgba(0, 50,0, 0.55)"]

double_clicked = (e) => {
    console.log("Double click")
    const nodes = data.nodes['_data']

    updates = []
    Object.keys(nodes).forEach((key, index) => {
        n = nodes[key]
        n.hidden = false;
        color = n['birthYear'] ? a[0] : m[0]
        n.color = { background: color}

        updates.push(n)

    })

    data.nodes.update(updates)

    
    const edges = data.edges['_data']
    
    edges_update = []
    Object.keys(edges).forEach((key, index) => {
        edge = edges[key]
        edge.color = { color: "lightblue" }
        edge.hidden = false
        edges_update.push(edge)
    })        
    data.edges.update(Object.values(edges_update))

}

node_clicked = (e) => {
    console.log(JSON.stringify(e))

    const node_id = e.nodes[0] || ""
    const nodes = data.nodes['_data']

    if(node_id == "") {
        console.log("Empty")
        double_clicked("")
    }


    if(nodes) {
        let updates = {}
        // console.log(JSON.stringify(updates, null, 2))

        Object.keys(nodes).forEach((key, index) => {
                nodes[key].color = { background: "yellow", opacity: 1.0 }
                nodes[key].hidden = true
                delete nodes[key]['is_selected']
                updates = { [key]: nodes[key], ...updates}
                // console.log(JSON.stringify(updates, null, 2))
        })


        const degrees = 2
        let connectedNodes = [{ node: node_id, degree: 0 }] // network.getConnectedNodes(node_id);
        let allConnectedNodes = [{ node: node_id, degree: 0 }];

        // get the second degree nodes
        for (i = 1; i < degrees; i++) {
            for (j = 0; j < connectedNodes.length; j++) {

                allConnectedNodes = allConnectedNodes.concat(
                    from_connected_list(network.getConnectedNodes(connectedNodes[j].node), i)
                );
            }
        connectedNodes = allConnectedNodes
        }

        stats = new Set()
        // stats.add(node_id)
        console.log("Node-ID: " + node_id)

        m = ["rgba(255,0,0, 1.0)", "rgba(200,0,0, 0.75)", "rgba(100,0,0, 0.75)", "rgba(50,0,0, 0.55)"]
        a = ["rgba(0,255,0, 1.0)", "rgba(0, 200,0, 0.75)", "rgba(0, 100,0, 0.75)", "rgba(0, 50,0, 0.55)"]


        allConnectedNodes.forEach((key) => {
            if(!stats.has(key.node)) {
                stats.add(key.node)
                n = nodes[key.node]
            
                //if (n) {
                    color = n && n['birthYear'] ? a[key.degree] : m[key.degree]
                    n.color = { background: color}
                    n.hidden = false
                    n.is_selected = true
                    updates = { [key]: n, ...updates}
                //}
            }
            
        })

        stats.forEach(key =>{
            n = nodes[key]
            if(n) console.log(`${n['name']} - ${n['year']}`)
        })

        console.log("Updating #node " + stats.size)

        data.nodes.update(Object.values(updates))


        const edges = data.edges['_data']


        // console.log(JSON.stringify(edges, null, 2))
        edges_update = []
        Object.keys(edges).forEach((key, index) => {
            edge = edges[key]
            if (edge.to == node_id || edge.from == node_id) {
                console.log("Watch")
            }
            if(stats.has(edge.from) && stats.has(edge.to)) {
                console.log("Found edge")
                edge.hidden = false
                edge.color = { color: "rgba(255, 0, 0, 0.5)" , highlight: "rgba(255, 0, 0, 1.0)" }
            } else {
                // console.log("Found NOT edge" +edge.from + " -> " +  edge.to)
                edge.hidden = true
                edge.color = { color: "lightblue" }
            }
            edges_update.push(edge)
        })        
        data.edges.update(Object.values(edges_update))

    }

    // node = network.findNode(node_id)

    // Object.keys(nodes).forEach((key, index) => {
    //     // nodes[key].color = { background: "red" }
    //     //data.nodes.update(nodes[key])
    //     console.log(JSON.stringify(nodes[key], null, 2))
    //     // key: the name of the object key
    //     // index: the ordinal position of the key within the object 
    // })
}


from_connected_list = (nodes, degree) => {
    return nodes.map(node => ({ node: node, degree: degree}))
}