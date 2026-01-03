"""
App para el proyecto final de Visualización de Datos.
Adriana Lorenzo Mingorance, 2º B iMAT
202314429
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.title("Dashboard de Ventas (Cierre de Año)")
st.caption("Proyecto final visualización de datos: Adriana Lorenzo")

#cargamos los datos
@st.cache_data(show_spinner='Cargamos los datos: ')
def cargar_datos(path1: str, path2: str) -> pd.DataFrame:
    df1 = pd.read_csv(path1, low_memory=False)
    df2 = pd.read_csv(path2, low_memory=False)

    #concatenamos ambos (ya que son 2 partes del mismo df)
    df = pd.concat([df1,df2], ignore_index=True)

    #hacemos una limpieza básica primero
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    
    #distinguimos tipos
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    return df

df = cargar_datos('parte_1/parte_1.csv', 'parte_2/parte_2.csv')


#creamos las pestañas
tab1, tab2, tab3, tab4 = st.tabs(['1) Vision global', '2) Por tienda', '3) Por estado', '4) Extra'])

#PESTAÑA 1:
with tab1:
    st.subheader("Vision global de la situación de ventas")

    #a) conteo general
    st.markdown('### a) Conteo general')

    total_tiendas = df['store_nbr'].nunique()
    total_productos = df['family'].nunique()
    total_estados = df['state'].nunique()
    meses_disponibles = df[['year', 'month']].drop_duplicates().shape[0] #nos quedamos con las fials que salgan de esto

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Número total de tiendas", f"{total_tiendas:,}")
    c2.metric("Número total de productos (familias)", f"{total_productos:,}")
    c3.metric("Estados en los que opera", f"{total_estados:,}")
    c4.metric("Meses con datos", f"{meses_disponibles:,}")

    #B) Análisis en términos medios
    st.markdown("### b) Análisis (rankings y distribución)")
    #para mejorar la visualización
    colA, colB = st.columns(2)

    #b.i) Ranking de productos más vendidos
    with colA: 
        st.markdown("**Top 10 productos más vendidos:**")
        #agrupamos por productos y sumamos su columna de ventas, ordenamos de más a menos y nos quedamos con los 10 mejores
        top_10_products = (df.groupby('family')['sales'].sum().sort_values(ascending=False).head(10))
        #los mostramos en una tabla 
        st.dataframe(top_10_products.reset_index(name='ventas'))
        #lo mostramos en gráfica
        st.bar_chart(top_10_products)

    #b. ii) Distribución de ventas por tiendas
    with colB:
        st.markdown("**Distribución de ventas por tiendas:**")

        sales_by_store = (df.groupby('store_nbr')['sales'].sum().sort_values(ascending=False))

        st.bar_chart(sales_by_store)
        st.caption("Gráfico de barras de las ventas totales por tienda (ordenadas)")

        #lo vemos más claramente con un histograma
        fig, ax = plt.subplots(figsize=(8,5))

        ax.hist(sales_by_store, bins=30, edgecolor='black')

        ax.set_title("Distribución de las ventas totales por tienda")
        ax.set_xlabel("Ventas totales por tienda")
        ax.set_ylabel("Número de tiendas")

        st.pyplot(fig)

    #b. iii) Ranking top 10 tiendas con venas en productos en promoción
    st.markdown("**Top 10 tiendas con ventas en productos en promoción:**")
    
    #creamos un df solo con las ventas en productos en promoción
    promo_df = df[(df['onpromotion'] >0) & (df['sales']>0)]

    #agrupamos las mejores tiendas y cogemos las 10 primeras
    top10_promo_tiendas =  promo_df.groupby('store_nbr')['sales'].sum().sort_values(ascending=False).head(10)

    #lo mostramos en una tabla
    st.dataframe(top10_promo_tiendas.reset_index(name='ventas_promo'), use_container_width=True)       
    #lo mostramos en gráfica
    st.bar_chart(top10_promo_tiendas)
    

    #C) Análisis de la estacionalidad de las ventas
    st.markdown('### c) Estacionalida de las ventas')

    colC, colD, colE = st.columns(3)

    #c. i) Día de la semana con más ventas por término medio
    with colC:
        st.markdown("**Ventas medias por día de la semana:**")

        #ordenamos bien day_of_week
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if 'day_of_week' in df.columns:
            df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=dow_order, ordered=True)

        #forzamos que estén los 7 días en orden y rellenamos valores NaN con 0
        dow_mean = df.groupby('day_of_week', observed=True)['sales'].mean().reindex(dow_order).fillna(0)

        #sacamos el día de la semana maximo
        dia_top = dow_mean.idxmax()
        valor_top = dow_mean.max()

        st.success(f"El dia con mas ventas medias es **{dia_top}** "
                   f"con una media de **{valor_top:,.2f}**."
                   )

        #gráfico para verlos todos
        st.bar_chart(dow_mean)

        
    #c. ii) Volumen de ventas medio por semana del año (todos los años)
    with colD:
        st.markdown("**Ventas medias por semana del año:**")

        week_mean = df.groupby('week')['sales'].mean().sort_index()

        st.line_chart(week_mean)

    #c. iii) Día de la semana con más ventas por término medio
    with colE:
        st.markdown("**Ventas medias por mes:**")

        month_mean = df.groupby('month')['sales'].mean().sort_index()

        st.line_chart(month_mean)

#PESTAÑA 2:
with tab2:
    st.subheader("Análisis por tienda (store_nbr)")

    #trabajamos con una copia
    df2 = df.copy()

    #creamos el desplegable de tiendas
    tiendas = sorted(df2['store_nbr'].unique())
    tienda_sel = st.selectbox("Selecciona una tienda", tiendas)

    df_store = df2[df2['store_nbr'] == tienda_sel]

    st.markdown(f'### Resultados para la tienda **{tienda_sel}**')

    #EXTRA: resumen de la tienda
    ventas_totales = df_store['sales'].sum()
    productos_distintos = df_store[df_store['sales'] > 0]['family'].nunique()
    productos_promo = df_store[(df_store['sales'] > 0) & (df_store['onpromotion'] > 0)]['family'].nunique()

    c1,c2,c3 = st.columns(3)
    c1.metric("Ventas totales", f"{ventas_totales:,.2f}")
    c2.metric("Productos vendidos (familia)", f"{productos_distintos}")
    c3.metric("Productos vendidos en promoción", f"{productos_promo}")


    st.divider()
    

    #a) Número total de ventas por año
    st.markdown("### a) Ventas totales por año")
    ventas_año = df_store.groupby('year')['sales'].sum().sort_index()

    st.bar_chart(ventas_año)

    #b) Número total de productos vendidos
    st.markdown("### b) Número total de productos vendidos")

    total_productos_store = df_store[df_store['sales']> 0]['family'].nunique()
    st.metric(label="Número total de productos vendidos", value=total_productos_store)


    productos_por_año = df_store[df_store['sales']> 0].groupby('year')['family'].nunique().sort_index()
    productos_por_año.index = productos_por_año.index.astype(int)
    st.bar_chart(productos_por_año)

    #c) Número total de productos vendidos en promoción
    st.markdown("### c) Número total de productos vendidos en promoción")

    total_productos_promo_store = df_store[(df_store['sales']> 0) & (df_store['onpromotion']>0)]['family'].nunique()
    st.metric(label="Número total de productos vendidos en promoción", value=total_productos_promo_store)

    productos_promo_por_año = df_store[(df_store['sales']> 0) & (df_store['onpromotion']>0)].groupby('year')['family'].nunique().sort_index()
    productos_promo_por_año.index = productos_promo_por_año.index.astype(int)
    st.bar_chart(productos_promo_por_año)


#PESTAÑA 3:
with tab3:
    st.subheader("Análisis por estado (state)")

    #creamos otra copia
    df3 = df.copy()

    #hacemos igual que con las tiendas, la seleccion a nivel de estado
    estados = sorted(df3['state'].dropna().unique()) #limpiamos
    estados_sel = st.selectbox("Selecciona un estado", estados)

    df_state = df3[df3['state'] == estados_sel]

    st.markdown(f"### Resultados para el estado **{estados_sel}** ")

    #EXTRA: resumen del estado
    ventas_totales = df_state['sales'].sum()
    transacciones_totales = df_state['transactions'].sum()
    tiendas_estado = df_state['store_nbr'].nunique()

    c1,c2,c3 = st.columns(3)
    c1.metric("Ventas totales", f"{ventas_totales:,.2f}")
    c2.metric("Transacciones totales", f"{transacciones_totales}")
    c3.metric("Tiendas en el estado", tiendas_estado)

    st.divider()    

    #a) Número total de transacciones por año
    st.markdown("### a) Transacciones totales por año")

    transacciones_año = df_state.groupby('year')['transactions'].sum().sort_index()

    #tomamos como eje el año en entero para una mejor lectura
    transacciones_año.index = transacciones_año.index.astype(int)

    st.bar_chart(transacciones_año)

    #b) Ranking de tiendas con más ventas
    st.markdown("### b) Ranking de tiendas con más ventas")
    
    ventas_tienda = df_state.groupby('store_nbr')['sales'].sum().sort_values(ascending=False)

    top10_tiendas = ventas_tienda.head(10)

    st.bar_chart(top10_tiendas)

    st.dataframe(top10_tiendas.reset_index(name='ventas'), use_container_width=True)

    #c) Producto más vendido en la tienda
    st.markdown("### c) Producto más vendido en la tienda")

    #tomamos la tienda con más ventas del estado
    tienda_top = ventas_tienda.idxmax()

    df_tienda_top = df_state[df_state['store_nbr'] == tienda_top]
    
    producto_top = df_tienda_top.groupby('family')['sales'].sum().sort_values(ascending=False)

    producto_mas_vendido = producto_top.idxmax()
    ventas_producto_top = producto_top.max()

    st.success(f"En el estado **{estados_sel}**, la tienda con más ventas es la **{tienda_top}**. "
               f"Su producto más vendido es **{producto_mas_vendido}** "
               f"con unas ventas totales de **{ventas_producto_top:,.2f}**. "

    )
    
    #gráfico extra: top 5 productos de la tienda líder
    st.markdown("**Top 5 productos de la tienda líder del estado** ")
    st.bar_chart(producto_top.head(5))

#PESTAÑA 4
with tab4:
    st.subheader('Gráficos extra')

    df4 = df.copy()

    #1) KPIs ejecutivos
    st.markdown("### 1) KPIs clave del periodo")

    ventas_totales = df4['sales'].sum()

    promo_sales = df4.loc[df4['onpromotion'] > 0, 'sales'].sum()
    nonpromo_sales = df4.loc[df4['onpromotion'] == 0, 'sales'].sum()

    pct_promo = (promo_sales/ventas_totales * 100) if ventas_totales > 0 else 0

    top_store = df4.groupby('store_nbr')['sales'].sum().sort_values(ascending=False).idxmax()

    top_family = df4.groupby('family')['sales'].sum().sort_values(ascending=False).idxmax()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Ventas totales', f'{ventas_totales:,.2f}')
    c2.metric('Ventas en promoción', f'{promo_sales:,.2f}')
    c3.metric('Tienda líder', f'{top_store}')
    c4.metric('Producto líder', f'{top_family}')


    st.divider()


    #2.) Evolución temporal
    st.markdown("### 2) Evolución temporal de las ventas (mensual)")

    #creamos una columna año-mes para agrupar
    df4['year_month'] = df4['date'].dt.to_period('M').astype(str)

    ventas_mes = df4.groupby('year_month')['sales'].sum()

    st.line_chart(ventas_mes)

    st.caption("Serie mensual para facilitar lectura ejecutiva y detectar tendencia")

    st.divider()


    #3) Mix promoción vs no promoción (comparativa)
    st.markdown("### 3) Mix de ventas: promoción vs no promoción")

    mix_df = (pd.DataFrame({'tipo': ['Promoción', 'No promoción'], 'ventas': [promo_sales, nonpromo_sales]}).set_index('tipo'))
    st.bar_chart(mix_df)

    st.write(f"Las ventas en promoción representan aproximadamente **{pct_promo:.1f}%** del total del periodo.")

    st.divider()

    #4) Heatmap mes x día semana (estacionalidad visual)
    st.markdown("### 4)Estacionalidad visual: mes x día de la semana")

    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df4['day_of_week'] = df4['day_of_week'].astype(str).str.strip()
    df4['day_of_week'] = pd.Categorical(df4['day_of_week'], categories=dow_order, ordered=True)

    #tabla pivote: media de ventas por (mes, día)
    pivot = (df4.pivot_table(values='sales', index='month', columns='day_of_week', aggfunc='mean', observed=True).reindex(columns=dow_order).sort_index())

    st.caption("medias de ventas: filas=mes, columnas=día. Valores más altos indican mayor actividad.")

    #estilado tipo heatmap  
    st.dataframe(pivot.style.background_gradient(axis=None), use_container_width=True)
