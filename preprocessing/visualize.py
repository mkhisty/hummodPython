import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

def visualize_dependencies(json_file="map.json"):
    """
    Create a visual graph of the dependency structure from the JSON file.
    """
    # Load the dependency map
    with open(json_file, 'r') as f:
        dependencyMap = json.load(f)
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add all nodes first
    for file in dependencyMap.keys():
        G.add_node(file)
    
    # Add edges for dependencies
    for file, data in dependencyMap.items():
        for dep in data['dependencies']:
            dep_file = dep + ".DES"
            if dep_file in dependencyMap:  # Only add edge if target exists
                G.add_edge(file, dep_file)
    
    # Create the visualization
    plt.figure(figsize=(16, 12))
    
    # Use spring layout for better node distribution
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    # Color nodes based on dependency count
    node_counts = [dependencyMap[node]['count'] for node in G.nodes()]
    max_count = max(node_counts) if node_counts else 1
    
    # Create custom colormap
    colors = ['#e8f4fd', '#4a90e2', '#1e3a8a', '#0f172a']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('dependency', colors, N=n_bins)
    
    # Normalize counts for coloring
    normalized_counts = [count / max_count for count in node_counts]
    
    # Size nodes based on in-degree (how many things depend on them)
    in_degrees = dict(G.in_degree())
    node_sizes = [max(200, in_degrees[node] * 100 + 300) for node in G.nodes()]
    
    # Draw the graph
    nx.draw_networkx_nodes(G, pos, 
                          node_color=normalized_counts,
                          node_size=node_sizes,
                          cmap=cmap,
                          alpha=0.8,
                          linewidths=1,
                          edgecolors='white')
    
    # Draw edges with varying transparency based on target dependency count
    edge_alphas = []
    for edge in G.edges():
        target_count = dependencyMap[edge[1]]['count']
        alpha = 0.1 + (target_count / max_count) * 0.4
        edge_alphas.append(alpha)
    
    nx.draw_networkx_edges(G, pos,
                          alpha=0.3,
                          edge_color='gray',
                          arrows=True,
                          arrowsize=10,
                          arrowstyle='->',
                          width=0.5,
                          connectionstyle="arc3,rad=0.1")
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=max_count))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=plt.gca(), shrink=0.8)
    cbar.set_label('Dependency Count', rotation=270, labelpad=20)
    
    plt.title('Dependency Graph\n(Node size = in-degree, Color = dependency count)', 
              fontsize=16, pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('dependency_graph.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.savefig('dependency_graph.pdf', bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    plt.show()
    
    # Print some graph statistics
    print(f"Graph Statistics:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"  Density: {nx.density(G):.3f}")
    print(f"  Is DAG: {nx.is_directed_acyclic_graph(G)}")
    
    if nx.is_directed_acyclic_graph(G):
        try:
            print(f"  Longest path: {len(nx.dag_longest_path(G)) - 1}")
        except:
            print("  Could not compute longest path")
    
    # Find nodes with highest in-degree (most depended upon)
    in_deg_sorted = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)
    print(f"\n  Most depended upon files:")
    for file, degree in in_deg_sorted[:5]:
        print(f"    {file}: {degree} dependents")
    
    # Find nodes with highest dependency count
    dep_sorted = sorted(dependencyMap.items(), key=lambda x: x[1]['count'], reverse=True)
    print(f"\n  Files with most dependencies:")
    for file, data in dep_sorted[:5]:
        print(f"    {file}: {data['count']} total dependencies")

if __name__ == "__main__":
    visualize_dependencies()