import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =========================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================
st.set_page_config(
    page_title="Calculadora ROI - Grupo Cerrado",
    page_icon="🚭",
    layout="wide"
)

# =========================================
# ESTILOS CSS PERSONALIZADOS (El Botón Mágico)
# =========================================
st.markdown("""
<style>
/* Animación de las olas de colores */
@keyframes gradient-animation {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Estilo del botón */
.wave-btn {
    display: block;
    width: 100%;
    padding: 12px 20px;
    margin: 10px 0;
    font-size: 16px;
    font-weight: bold;
    text-align: center;
    color: white !important;
    text-decoration: none !important;
    border-radius: 8px;
    /* Fondo base con gradiente multicolor */
    background: linear-gradient(270deg, #FF512F, #DD2476, #40E0D0, #FF512F);
    background-size: 300% 300%;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: all 0.4s ease;
    border: none;
}

/* Efecto al pasar el mouse (Hover) */
.wave-btn:hover {
    /* Activar la animación de olas */
    animation: gradient-animation 3s ease infinite;
    /* Efecto de iluminación/resplandor */
    box-shadow: 0 0 15px rgba(221, 36, 118, 0.6), 0 0 30px rgba(64, 224, 208, 0.4);
    transform: scale(1.02); /* Crece un poquito */
}
</style>
""", unsafe_allow_html=True)

# =========================================
# LÓGICA DE NEGOCIO (Funciones de cálculo)
# =========================================

def calcular_costo_actual(num_participantes, salario_mensual):
    """Calcula el costo oculto actual de los participantes del grupo"""
    MINUTOS_PERDIDOS_DIA = 60
    DIAS_LABORALES_ANIO = 250
    DIAS_EXTRA_AUSENTISMO = 3
    
    salario_diario = salario_mensual / 30
    salario_minuto = salario_diario / 8 / 60
    
    costo_pausas = num_participantes * MINUTOS_PERDIDOS_DIA * salario_minuto * DIAS_LABORALES_ANIO
    costo_absentismo = num_participantes * DIAS_EXTRA_AUSENTISMO * salario_diario
    
    return costo_pausas + costo_absentismo

def modelo_roi_bienestar(num_participantes, salario_mensual, costo_curso, moneda):
    """Genera un modelo predictivo de ROI para un grupo cerrado."""
    costo_anual_actual = calcular_costo_actual(num_participantes, salario_mensual)
    costo_por_participante = costo_anual_actual / num_participantes if num_participantes > 0 else 0

    escenarios = {
        'Conservador (10%)': 0.10,
        'Moderado (30%)': 0.30,
        'Optimista (50%)': 0.50
    }
    
    resultados = []
    
    for nombre, tasa_exito in escenarios.items():
        personas_recuperadas = int(num_participantes * tasa_exito)
        ahorro_anual = personas_recuperadas * costo_por_participante
        
        if costo_curso > 0:
            roi_pct = ((ahorro_anual - costo_curso) / costo_curso) * 100
            meses_recuperacion = (costo_curso / ahorro_anual) * 12 if ahorro_anual > 0 else 999
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
# BARRA LATERAL (INPUTS)
# =========================================
with st.sidebar:
    # --- LOGO CENTRADO ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Asegúrate de que este nombre sea el correcto
        st.image("image_ef75e0.png", width=150) 
        
    st.header("⚙️ Parámetros del Grupo")
    st.markdown("Configuración para grupo cerrado.")
    
    moneda_input = st.selectbox("Moneda", ["$", "€", "S/", "MXN"], index=0)
    
    st.subheader("Datos del Grupo")
    num_participantes_in = st.number_input("Participantes (Fumadores)", min_value=1, value=20, step=1, help="Tamaño del grupo que tomará el curso")
    salario_promedio_in = st.number_input("Salario Promedio Mensual", min_value=0, value=15000, step=500)
    
    st.subheader("Datos del Curso")
    costo_curso_in = st.number_input("Costo Total del Curso (Grupo)", min_value=0, value=45000, step=1000)
    
    # --- LLAMADA A LA ACCIÓN ---
    st.markdown("---")
    st.markdown("### ¿Listo para recuperar la productividad?")
    
    link_agenda = "https://meetings.hubspot.com/eliuth-misraim?uuid=169366e7-ae2e-4855-8083-cc554bb3db85"
    st.markdown(f"""
        <a href="{link_agenda}" target="_blank" class="wave-btn">
            📅 Agendar Consulta
        </a>
    """, unsafe_allow_html=True)

