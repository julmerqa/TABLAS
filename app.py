# app.py
# ──────────────────────────────────────────────────────────────────────────────
# 📊 Analizador de Distribuciones — Tabla de Frecuencias + Medidas + Gráficos
# ──────────────────────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO

# ---------------------------
# CONFIGURACIÓN DE PÁGINA + ESTILOS
# ---------------------------
st.set_page_config(
    page_title="Tabla de Frecuencias y Estadísticos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos suaves (puedes ajustar colores si lo deseas)
st.markdown(
    """
    <style>
    .metric-small .stMetric { padding: 0.25rem 0.5rem; }
    .css-1dp5vir, .e1f1d6gn4 { border-radius: 16px !important; }
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    .st-emotion-cache-13ln4jf { padding-top: 0 !important; } /* reduce top spacing */
    .stDataFrame, .st-emotion-cache-1wmy9hl { border-radius: 12px; overflow: hidden; }
    .badge {
      display:inline-block; padding:0.15rem 0.5rem; font-size:0.75rem;
      background:#eef2ff; color:#3730a3; border-radius:999px; margin-left:6px
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# FUNCIONES (Lógica de Procesamiento de Datos - LP)
# ---------------------------

def generar_intervalos(minimo: float, maximo: float, amplitud: float) -> pd.DataFrame:
    """
    Genera intervalos [Li, Ls) equiespaciados y columnas base:
    Li, Ls, Intervalo (string), xi (marca de clase) y fi inicial en 0.
    """
    limites = np.arange(minimo, maximo, amplitud)
    if len(limites) == 0 or amplitud <= 0 or maximo <= minimo:
        return pd.DataFrame(columns=["Li","Ls","Intervalo","xi","fi"])
    Li = limites
    Ls = limites + amplitud
    intervalo_str = [f"[{a:.2f}, {b:.2f})" for a, b in zip(Li, Ls)]
    xi = (Li + Ls) / 2
    df = pd.DataFrame({"Li": Li, "Ls": Ls, "Intervalo": intervalo_str, "xi": xi, "fi": 0})
    return df

def completar_tabla_frecuencias(df: pd.DataFrame) -> pd.DataFrame:
    """
    A partir de (Li, Ls, xi, fi) calcula: hi, Fi, Hi y porcentajes.
    """
    if df.empty:
        return df
    df = df.copy()
    df["fi"] = pd.to_numeric(df["fi"], errors="coerce").fillna(0).astype(int).clip(lower=0)
    N = df["fi"].sum()
    if N == 0:
        df["hi"] = 0.0
        df["Fi"] = df["fi"].cumsum()
        df["Hi"] = 0.0
        df["%"] = 0.0
        df["% Acum."] = 0.0
        return df

    df["hi"] = df["fi"] / N
    df["Fi"] = df["fi"].cumsum()
    df["Hi"] = df["hi"].cumsum()
    df["%"] = df["hi"] * 100
    df["% Acum."] = df["Hi"] * 100
    return df

def expandir_datos_por_midpoints(df: pd.DataFrame) -> np.ndarray:
    """
    Expande los datos replicando la marca de clase xi según fi.
    Se usa para medianas, modas, cuartiles y gráficos (hist/box).
    """
    if df.empty or df["fi"].sum() == 0:
        return np.array([])
    datos = np.repeat(df["xi"].to_numpy(), df["fi"].to_numpy())
    return datos

def medidas_posicion_dispersión(df: pd.DataFrame) -> dict:
    """
    Calcula medidas usando los datos expandidos por xi (aprox. para datos agrupados).
    Devuelve dict con medidas clave para mostrar.
    """
    datos = expandir_datos_por_midpoints(df)
    if datos.size == 0:
        return {}

    # Posición
    media = float(np.mean(datos))
    mediana = float(np.median(datos))
    moda_vals = pd.Series(datos).mode().tolist()
    q1, q2, q3 = np.percentile(datos, [25, 50, 75])

    # Dispersión
    rango = float(np.max(datos) - np.min(datos))
    varianza = float(np.var(datos, ddof=1)) if len(datos) > 1 else 0.0
    desviacion = float(np.std(datos, ddof=1)) if len(datos) > 1 else 0.0
    iqr = float(q3 - q1)
    cv = float((desviacion / media) * 100) if media != 0 else np.nan

    return {
        "N": int(len(datos)),
        "Media": media,
        "Mediana": mediana,
        "Moda": moda_vals,
        "Q1": float(q1),
        "Q2": float(q2),
        "Q3": float(q3),
        "Rango": rango,
        "Varianza (muestral)": varianza,
        "Desv. estándar (muestral)": desviacion,
        "IQR (Q3 - Q1)": iqr,
        "CV (%)": cv,
    }

# ---------------------------
# SIDEBAR (Interfaz de Usuario)
# ---------------------------
with st.sidebar:
    st.header("⚙️ Parámetros")
    minimo = st.number_input("Valor mínimo", value=20.0, step=1.0, format="%.2f")
    maximo = st.number_input("Valor máximo", value=90.0, step=1.0, format="%.2f")
    amplitud = st.number_input("Amplitud de intervalo", value=10.0, min_value=0.01, step=0.5, format="%.2f")
    st.caption("Los intervalos se construyen como [Li, Ls).")

    st.markdown("---")
    st.subheader("📥 Opcional: Cargar fi")
    st.caption("Puedes pegar una columna de frecuencias (fi), una por fila de intervalo.")
    texto_fi = st.text_area("Pegar fi (uno por línea)", height=120, placeholder="10\n12\n8\n...")

    st.markdown("---")
    st.subheader("💾 Descarga")
    auto_descarga_cols = st.columns(2)
    with auto_descarga_cols[0]:
        habilitar_descarga = st.checkbox("Habilitar descarga CSV", value=True)
    with auto_descarga_cols[1]:
        mostrar_graficos = st.checkbox("Mostrar gráficos", value=True)

# ---------------------------
# ENCABEZADO
# ---------------------------
st.title("📊 Analizador de Distribuciones")
st.caption("Genera **tablas de frecuencia**, calcula **medidas de posición y dispersión** y crea **gráficos** útiles para explorar tus datos. <span class='badge'>v2.0</span>", unsafe_allow_html=True)

# ---------------------------
# GENERACIÓN Y EDICIÓN DE TABLA
# ---------------------------
error_container = st.empty()
if maximo <= minimo:
    error_container.error("El **valor máximo** debe ser mayor que el **mínimo**.")
elif amplitud <= 0:
    error_container.error("La **amplitud** debe ser mayor que 0.")
else:
    error_container.empty()
    base = generar_intervalos(minimo, maximo, amplitud)

    if base.empty:
        st.warning("No se pudieron generar intervalos. Verifica los valores de entrada.")
        st.stop()

    # Inyectar fi desde textarea si se pegó algo
    if texto_fi.strip():
        try:
            fi_list = [int(float(x.strip())) for x in texto_fi.strip().splitlines() if x.strip() != ""]
            if len(fi_list) != len(base):
                st.warning(f"Se detectaron **{len(fi_list)}** valores fi pero hay **{len(base)}** intervalos. Ajusta la lista o edita manualmente.")
            else:
                base["fi"] = fi_list
        except Exception:
            st.warning("No se pudo parsear la lista pegada de **fi**. Asegúrate de que cada línea sea un número.")

    st.subheader("📝 Tabla editable — ingresa la **Frecuencia (fi)**")
    edited = st.data_editor(
        base[["Intervalo", "Li", "Ls", "xi", "fi"]],
        num_rows="fixed",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Intervalo": st.column_config.TextColumn("Intervalo", disabled=True),
            "Li": st.column_config.NumberColumn("Li", step=0.01, disabled=True),
            "Ls": st.column_config.NumberColumn("Ls", step=0.01, disabled=True),
            "xi": st.column_config.NumberColumn("Marca de clase (xi)", step=0.01, disabled=True),
            "fi": st.column_config.NumberColumn("Frecuencia (fi)", step=1, help="Ingresa frecuencias enteras ≥ 0"),
        },
    )

    # Completar tabla
    tabla = completar_tabla_frecuencias(edited)

    # ---------------------------
    # MÉTRICAS RÁPIDAS
    # ---------------------------
    N = int(tabla["fi"].sum())
    k = len(tabla)
    rango_clases = f"[{tabla['Li'].min():.2f}, {tabla['Ls'].max():.2f})"
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Observaciones (N)", f"{N}")
    c2.metric("Clases (k)", f"{k}")
    c3.metric("Amplitud", f"{amplitud:.2f}")
    c4.metric("Rango cubierto", rango_clases)

    # ---------------------------
    # TABLAS
    # ---------------------------
    st.subheader("📋 Tabla de Frecuencias")
    st.dataframe(
        tabla[["Intervalo", "fi", "hi", "Fi", "Hi", "%", "% Acum."]],
        use_container_width=True,
        hide_index=True,
    )
    st.caption("hi = fi/N, Fi = acumulada, Hi = acumulada relativa.")

    # ---------------------------
    # MEDIDAS ESTADÍSTICAS
    # ---------------------------
    st.subheader("📐 Medidas de Posición y Dispersión")
    medidas = medidas_posicion_dispersión(tabla)

    if not medidas:
        st.info("Ingresa frecuencias (fi) para calcular las medidas.")
    else:
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("**Medidas de posición**")
            st.write(f"- Media: **{medidas['Media']:.4f}**")
            st.write(f"- Mediana: **{medidas['Mediana']:.4f}**")
            st.write(f"- Moda: **{', '.join([f'{x:.4f}' for x in medidas['Moda']]) if medidas['Moda'] else '—'}**")
            st.write(f"- Q1: **{medidas['Q1']:.4f}**")
            st.write(f"- Q2: **{medidas['Q2']:.4f}**")
            st.write(f"- Q3: **{medidas['Q3']:.4f}**")
        with m2:
            st.markdown("**Medidas de dispersión**")
            st.write(f"- Rango: **{medidas['Rango']:.4f}**")
            st.write(f"- Varianza (muestral): **{medidas['Varianza (muestral)']:.4f}**")
            st.write(f"- Desv. estándar (muestral): **{medidas['Desv. estándar (muestral)']:.4f}**")
            st.write(f"- IQR (Q3−Q1): **{medidas['IQR (Q3 - Q1)']:.4f}**")
        with m3:
            st.markdown("**Resumen**")
            st.write(f"- N (expandido): **{medidas['N']}**")
            st.write(f"- CV (%): **{medidas['CV (%)']:.2f}**")

    # ---------------------------
    # VISUALIZACIÓN
    # ---------------------------
    if mostrar_graficos:
        st.subheader("📈 Visualización de Resultados")
        tab1, tab2, tab3, tab4 = st.tabs(["Barras de frecuencia", "Histograma (xi)", "Ojiva (Fi)", "Boxplot (xi)"])

        # 1) Barras por intervalo
        with tab1:
            fig, ax = plt.subplots()
            ax.bar(tabla["Intervalo"], tabla["fi"], edgecolor="black")
            ax.set_xlabel("Intervalos")
            ax.set_ylabel("Frecuencia (fi)")
            ax.set_title("Distribución de Frecuencias por Intervalo")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig, clear_figure=True)

        # 2) Histograma usando datos expandidos por marcas de clase (aprox.)
        with tab2:
            datos = expandir_datos_por_midpoints(tabla)
            if datos.size == 0:
                st.info("No hay datos para graficar.")
            else:
                fig, ax = plt.subplots()
                bins = np.arange(tabla["Li"].min(), tabla["Ls"].max() + amplitud, amplitud)
                ax.hist(datos, bins=bins, edgecolor="black")
                ax.set_xlabel("Valores (aprox. por xi)")
                ax.set_ylabel("Frecuencia")
                ax.set_title("Histograma (datos aproximados por marcas de clase)")
                st.pyplot(fig, clear_figure=True)

        # 3) Ojiva (acumulada)
        with tab3:
            fig, ax = plt.subplots()
            # Punto en el Ls de cada clase vs Fi
            ax.plot(tabla["Ls"], tabla["Fi"], marker="o")
            ax.set_xlabel("Límites superiores (Ls)")
            ax.set_ylabel("Frecuencia acumulada (Fi)")
            ax.set_title("Ojiva de Frecuencias Acumuladas")
            ax.grid(True, alpha=0.3)
            st.pyplot(fig, clear_figure=True)

        # 4) Boxplot con datos expandidos por xi
        with tab4:
            datos = expandir_datos_por_midpoints(tabla)
            if datos.size == 0:
                st.info("No hay datos para graficar.")
            else:
                fig, ax = plt.subplots()
                ax.boxplot(datos, vert=True, showmeans=True)
                ax.set_ylabel("Valores (aprox. por xi)")
                ax.set_title("Diagrama de Caja (aprox.)")
                st.pyplot(fig, clear_figure=True)

    # ---------------------------
    # DESCARGA
    # ---------------------------
    if habilitar_descarga:
        st.subheader("⬇️ Descargar tabla")
        csv_buf = StringIO()
        tabla.to_csv(csv_buf, index=False)
        st.download_button(
            label="Descargar CSV",
            data=csv_buf.getvalue(),
            file_name="tabla_frecuencias.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ---------------------------
    # NOTAS
    # ---------------------------
    with st.expander("📎 Notas y supuestos"):
        st.markdown(
            """
            - Los intervalos se construyen como **[Li, Ls)** con amplitud constante.
            - Las **medidas** se calculan a partir de la **expansión por marcas de clase (xi)** como aproximación para datos agrupados.
            - Para una estimación más precisa con datos originales sin agrupar, reemplaza la expansión por los datos reales.
            """
        )
