import streamlit as st
import json
from datetime import datetime

# Configuración inicial
st.set_page_config(page_title="FlashCart Pro", layout="wide")
st.title("⚡ FlashCart Pro: NoSQL con TTL")

# Inicializar el almacén con metadatos de tiempo
if 'kv_store' not in st.session_state:
    st.session_state.kv_store = {}

# --- FUNCIÓN DE LIMPIEZA TTL ---
def limpiar_expirados():
    ahora = datetime.now()
    claves_a_borrar = []
    for clave, info in st.session_state.kv_store.items():
        segundos_vividos = (ahora - info['timestamp']).total_seconds()
        if segundos_vividos > 60:
            claves_a_borrar.append(clave)
    
    for clave in claves_a_borrar:
        del st.session_state.kv_store[clave]
    
    return len(claves_a_borrar)

# Interfaz de Usuario
col1, col2 = st.columns(2)

with col1:
    st.header("📥 Registro de Sesión (SET)")
    with st.form("set_form"):
        cliente_id = st.text_input("Clave (ID Cliente):")
        valor_json = st.text_area("Valor (Carrito JSON):", value='{"prod": "Monitor", "precio": 300}')
        submit = st.form_submit_button("Guardar en RAM")
        
        if submit and cliente_id:
            # Guardamos el valor Y el timestamp actual 
            st.session_state.kv_store[cliente_id] = {
                "valor": json.loads(valor_json),
                "timestamp": datetime.now()
            }
            st.success(f"✅ Guardado. TTL de 60s activado.")

with col2:
    st.header("🧹 Gestión de Memoria")
    if st.button("Ejecutar Limpieza TTL (60s)"):
        borrados = limpiar_expirados()
        st.info(f"🗑️ Se han liberado {borrados} registros expirados de la RAM.")

# --- TABLA DE ESTADO EN TIEMPO REAL ---
st.header("📊 Monitor de Memoria Instantáneo")
if st.session_state.kv_store:
    datos_tabla = []
    ahora = datetime.now()
    
    for clave, info in st.session_state.kv_store.items():
        segundos = int((ahora - info['timestamp']).total_seconds())
        estado = "🟢 Activo" if segundos <= 60 else "🔴 Expirado" # 
        
        datos_tabla.append({
            "ID Cliente": clave,
            "Creado hace (seg)": segundos,
            "Estado": estado
        })
    
    st.table(datos_tabla) # Explicación visual del estado 
else:
    st.write("El almacén está vacío.")
