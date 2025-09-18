import paramiko
from dotenv import dotenv_values
import time
import traceback

# Load .env (expects USERNAME and PASSWORD)
config = dotenv_values(".env")
SSH_USERNAME = config.get("USERNAME", "projadm")
SSH_PASSWORD = config.get("PASSWORD", "")

# --- Utilities: SSH and command helpers (based on your original app.py) ---
SSH_CONNECT_TIMEOUT = 10

def get_ssh(hostname):
    """
    Create and return a connected paramiko.SSHClient using PASSWORD auth.
    (If you prefer keys, update this function accordingly.)
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname=hostname,
        username=SSH_USERNAME,
        password=SSH_PASSWORD,
        timeout=SSH_CONNECT_TIMEOUT,
    )
    return ssh


def run_cmd(hostname, cmd, timeout=60):
    """
    Execute a remote command and return (exit_status, stdout, stderr).
    """
    ssh = None
    try:
        ssh = get_ssh(hostname)
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode(errors="ignore")
        err = stderr.read().decode(errors="ignore")
        exit_status = stdout.channel.recv_exit_status()
        return exit_status, out, err
    finally:
        if ssh:
            ssh.close()


# ---------------------------
# Health checks & service ops
# ---------------------------
def is_hadoop_working(hostname):
    try:
        cmd = "hdfs dfsadmin -report"
        exit_status, out, err = run_cmd(hostname, cmd, timeout=30)
        ok = "Configured Capacity" in out
        snippet = out[:] or err[:600]
        return ok, snippet
    except Exception as e:
        return False, f"Exception: {e}"

def is_apache_kafka_working(hostname):
    try:
        cmd1 = 'export JAVA_HOME="/usr/lib/jvm/java-21-openjdk-21.0.8.0.9-1.el9.x86_64"'
        exit_status1, out1, err1 = run_cmd(hostname, cmd1, timeout=30)

        cmd2 = "kafka-topics.sh --list --bootstrap-server localhost:9092"
        exit_status2, out2, err2 = run_cmd(hostname, cmd2, timeout=30)

        if len(out2.strip()) > 0:
            return True, f"{len(out2.splitlines())} topics found"
        else:
            return True, "No topics found"
    
    except Exception as e:
        return False, f"Exception: {e}"

# Restart helpers (shortened/wrapped versions of your original functions to stream output)
def restart_hadoop(hostname, log_fn=print):
    # Stops and starts Hadoop services (same sequence you had)
    try:
        log_fn("Stopping YARN...")
        run_cmd(hostname, 'stop-yarn.sh')
        time.sleep(3)
        log_fn("Stopping DFS...")
        run_cmd(hostname, 'stop-dfs.sh')
        time.sleep(3)
        log_fn("Starting DFS...")
        run_cmd(hostname, 'start-dfs.sh')
        time.sleep(3)
        log_fn("Starting YARN...")
        run_cmd(hostname, 'start-yarn.sh')
        time.sleep(3)
        log_fn("Restart Completed.")
        return True, "Hadoop restart completed."
    except Exception as e:
        return False, f"Exception during restart_hadoop: {e}\n{traceback.format_exc()}"

