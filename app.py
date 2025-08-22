import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------
# FUNCIONES
# ---------------------------
def generar_tabla(minimo, maximo, amplitud):
    # Generar intervalos
    intervalos = []
    inicio = minimo
    while inicio < maximo:
        fin = inicio + amplitud
        intervalos.append(f"[{inicio}, {fin}[")
        inicio = fin

    # Crear DataFrame inicial con frecuencias vacías
    df = pd.DataFrame({
        "Valores": intervalos,
        "Frecuencia (fi)": [0] * len(intervalos)
    })

    return df

def calcular_medidas(df):
    # Expandir datos a partir de frecuencias
    datos = []
    for i, row in df.iterrows():
        intervalo = row["Valores"]
        a, b = intervalo.strip("[]").split(",")
        a, b = float(a), float(b[:-1])  
        punto_medio = (a + b) / 2
        datos.extend([punto_medio] * row["Frecuencia (fi)"])

    datos = np.array(datos)

    if len(datos) == 0 or sum(df["Frecuencia (fi)"]) == 0:
        return "⚠ No hay datos ingresados."

    # Medidas de posición
    media = np.mean(datos)
    mediana = np.median(datos)
    moda = pd.Series(datos).mode().tolist()

    # Cuartiles
    q1 = np.percentile(datos, 25)
    q2 = np.percentile(datos, 50)
    q3 = np.percentile(datos, 75)

    # Medidas de dispersión
    rango = np.max(datos) - np.min(datos)
    varianza = np.var(datos, ddof=1)
    desviacion = np.std(datos, ddof=1)

    resumen = f"""
    ### 📌 Medidas de posición
    - Media: {media:.2f}
    - Mediana: {mediana:.2f}
    - Moda: {moda}
    - Q1: {q1:.2f}, Q2: {q2:.2f}, Q3: {q3:.2f}

    ### 📌 Medidas de dispersión
    - Rango: {rango:.2f}
    - Varianza: {varianza:.2f}
    - Desviación estándar: {desviacion:.2f}
    """
    return resumen

# ---------------------------
# INTERFAZ STREAMLIT
# ---------------------------
st.set_page_config(page_title="Tabla de Frecuencias", layout="centered")
st.title("📊 Generador de Tablas de Frecuencia con Estadísticos")

# Entradas de usuario
col1, col2, col3 = st.columns(3)
with col1:
    minimo = st.number_input("Valor mínimo", value=20)
with col2:
    maximo = st.number_input("Valor máximo", value=90)
with col3:
    amplitud = st.number_input("Amplitud del intervalo", value=10)

# Generar tabla editable
st.subheader("📋 Edita la Frecuencia (fi) en la tabla")
df = generar_tabla(minimo, maximo, amplitud)
df = st.data_editor(df, num_rows="dynamic")

# Calcular acumulada
df["Frecuencia acumulada (Fi)"] = df["Frecuencia (fi)"].cumsum()

# Mostrar tabla final
st.subheader("📋 Tabla de Frecuencias")
st.dataframe(df)

# Mostrar totales
st.write(f"*TOTAL fi =* {df['Frecuencia (fi)'].sum()}")
st.write(f"*TOTAL Fi =* {df['Frecuencia acumulada (Fi)'].iloc[-1]}")

# Calcular medidas
st.subheader("📐 Medidas Estadísticas")
resumen = calcular_medidas(df)
st.markdown(resumen)

# Gráfico
st.subheader("📈 Gráfico de Frecuencias")
fig, ax = plt.subplots()
ax.bar(df["Valores"], df["Frecuencia (fi)"], color="skyblue", edgecolor="black")
plt.xticks(rotation=45)
plt.xlabel("Intervalos")
plt.ylabel("Frecuencia")
plt.title("Distribución de Frecuencias")
st.pyplot(fig)
