
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Title
st.title("Transient Hole Cleaning Model (THCM) Dashboard")

# Sidebar inputs
st.sidebar.header("Input Parameters")

# Input sliders and fields
flow_rate_gpm = st.sidebar.slider("Flow Rate (gpm)", min_value=100, max_value=1000, value=400)
rop_mph = st.sidebar.slider("Rate of Penetration (m/h)", min_value=5, max_value=100, value=30)
rpm = st.sidebar.slider("Rotations Per Minute (RPM)", min_value=0, max_value=300, value=100)
wob_lbf = st.sidebar.slider("Weight on Bit (WOB) [lbf]", min_value=1000, max_value=60000, value=20000)
mud_density_ppg = st.sidebar.slider("Mud Density (ppg)", min_value=8.0, max_value=16.0, value=10.0)
mud_viscosity_cp = st.sidebar.slider("Mud Viscosity (cP)", min_value=10, max_value=100, value=40)

# Convert units
flow_rate_ft3s = flow_rate_gpm * 0.002228  # gpm to ft³/s
rop_fph = rop_mph * 3.28084  # m/h to ft/h

# Simulated depth range
depth = np.linspace(0, 10000, 100)

# Simulate concentration of cuttings
cuttings_conc = 0.1 + 0.00001 * wob_lbf - 0.00005 * rpm - 0.0001 * flow_rate_ft3s + 0.00002 * rop_fph
cuttings_profile = cuttings_conc * np.exp(-depth / 5000)

# Simulate bed height
bed_height = 0.5 * cuttings_profile * (mud_viscosity_cp / 40)

# Simulate bottom hole pressure
bhp = 0.052 * mud_density_ppg * depth + 0.5 * bed_height * 0.052 * mud_density_ppg

# Detect critical zones
critical_zones = depth[cuttings_profile > 0.08]

# Recommendations
st.subheader("Operational Recommendations")
if len(critical_zones) > 0:
    st.write(f"⚠️ Detected {len(critical_zones)} critical zones with poor hole cleaning.")
    st.write("Suggested actions:")
    if rpm < 200:
        st.write("- Increase RPM to improve agitation.")
    if flow_rate_gpm < 600:
        st.write("- Increase flow rate to enhance cuttings transport.")
    if wob_lbf > 30000:
        st.write("- Reduce WOB to minimize buckling and improve cleaning.")
else:
    st.write("✅ Hole cleaning is within acceptable limits.")

# Plotting
fig, ax = plt.subplots(3, 1, figsize=(6, 12))

ax[0].plot(cuttings_profile, depth)
ax[0].invert_yaxis()
ax[0].set_title("Cuttings Concentration vs Depth")
ax[0].set_xlabel("Concentration")
ax[0].set_ylabel("Depth (ft)")

ax[1].plot(bed_height, depth)
ax[1].invert_yaxis()
ax[1].set_title("Bed Height vs Depth")
ax[1].set_xlabel("Height (ft)")
ax[1].set_ylabel("Depth (ft)")

ax[2].plot(bhp, depth)
ax[2].invert_yaxis()
ax[2].set_title("Bottom Hole Pressure vs Depth")
ax[2].set_xlabel("Pressure (psi)")
ax[2].set_ylabel("Depth (ft)")

st.pyplot(fig)

# Allow file upload for real well data
st.subheader("Upload Real Well Data")
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        st.write("📄 Uploaded Well Data:")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error reading file: {e}")
