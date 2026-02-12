import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# =========================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================
st.set_page_config(
    page_title="Calculadora ROI - Bienestar Corporativo",
    page_icon="🚭",
    layout="wide"
)

# =========================================
# 1. LÓGICA DE NEGOCIO (Funciones de cálculo)
# =========================================

def calcular_costo_actual(num_empleados, salario_mensual, pct_fumadores):
    """Calcula el costo oculto actual (Línea Base)"""
    # Constantes
    MINUTOS_PERDIDOS_DIA = 60
    DIAS_LABORALES_ANIO = 250
    DIAS_EXTRA_AUSENTISMO = 3
    
    # Tasas
    salario_diario = salario_mensual / 30
    salario_minuto = salario_diario / 8 / 60
    
    num_fumadores = int(num_empleados * pct_fumadores)
    
    # Costos
    costo_pausas = num_fumadores * MINUTOS_PERDIDOS_DIA * salario_minuto * DIAS_LABORALES_ANIO
    costo_absentismo = num_fumadores * DIAS_EXTRA_AUSENTISMO * salario_diario
    
    return costo_pausas + costo_absentismo, num_fumadores

def modelo_roi_bienestar(num_empleados, salario_mensual, costo_curso, moneda, pct_fumadores_base):
    """
    Genera un modelo predictivo de ROI bajo 3 escenarios de efectividad.
    """
    # 1. Situación Actual
    costo_anual_actual, total_fumadores = calcular_costo_actual(num_empleados, salario_mensual, pct_fumadores_base)
    costo_por_fumador = costo_anual_actual / total_fumadores if total_fumadores > 0 else 0

    # 2. Escenarios
    escenarios = {
        'Conservador (10%)': 0.10,
        'Moderado (30%)': 0.30,
        'Optimista (50%)': 0.50
    }
    
    resultados = []
    
    for nombre, tasa_exito in escenarios.items():
        empleados_recuperados = int(total_fumadores * tasa_exito)
        ahorro_anual = empleados_recuperados * costo_por_fumador
        
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
            'Fumadores que dejan': empleados_recuperados,
            'Ahorro Anual Proyectado': ahorro_anual,
            'ROI (%)': roi_pct,
            'Meses para recuperar $$': meses_recuperacion
        })
        
    return pd.DataFrame(resultados), costo_anual_actual, total_fumadores

# =========================================
# 2. FUNCIONES DE GRÁFICOS
# =========================================

