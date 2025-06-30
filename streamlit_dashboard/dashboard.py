import streamlit as st
import requests

st.set_page_config(page_title="East Africa Admin Lookup", layout="centered")
API_BASE = "https://admin-lookup-api.onrender.com/"


st.title("📍 Admin Locator from Coordinates")
st.markdown("Enter coordinates below to find the administrative area.")

lat = st.number_input("Latitude", value=-1.2921, format="%.6f")
lon = st.number_input("Longitude", value=36.8219, format="%.6f")
if st.button("Locate"):
    with st.spinner("Checking..."):
        resp = requests.post(f"{API_BASE}/locate", json={
            "latitude": lat,
            "longitude": lon
        })
        if resp.status_code == 200:
            data = resp.json()
            st.success("Administrative levels found:")
            st.json(data["Administrative Levels"])
        else:
            st.error("Error: " + resp.text)

st.markdown("---")
##add download button
st.subheader("📦 Download GeoJSON")
st.markdown("---")
# Store available levels and selected level in session_state
if "available_levels" not in st.session_state:
    st.session_state.available_levels = []
if "selected_level" not in st.session_state:
    st.session_state.selected_level = None
# After entering coordinates
# ---------- Check Available Levels ----------
if st.button("Check Available Levels"):
    res = requests.get(f"{API_BASE}/available-levels?latitude={lat}&longitude={lon}")
    if res.status_code == 200:
        levels = res.json().get("available_levels", [])
        if levels:
            st.session_state.available_levels = levels
            st.success("Available levels found. Please select from the dropdown.")
        else:
            st.warning("No ADM levels found for this location.")
            st.session_state.available_levels = []
    else:
        st.error("Error checking ADM levels.")

# ---------- Select Level Dropdown ----------
if st.session_state.available_levels:
    st.session_state.selected_level = st.selectbox("Select ADM Level", st.session_state.available_levels)

# ---------- Download ----------
if st.button("Download Boundary"):
    if st.session_state.selected_level:
        with st.spinner("Downloading..."):
            level = st.session_state.selected_level
            try:
                download_url = f"{API_BASE}/download?latitude={lat}&longitude={lon}&level={level.lower()}"
                response = requests.get(download_url)

                if response.status_code == 200:
                    filename = f"{level}_{lat}_{lon}.geojson"
                    st.download_button(
                        label="📥 Click to Download",
                        data=response.content,
                        file_name=filename,
                        mime="application/geo+json"
                    )
                else:
                    st.error("❌ Could not download file.")
                    st.text(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please check available levels and select one before downloading.")
st.markdown("---")
st.subheader("About")
st.markdown("Made with ❤️ by Elkana Kipruto (https://elkanakipruto.vercel.app)")
