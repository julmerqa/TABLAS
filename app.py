import streamlit as st

# Ajustes de página
st.set_page_config(
    page_title="Resolución de Problemas Numéricos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Importa las funciones mostrar() de cada problema
from problemas.problema_1 import mostrar as mostrar_p1
from problemas.problema_2 import mostrar as mostrar_p2
from problemas.problema_3 import mostrar as mostrar_p3
from problemas.problema_4 import mostrar as mostrar_p4
from problemas.problema_5 import mostrar as mostrar_p5

# ----------------------------------------
# Estilos globales (ajuste de colores y fuentes)
# ----------------------------------------
st.markdown("""
    <style>
        body {
            background-color: #f4f4f9; 
            font-family: 'Roboto', sans-serif; 
            color: #333;
        }
        .stButton>button {
            background: #0073e6; 
            color: white; 
            border-radius: 12px; 
            padding: 10px 20px; 
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background: #005bb5;
        }
        .stSidebar {
            background-color: #ffffff; 
            box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
            padding: 20px;
        }
        .stSelectbox>label, .stRadio>label {
            font-size: 18px; 
            color: #444;
            font-weight: 500;
        }
        .stTitle {
            color: #2e4a8a; 
            font-size: 36px; 
            font-weight: 600;
        }
        .stHeader {
            color: #2e4a8a; 
            font-size: 28px; 
            font-weight: 500;
        }
        .stMarkdown {
            color: #555;
            font-size: 18px;
        }
        .st-expanderHeader {
            font-size: 20px; 
            font-weight: 600;
            color: #2e4a8a;
        }
        .stTextInput input {
            font-size: 18px;
        }
        .stSelectbox select, .stNumberInput input {
            font-size: 18px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------
# Sidebar de navegación
# ----------------------------------------
st.sidebar.title("🔢 Resolución de Problemas")

selección = st.sidebar.radio(
    "Selecciona un problema:",
    (
        "1. Problema 1",
        "2. Problema 2",
        "3. Problema 3",
        "4. Problema 4",
        "5. Problema 5",
    )
)

# ----------------------------------------
# Área principal: solo mostramos el problema elegido
# ----------------------------------------
st.title("Resolución de Problemas Numéricos")

if selección.startswith("1."):
    mostrar_p1()
elif selección.startswith("2."):
    mostrar_p2()
elif selección.startswith("3."):
    mostrar_p3()
elif selección.startswith("4."):
    mostrar_p4()
else:
    mostrar_p5()