def crear_graficos(df_resultados, costo_curso, moneda):
    """Genera la figura de matplotlib para Streamlit"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='#f0f2f6')
    
    # --- Gráfico 1: ROI ---
    colores = ['#ff9999', '#66b3ff', '#99ff99']
    barras = ax1.bar(df_resultados['Escenario'], df_resultados['ROI (%)'], color=colores, edgecolor='grey')
    
    ax1.set_title(f'Retorno de Inversión (ROI) Proyectado', fontsize=12, fontweight='bold', color='#333333')
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
    
    ax2.set_title(f'Tiempo de Recuperación (Escenario Moderado)', fontsize=12, fontweight='bold', color='#333333')
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
    st.header("⚙️ Parámetros de Entrada")
    st.markdown("Ajusta los valores para actualizar el reporte en tiempo real.")
    
    moneda_input = st.selectbox("Moneda", ["$", "€", "S/", "MXN"], index=0)
    
    st.subheader("Datos de la Empresa")
    num_empleados_in = st.number_input("Número de Empleados", min_value=10, value=500, step=10)
    salario_promedio_in = st.number_input("Salario Promedio Mensual", min_value=0, value=15000, step=500)
    pct_fumadores_in = st.slider("% Estimado de Fumadores", 5, 60, 25) / 100
    
    st.subheader("Datos del Curso")
    costo_curso_in = st.number_input("Costo Total del Curso (Inversión)", min_value=0, value=45000, step=1000)
    
    st.markdown("---")
    st.caption("Desarrollado con Python & Streamlit")

# --- CUERPO PRINCIPAL ---

st.title("🚭 Reporte de Factibilidad Financiera: Programa de Cesación de Tabaco")
st.markdown(f"""
Este dashboard interactivo calcula el **impacto financiero** de implementar un curso para dejar de fumar en una empresa de 
**{num_empleados_in} colaboradores**. Se comparan los costos ocultos actuales vs. la inversión del curso.
""")

# Ejecutar Cálculos
df_roi, costo_base, total_fumadores = modelo_roi_bienestar(
    num_empleados_in, 
    salario_promedio_in, 
    costo_curso_in, 
    moneda_input,
    pct_fumadores_in
)

# --- 1. MÉTRICAS CLAVE ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📉 Costo Oculto Actual (Anual)",
        value=f"{moneda_input}{costo_base:,.0f}",
        help="Costo por pausas para fumar y ausentismo extra anual."
    )

with col2:
    st.metric(
        label="💰 Inversión Requerida",
        value=f"{moneda_input}{costo_curso_in:,.0f}",
        delta=f"-{moneda_input}{costo_curso_in:,.0f}",
        delta_color="inverse",
        help="Costo único del curso."
    )

with col3:
    st.metric(
        label="👥 Fumadores Estimados",
        value=f"{total_fumadores}",
        help=f"Basado en un {pct_fumadores_in*100:.0f}% de la plantilla."
    )

st.divider()

# --- 2. GRÁFICOS ---
st.subheader("📊 Proyección de Resultados")
fig = crear_graficos(df_roi, costo_curso_in, moneda_input)
st.pyplot(fig)

# --- 3. TABLA DE ESCENARIOS ---
st.subheader("📋 Detalle de Escenarios")
st.markdown("Comparativa financiera según el porcentaje de éxito del programa:")

# Formatear el dataframe para mostrarlo bonito
df_display = df_roi.copy()
df_display['Ahorro Anual Proyectado'] = df_display['Ahorro Anual Proyectado'].apply(lambda x: f"{moneda_input}{x:,.2f}")
df_display['ROI (%)'] = df_display['ROI (%)'].apply(lambda x: f"{x:,.1f}%")
df_display['Meses para recuperar $$'] = df_display['Meses para recuperar $$'].apply(lambda x: f"{x:.1f}")

st.dataframe(
    df_display,
    column_config={
        "Escenario": st.column_config.TextColumn("Escenario"),
        "Fumadores que dejan": st.column_config.NumberColumn("Colaboradores recuperados"),
    },
    use_container_width=True,
    hide_index=True
)

# --- 4. INTERPRETACIÓN DE RESULTADOS ---
st.divider()
st.header("💡 Interpretación de Resultados")

# Obtenemos datos del escenario moderado para el texto dinámico
escenario_mod = df_roi.iloc[1]
roi_mod = escenario_mod['ROI (%)']
payback_mod = escenario_mod['Meses para recuperar $$']
ahorro_mod = escenario_mod['Ahorro Anual Proyectado']

st.info(f"""
**Análisis del Escenario Moderado (30% de éxito):**

1.  **Retorno de Inversión (ROI) del {roi_mod:,.0f}%:** * Esto significa que por cada {moneda_input}1 invertido en el curso, la empresa recupera su {moneda_input}1 y genera un beneficio adicional.
    * Un ROI superior al 100% indica que el programa se paga solo con creces en el primer año.

2.  **Tiempo de Recuperación (Payback) de {payback_mod:.1f} meses:**
    * La inversión de {moneda_input}{costo_curso_in:,.0f} se recupera en menos de **{int(payback_mod)+1} meses** gracias a la productividad recuperada.
    * A partir del mes {int(payback_mod)+1}, todo el ahorro generado ({moneda_input}{ahorro_mod:,.0f} anuales) es ganancia neta para la empresa.

3.  **Conclusión:**
    * Incluso en un escenario **Conservador**, el proyecto es financieramente viable.
    * El costo de *no hacer nada* es de **{moneda_input}{costo_base:,.0f} al año**, una cifra significativamente mayor al costo del curso.
""")