import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# =========================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================
st.set_page_config(
    page_title="Calculadora ROI - Grupo Cerrado",
    page_icon="🚭",
    layout="wide"
)

# =========================================
# 1. LÓGICA DE NEGOCIO (Funciones de cálculo)
# =========================================

def calcular_costo_actual(num_participantes, salario_mensual):
    """Calcula el costo oculto actual de los participantes del grupo"""
    # Constantes
    MINUTOS_PERDIDOS_DIA = 60
    DIAS_LABORALES_ANIO = 250
    DIAS_EXTRA_AUSENTISMO = 3
    
    # Tasas
    salario_diario = salario_mensual / 30
    salario_minuto = salario_diario / 8 / 60
    
    # Costos (Asumimos que los 20 son fumadores)
    costo_pausas = num_participantes * MINUTOS_PERDIDOS_DIA * salario_minuto * DIAS_LABORALES_ANIO
    costo_absentismo = num_participantes * DIAS_EXTRA_AUSENTISMO * salario_diario
    
    return costo_pausas + costo_absentismo

def modelo_roi_bienestar(num_participantes, salario_mensual, costo_curso, moneda):
    """
    Genera un modelo predictivo de ROI para un grupo cerrado.
    """
    # 1. Situación Actual (Línea Base del grupo)
    costo_anual_actual = calcular_costo_actual(num_participantes, salario_mensual)
    
    # Costo individual
    costo_por_participante = costo_anual_actual / num_participantes if num_participantes > 0 else 0

    # 2. Escenarios
    escenarios = {
        'Conservador (10%)': 0.10,
        'Moderado (30%)': 0.30,
        'Optimista (50%)': 0.50
    }
    
    resultados = []
    
    for nombre, tasa_exito in escenarios.items():
        # Personas del grupo que dejan de fumar
        personas_recuperadas = int(num_participantes * tasa_exito)
        
        # Ahorro generado por esas personas
        ahorro_anual = personas_recuperadas * costo_por_participante
        
        # ROI
        if costo_curso > 0:
            roi_pct = ((ahorro_anual - costo_curso) / costo_curso) * 100
            if ahorro_anual > 0:
                meses_recuperacion = (costo_curso / ahorro_anual) * 12
            else:
                meses_recuperacion = 999
        else:
            roi_pct = 0
            meses_recuperacion = 0
            
        resultados.append({
            'Escenario': nombre,
            'Personas que dejan': personas_recuperadas,
            'Ahorro Anual Proyectado': ahorro_anual,
            'ROI (%)': roi_pct,
            'Meses para recuperar $$': meses_recuperacion
        })
        
    return pd.DataFrame(resultados), costo_anual_actual

# =========================================
# 2. FUNCIONES DE GRÁFICOS
# =========================================

