
import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
from io import BytesIO
import tempfile

from fuzzy_pipeline import fuzzy_pipeline, parse_interval
from plot_fuzzy_3D_triangle_evolution import plot_fuzzy_triangle_evolution_with_centroids

st.set_page_config(page_title='Generalised FCM Simulator', layout='wide')
st.title('Generalised Fuzzy Cognitive Maps Simulator')

# Sidebar inputs
st.sidebar.header('Upload Data')
W_file = st.sidebar.file_uploader('Upload W matrix (CSV or XLSX)', type=['csv','xlsx'])
I_file = st.sidebar.file_uploader('Upload I vector (CSV or XLSX)', type=['csv','xlsx'])

if W_file and I_file:
    try:
        W_df = (pd.read_csv(W_file, index_col=0)
                if W_file.name.endswith('.csv') else
                pd.read_excel(W_file, index_col=0))
        I_df = (pd.read_csv(I_file, index_col=0)
                if I_file.name.endswith('.csv') else
                pd.read_excel(I_file, index_col=0))
    except Exception as e:
        st.error(f'Error reading files: {e}')
        st.stop()

    concepts = list(W_df.index)
    if list(W_df.columns) != concepts:
        st.error('🔴 W rows and columns must have identical labels.')
        st.stop()

    if I_df.shape[1] == 1 and list(I_df.index) == concepts:
        I_df = I_df.T
    if list(I_df.columns) != concepts:
        st.error('🔴 I vector must have same concept names as W columns.')
        st.stop()

    # Simulation controls
    st.sidebar.header('Simulation Parameters')
    lam = st.sidebar.slider('λ (steepness)', 0.1, 3.0, 1.0, 0.1)
    iterations = st.sidebar.slider('Iterations', 1, 100, 15, 1)
    clamp_concepts = st.sidebar.multiselect('Clamp Concepts', concepts)
    layout_option = st.sidebar.selectbox(
        'Network Layout',
        ['spring','circular','shell','kamada_kawai','spectral','hierarchical']
    )

    if st.sidebar.button('Run Simulation'):
        fuzzy_hist, crisp_hist, names = fuzzy_pipeline(
            W_df, I_df,
            clamp_concepts=clamp_concepts,
            lam=lam,
            iterations=iterations
        )
        st.session_state.run_sim = True
        st.session_state.fuzzy_hist = fuzzy_hist
        st.session_state.crisp_hist = crisp_hist
        st.session_state.names = names

    if st.session_state.get('run_sim'):
        # Centroid Table
        df_cent = pd.DataFrame(
            np.stack(st.session_state.crisp_hist),
            columns=st.session_state.names
        )
        df_cent.index.name = 'Iteration'
        st.subheader('Centroid Table')
        st.dataframe(df_cent)
        st.download_button(
            'Download Centroids CSV',
            df_cent.to_csv().encode(),
            'centroids.csv'
        )

        # 2D Centroid Evolution Charts
        st.subheader('Centroid Evolution (2D)')
        sel = st.multiselect('Select concepts for 2D plot', st.session_state.names, default=st.session_state.names[:3])
        if sel:
            fig2 = go.Figure()
            for c in sel:
                idx = st.session_state.names.index(c)
                fig2.add_trace(go.Scatter(
                    x=list(range(len(st.session_state.crisp_hist))),
                    y=[v[idx] for v in st.session_state.crisp_hist],
                    mode='lines+markers',
                    name=c
                ))
            fig2.update_layout(
                title='Centroid Trajectories',
                xaxis_title='Iteration',
                yaxis_title='Centroid Value',
                legend_title='Concept'
            )
            st.plotly_chart(fig2, use_container_width=True)
            buf2 = BytesIO()
            try:
                fig2.write_image(buf2, format='png')
                st.download_button(
                    'Download 2D Centroid Plot',
                    buf2.getvalue(),
                    'centroid_2d.png',
                    'image/png'
                )
            except:
                st.warning('⚠️ Install Kaleido for 2D image export: `pip install --upgrade kaleido`')

        # Graph Theoretical Indices
        st.subheader('Graph Theoretical Indices')
        G = nx.DiGraph()
        G.add_nodes_from(st.session_state.names)
        for i,u in enumerate(st.session_state.names):
            for j,v in enumerate(st.session_state.names):
                lo, mid, hi = parse_interval(str(W_df.iloc[i,j]))
                if not (lo==0 and mid==0 and hi==0):
                    G.add_edge(u, v, weight=mid)
        metrics = {
            'Degree Centrality': nx.degree_centrality(G),
            'In-Degree': dict(G.in_degree()),
            'Out-Degree': dict(G.out_degree()),
            'Betweenness': nx.betweenness_centrality(G),
            'Closeness': nx.closeness_centrality(G)
        }
        df_metrics = pd.DataFrame(metrics)
        df_metrics.index.name = 'Concept'
        st.dataframe(df_metrics)
        st.download_button(
            'Download Graph Metrics CSV',
            df_metrics.to_csv().encode(),
            'graph_metrics.csv'
        )

        # Network Visualization
        st.subheader('W-Network Visualization')
        for n,val in zip(st.session_state.names, I_df.values.tolist()[0]):
            G.nodes[n]['I'] = val
        if layout_option == 'hierarchical':
            try:
                pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
            except:
                st.warning('Install pygraphviz or pydot for hierarchical layouts.')
                pos = nx.spring_layout(G)
        else:
            pos = getattr(nx, f"{layout_option}_layout")(G)

        edge_x, edge_y, edge_annotations = [], [], []
        for u,v,data in G.edges(data=True):
            x0,y0 = pos[u]; x1,y1 = pos[v]
            edge_x += [x0, x1, None]; edge_y += [y0, y1, None]
            edge_annotations.append(dict(ax=x0, ay=y0, axref='x', ayref='y',
                                      x=x1, y=y1, xref='x', yref='y',
                                      showarrow=True, arrowhead=3,
                                      arrowsize=1, arrowwidth=1, arrowcolor='grey'))
        node_x = [pos[n][0] for n in G.nodes()]; node_y = [pos[n][1] for n in G.nodes()]
        node_text = [f"{n}<br>I={G.nodes[n]['I']}" for n in G.nodes()]

        fig_net = go.Figure()
        fig_net.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(color='grey'), hoverinfo='none'))
        fig_net.add_trace(go.Scatter(
            x=node_x, y=node_y, mode='markers+text',
            marker=dict(size=20, color='skyblue'),
            text=list(G.nodes()), textposition='top center',
            hovertext=node_text, hoverinfo='text'
        ))
        fig_net.update_layout(
            title='FCM Directed Network',
            showlegend=False,
            annotations=edge_annotations,
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            margin=dict(t=30, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_net, use_container_width=True)

        # 3D Fuzzy Triangle Evolution (replaced)
        st.subheader('3D Fuzzy Triangle Evolution')
        selected_3d = st.multiselect(
            'Select Concept(s) for 3D Evolution',
            st.session_state.names,
            default=st.session_state.names
        )

        # Prepare data per concept
        fuzzy_data_stack = {c: [] for c in st.session_state.names}
        for step in st.session_state.fuzzy_hist:
            for i, c in enumerate(st.session_state.names):
                fuzzy_data_stack[c].append(step[i])

        # Filter to only selected concepts
        filtered_data = {c: fuzzy_data_stack[c] for c in selected_3d}

        # Generate and display the 3D triangle evolution plot
        fig3d = plot_fuzzy_triangle_evolution_with_centroids(
            filtered_data,
            iterations=len(st.session_state.fuzzy_hist)
        )
        # Correct axes and titles
        fig3d.update_layout(
            title='3D Fuzzy Triangle Evolution',
            scene=dict(
                xaxis_title='Value',
                yaxis_title='Iteration',
                zaxis_title='Height',
                xaxis=dict(range=[-1, 1]),
                yaxis=dict(range=[0, len(st.session_state.fuzzy_hist)]),
                zaxis=dict(range=[0, 1]),
            ),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig3d, use_container_width=True)

        # Export 3D plot as HTML
        buf_html = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        fig3d.write_html(buf_html.name)
        with open(buf_html.name, "rb") as fp:
            st.download_button(
                'Download 3D Plot as HTML',
                fp,
                file_name='fuzzy_3d_plot.html',
                mime='text/html'
            )

        # Export 3D plot as PNG image
        try:
            buf_png = BytesIO()
            fig3d.write_image(buf_png, format='png')
            st.download_button(
                'Download 3D Plot as PNG',
                buf_png.getvalue(),
                file_name='fuzzy_3d_plot.png',
                mime='image/png'
            )
        except Exception:
            st.warning('⚠️ Install Kaleido for 3D image export: `pip install --upgrade kaleido`')
