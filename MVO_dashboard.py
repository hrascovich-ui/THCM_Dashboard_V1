import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import socket

# Configuración de página
st.set_page_config(page_title="MVO Dashboard", layout="wide")

# Modo claro/oscuro
modo = st.sidebar.radio("Modo de visualización", ["Claro", "Oscuro"])
if modo == "Oscuro":
    st.markdown(
        """
        <style>
        body { background-color: #1e1e1e; color: white; }
        .stApp { background-color: #1e1e1e; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Menú de módulos
modulo = st.sidebar.selectbox("Seleccionar módulo", ["Visualización del Pozo", "THCM Simulation", "WOB Effective"])

# Inputs generales
st.sidebar.header("Parámetros de Entrada")
rpm = st.sidebar.number_input("RPM [rpm]", value=120)
wob = st.sidebar.number_input("WOB [Klbs]", value=20.0)
caudal = st.sidebar.number_input("Caudal [gpm]", value=600)
rop = st.sidebar.number_input("ROP [m/h]", value=15.0)

# Propiedades del lodo
st.sidebar.header("Propiedades del Lodo")
densidad_lodo = st.sidebar.number_input("Densidad del lodo [ppg]", value=10.5)
pv = st.sidebar.number_input("Plastic Viscosity", value=35)
yp = st.sidebar.number_input("Yield Point", value=25)

# Geometría del pozo
st.sidebar.header("Geometría del Pozo")
diam_pozo = st.sidebar.number_input("Diámetro del pozo [in]", value=8.5)
diam_tuberia = st.sidebar.number_input("Diámetro de la tubería [in]", value=5.0)
long_tuberia = st.sidebar.number_input("Longitud de tubería [m]", value=3000)
diam_bha = st.sidebar.number_input("Diámetro del BHA [in]", value=6.5)
long_bha = st.sidebar.number_input("Longitud del BHA [m]", value=150)

# Survey
archivo_survey = st.sidebar.file_uploader("Subir archivo de survey (.csv, .xlsx)", type=["csv", "xlsx"])

# Visualización del pozo
if modulo == "Visualización del Pozo":
    st.title("Visualización del Pozo")
    if archivo_survey:
        try:
            df = pd.read_csv(archivo_survey) if archivo_survey.name.endswith(".csv") else pd.read_excel(archivo_survey, engine="openpyxl")
            st.success("Archivo cargado correctamente.")
            fig = go.Figure()
            fig.add_trace(go.Scatter3d(
                x=df["Azimuth"],
                y=df["Inclination"],
                z=df["MD"],
                mode='lines+markers',
                line=dict(color='blue', width=4),
                marker=dict(size=3),
                name="Trayectoria del Pozo"
            ))
            fig.update_layout(scene=dict(
                xaxis_title='Azimuth [°]',
                yaxis_title='Inclinación [°]',
                zaxis_title='MD [m]'
            ), title="Trayectoria 3D del Pozo")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    else:
        st.info("Por favor, suba un archivo de survey para visualizar el pozo.")

# Módulo THCM
elif modulo == "THCM Simulation":
    st.title("Simulación Transitoria THCM")
    profundidad = np.linspace(0, long_tuberia, 100)
    concentracion = np.exp(-profundidad / 1000) * (caudal / 600) * (rpm / 120)
    lecho = np.maximum(0, 1 - concentracion)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=profundidad, y=concentracion, mode='lines', name='Concentración de Recortes'))
    fig1.update_layout(title="Concentración de Recortes vs Profundidad", xaxis_title="Profundidad [m]", yaxis_title="Concentración")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=profundidad, y=lecho, mode='lines', name='Altura del Lecho'))
    fig2.update_layout(title="Altura del Lecho vs Profundidad", xaxis_title="Profundidad [m]", yaxis_title="Altura relativa")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Recomendaciones Operativas")
    if np.min(concentracion) < 0.3:
        st.warning("⚠️ Se recomienda aumentar RPM o caudal para mejorar la limpieza.")
    else:
        st.success("✅ La eficiencia de limpieza es adecuada.")

# Módulo WOB Effective
elif modulo == "WOB Effective":
    st.title("Análisis de WOB Efectivo")
    inclinacion = np.linspace(0, 90, 100)
    wob_real = wob * np.exp(-inclinacion / 45) * (1 - np.minimum(1, np.exp(-inclinacion / 30)))

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=inclinacion, y=wob_real, mode='lines', name='WOB Efectivo'))
    fig3.update_layout(title="WOB Efectivo vs Inclinación", xaxis_title="Inclinación [°]", yaxis_title="WOB Real [Klbs]")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Recomendaciones")
    if np.min(wob_real) < wob * 0.5:
        st.warning("⚠️ El WOB efectivo es bajo. Verificar pandeo y acumulación de recortes.")
    else:
        st.success("✅ El WOB efectivo está dentro del rango esperado.")
