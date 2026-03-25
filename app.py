import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Log Error Extractor", layout="wide")

st.title("🚨 Log Error Extractor (TXT / CSV / Excel)")

uploaded_file = st.file_uploader(
    "📥 Upload Log File",
    type=["txt", "csv", "xlsx"]
)

# =========================
# REGEX
# =========================
REQ_ID_REGEX = r"Request ID:\s*([0-9a-fA-F\-]{36})"
VIN_REGEX = r"VIN[:=]\s*([A-Za-z0-9]+)"
DEVICE_REGEX = r"DeviceID[:=]\s*([A-Za-z0-9\-]+)"

# =========================
# READ FILE
# =========================
def read_file(file):
    filename = file.name.lower()

    if filename.endswith(".txt"):
        content = file.read().decode("utf-8", errors="ignore")
        return content.splitlines()

    elif filename.endswith(".csv"):
        df = pd.read_csv(file, dtype=str)
        return df.astype(str).apply(lambda x: " ".join(x), axis=1).tolist()

    elif filename.endswith(".xlsx"):
        df = pd.read_excel(file, dtype=str)
        return df.astype(str).apply(lambda x: " ".join(x), axis=1).tolist()

    return []

# =========================
# EXTRACT
# =========================
def extract_data(lines):
    results = []
    no = 1

    for i in range(len(lines)):
        line = str(lines[i])

        if "ERROR" in line:
            vin = None
            device = None
            request_id = None

            # VIN
            vin_match = re.search(VIN_REGEX, line)
            if vin_match:
                vin = vin_match.group(1)

            # DeviceID
            device_match = re.search(DEVICE_REGEX, line)
            if device_match:
                device = device_match.group(1)

            # Request ID (next line)
            if i + 1 < len(lines):
                next_line = str(lines[i + 1])
                req_match = re.search(REQ_ID_REGEX, next_line)
                if req_match:
                    request_id = req_match.group(1)

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
# MAIN
# =========================
if uploaded_file:
    lines = read_file(uploaded_file)

    df = extract_data(lines)

    st.success(f"✅ Extracted {len(df)} error records")
    st.dataframe(df, use_container_width=True)

    # Download CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="error_log_result.csv",
        mime="text/csv"
    )

    # Download Excel
    excel = df.to_excel(index=False, engine='openpyxl')
    st.download_button(
        label="📥 Download Excel",
        data=open("error_log_result.xlsx", "rb"),
        file_name="error_log_result.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
