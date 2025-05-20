import streamlit as st
import requests
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import re

# Zona horaria 
tz = pytz.timezone("America/Argentina/Mendoza")
hora_actual = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

# Configuración 
st.set_page_config(page_title="Estado GeoNodos", layout="centered")

st.markdown("""
<h2 style="margin-bottom:0;">Estado de GeoNodos Municipales</h2>
<p style="font-size:24px; margin-top:4px;">Provincia de Mendoza</p>
""", unsafe_allow_html=True)
st.markdown(f" Chequeo realizado el: **{hora_actual}**")

# Diccionario de GeoNodos
geonodos = {
    "San Martín": {"url": "https://sig.sanmartinmza.gob.ar/", "geoserver": "https://sig.sanmartinmza.gob.ar/geoserver/"},
    "Godoy Cruz": {"url": "https://ide.godoycruz.gob.ar/", "geoserver": "https://ide.godoycruz.gob.ar/geoserver/"},
    "Guaymallén": {"url": "https://ides.guaymallen.gob.ar/", "geoserver": "https://ides.guaymallen.gob.ar/geoserver/"},
    "General Alvear": {"url": "https://ides.alvearmendoza.gob.ar/", "geoserver": "https://ides.alvearmendoza.gob.ar/geoserver/"},
    "Lavalle": {"url": "https://geoserver.lavallemendoza.gob.ar/", "geoserver": "https://geoserver.lavallemendoza.gob.ar/geoserver/"},
    "Tupungato": {"url": "https://ides.tupungato.gob.ar/", "geoserver": "https://ides.tupungato.gob.ar/geoserver/"},
    "Luján de Cuyo": {"url": "https://geoportal.lujandecuyo.gob.ar/", "geoserver": "https://geoportal.lujandecuyo.gob.ar/geoserver/"},
}

# chequear el estado de un GeoNodo
def check_status(url):
    try:
        r = requests.get(url, timeout=5)
        if "lavallemendoza" in url:
            wfs_url = "https://geoserver.lavallemendoza.gob.ar/geoserver/ows?service=WFS&request=GetCapabilities"
            test = requests.get(wfs_url, timeout=5)
            if test.status_code != 200 or "<ows:Exception>" in test.text:
                return "🔴 Caído", None
            else:
                return "🟢 En línea", test.text

        if r.status_code == 200:
            if any(err in r.text for err in ["Error", "502 Bad Gateway", "404 Not Found"]):
                return "🔴 Caído", None
            return "🟢 En línea", r.text
        else:
            return f"🔴 Caído", None

    except requests.exceptions.RequestException as e:
        return "🔴 Caído", None

# Contar capas WFS
def count_wfs_layers(geoserver_url):
    try:
        wfs_url = f"{geoserver_url}wfs?request=GetCapabilities"
        response = requests.get(wfs_url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'xml')
            feature_types = soup.find_all('FeatureType')
            return len(feature_types)
        else:
            st.warning(f" Error {response.status_code} al acceder a WFS en {geoserver_url}")
            return None
    except Exception:
        return None 

# Estilos
st.markdown("""
<style>
.status-card {
    background-color: #1f1917;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    border-left: 5px solid;
    color: white;
}
.status-online {
    border-left-color: #4CAF50;
}
.status-offline {
    border-left-color: #F44336;
}
.status-card a {
    color: #4dabf7 !important;
    text-decoration: none;
}
.status-card a:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

# Mostrar resultados
for nombre, data in geonodos.items():
    estado, html = check_status(data['url'])
    status_class = "status-online" if "🟢" in estado else "status-offline"

    dataset_count = None
    fuente = ""


    # Siempre contar los datasets, independientemente del estado
    if 'geoserver' in data:
        dataset_count = count_wfs_layers(data['geoserver'])
        if dataset_count is not None:
            fuente = " (desde WFS)"
            
    count_text = f"<br> <strong>{dataset_count}</strong> datasets{fuente}" if dataset_count is not None else ""

    st.markdown(
        f"""
        <div class="status-card {status_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{nombre}</strong> → {estado}{count_text}
                </div>
                <a href="{data['url']}" target="_blank">🌐 Abrir sitio</a>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Pie de página 
st.markdown("""
<br>
<p style="font-size:18px; text-align:center; color:gray; margin-top: 10px;">
    © 2025 NPL
</p>
""", unsafe_allow_html=True)