# =========================================
# CUERPO PRINCIPAL
# =========================================

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
col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.metric(
        label="📉 Costo Oculto Actual (Grupo)",
        value=f"{moneda_input}{costo_base_grupo:,.0f}",
        help=f"Lo que le cuesta a la empresa que estas {num_participantes_in} personas fumen (anual)."
    )

with col_m2:
    st.metric(
        label="💰 Inversión del Curso",
        value=f"{moneda_input}{costo_curso_in:,.0f}",
        delta=f"-{moneda_input}{costo_curso_in:,.0f}",
        delta_color="inverse",
        help="Costo único por el grupo completo."
    )

with col_m3:
    st.metric(
        label="👥 Tamaño del Grupo",
        value=f"{num_participantes_in} Personas",
        help="Todos considerados fumadores activos."
    )

st.divider()

# --- 2. GRÁFICOS INTERACTIVOS (PLOTLY) ---
st.subheader("📊 Proyección de Resultados")

# Usamos dos columnas para colocar los gráficos lado a lado
col_graf1, col_graf2 = st.columns(2)
colores_graficos = ['#e74c3c', '#f39c12', '#2ecc71'] # Rojo, Amarillo, Verde

# -- Gráfico 1: ROI (Barras) --
fig_roi = go.Figure()
fig_roi.add_trace(go.Bar(
    x=df_roi['Escenario'],
    y=df_roi['ROI (%)'],
    marker_color=colores_graficos,
    text=df_roi['ROI (%)'].apply(lambda x: f'{x:,.0f}%'),
    textposition='auto',
    hovertemplate='<b>%{x}</b><br>ROI: %{y:,.0f}%<extra></extra>'
))
fig_roi.update_layout(
    title=dict(text="Retorno de Inversión (ROI)", font=dict(size=18)),
    yaxis_title="ROI (%)",
    height=400,
    template="plotly_white",
    margin=dict(t=50, b=0, l=0, r=0),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)' # Fondo transparente para adaptarse al tema oscuro
)
col_graf1.plotly_chart(fig_roi, use_container_width=True)

# -- Gráfico 2: Payback (Líneas e Intersecciones) --
fig_payback = go.Figure()

meses = list(range(0, 13)) # Proyección de 0 a 12 meses

for index, row in df_roi.iterrows():
    escenario = row['Escenario']
    ahorro_mensual = row['Ahorro Anual Proyectado'] / 12
    flujo_acumulado = [-costo_curso_in + (ahorro_mensual * m) for m in meses]
    
    # Añadir línea del flujo de caja
    fig_payback.add_trace(go.Scatter(
        x=meses,
        y=flujo_acumulado,
        mode='lines+markers',
        name=escenario,
        line=dict(color=colores_graficos[index], width=3),
        hovertemplate=f'<b>{escenario}</b><br>Mes %{{x}}<br>Balance: {moneda_input}%{{y:,.0f}}<extra></extra>'
    ))

    # Añadir estrella en la intersección exacta (Punto de equilibrio)
    meses_recuperacion = row['Meses para recuperar $$']
    if 0 < meses_recuperacion <= 12:
        fig_payback.add_trace(go.Scatter(
            x=[meses_recuperacion],
            y=[0],
            mode='markers+text',
            marker=dict(color=colores_graficos[index], size=14, symbol='star', line=dict(color='white', width=1)),
            text=[f"{meses_recuperacion:.1f}m"],
            textposition="top left",
            showlegend=False,
            hoverinfo='skip'
        ))

# Línea base de Punto de Equilibrio (Cero)
fig_payback.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Punto de Equilibrio", annotation_position="bottom right")

fig_payback.update_layout(
    title=dict(text="Tiempo de Recuperación por Escenario", font=dict(size=18)),
    xaxis_title="Meses después del curso",
    yaxis_title=f"Balance Acumulado ({moneda_input})",
    height=400,
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
    template="plotly_white",
    margin=dict(t=50, b=0, l=0, r=0),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)' # Fondo transparente
)
col_graf2.plotly_chart(fig_payback, use_container_width=True)


# --- 3. TABLA DE ESCENARIOS ---
st.divider()
st.subheader("📋 Detalle de Escenarios")

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