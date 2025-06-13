import plotly.graph_objects as go

def plot_fuzzy_triangle_evolution_with_centroids(fuzzy_data_stack, iterations=15):
    fig = go.Figure()
    concepts = list(fuzzy_data_stack.keys())
    centroid_lines = {concept: {'x': [], 'y': [], 'z': []} for concept in concepts}

    for concept_idx, (concept, triples) in enumerate(fuzzy_data_stack.items()):
        for t, (lo, mid, hi) in enumerate(triples):
            y = t + 1
            x = [lo, mid, hi]
            y_fixed = [y, y, y]
            z = [0, 1, 0]

            x_loop = x + [x[0]]
            y_loop = y_fixed + [y_fixed[0]]
            z_loop = z + [z[0]]

            fig.add_trace(go.Scatter3d(
                x=x_loop, y=y_loop, z=z_loop,
                mode="lines",
                line=dict(color="blue"),
                name=f"{concept} Triangle" if t == 0 else None,
                showlegend=(t == 0)
            ))

            cx = (lo + mid + hi) / 3
            cy = y
            cz = 1 / 3

            centroid_lines[concept]['x'].append(cx)
            centroid_lines[concept]['y'].append(cy)
            centroid_lines[concept]['z'].append(cz)

            fig.add_trace(go.Scatter3d(
                x=[cx], y=[cy], z=[cz],
                mode="markers",
                marker=dict(size=4, color="red", symbol="diamond"),
                name=f"{concept} Centroid" if t == 0 else None,
                showlegend=(t == 0)
            ))

    for concept, coords in centroid_lines.items():
        fig.add_trace(go.Scatter3d(
            x=coords['x'],
            y=coords['y'],
            z=coords['z'],
            mode="lines",
            line=dict(color="red", width=6),
            name=f"{concept} Centroid Path"
        ))

    fig.update_layout(
        title="3D Fuzzy Triangles with Thick Connected Centroids",
        scene=dict(
            xaxis_title="Fuzzy Value (lo–mid–hi)",
            yaxis_title="Iteration",
            zaxis_title="Triangle Height (Z)",
            xaxis=dict(range=[0, 1]),
            yaxis=dict(range=[0, iterations + 2]),
            zaxis=dict(range=[0, 1])
        ),
        margin=dict(l=0, r=0, b=0, t=40)
    )

    return fig