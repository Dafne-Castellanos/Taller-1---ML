import pandas as pd
import plotly.express as px
import json
import dash
import dash_core_components as dcc
import dash_html_components as html

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

data = pd.read_csv('data.csv', delimiter = ';', thousands='.', decimal=',')

columns_to_select = data.columns[:-2]
data = data[columns_to_select]

data = data[['continent', 'country','income','gdppc','lifeE','lifeEM','lifeEF', 'births','birthsCR', 'fer']]

data['country'] = data['country'].replace('United States', 'United States of America')
data['country'] = data['country'].replace('Congo, Dem. Rep.', 'Dem. Rep. Congo') 
data['country'] = data['country'].replace('Congo, Rep.','Congo')
data['country'] = data['country'].replace('Central African Republic','Central African Rep.')
data['country'] = data['country'].replace('South Sudan','S. Sudan')
data['country'] = data['country'].replace('Czech Republic','Czechia')
data['country'] = data['country'].replace('Slovak Republic','Slovakia')
data['country'] = data['country'].replace('Kyrgyz Republic','Kyrgyzstan')
data['country'] = data['country'].replace("Cote d'Ivoire","Côte d'Ivoire")

data_grouped_continent = data.groupby('continent')
data_grouped_continent.sum()
data_grouped_continent.describe()

