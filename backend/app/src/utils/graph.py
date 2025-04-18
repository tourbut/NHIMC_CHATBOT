# LangGraph → SvelteFlow 변환기
def convert_to_svelteflow(langgraph_data):
    nodes = [
        {
            'id': node.id,
            'data': {'label': node.name},
            'type': 'input' if node.id == '__start__' else 'output' if node.id == '__end__' else 'default',
            'position': {'x': 0, 'y': 0}
        }
        for node in langgraph_data.nodes.values()
    ]
    
    edges = [
        {
            'id': f"{edge.source}-{edge.target}",
            'source': edge.source,
            'target': edge.target
        }
        for edge in langgraph_data.edges
    ]
    return nodes, edges

def draw_graph(graph):
    print("Graph preview")
    print("" + "-"*40)
    print(graph.get_graph().draw_ascii())
    print("" + "-"*40)