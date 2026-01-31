import streamlit as st
import json
from datetime import datetime

# 1. Configuración de la App
st.set_page_config(page_title="FlashCart Pro", layout="wide")
st.title("⚡ FlashCart Pro: Gestión de Ciclo de Vida (TTL)")

# Inicializar el almacén NoSQL en la sesión (RAM)
if 'kv_store' not in st.session_state:
    st.session_state.kv_store = {}

# --- FUNCIÓN DE LIMPIEZA TTL (Paso B) ---
def limpiar_expirados():
    ahora = datetime.now()
    # Identificamos claves con más de 60 segundos de antigüedad
    claves_a_borrar = [k for k, v in st.session_state.kv_store.items() 
                       if (ahora - v['timestamp']).total_seconds() > 60]
    for k in claves_a_borrar:
        del st.session_state.kv_store[k]
    return len(claves_a_borrar)

# 2. Interfaz de Usuario: Columnas para SET y GET
col1, col2 = st.columns(2)

with col1:
    st.header("📥 SET: Guardar Sesión")
    with st.form("registro_form", clear_on_submit=True):
        id_cliente = st.text_input("ID Cliente (Clave):", placeholder="USER_001")
        carrito_json = st.text_area("Carrito (Valor JSON):", value='{"items": ["Café", "Pan"], "total": 15.0}')
        
        if st.form_submit_button("Guardar en RAM"):
            if id_cliente and carrito_json:
                try:
                    # Guardamos el valor junto con el timestamp de creación
                    st.session_state.kv_store[id_cliente] = {
                        "valor": json.loads(carrito_json),
                        "timestamp": datetime.now()
                    }
                    st.success(f"✅ {id_cliente} guardado. TTL iniciado (60s).")
                except:
                    st.error("❌ Formato JSON inválido.")

with col2:
    st.header("🔍 GET: Buscar Cliente")
    busqueda = st.text_input("Ingresa ID para recuperar:")
    if busqueda:
        if busqueda in st.session_state.kv_store:
            st.json(st.session_state.kv_store[busqueda]["valor"])
            st.info("⚡ Dato recuperado instantáneamente de RAM.")
        else:
            st.warning("Ese ID no existe o ya expiró.")

# --- 3. MONITOR DE ESTADO Y TTL (Paso B) ---
