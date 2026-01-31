import streamlit as st
import pandas as pd
import json
from datetime import datetime

# 1. Configuración de la App
st.set_page_config(page_title="FlashCart Pro", layout="wide")
st.title("⚡ FlashCart Pro: Analítica de RAM")

if 'kv_store' not in st.session_state:
    st.session_state.kv_store = {}

# --- Función de Limpieza TTL ---
def limpiar_expirados():
    ahora = datetime.now()
    claves_a_borrar = [k for k, v in st.session_state.kv_store.items() 
                       if (ahora - v['timestamp']).total_seconds() > 60]
    for k in claves_a_borrar:
        del st.session_state.kv_store[k]
    return len(claves_a_borrar)

# 2. Ingesta de Datos (SET)
col1, col2 = st.columns(2)

with col1:
    st.header("📥 SET: Guardar en Caché")
    with st.form("registro_carrito", clear_on_submit=True):
        id_cliente = st.text_input("ID del Cliente:")
        contenido_json = st.text_area("Carrito (JSON):", value='{"item": "Smartphone", "precio": 800}')
        
        if st.form_submit_button("Inyectar a RAM"):
            if id_cliente:
                try:
                    data = json.loads(contenido_json)
                    # --- REQUERIMIENTO C.1: Calcular tamaño en bytes --- 
                    peso_bytes = len(json.dumps(data).encode('utf-8'))
                    
                    st.session_state.kv_store[id_cliente] = {
                        "valor": data,
                        "timestamp": datetime.now(),
                        "size": peso_bytes
                    }
                    st.success(f"Dato guardado. Peso: {peso_bytes} bytes")
                except:
                    st.error("Error: JSON inválido")

with col2:
    st.header("⚙️ Mantenimiento")
    if st.button("🔄 Actualizar Cronómetros"):
        st.rerun()
    if st.button("🧹 Ejecutar Limpieza TTL"):
        limpiar_expirados()

# --- 3. ANALÍTICA DE INFRAESTRUCTURA (Paso C) ---
st.divider()

# Solo mostramos analítica si hay datos en el almacén
if st.session_state.kv_store:
    ahora = datetime.now()
    lista_metricas = []
    
    for k, v in st.session_state.kv_store.items():
        segundos = int((ahora - v['timestamp']).total_seconds())
        lista_metricas.append({
            "Cliente": k,
            "Bytes": v['size'],
            "Estado": "🟢 Activo" if segundos <= 60 else "🔴 Expirado"
        })
    
    df = pd.DataFrame(lista_metricas)

    # --- REQUERIMIENTO C.3: Métrica st.metric con peso total --- 
    total_ram = df["Bytes"].sum()
    st.metric("Consumo Total de Memoria", f"{total_ram} Bytes", delta="RAM en uso")

    # --- REQUERIMIENTO C.2: Gráfico de barras st.bar_chart --- 
    st.subheader("📊 Consumo de Memoria RAM por Sesión")
    st.bar_chart(df.set_index("Cliente")["Bytes"])

    # Monitor Detallado
    st.subheader("📋 Estado Detallado del Almacén")
    st.table(df)
else:
    # Mensaje si no hay datos
    st.info("El almacén está vacío. Registra un ID de cliente arriba para ver el gráfico de barras y la métrica de peso.")
