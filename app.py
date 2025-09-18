# app.py
import streamlit as st
import time
from datetime import datetime
import traceback
import utility  # Assuming this contains your SSH and command functions

# --- Cluster definitions ---
CLUSTERS = {
    "Cluster 14": {
        "display": "Cluster 14 (namenode: node14, datanodes: node15, node16)",
        "nodes": {
            "node14": "10.232.167.203",
            "node15": "10.232.167.192",
            "node16": "10.232.167.119"
        }
    },
    "Cluster 17": {
        "display": "Cluster 17 (namenode: node17, datanodes: node18, node19)",
        "nodes": {
            "node17": "10.232.167.231",
            "node18": "10.232.167.66",
            "node19": "10.232.167.44"
        }
    }
}

# --- Streamlit UI ---
st.set_page_config(page_title="Big Data Cluster Automation", layout="wide", initial_sidebar_state="expanded")

# --- Simple custom theme via markdown/CSS ---
st.markdown(
    """
    <style>
        :root {
            --bg-primary: #0A1633;
            --bg-secondary: linear-gradient(135deg, rgba(34, 83, 197, 0.95), rgba(27, 148, 230, 0.95));
            --card-bg: #ffffff;
            --accent: #1F6FEB;
            --accent-soft: rgba(31, 111, 235, 0.1);
        }

        .main {
            background: linear-gradient(180deg, rgba(10, 22, 51, 0.94) 0%, rgba(12, 35, 68, 0.94) 60%, rgba(14, 47, 89, 0.96) 100%),
                        url('https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80');
            background-size: cover;
        }

        .main > .block-container {
            padding-top: 2.5rem;
            padding-bottom: 4rem;
        }

        .hero-card {
            background: var(--bg-secondary);
            border-radius: 20px;
            padding: 2.2rem 2.8rem;
            color: white;
            box-shadow: 0 30px 45px rgba(0, 0, 0, 0.25);
            position: relative;
            overflow: hidden;
        }

        .hero-card::after {
            content: "";
            position: absolute;
            top: -60px;
            right: -60px;
            width: 220px;
            height: 220px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 50%;
        }

        .hero-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 0.35rem;
            letter-spacing: 0.02em;
        }

        .hero-subtitle {
            font-size: 16px;
            opacity: 0.85;
            margin-bottom: 0.4rem;
        }

        .hero-tag {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background-color: rgba(255, 255, 255, 0.15);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 18px;
            padding: 1.35rem 1.5rem;
            box-shadow: 0 22px 40px rgba(13, 27, 62, 0.25);
            backdrop-filter: blur(6px);
        }

        .section-title {
            color: #0c203f;
            font-weight: 700;
            font-size: 18px;
            letter-spacing: 0.04em;
        }

        .status-green { color: #33d69f; font-weight: 700; }
        .status-red { color: #ff6b6b; font-weight: 700; }

        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.4);
            border-radius: 999px;
            padding: 0.6rem 1.4rem;
            color: #0c203f;
            font-weight: 600;
            border: 1px solid transparent;
        }
        .stTabs [aria-selected="true"] {
            background-color: var(--accent);
            color: white !important;
            box-shadow: 0 14px 24px rgba(31, 111, 235, 0.35);
        }

        .metric-card {
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
            padding: 1.1rem 1.3rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.9);
            box-shadow: 0 18px 30px rgba(22, 35, 69, 0.25);
        }

        .metric-label {
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.18em;
            color: rgba(12, 32, 63, 0.65);
            font-weight: 600;
        }

        .metric-value {
            font-size: 24px;
            font-weight: 700;
            color: #0c203f;
        }

        .stButton>button {
            background: linear-gradient(135deg, #1f6feb 0%, #22a8f2 90%);
            color: white;
            border-radius: 999px;
            border: none;
            padding: 0.55rem 1.5rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            box-shadow: 0 12px 22px rgba(31, 111, 235, 0.35);
            transition: transform 0.15s ease, box-shadow 0.2s ease;
        }

        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 16px 30px rgba(31, 111, 235, 0.45);
        }

        .stAlert, .stTextArea, .stRadio, .stSelectbox, .stTextInput, .stMarkdown {
            color: #0c203f;
        }

        .log-area textarea {
            background-color: rgba(15, 32, 63, 0.07) !important;
            border-radius: 14px !important;
            border: 1px solid rgba(15, 32, 63, 0.12) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Hero Header ---
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-tag">Operational Console</div>
        <div class="hero-title">Big Data Cluster Automation</div>
        <div class="hero-subtitle">Monitor health, orchestrate services and administer user access across clusters 14 & 17.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
    <style>
        .sidebar .sidebar-content { background-color: #0b1833; }
    </style>
""", unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.image(
        "https://img.icons8.com/color/96/cluster.png",
        width=64,
        caption="Cluster automation",
    )
    st.header("Cluster Lens")
    cluster_choice = st.selectbox("Cluster", list(CLUSTERS.keys()))
    nodes = CLUSTERS[cluster_choice]["nodes"]
    node_choice = st.selectbox("Node", list(nodes.keys()), help="Pick a target node to run checks on.")
    host_ip = nodes[node_choice]

    st.markdown("""
        <div class="metric-card" style="margin-top:1.1rem;">
            <div class="metric-label">Selected Node</div>
            <div class="metric-value">{node}</div>
            <div style="color: rgba(12,32,63,0.58); font-size: 13px;">IP: {ip}</div>
        </div>
    """.format(node=node_choice, ip=host_ip), unsafe_allow_html=True)

    st.markdown("""
        <div class="card" style="margin-top:1.3rem;">
            <div class="section-title" style="margin-bottom:0.6rem;">Cluster profile</div>
            <p style="font-size:14px; line-height:1.45; margin-bottom:0;">{desc}</p>
        </div>
    """.format(desc=CLUSTERS[cluster_choice]["display"]), unsafe_allow_html=True)

    st.markdown("""
        <div class="card" style="margin-top:1.3rem;">
            <div class="section-title" style="margin-bottom:0.8rem;">SSH / Auth</div>
    """, unsafe_allow_html=True)
    st.text_input("SSH username", value=utility.SSH_USERNAME, key="ssh_user", disabled=True)
    if not utility.SSH_PASSWORD:
        st.warning(
            "SSH password not found in .env — add PASSWORD in .env or use SSH keys (recommended)."
        )
    st.markdown("""<p style='font-size:12px; color:rgba(12,32,63,0.55); margin-top:0.6rem;'>All actions run remote commands over Paramiko SSH.</p></div>""", unsafe_allow_html=True)

# Main area: controls and output
overview_tab, ops_tab, users_tab = st.tabs([
    "Overview & Links",
    "Cluster Operations",
    "User Administration",
])

with overview_tab:
    st.markdown("<div class='section-title'>Cluster snapshot</div>", unsafe_allow_html=True)
    cards = st.columns(3)
    cards[0].markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Active Cluster</div>
            <div class="metric-value">{cluster}</div>
            <div style="color: rgba(12,32,63,0.55); font-size: 13px;">Nodes: {count}</div>
        </div>
        """.format(cluster=cluster_choice, count=len(nodes)),
        unsafe_allow_html=True,
    )
    cards[1].markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Target Node</div>
            <div class="metric-value">{node_choice}</div>
            <div style="color: rgba(12,32,63,0.55); font-size: 13px;">IP: {host_ip}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cards[2].markdown(
        """
        <div class="metric-card">
            <div class="metric-label">Utilities</div>
            <div class="metric-value">Paramiko</div>
            <div style="color: rgba(12,32,63,0.55); font-size: 13px;">Secured via SSH</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("""
        <div class="card" style="margin-top:1.6rem;">
            <div class="section-title" style="margin-bottom:0.9rem;">Hadoop dashboards</div>
            <div style="font-size:15px; line-height:1.7;">
                <a href="http://{ip}:9870" target="_blank" style="color:#1F6FEB; font-weight:600; text-decoration:none;">HDFS NameNode UI</a><br/>
                <a href="http://{ip}:8088" target="_blank" style="color:#1F6FEB; font-weight:600; text-decoration:none;">YARN Resource Manager</a>
            </div>
            <p style="color: rgba(12,32,63,0.6); font-size:12px; margin-top:1.2rem;">Links open in a new tab to preserve session context.</p>
        </div>
    """.format(ip=host_ip), unsafe_allow_html=True)

with ops_tab:
    st.markdown("<div class='section-title'>Health Checks</div>", unsafe_allow_html=True)
    with st.container():
        col_actions = st.columns(2)
        with col_actions[0]:
            if st.button("Check Hadoop status", key="check_hadoop"):
                st.info(f"Checking Hadoop on {node_choice}/{host_ip} ...")
                ok, out = utility.is_hadoop_working(host_ip)
                if ok:
                    st.markdown(
                        "<div class='status-green'>Hadoop OK</div>",
                        unsafe_allow_html=True,
                    )
                    st.code(out)
                else:
                    st.markdown(
                        "<div class='status-red'>Hadoop NOT OK</div>",
                        unsafe_allow_html=True,
                    )
                    st.code(out)
        with col_actions[1]:
            if st.button("Check Apache Kafka", key="check_kafka"):
                st.info(f"Checking Kafka on {node_choice}/{host_ip} ...")
                ok, out = utility.is_apache_kafka_working(host_ip)
                if ok:
                    st.markdown(
                        "<div class='status-green'>Kafka OK</div>",
                        unsafe_allow_html=True,
                    )
                    st.write(out)
                else:
                    st.markdown(
                        "<div class='status-red'>Kafka NOT OK</div>",
                        unsafe_allow_html=True,
                    )
                    st.write(out)

    st.markdown("""
        <div class="card" style="margin-top:1.9rem;">
            <div class="section-title" style="margin-bottom:0.9rem;">Service Restarts</div>
    """, unsafe_allow_html=True)
    restart_container = st.container()
    with restart_container:
        if st.button(f"Restart Hadoop ({node_choice})", key="restart_hadoop"):
            status_placeholder = st.empty()
            log = []

            def log_fn(msg):
                log.append(msg)
                status_placeholder.text_area(
                    "Restart Hadoop logs",
                    value="\n".join(log),
                    height=240,
                )

            status_placeholder.text_area(
                "Restart Hadoop logs",
                value="Starting...",
                height=240,
            )
            ok, msg = utility.restart_hadoop(host_ip, log_fn=log_fn)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
    st.markdown("</div>", unsafe_allow_html=True)

with users_tab:
    st.markdown("<div class='section-title'>Identity Operations</div>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: rgba(12,32,63,0.62); font-size:14px;'>Create, delete or reset credentials for Hadoop ecosystem services. Actions are executed on the selected node.</p>",
        unsafe_allow_html=True,
    )
    with st.form("user_form"):
        action = st.radio("Action", ["Create user", "Delete user", "Reset password"], horizontal=True)
        username_field = st.text_input("Username", placeholder="Enter Linux service account")
        password_field = st.text_input("Password", type="password", placeholder="Leave blank to auto-generate")
        submitted = st.form_submit_button("Run command")
        if submitted:
            if not username_field:
                st.error("Please enter username")
            else:
                status_box = st.empty()
                logs = []

                def lfn(m):
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")
                    status_box.text_area(
                        "Logs",
                        value="\n".join(logs),
                        height=220,
                    )

                if action == "Create user":
                    status_box.text("Creating user...")
                    ok, msg = utility.create_credentials(
                        node_choice,
                        username_field,
                        password_field or "Hadoop@123",
                        log_fn=lfn,
                    )
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                elif action == "Delete user":
                    ok, msg = utility.delete_credentials(
                        node_choice, username_field, log_fn=lfn
                    )
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:  # Reset password
                    if not password_field:
                        st.error("Please supply new password for reset")
                    else:
                        ok, msg = utility.reset_password(
                            node_choice, username_field, password_field, log_fn=lfn
                        )
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

st.markdown("""
    <p style='color: rgba(255,255,255,0.72); font-size: 13px; text-align:center; margin-top:2.8rem;'>
        Built using Paramiko + Streamlit. Ensure the Streamlit server can reach cluster nodes and that SSH credentials are valid.
    </p>
""", unsafe_allow_html=True)
