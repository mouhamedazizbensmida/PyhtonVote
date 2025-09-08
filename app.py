import streamlit as st
import requests
import json
import time

st.title("Automatic POST Request Sender")

# Default request body
default_body = {
    "data": {
        "influencer_id": 1564,
        "category_id": 26
    },
    "recaptcha": "0cAFcWeA7TbuDpLiYMy0A8M5fIdTK7QBtnq97bHkr86LKwSBqSGlNGqjfgNcuQWHvRyxWdZ_dOEVoPTSNL3kRV4l66j-8hb8hDOtBEiWzYRDPDCea94-_9enbCQAoF3_d6rOinDIHdpaKNiNdhELCHHC3VAeUF-x24M5QwO0EEwbTLAMZp1msJM-ua2ZmdW_bkBq0qitRbyNi16SK8dIQ_HaukL7xoDcqAJrTbHKQ7PXnIcY3vHqkJY9szLJwFAop34eopNwDIELv56MLhUPgm7Mlmn0peyyEXRzvLnrRSwOjLhXi6zW1SIBbFtUYG71jSb-vo6u_dbY-xV5cTM3cpBGUkeYpM8ghvu2WlGan3lDUI2dVekV64Vn1Xog4cHbA_XAYrTfyMWQc3M2cH4TI39YDGsTXyfAUtEliQPqiMk5Eyjt-COhz2EW5Wsk6rGI_fDp3KIskj2boNZUpdFU0dFWeNp__jxtLm9k-mu0EY0mrqpULx1GxxPH32Zpdd_lVmkVV0CaQypRITtMsmaLQvCBAhkgbLiSwqZxFPJsywByRV5MNWvPdSK9Bh8JGNG3pxTWhucaGSo5JD4nehVZ_KVAlveDhzVJIOzgJ0B5DCSXB-theyf4jpeEldDcPtIu6yoG2jyzlXaEe7tuXm6T6ytch2hvBHiuSGBF81WDAw2ZO_JSlAVIg25Iobgrh8EMK9rMgWd_4ELIU64uqFTRIdZi3mBNK7de4u2LYR4thdJ0Ke_5pRoZpG0TLvSTxiK-HnfPkHCP2hffuwO1vjUu4GTRs1T_QeyT1LKeTstGgkElhAiI89TZsU77I3wkQrjqgBf6AbipNpc6PdXulfoAz7gvfW0h0_hMjHr02gQNmp3hMlHcce5F2U_XBSS3pl4G9Z2XUgsIOB9Jp13eKjSYBIBSxcqDJp4kEW6Bj6bSw6uzwnPw8TzxmZWqDLsXNuLnrFb5ApsTnhpAMiiGBoVycwb6CSQid0jmQP9VJF3Ot0sBM5b-kL45F3XCKJaJdBVze3APMSB47wPrQSdnHSjjlAedsCPif9pYpThmxBxutQNf68oPHn8OTZQDsmSc9EX0_K8w3XlRH-iEIfC5zRW-DadZUgzKMVkLDkeTEnP98eBKmk7-hE6vJRrZe0rBgH71d13CNiTIjRSbtTcxq6rHPNQp_6SJDsKp4qCdnMcuZ7_huO7Ri2YLul2Gv8cXO3tN5oaKTfSWL5xna42HuPFVHqioh-h6hUbDFI_9egKxlZ668gdjJytQuDQkiufZILr_aSQKUW6LSqmrqVAIqXkKE3fZZXbLqQK6Vptv3Q7aAJDOqPevfNM-bkEdt1wEUlz2K5QjFx8alTtT1rf7jL94cH2iuqFzsZyASUTP0-kvkiJLHHnVaV2nzZ5yQNkk4-4cbZZYyeEi3RX5Lc6-GEPr4TVuiPdGfMTkOGOnjU5K4GkGD9qGPLqVcJx5D2sShi7cO42r0c9Ds2fO7_k2XnIuCmcBooLZDe9ZJitrMCA4yY--FsSkOu4n5wO3l8uzdU8FQyNUvvAoe1dty0TE0tMkQ7QinxqRi1edLJHtvocKtJ830MY616eXIFbwHFhSy3KPJky2y92GRasDv0J8kHSllEhQJxk87qm5N7-Pm7nkpJAfWtGwggz_WwuCvZ4dlANd6wj3-bvWa9dtjm8Qdw-OHe923nugA3c3kjf1lUg7iEhbCPwIzxYZfo5X7062sw-Rn8psv7xvcDAs8x5Whm8OM45dkgBrSvOqeirmN5b14_SWk3wRiR5dqoEL84VwFvPjMbhbM6LGu9rg_W"
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

# Automatic sending logic
placeholder = st.empty()  # for updating status dynamically

if st.session_state.running:
    while st.session_state.running:
        try:
            response = requests.post(api_url, json=body, timeout=20000)
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
