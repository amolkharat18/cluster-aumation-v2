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

# Simple custom theme via markdown/CSS
st.markdown(
    """
    <style>
    .main > .block-container { padding: 1.5rem 2rem; }
    .big-title { font-size:28px; font-weight:700; }
    .muted { color: #9aa1a6; }
    .card { background: linear-gradient(135deg, #FFFFFF 0%, #F5F8FF 100%); padding: 1rem; border-radius: 12px; box-shadow: 0 6px 18px rgba(36,44,80,0.06); }
    .status-green { color: #0f9d58; font-weight:700; }
    .status-red { color: #d93025; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='big-title'>Big Data Cluster Automation</div>", unsafe_allow_html=True)
st.markdown("<div class='muted'>Manage & inspect Cluster 14 and Cluster 17 from a single UI</div>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar controls
with st.sidebar:
    st.header("Cluster Selection")
    cluster_choice = st.selectbox("Cluster", list(CLUSTERS.keys()))
    nodes = CLUSTERS[cluster_choice]["nodes"]
    node_choice = st.selectbox("Node", list(nodes.keys()))
    host_ip = nodes[node_choice]
    st.markdown(f"**Selected Node IP:** {host_ip}")
    st.write(CLUSTERS[cluster_choice]["display"])
    st.markdown("---")
    st.markdown("**SSH / Auth**")
    st.text_input("SSH username", value=utility.SSH_USERNAME, key="ssh_user", disabled=True)
    if not utility.SSH_PASSWORD:
        st.warning("SSH password not found in .env — add PASSWORD in .env or use SSH keys (recommended).")
    st.markdown("---")
    st.caption("Actions run remote commands using Paramiko (SSH).")

# Main area: controls and output
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Hadoop Links")
    url1 = f"http://{host_ip}:9870"
    url2 = f"http://{host_ip}:8088"
    link = f'Cluster {node_choice}: <a href="{url1}" target="_blank">HDFS</a> | ' + \
            f'<a href="{url2}" target="_blank">YARN</a>'
    st.markdown(link, unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("Cluster Actions")
    if st.button("Check Hadoop status", key="check_hadoop"):
        st.info(f"Checking Hadoop on {node_choice}/{host_ip} ...")
        ok, out = utility.is_hadoop_working(host_ip)
        if ok:
            st.markdown(f"<div class='status-green'>Hadoop OK</div>", unsafe_allow_html=True)
            st.code(out)
        else:
            st.markdown(f"<div class='status-red'>Hadoop NOT OK</div>", unsafe_allow_html=True)
            st.code(out)

    if st.button("Check Apache Kafka", key="check_kafka"):
        st.info(f"Checking Kafka on {node_choice}/{host_ip} ...")
        ok, out = utility.is_apache_kafka_working(host_ip)
        if ok:
            st.markdown(f"<div class='status-green'>Kafka OK</div>", unsafe_allow_html=True)
            st.write(out)
        else:
            st.markdown(f"<div class='status-red'>Kafka NOT OK</div>", unsafe_allow_html=True)
            st.write(out)

    st.markdown("---")
    st.subheader("Service restarts")
    if st.button(f"Restart Hadoop ({node_choice})", key="restart_hadoop"):
        status_placeholder = st.empty()
        log = []
        def log_fn(msg):
            log.append(msg)
            status_placeholder.text_area("Restart Hadoop logs", value="\n".join(log), height=240)

        status_placeholder.text_area("Restart Hadoop logs", value="Starting...", height=240)
        ok, msg = utility.restart_hadoop(host_ip, log_fn=log_fn)
        if ok:
            st.success(msg)
        else:
            st.error(msg)

with col2:
    st.subheader("User / Credentials")
    with st.form("user_form"):
        action = st.radio("Action", ["Create user", "Delete user", "Reset password"])
        username_field = st.text_input("Username")
        password_field = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Run")
        if submitted:
            if not username_field:
                st.error("Please enter username")
            else:
                status_box = st.empty()
                logs = []
                def lfn(m):
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {m}")
                    status_box.text_area("Logs", value="\n".join(logs), height=220)

                if action == "Create user":
                    status_box.text("Creating user...")
                    ok, msg = utility.create_credentials(node_choice, username_field, password_field or "Hadoop@123", log_fn=lfn)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                elif action == "Delete user":
                    ok, msg = utility.delete_credentials(node_choice, username_field, log_fn=lfn)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
                else:  # Reset password
                    if not password_field:
                        st.error("Please supply new password for reset")
                    else:
                        ok, msg = utility.reset_password(node_choice, username_field, password_field, log_fn=lfn)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)

st.markdown("---")
st.caption("Built using Paramiko + Streamlit. Make sure the Streamlit server can reach the cluster hostnames over the network and that SSH credentials are valid.")
