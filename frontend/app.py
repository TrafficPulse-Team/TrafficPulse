import os, requests, streamlit as st, pandas as pd, plotly.express as px

API=os.getenv("TRAFFICPULSE_API_URL","http://127.0.0.1:8000")
st.set_page_config(page_title="TrafficPulse AI",layout="wide")
st.title("TrafficPulse AI")
st.caption("Deep Learning + Computer Vision traffic monitoring and road-safety research prototype")

tab1,tab2=st.tabs(["Analyze","History"])
with tab1:
    uploaded=st.file_uploader("Upload traffic video",type=["mp4","avi","mov","mkv","m4v"])
    if uploaded and st.button("Analyze video",type="primary"):
        try:
            with st.spinner("Uploading..."):
                r=requests.post(f"{API}/videos/upload",
                    files={"file":(uploaded.name,uploaded.getvalue(),uploaded.type or "application/octet-stream")},timeout=120)
                r.raise_for_status(); vid=r.json()["video_id"]
            with st.spinner("Running detection, tracking and traffic analysis..."):
                r=requests.post(f"{API}/videos/{vid}/analyze",timeout=3600)
                r.raise_for_status(); data=r.json()
            cv=data["cv"]; intel=data["intelligence"]
            a,b,c,d=st.columns(4)
            a.metric("Vehicles",cv["total_vehicles"])
            b.metric("Traffic",intel["traffic_level"])
            c.metric("Congestion",f'{intel["congestion_score"]:.0%}')
            d.metric("Estimated speed", "N/A" if cv["average_speed"] is None else f'{cv["average_speed"]:.1f} km/h')
            counts={"Cars":cv["cars"],"Motorcycles":cv["motorcycles"],"Buses":cv["buses"],"Trucks":cv["trucks"],"Pedestrians":cv["pedestrians"]}
            fig=px.bar(x=list(counts.keys()),y=list(counts.values()),labels={"x":"Class","y":"Count"},title="Detected / counted road users")
            st.plotly_chart(fig,use_container_width=True)
            st.info("Speed is an estimate only when calibration is configured. Anomaly detection is a research baseline, not a verified accident detector.")
        except requests.RequestException as e:
            st.error(f"API error: {e}")

with tab2:
    try:
        r=requests.get(f"{API}/videos",timeout=15); r.raise_for_status()
        rows=r.json()
        st.dataframe(pd.DataFrame(rows),use_container_width=True) if rows else st.info("No analyses yet.")
    except requests.RequestException:
        st.warning("Backend is not reachable. Start FastAPI first.")
