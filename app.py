import streamlit as st
import pandas as pd
import json
from datetime import datetime

# 1. Configuración de la App (Paso A)
st.set_page_config(page_title="FlashCart Pro", layout="wide")
st.title("⚡ FlashCart Pro: NoSQL & Analítica RAM")

# Inicialización del almacén Key-Value en RAM
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

# 2. Interfaz de Ingesta y Búsqueda (Paso A)
col1, col2 = st.columns(2)

with col1:
    st.header("📥 SET: Guardar Carrito")
    with st.form("form_registro", clear_on_submit=True):
        id_cliente = st.text_input("ID Cliente (Clave):", placeholder="USER_123")
        carrito_json = st.text_area("Valor (JSON):", value='{"productos": ["Pan", "Leche"], "total": 12.5}')
        
        if st.form_submit_button("Inyectar a RAM"):
            if id_cliente and carrito_json:
                try:
                    data = json.loads(carrito_json)
                    # Paso C: Calcular tamaño en bytes del string JSON
                    peso = len(json.dumps(data).encode('utf-8'))
                    
                    st.session_state.kv_store[id_cliente] = {
                        "valor": data,
                        "timestamp": datetime.now(),
                        "size": peso
                    }
                    st.success(f"✅ {id_cliente} guardado con éxito ({peso} bytes).")
                except json.JSONDecodeError:
                    st.error("❌ El formato JSON no es válido.")

with col2:
    st.header("🔍 GET: Consultar Sesión")
    busqueda = st.text_input("ID a buscar:")
    if busqueda:
        if busqueda in st.session_state.kv_store:
            st.json(st.session_state.kv_store[busqueda]["valor"])
            st.info("⚡ Acceso instantáneo desde memoria RAM.")
        else:
            st.warning("⚠️ ID no encontrado (puede haber expirado).")

# --- 3. PANEL DE ANALÍTICA E INFRAESTRUCTURA (Paso B y C) ---
st.divider()
st.header("📊 Monitor de Memoria en Tiempo Real")

# Botones globales para control de sesión
b1, b2 = st.columns(2)
with b1:
    if st.button("🔄 Actualizar Cronómetros"):
        st.rerun() # Recalcula los tiempos sin borrar los datos
with b2:
    if st.button("🧹 Ejecutar Limpieza TTL"):
        num = limpiar_expirados()
        st.warning(f"Se liberaron {num} registros de la RAM.")

# Verificación de datos para mostrar gráficos
if st.session_state.kv_store:
    ahora = datetime.now()
    datos_analitica = []
    
    for k, v in st.session_state.kv_store.items():
        segundos = int((ahora - v['timestamp']).total_seconds())
        estado = "🟢 Activo" if segundos <= 60 else "🔴 Expirado"
        
        datos_analitica.append({
            "Cliente": k,
            "Bytes": v['size'],
            "Antigüedad (s)": segundos,
            "Estado": estado
        })
    
    df = pd.DataFrame(datos_analitica)

    # Paso