# --------------------------------- Mapas de calor -----------------------------------
with open('custom.geo.json', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Crear el mapa de calor
fig_births_per_continent = px.choropleth(
    data,
    geojson=geojson_data,
    locations='country',
    featureidkey='properties.name',
    color='births',
    hover_name='country',            # Nombre del país que aparecerá al pasar el ratón
    color_continuous_scale='Plasma',
    title='Número de nacimientos por continente'
)

# Configurar el mapa
fig_births_per_continent.update_geos(fitbounds="locations", visible=False)

# Cambiar los nombres de las columnas en las etiquetas
fig_births_per_continent.update_layout(
    coloraxis_colorbar_title="Nacimientos",
    title_text='Número de Nacimientos por País'
)

fig_births_per_continent.update_traces(
    hovertemplate='%{location}: %{z} Nacimientos'
)



# -------------------------------------------------------------
# Crear el mapa de calor
fig_fer_per_continent = px.choropleth(
    data,
    geojson=geojson_data,
    locations='country',
    featureidkey='properties.name',
    color='fer',
    hover_name='country',            # Nombre del país que aparecerá al pasar el ratón
    color_continuous_scale='Plasma',
    title='Fertilidad total por continente'
)

# Configurar el mapa
fig_fer_per_continent.update_geos(fitbounds="locations", visible=False)

# Cambiar los nombres de las columnas en las etiquetas
fig_fer_per_continent.update_layout(
    coloraxis_colorbar_title="Fertilidad",
    title_text='Fertilidad total por País'
)

fig_fer_per_continent.update_traces(
    hovertemplate='%{location}: %{z} Fertilidad'
)



# ------------------------------------------------------
# Crear el mapa de calor
fig_life_exp_per_continet = px.choropleth(
    data,
    geojson=geojson_data,
    locations='country',
    featureidkey='properties.name',
    color='lifeE',
    hover_name='country',            # Nombre del país que aparecerá al pasar el ratón
    color_continuous_scale='Plasma',
    title='Esperanza de vida al nacer de ambos sexos por continente'
)

# Configurar el mapa
fig_life_exp_per_continet.update_geos(fitbounds="locations", visible=False)

# Cambiar los nombres de las columnas en las etiquetas
fig_life_exp_per_continet.update_layout(
    coloraxis_colorbar_title="Expectativa de Vida",
    title_text='Expectativa de Vida por País'
)

fig_life_exp_per_continet.update_traces(
    hovertemplate='%{location}: %{z} Expectativa de Vida'
)



# ---------------------- Matrices de Correlacion ---------------------------------

data_cuant = data[['income','gdppc', 'lifeE', 'lifeEM', 'lifeEF', 'births', 'birthsCR', 'fer']]
correlation_matrix = data_cuant.corr()

# Crear el mapa de calor
fig_matrix = px.imshow(
    correlation_matrix,
    text_auto=True,
    color_continuous_scale='Plasma',
    title='Matriz de Correlación'
)



# --------------------------- Diagramas de barras ------------------------


# ------------------------------------------------------
mean_gdp_per_capita = data.groupby('continent')['gdppc'].mean().reset_index()
# Crear el diagrama de barras
fig_bars_gdp_per_capita = px.bar(mean_gdp_per_capita, x='continent', y='gdppc',
             title="Promedio del PIB per cápita por Continente",
             labels={'gdppc': 'PIB per cápita promedio', 'continent': 'Continente'},
             color='continent',
             color_discrete_sequence= px.colors.sequential.Plasma_r)

# ---------------------------------------
data_lifeE = data[['lifeE', 'lifeEM', 'lifeEF','continent']]
mean_values_per_continent = data_lifeE.groupby('continent').mean().reset_index()
df_long = pd.melt(mean_values_per_continent, id_vars='continent', value_vars=['lifeE', 'lifeEM', 'lifeEF'],
                  var_name='Variable', value_name='Value')

fig_bars_lifeE_per_continent = px.bar(df_long, x='continent', y='Value', color='Variable',
             barmode='group',
             title='Esperanza de Vida por Continente',
             labels={'Value': 'Años'},
             color_discrete_sequence= px.colors.sequential.Plasma_r)


# -----------------------------------------------
# Crear un diccionario para traducir los percentiles a nombres legibles
income_labels = {
    1: 'P10',
    2: 'P10-P20',
    3: 'P30-P50',
    4: 'P50-P70',
    5: 'P70-P90',
    6: '>P90'
}

# Aplicar la transformación
data['Income_label'] = data['income'].map(income_labels)

# Agrupar por continente e income_label y contar las ocurrencias
grouped_data = data.groupby(['continent', 'Income_label']).size().reset_index(name='count')



# Graficar
fig_bars_income = px.bar(grouped_data, x='continent', y='count', color='Income_label',
             title="Distribución del PIB por Percentil por Continente",
             labels={'count': 'Número de Países', 'continent': 'Continente', 'Income_label': 'Percentil del PIB'},
             color_discrete_sequence=px.colors.sequential.Plasma_r)


# ------------------------------------------------
mean_births_per_capita = data.groupby('continent')['births'].mean().reset_index()

# Crear el diagrama de barras
fig_bars_births_per_continent = px.bar(mean_births_per_capita, x='continent', y='births',
             title='Nacimientos por Continente',
             labels={'births': 'Nacimientos (en miles)', 'continent': 'Continente'},
             color='continent',
             color_discrete_sequence=px.colors.sequential.Plasma_r)


# ----------------------------------------------
mean_fer = data.groupby('continent')['fer'].mean().reset_index()
fig_bars_fer = px.bar(mean_fer, x='continent', y='fer',
             title='Nacimientos por Mujer por Continete',
             labels={'births': 'Nacimientos por Mujer', 'continent':'Continente'},
             color='continent',
             color_discrete_sequence=px.colors.sequential.Plasma_r)



# ---------------------------- Boxplots ---------------------------------
# Boxplot para Expectativa de Vida
fig_box_life_expectancy = px.box(data, y='lifeE',
                            title="Boxplot de Expectativa de Vida por País",
                            labels={'life_expectancy': 'Expectativa de Vida'},
                            points='all',
                            hover_data={'country': True},
                            color_discrete_sequence=px.colors.sequential.Plasma_r)  # Mostrar nombres de países en hover

# Boxplot para Nacimientos
fig_box_births = px.box(data, y='births',
                    title="Boxplot de Nacimientos por País",
                    labels={'births': 'Nacimientos'},
                    points='all',
                    hover_data={'country': True},
                    color_discrete_sequence=px.colors.sequential.Plasma_r)  # Mostrar nombres de países en hover


# Crear etiquetas para el ingreso
income_labels = {
    1: 'P10',
    2: 'P10-P20',
    3: 'P30-P50',
    4: 'P50-P70',
    5: 'P70-P90',
    6: '>P90'
}

data['income_label'] = data['income'].map(income_labels)

# Boxplot para Ingreso
fig_box_income = px.box(data, x='income_label', y='gdppc',
                    title="Boxplot de PIB per Cápita por Percentil de Ingreso",
                    labels={'gdppc': 'PIB per Cápita', 'income_label': 'Percentil de Ingreso'},
                    points='all',
                    hover_data={'country': True},
                    color_discrete_sequence=px.colors.sequential.Plasma_r)  # Mostrar nombres de países en hover

# Boxplot para PIB per Cápita
fig_box_gdppc = px.box(data, y='gdppc',
                   title="Boxplot de PIB per Cápita por País",
                   labels={'gdppc': 'PIB per Cápita'},
                   points='all',
                   hover_data={'country': True},
                   color_discrete_sequence=px.colors.sequential.Plasma_r)  # Mostrar nombres de países en hover


# Layout de la aplicación
app.layout = html.Div([
    html.H1("Análisis Global del PIB per Cápita, Tasas de Natalidad y Esperanza de Vida en 2018"),
    
    html.H2('Laura Salazar y Dafne Castellanos'),

    html.Div([
        html.H2("Mapas de Calor"),
        dcc.Graph(figure=fig_births_per_continent),
        dcc.Graph(figure=fig_fer_per_continent),
        dcc.Graph(figure=fig_life_exp_per_continet),
    ]),
    
    html.Div([
        html.H2("Matriz de Correlación"),
        dcc.Graph(figure=fig_matrix),
    ]),
    
    html.Div([
        html.H2("Diagramas de Barras"),
        dcc.Graph(figure=fig_bars_gdp_per_capita),
        dcc.Graph(figure=fig_bars_lifeE_per_continent),
        dcc.Graph(figure=fig_bars_income),
        dcc.Graph(figure=fig_bars_births_per_continent),
        dcc.Graph(figure=fig_bars_fer),
    ]),
    
    html.Div([
        html.H2("Boxplots"),
        dcc.Graph(figure=fig_box_life_expectancy),
        dcc.Graph(figure=fig_box_births),
        dcc.Graph(figure=fig_box_income),
        dcc.Graph(figure=fig_box_gdppc),
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)