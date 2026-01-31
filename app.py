import streamlit as st
import json

# Configuración inicial
st.set_page_config(page_title="FlashCart Pro", layout="wide")
st.title("⚡ FlashCart Pro: NoSQL Key-Value Store")

# Inicializar el almacén en la 'RAM' de la sesión (kv_store)
if 'kv_store' not in st.session_state:
    st.session_state.kv_store = {}

# Diseño de la interfaz
col1, col2 = st.columns(2)

with col1:
    st.header("📥 Guardar Datos (SET)")
    with st.form("set_form", clear_on_submit=True):
        cliente_id = st.text_input("Clave (ID Cliente):", placeholder="ej: USER_123")
        # JSON de ejemplo para facilitar la prueba
        ejemplo_carrito = {"productos": ["Laptop", "Mouse"], "total": 1250.50}
        valor_json = st.text_area("Valor (JSON del Carrito):", 
                                  value=json.dumps(ejemplo_carrito, indent=2))
        
        submit = st.form_submit_button("Guardar en Caché")
        
        if submit:
            if cliente_id and valor_json:
                try:
                    # Validamos que el texto sea un JSON válido
                    data = json.loads(valor_json)
                    # Guardamos en nuestro diccionario (simulando Redis)
                    st.session_state.kv_store[cliente_id] = data
                    st.success(f"✅ Cliente {cliente_id} guardado con éxito.")
                except json.JSONDecodeError:
                    st.error("❌ Error: El valor debe ser un JSON válido.")
            else:
                st.warning("⚠️ Por favor, rellena todos los campos.")

with col2:
    st.header("🔍 Recuperar Datos (GET)")
    search_id = st.text_input("Buscar por ID de Cliente:")
    
    if search_id:
        if search_id in st.session_state.kv_store:
            resultado = st.session_state.kv_store[search_id]
            st.json(resultado)
            st.info(f"⚡ Acceso instantáneo desde RAM para: {search_id}")
        else:
            st.error("❌ ID no encontrado en el almacén.")

# Mostrar estado actual del almacén (opcional, para depuración)
if st.checkbox("Ver estado total del almacén"):
    st.write(st.session_state.kv_store)
