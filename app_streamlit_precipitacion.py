"""
Dashboard simple de precipitación con Streamlit
------------------------------------------------
Ejecutar localmente:
    pip install streamlit pandas
    streamlit run app_streamlit_precipitacion.py

Formato esperado del CSV:
    fecha,precipitacion_mm
    2025-01-01,0
    2025-01-02,3.2
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard de precipitación", page_icon="🌧️", layout="wide")


def crear_datos_ejemplo() -> pd.DataFrame:
    """Crea una serie corta para probar el dashboard sin cargar archivos."""
    fechas = pd.date_range("2025-01-01", periods=30, freq="D")
    lluvia = [
        0, 3.2, 8.1, 0, 0, 12.4, 4.6, 1.0, 0, 22.2,
        7.5, 0, 0, 15.3, 5.8, 2.1, 0, 0, 10.4, 18.0,
        3.7, 0, 0, 6.5, 13.2, 0, 2.9, 9.8, 0, 4.1,
    ]
    return pd.DataFrame({"fecha": fechas, "precipitacion_mm": lluvia})


@st.cache_data
def leer_csv(archivo) -> pd.DataFrame:
    """Lee un CSV y devuelve un DataFrame. Streamlit evita releerlo si no cambia."""
    return pd.read_csv(archivo)


def preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Valida columnas, convierte tipos y ordena la serie temporal."""
    columnas_requeridas = {"fecha", "precipitacion_mm"}
    if not columnas_requeridas.issubset(df.columns):
        faltantes = columnas_requeridas - set(df.columns)
        raise ValueError(f"Faltan columnas en el CSV: {', '.join(faltantes)}")

    limpio = df.copy()
    limpio["fecha"] = pd.to_datetime(limpio["fecha"], errors="coerce")
    limpio["precipitacion_mm"] = pd.to_numeric(limpio["precipitacion_mm"], errors="coerce")
    limpio = limpio.dropna(subset=["fecha", "precipitacion_mm"]).sort_values("fecha")
    return limpio


def calcular_resumen(df: pd.DataFrame) -> dict:
    """Calcula indicadores básicos para mostrar en el dashboard."""
    return {
        "mínimo": df["precipitacion_mm"].min(),
        "máximo": df["precipitacion_mm"].max(),
        "promedio": df["precipitacion_mm"].mean(),
        "acumulado": df["precipitacion_mm"].sum(),
    }


# En un dashboard WaPOR, esta función podría reemplazarse por una llamada a la API:
# def obtener_datos_wapor(aoi, fecha_inicio, fecha_fin, indicador):
#     """Consultar FAO WaPOR API y devolver un DataFrame listo para graficar."""
#     pass


st.title("🌧️ Dashboard simple de precipitación")
st.write(
    "Este ejemplo convierte un script de Python en una interfaz interactiva: "
    "subir datos, calcular indicadores y visualizar una serie temporal."
)

with st.sidebar:
    st.header("Datos de entrada")
    archivo = st.file_uploader("Sube un CSV", type=["csv"])
    usar_ejemplo = st.checkbox("Usar datos de ejemplo", value=True)
    st.caption("Columnas esperadas: fecha, precipitacion_mm")

try:
    if archivo is not None:
        datos_crudos = leer_csv(archivo)
    elif usar_ejemplo:
        datos_crudos = crear_datos_ejemplo()
    else:
        st.info("Sube un CSV o activa los datos de ejemplo.")
        st.stop()

    datos = preparar_datos(datos_crudos)
    resumen = calcular_resumen(datos)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mínimo", f"{resumen['mínimo']:.2f} mm")
    col2.metric("Máximo", f"{resumen['máximo']:.2f} mm")
    col3.metric("Promedio", f"{resumen['promedio']:.2f} mm/día")
    col4.metric("Acumulado", f"{resumen['acumulado']:.2f} mm")

    st.subheader("Precipitación vs tiempo")
    serie = datos.set_index("fecha")[["precipitacion_mm"]]
    st.line_chart(serie)

    with st.expander("Ver tabla de datos"):
        st.dataframe(datos, use_container_width=True)

    st.download_button(
        "Descargar datos limpios",
        data=datos.to_csv(index=False).encode("utf-8"),
        file_name="precipitacion_limpia.csv",
        mime="text/csv",
    )

except Exception as e:
    st.error("No fue posible procesar los datos.")
    st.exception(e)
