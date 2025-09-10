import streamlit as st
import requests
import json
import time
import random
import string

st.title("Automatic POST Request Sender")

# Default request body
default_body = {
    "data": {
        "influencer_id": 1564,
        "category_id": 26
    },
    "recaptcha": "0cAFcWeA7TbuDpLiYMy0A8M5fIdTK7QBtnq97bHkr86LKwSBqSGlNGqjfgNcuQWHvRyxWdZ_dOEVoPTSNL3kRV4l66j"
}

# Editable JSON input
st.subheader("Request Body")
body_text = st.text_area("Edit JSON body:", json.dumps(default_body, indent=4), height=300)

try:
    body = json.loads(body_text)
except Exception as e:
    st.error(f"Invalid JSON: {e}")
    st.stop()

# API URL input
api_url = st.text_input("API URL", "https://api.digitalcreatorawards.com/api/influencer/vote")

# Session state initialization
for key, default in [
    ("running", False),
    ("success_count", 0),
    ("failure_count", 0),
    ("status", "Idle"),
    ("last_response", "")
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Buttons
col1, col2 = st.columns(2)
if col1.button("▶️ Start"):
    st.session_state.running = True
    st.session_state.status = "Running"

if col2.button("⏹️ Stop"):
    st.session_state.running = False
    st.session_state.status = "Stopped"

# Last response
st.subheader("Last Response")
try:
    st.json(json.loads(st.session_state.last_response))
except:
    st.text(st.session_state.last_response)

# Function to generate random suffix
def random_suffix(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Automatic sending logic
placeholder = st.empty()  # for updating status dynamically

if st.session_state.running:
    while st.session_state.running:
        try:
            # Change last 20 chars of recaptcha
            recaptcha_value = body["recaptcha"]
            if len(recaptcha_value) > 20:
                base = recaptcha_value[:-20]
            else:
                base = recaptcha_value
            body["recaptcha"] = base + random_suffix(20)

            response = requests.post(api_url, json=body, timeout=20)
            st.session_state.last_response = response.text

            if response.status_code == 200:
                st.session_state.success_count += 1
                st.session_state.failure_count = 0
            else:
                st.session_state.failure_count += 1

            # Auto stop after 10 consecutive failures
            if st.session_state.failure_count >= 10:
                st.session_state.running = False
                st.session_state.status = "Stopped: 10 consecutive failures"
                break

            # Update placeholder with current status
            with placeholder.container():
                st.text(f"Status: {st.session_state.status}")
                st.metric("✅ Successful Requests", st.session_state.success_count)
                st.metric("❌ Consecutive Failures", st.session_state.failure_count)
                try:
                    st.json(json.loads(st.session_state.last_response))
                except:
                    st.text(st.session_state.last_response)

            time.sleep(0.5)  # small delay to avoid flooding

        except requests.exceptions.ReadTimeout:
            st.session_state.failure_count += 1
            st.session_state.last_response = "Timeout!"
            if st.session_state.failure_count >= 10:
                st.session_state.running = False
                st.session_state.status = "Stopped: 10 consecutive timeouts"
                break

        except Exception as e:
            st.session_state.failure_count += 1
            st.session_state.last_response = f"Error: {e}"
            if st.session_state.failure_count >= 10:
                st.session_state.running = False
                st.session_state.status = "Stopped: 10 consecutive errors"
                break