def crear_graficos(df_resultados, costo_curso, moneda):
    """Genera la figura de matplotlib para Streamlit"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='#f0f2f6')
    
    # --- Gráfico 1: ROI ---
    colores = ['#ff9999', '#66b3ff', '#99ff99']
    barras = ax1.bar(df_resultados['Escenario'], df_resultados['ROI (%)'], color=colores, edgecolor='grey')
    
    ax1.set_title(f'Retorno de Inversión (ROI)', fontsize=12, fontweight='bold', color='#333333')
    ax1.set_ylabel('ROI (%)')
    ax1.axhline(0, color='grey', linewidth=0.8)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    ax1.set_facecolor('white')
    
    for bar in barras:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{height:,.0f}%', ha='center', va='bottom', fontweight='bold', fontsize=10)

    # --- Gráfico 2: Payback (Escenario Moderado) ---
    escenario_mod = df_resultados.iloc[1]
    ahorro_mensual = escenario_mod['Ahorro Anual Proyectado'] / 12
    
    meses = range(0, 13)
    flujo_acumulado = [-costo_curso + (ahorro_mensual * m) for m in meses]
    
    ax2.plot(meses, flujo_acumulado, marker='o', color='#2ecc71', linewidth=2, label='Flujo de Caja')
    ax2.axhline(0, color='red', linestyle='--', label='Punto de Equilibrio')
    
    ax2.set_title(f'Recuperación de Inversión (Escenario Moderado)', fontsize=12, fontweight='bold', color='#333333')
    ax2.set_xlabel('Meses después del curso')
    ax2.set_ylabel(f'Balance Acumulado ({moneda})')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_facecolor('white')
    
    # Rellenar área de ganancia
    ax2.fill_between(meses, 0, flujo_acumulado, where=np.array(flujo_acumulado)>=0, facecolor='green', alpha=0.1)
    
    plt.tight_layout()
    return fig

# =========================================
# 3. INTERFAZ DE USUARIO (STREAMLIT)
# =========================================

# --- BARRA LATERAL (INPUTS) ---
with st.sidebar:
    st.header("⚙️ Parámetros del Grupo")
    st.markdown("Configuración para grupo cerrado.")
    
    moneda_input = st.selectbox("Moneda", ["$", "€", "S/", "MXN"], index=0)
    
    # INPUTS SIMPLIFICADOS
    st.subheader("Datos del Grupo")
    num_participantes_in = st.number_input("Participantes (Fumadores)", min_value=1, value=20, step=1, help="Tamaño del grupo que tomará el curso")
    salario_promedio_in = st.number_input("Salario Promedio Mensual", min_value=0, value=15000, step=500)
    
    st.subheader("Datos del Curso")
    costo_curso_in = st.number_input("Costo Total del Curso (Grupo)", min_value=0, value=45000, step=1000)
    
    st.markdown("---")
    st.caption("ROI para Grupos Cerrados")

# --- CUERPO PRINCIPAL ---

st.title("🚭 Reporte de Factibilidad: Curso de Cesación (Grupo Cerrado)")
st.markdown(f"""
Este análisis calcula el impacto financiero de impartir el curso a un grupo específico de **{num_participantes_in} colaboradores fumadores**.
""")

# Ejecutar Cálculos
df_roi, costo_base_grupo = modelo_roi_bienestar(
    num_participantes_in, 
    salario_promedio_in, 
    costo_curso_in, 
    moneda_input
)

# --- 1. MÉTRICAS CLAVE ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📉 Costo Oculto Actual (Grupo)",
        value=f"{moneda_input}{costo_base_grupo:,.0f}",
        help=f"Lo que le cuesta a la empresa que estas {num_participantes_in} personas fumen (anual)."
    )

with col2:
    st.metric(
        label="💰 Inversión del Curso",
        value=f"{moneda_input}{costo_curso_in:,.0f}",
        delta=f"-{moneda_input}{costo_curso_in:,.0f}",
        delta_color="inverse",
        help="Costo único por el grupo completo."
    )

with col3:
    st.metric(
        label="👥 Tamaño del Grupo",
        value=f"{num_participantes_in} Personas",
        help="Todos considerados fumadores activos."
    )

st.divider()

# --- 2. GRÁFICOS ---
st.subheader("📊 Proyección de Resultados")
fig = crear_graficos(df_roi, costo_curso_in, moneda_input)
st.pyplot(fig)

# --- 3. TABLA DE ESCENARIOS ---
st.subheader("📋 Detalle de Escenarios")
st.markdown("Comparativa financiera según cuántas personas del grupo logren dejar de fumar:")

# Formatear el dataframe para mostrarlo bonito
df_display = df_roi.copy()
df_display['Ahorro Anual Proyectado'] = df_display['Ahorro Anual Proyectado'].apply(lambda x: f"{moneda_input}{x:,.2f}")
df_display['ROI (%)'] = df_display['ROI (%)'].apply(lambda x: f"{x:,.1f}%")
df_display['Meses para recuperar $$'] = df_display['Meses para recuperar $$'].apply(lambda x: f"{x:.1f}")

st.dataframe(
    df_display,
    column_config={
        "Escenario": st.column_config.TextColumn("Escenario de Éxito"),
        "Personas que dejan": st.column_config.NumberColumn("Personas recuperadas"),
    },
    use_container_width=True,
    hide_index=True
)

# --- 4. INTERPRETACIÓN DE RESULTADOS ---
st.divider()
st.header("💡 Interpretación de Resultados")

# Datos del escenario moderado
escenario_mod = df_roi.iloc[1]
roi_mod = escenario_mod['ROI (%)']
payback_mod = escenario_mod['Meses para recuperar $$']
ahorro_mod = escenario_mod['Ahorro Anual Proyectado']
personas_recuperadas = int(escenario_mod['Personas que dejan'])

st.info(f"""
**Análisis para el grupo de {num_participantes_in} personas (Escenario Moderado - 30% de éxito):**

1.  **Impacto en Salud:** Se estima que **{personas_recuperadas} personas** del grupo dejarán de fumar permanentemente.

2.  **Retorno de Inversión (ROI):** * La empresa obtendrá un retorno del **{roi_mod:,.0f}%**.
    * Esto genera un flujo de caja positivo anual de **{moneda_input}{ahorro_mod:,.0f}** solo en productividad recuperada.

3.  **Tiempo de Recuperación:**
    * La inversión de {moneda_input}{costo_curso_in:,.0f} se paga sola en **{payback_mod:.1f} meses**.
    * Esto significa que antes de terminar el primer año, el curso ya habrá generado ganancias netas para la organización.

**Conclusión:** Dado que el costo oculto de este grupo es de **{moneda_input}{costo_base_grupo:,.0f} anuales**, intervenir es altamente rentable incluso si solo una fracción del grupo tiene éxito.
""")