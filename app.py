import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Log Error Extractor", layout="wide")

st.title("🚨 Log Error Extractor Tool")

uploaded_file = st.file_uploader("📥 Upload Log File (.txt)", type=["txt"])

# =========================
# REGEX
# =========================
REQ_ID_REGEX = r"Request ID:\s*([0-9a-fA-F\-]{36})"
VIN_REGEX = r"VIN[:=]\s*([A-Za-z0-9]+)"
DEVICE_REGEX = r"DeviceID[:=]\s*([A-Za-z0-9\-]+)"

# =========================
# FUNCTION
# =========================
def extract_data(lines):
    results = []
    no = 1

    for i in range(len(lines)):
        line = lines[i]

        if "ERROR" in line:
            vin = None
            device = None
            request_id = None

            # ===== Extract VIN =====
            vin_match = re.search(VIN_REGEX, line)
            if vin_match:
                vin = vin_match.group(1)

            # ===== Extract DeviceID =====
            device_match = re.search(DEVICE_REGEX, line)
            if device_match:
                device = device_match.group(1)

            # ===== Get Request ID from next line =====
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                req_match = re.search(REQ_ID_REGEX, next_line)
                if req_match:
                    request_id = req_match.group(1)

            # ===== Append only if it's real error block =====
            if request_id or vin or device:
                results.append({
                    "No.": no,
                    "Request ID": request_id,
                    "VIN": vin,
                    "DeviceID": device
                })
                no += 1

    return pd.DataFrame(results)


# =========================
# PROCESS
# =========================
if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    lines = content.splitlines()

    df = extract_data(lines)

    st.success(f"✅ Extracted {len(df)} error records")

    st.dataframe(df, use_container_width=True)

    # Download
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="error_log_result.csv",
        mime="text/csv"
    )
