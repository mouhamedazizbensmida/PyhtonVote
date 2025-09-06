import streamlit as st
import requests
import time
import json

API_URL = "https://api.digitalcreatorawards.com/api/influencer/vote"

st.set_page_config(page_title="API Request Sender", layout="wide")

st.title("API Request Sender & Monitor")

# Default body
default_body = {
    "data": {
        "influencer_id": 1564,
        "category_id": 26
    },
    "recaptcha": "YOUR_RECAPTCHA_TOKEN_HERE"
}

# Editable JSON input
st.subheader("Request Body")
body_text = st.text_area("Edit JSON body:", json.dumps(default_body, indent=4), height=300)
try:
    body = json.loads(body_text)
except Exception as e:
    st.error(f"Invalid JSON: {e}")
    st.stop()

# Control panel
col1, col2 = st.columns(2)
with col1:
    max_failures = st.number_input("Max consecutive failures before stop:", min_value=1, value=10)
with col2:
    delay = st.number_input("Delay between requests (seconds):", min_value=0.0, value=1.0)

# Start button
if st.button("🚀 Start Sending Requests"):
    st.session_state["running"] = True
    st.session_state["success_count"] = 0
    st.session_state["failure_count"] = 0
    st.session_state["logs"] = []

# Execution loop
if st.session_state.get("running", False):
    placeholder = st.empty()
    while st.session_state["running"]:
        try:
            response = requests.post(API_URL, json=body, timeout=10)
            status_code = response.status_code

            if status_code == 200:
                st.session_state["success_count"] += 1
                st.session_state["failure_count"] = 0
                log_entry = f"✅ 200 OK - Success #{st.session_state['success_count']}"
            else:
                st.session_state["failure_count"] += 1
                log_entry = f"❌ {status_code} - Failure #{st.session_state['failure_count']}"

            st.session_state["logs"].append(log_entry)

            # Stop if too many failures
            if st.session_state["failure_count"] >= max_failures:
                st.session_state["running"] = False
                st.session_state["logs"].append("🚨 Stopped after too many failures.")
                break

            # Update UI
            with placeholder.container():
                st.metric("✅ Successful requests", st.session_state["success_count"])
                st.metric("❌ Consecutive failures", st.session_state["failure_count"])
                st.subheader("Logs")
                for log in st.session_state["logs"][-10:]:  # show last 10 logs
                    st.text(log)

            time.sleep(delay)

        except Exception as e:
            st.session_state["failure_count"] += 1
            st.session_state["logs"].append(f"⚠️ Exception: {e}")

            if st.session_state["failure_count"] >= max_failures:
                st.session_state["running"] = False
                st.session_state["logs"].append("🚨 Stopped after too many exceptions.")
                break
