import streamlit as st
import speedtest
from ping3 import ping
import statistics

# -------------------------------
# Speed Test Functions
# -------------------------------

def get_speeds():
    st_text = st.empty()
    st_text.text("Running speed test...")
    try:
        st_obj = speedtest.Speedtest()
        st_obj.get_best_server()
        download_speed = st_obj.download() / 1_000_000  # Mbps
        upload_speed = st_obj.upload() / 1_000_000  # Mbps
        return round(download_speed, 2), round(upload_speed, 2)
    except Exception as e:
        return None, None

# -------------------------------
# Ping & Jitter
# -------------------------------

def get_ping_jitter(host="8.8.8.8", count=10):
    pings = []
    for _ in range(count):
        latency = ping(host, timeout=2)
        if latency is not None:
            pings.append(latency * 1000)  # convert to ms
    if len(pings) >= 2:
        avg_ping = round(statistics.mean(pings), 2)
        jitter = round(statistics.stdev(pings), 2)
    elif len(pings) == 1:
        avg_ping = round(pings[0], 2)
        jitter = 0.0
    else:
        avg_ping = None
        jitter = None
    return avg_ping, jitter

# -------------------------------
# Streamlit UI
# -------------------------------

st.set_page_config(page_title="🌐 Internet Speed Test", layout="centered")

st.title("🚀 Internet Speed Test")
st.markdown("Test your internet's **Download**, **Upload**, **Ping**, and **Jitter** in one click.")

if st.button("Start Test"):
    with st.spinner("Testing in progress... ⏳"):
        download_speed, upload_speed = get_speeds()
        ping_val, jitter = get_ping_jitter()

    st.success("Test Completed ✅")

    st.markdown("### 📊 Results")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Download Speed", f"{download_speed} Mbps" if download_speed else "Error")
        st.metric("Ping", f"{ping_val} ms" if ping_val is not None else "Error")
    with col2:
        st.metric("Upload Speed", f"{upload_speed} Mbps" if upload_speed else "Error")
        st.metric("Jitter", f"{jitter} ms" if jitter is not None else "Error")

st.markdown("---")
st.caption("Developed by Kshitiz")
