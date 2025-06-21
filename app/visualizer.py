import uuid
from pyvis.network import Network

def create_graph_visualization(graph):
    """Creates an interactive HTML graph from a networkx graph."""
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", notebook=False, directed=True)
    net.from_nx(graph)

    for node in net.nodes:
        node_data = graph.nodes[node['id']]
        node_type = node_data.get('type', 'Unknown')
        risk = node_data.get('risk', {'level': 'None'})

        # Customize node appearance based on type and risk
        color_map = {
            'Subscription': '#1E90FF',
            'Microsoft.Network/virtualNetworks': '#00C49F',
            'Subnet': '#0088FE',
            'Microsoft.Network/networkSecurityGroups': '#FFBB28',
        }
        node['color'] = color_map.get(node_type, '#FF8042')
        node['shape'] = 'box'
        node['title'] = f"Type: {node_type}\nID: {node['id']}"

        if risk.get('level') == 'High':
            node['color'] = '#FF0000'
            node['shape'] = 'ellipse'
            node['borderWidth'] = 3
            node['title'] += f"\n\nRISK (High): {risk.get('description')}"
        elif risk.get('level') == 'Medium':
            node['color'] = '#FFA500'
            node['borderWidth'] = 2
            node['title'] += f"\n\nRISK (Medium): {risk.get('description')}"

    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -30000,
          "centralGravity": 0.1,
          "springLength": 150
        },
        "minVelocity": 0.75
      }
    }
    """)
    
    report_filename = f"azure_report_{uuid.uuid4()}.html"
    report_path = f"reports/{report_filename}"
    net.save_graph(report_path)
    
    return report_filename
