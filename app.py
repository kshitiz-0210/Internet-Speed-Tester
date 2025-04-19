import streamlit as st
import speedtest
import statistics
import pandas as pd
import os
from datetime import datetime
import socket
import plotly.graph_objects as go

def get_speeds():
    try:
        st_obj = speedtest.Speedtest()
        best_server = st_obj.get_best_server()
        download_speed = st_obj.download() / 1_000_000  
        upload_speed = st_obj.upload() / 1_000_000
        latency = round(best_server['latency'], 2)
        return round(download_speed, 2), round(upload_speed, 2), latency
    except:
        return None, None, None

def get_ping_jitter(latency):
    # Use latency from Speedtest server as ping; jitter not available
    return latency, None

def get_device_id():
    return socket.gethostname()  

def log_results(device_id, timestamp, download, upload, ping_val, jitter):
    user_folder = f"speed_test_data/{device_id}"
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    
    file_path = f"{user_folder}/speed_test_results.xlsx"
    
    data = {
        "Timestamp": [timestamp],
        "Download_Mbps": [download],
        "Upload_Mbps": [upload],
        "Ping_ms": [ping_val],
        "Jitter_ms": [jitter]
    }
    
    df = pd.DataFrame(data)
    
    if os.path.exists(file_path):
        with pd.ExcelFile(file_path, engine='openpyxl') as xls:
            existing_df = pd.read_excel(xls, sheet_name="SpeedTestData")
            updated_df = pd.concat([existing_df, df], ignore_index=True)
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            updated_df.to_excel(writer, sheet_name="SpeedTestData", index=False)
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="SpeedTestData", index=False)

def load_user_logs(device_id):
    user_folder = f"speed_test_data/{device_id}"
    file_path = f"{user_folder}/speed_test_results.xlsx"
    if os.path.exists(file_path):
        return pd.read_excel(file_path, sheet_name="SpeedTestData")
    else:
        return pd.DataFrame()

st.set_page_config(page_title="🌐 Internet Speed Test", layout="centered")
st.title("🚀 Internet Speed Test")
st.markdown("Quickly check your internet performance and track trends over time.")

device_id = get_device_id()
st.markdown(f"Testing for Device: **{device_id}**")

st.markdown("Click the button below to begin the test. It may take a few seconds.")

if st.button("🔍 Start Speed Test"):
    with st.spinner("Running test..."):
        download_speed, upload_speed, latency = get_speeds()
        ping_val, jitter = get_ping_jitter(latency)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_results(device_id, timestamp, download_speed, upload_speed, ping_val, jitter)

    st.success("✅ Test Completed!")

    st.markdown("### 📊 Test Results")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📤 Upload Speed", f"{upload_speed} Mbps" if upload_speed else "Error")
        st.metric("📶 Ping", f"{ping_val} ms" if ping_val is not None else "Error")
    with col2:
        st.metric("📥 Download Speed", f"{download_speed} Mbps" if download_speed else "Error")
        st.metric("🔄 Jitter", f"{jitter} ms" if jitter is not None else "N/A")

st.markdown("### 📈 Speed History")

log_df = load_user_logs(device_id)

if not log_df.empty:
    st.dataframe(log_df.tail(10), use_container_width=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=log_df["Timestamp"],
        y=log_df["Download_Mbps"],
        mode='lines+markers',
        name='Download Speed',
        line=dict(color='royalblue', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=log_df["Timestamp"],
        y=log_df["Upload_Mbps"],
        mode='lines+markers',
        name='Upload Speed',
        line=dict(color='limegreen', width=2)
    ))

    fig.update_layout(
        title="Internet Speed Over Time",
        xaxis_title="Time",
        yaxis_title="Speed (Mbps)",
        template="plotly_white",
        hovermode="x unified",
        legend=dict(x=1, y=1, orientation="h", xanchor="right", yanchor="bottom"),
        margin=dict(l=20, r=20, t=60, b=40),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No historical test data found. Run a test to see trends here.")

st.markdown("---")
st.caption("Built by Kshitiz")
