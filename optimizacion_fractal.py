import numpy as np

def generate_fractal_geometry(vertices, edges, iterations=1):
    new_vertices = vertices.tolist()
    for _ in range(iterations):
        edge_to_new_vertex = {}
        for edge in edges:
            edge = tuple(sorted(edge))
            if edge not in edge_to_new_vertex:
                midpoint = (vertices[edge[0]] + vertices[edge[1]]) / 2.0
                new_vertex_index = len(new_vertices)
                new_vertices.append(midpoint)
                edge_to_new_vertex[edge] = new_vertex_index

    return np.array(new_vertices), edges