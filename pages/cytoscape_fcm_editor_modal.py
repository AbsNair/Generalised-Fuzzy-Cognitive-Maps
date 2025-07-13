import streamlit as st
import pandas as pd
import json
from io import BytesIO
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("🧠 Generalised Fuzzy Cognitive Map Builder")

# --- Embed Cytoscape canvas (HTML contains no uploader) ---
components.html(Path("pages/cytoscape_fcm_editor_modal_embed.html").read_text(), height=550)
st.markdown("---")

# --- Single uploader in Streamlit ---
uploaded = st.file_uploader("📥 Upload your graph (JSON or GFCM)", type=["json", "gfcm"])

def normalise(data):
    """Return flat list of {group:'nodes'|'edges', data:{...}}"""
    if isinstance(data, dict):
        if "elements" in data:
            out = []
            for g in ("nodes", "edges"):
                out += [{"group": g, "data": d.get("data", d)} for d in data["elements"].get(g, [])]
            return out
        if "nodes" in data and "edges" in data:
            return ([{"group": "nodes", "data": d.get("data", d)} for d in data["nodes"]] +
                    [{"group": "edges", "data": d.get("data", d)} for d in data["edges"]])
        return []
    return data if isinstance(data, list) else []

if uploaded:
    try:
        raw = uploaded.read()
        data = json.loads(raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw)
        elems = normalise(data)
        if not elems:
            st.error("⚠️ Could not recognise JSON structure.")
            st.stop()

        nodes = []
        edges = []
        for el in elems:
            grp = el.get("group")
            d = el.get("data", {})
            if grp == "nodes":
                nodes.append({
                    "id": str(d.get("id", "")),
                    "label": d.get("label", str(d.get("id", ""))),
                    "tfn": d.get("tfn", "0.0,0.0,0.0")
                })
            elif grp == "edges":
                edges.append({
                    "source": str(d.get("source", "")),
                    "target": str(d.get("target", "")),
                    "tfn": d.get("tfn", "0.0,0.0,0.0")
                })

        labels = [n["label"] for n in nodes]
        tfns   = [f"[{n['tfn']}]" for n in nodes]

        # --- Matrix I: 1 x n, blank row 2 first cell ---
        df_I = pd.DataFrame([
            [""] + labels,
            [""] + tfns
        ])

        # --- Matrix W: n x n ---
        id_map = {n["id"]: i for i, n in enumerate(nodes)}
        size = len(nodes)
        mat = [["[0.0,0.0,0.0]"] * size for _ in range(size)]
        for e in edges:
            i = id_map.get(e["source"])
            j = id_map.get(e["target"])
            if i is not None and j is not None:
                mat[i][j] = f"[{e['tfn']}]"
        df_W = pd.DataFrame(mat, index=labels, columns=labels)
        df_W.index.name = ""

        st.subheader("📊 Export Matrices")

        # --- Excel downloads ---
        bufI = BytesIO()
        with pd.ExcelWriter(bufI, engine="openpyxl") as w:
            df_I.to_excel(w, sheet_name="Matrix_I", index=False, header=False)
        bufI.seek(0)
        st.download_button("Download Matrix I (.xlsx)", bufI, file_name="Matrix_I.xlsx")

        bufW = BytesIO()
        with pd.ExcelWriter(bufW, engine="openpyxl") as w:
            df_W.to_excel(w, sheet_name="Matrix_W")
        bufW.seek(0)
        st.download_button("Download Matrix W (.xlsx)", bufW, file_name="Matrix_W.xlsx")

        # --- Separate CSV downloads ---
        csvI = df_I.to_csv(index=False, header=False)
        st.download_button("Download Matrix I (.csv)", csvI, file_name="Matrix_I.csv", mime="text/csv")

        csvW = df_W.to_csv()
        st.download_button("Download Matrix W (.csv)", csvW, file_name="Matrix_W.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Parse error: {e}")
