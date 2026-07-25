import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Behavioral Anomaly Detection Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('final_results_with_explanations.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df.sort_values('timestamp').reset_index(drop=True)

df = load_data()

st.title("🛡️ AI-Powered Behavioral Anomaly Detection")
st.caption("SOC Analyst Dashboard — Live Monitoring Mode")

mode = st.sidebar.radio("Dashboard Mode", ["📊 Static Overview", "🔴 Live Feed Simulation"])

# ============ STATIC MODE ============
if mode == "📊 Static Overview":
    st.sidebar.header("Filters")
    attack_types = df[df['predicted_anomaly'] == 1]['predicted_attack_type'].unique().tolist()
    selected_types = st.sidebar.multiselect("Attack Type", options=attack_types, default=[])
    min_risk = st.sidebar.slider("Minimum Risk Score", 0.0, 1.0, 0.5, 0.01)

    alerts = df[(df['predicted_anomaly'] == 1) & (df['risk_score'] >= min_risk)]
    if selected_types:
        alerts = alerts[alerts['predicted_attack_type'].isin(selected_types)]
    else:
        alerts = alerts.iloc[0:0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sessions", f"{len(df):,}")
    col2.metric("Active Alerts", f"{len(alerts):,}")
    col3.metric("Unique Entities Flagged", f"{alerts['entity_id'].nunique():,}")
    col4.metric("Avg Risk Score", f"{alerts['risk_score'].mean():.2f}" if len(alerts) else "N/A")

    st.divider()
    st.subheader("🚨 Ranked Alert Queue")
    if selected_types:
        display_cols = ['entity_id', 'entity_type', 'timestamp', 'predicted_attack_type', 'risk_score', 'explanation']
        st.dataframe(alerts[display_cols].sort_values('risk_score', ascending=False), use_container_width=True, height=400)
    else:
        st.info("Select an attack type from the sidebar to view alerts.")

    st.divider()
    st.subheader("🔍 Entity History Lookup")
    entity_search = st.selectbox("Select an entity to inspect", options=sorted(df['entity_id'].unique()))
    entity_history = df[df['entity_id'] == entity_search].sort_values('timestamp')
    st.write(f"**{len(entity_history)}** total sessions for `{entity_search}`")
    hist_cols = ['timestamp', 'geo_location', 'source_ip', 'resource_accessed', 'auth_success', 'risk_score', 'predicted_attack_type', 'explanation']
    st.dataframe(entity_history[hist_cols], use_container_width=True, height=300)

    st.divider()
    st.subheader("📈 Risk Score Trend Over Time")
    st.caption(f"Risk score history for `{entity_search}` — spikes indicate detected anomalous sessions.")
    st.line_chart(entity_history.set_index('timestamp')['risk_score'])

# ============ LIVE FEED MODE ============
else:
    st.subheader("🔴 Live Session Feed (Simulated)")
    st.caption("Replaying historical sessions as if they're arriving in real-time. Each session is scored instantly against the pre-trained model.")

    live_attack_types = df[df['predicted_anomaly'] == 1]['predicted_attack_type'].unique().tolist()
    selected_live_types = st.sidebar.multiselect("Attack Types to Include", options=live_attack_types, default=[])
    include_normal = st.sidebar.checkbox("Also include normal sessions", value=True)

    speed = st.sidebar.slider("Playback speed (sessions/sec)", 1, 20, 5)
    batch_size = st.sidebar.slider("Sessions per tick", 1, 10, 3)
    n_replay = st.sidebar.slider("Total sessions to replay", 50, 500, 200, 50)

    start_btn = st.sidebar.button("▶️ Start Live Feed")
    stop_btn = st.sidebar.button("⏹️ Stop")

    if 'live_running' not in st.session_state:
        st.session_state.live_running = False

    if start_btn:
        if not selected_live_types:
            st.sidebar.error("Select at least one attack type to include.")
        else:
            st.session_state.live_running = True
            st.session_state.live_data = pd.DataFrame(columns=df.columns)

            attack_pool = df[(df['predicted_anomaly'] == 1) & (df['predicted_attack_type'].isin(selected_live_types))]
            normal_pool = df[df['predicted_anomaly'] == 0]

            # Always include ALL selected attack sessions (they're rare)
            guaranteed_attacks = attack_pool.copy()

            if include_normal:
                remaining_slots = max(0, n_replay - len(guaranteed_attacks))
                normal_sample_n = min(remaining_slots, len(normal_pool))
                normal_sample = normal_pool.sample(normal_sample_n, random_state=None) if normal_sample_n > 0 else normal_pool.iloc[0:0]
                combined_pool = pd.concat([guaranteed_attacks, normal_sample])
            else:
                combined_pool = guaranteed_attacks

            st.session_state.replay_pool = combined_pool.sort_values('timestamp').reset_index(drop=True)
            st.session_state.idx = 0

    if stop_btn:
        st.session_state.live_running = False

    metric_placeholder = st.empty()
    chart_placeholder = st.empty()
    table_placeholder = st.empty()

    if st.session_state.live_running:
        pool = st.session_state.replay_pool
        while st.session_state.idx < len(pool) and st.session_state.live_running:
            end_idx = min(st.session_state.idx + batch_size, len(pool))
            new_rows = pool.iloc[st.session_state.idx:end_idx]
            st.session_state.live_data = pd.concat([st.session_state.live_data, new_rows], ignore_index=True)
            st.session_state.idx = end_idx

            live_df = st.session_state.live_data
            live_alerts = live_df[live_df['predicted_anomaly'] == 1]

            with metric_placeholder.container():
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Sessions Processed", f"{len(live_df):,}")
                c2.metric("Alerts Raised", f"{len(live_alerts):,}")
                c3.metric("Entities Flagged", f"{live_alerts['entity_id'].nunique():,}")
                c4.metric("Avg Risk (live)", f"{live_df['risk_score'].mean():.2f}" if len(live_df) else "N/A")

            with chart_placeholder.container():
                st.line_chart(live_df.set_index('timestamp')['risk_score'])

            with table_placeholder.container():
                st.markdown("**Most Recent Alerts**")
                recent_alerts = live_alerts.sort_values('timestamp', ascending=False).head(10)
                st.dataframe(
                    recent_alerts[['entity_id','entity_type','timestamp','predicted_attack_type','risk_score','explanation']],
                    use_container_width=True, height=300
                )

            time.sleep(1.0 / speed)

        st.session_state.live_running = False
        st.success(f"Live feed complete — {len(st.session_state.live_data)} sessions processed.")
    else:
        st.info("Select attack type(s) above, then click ▶️ Start Live Feed in the sidebar to begin.")
