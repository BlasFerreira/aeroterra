import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as np

# from shapely.geometry import Point
st.title('Aeroterra (Evaluación Técnica de Ingreso)')

df_ships = pd.read_csv('./ships.csv')
gdf_new = gpd.read_file('./zonas.shp')



st.header('Actividad y Tiempo de Permanencia de los Barcos en Diferentes Zonas Geográficas')


# Opciones para el selector
opciones_buques = [8840908, 2410206, 2040206, 4415, 7315, "Todas las opciones"]
# Widget de selector
seleccion_buques = st.selectbox("Seleccione el buque quiere ver:", opciones_buques,index = 5)


# Opciones para el selector
opciones_zonas = ['Rio Parana', 'Rio de la plata','Todas las opciones']
# Widget de selector
seleccion_zonas = st.selectbox("Seleccione el rio que quiere ver:", opciones_zonas,index = 2)



def plot_velocidad(	df_ships_aux , gdf_new_aux ) :

	df_ships = df_ships_aux
	gdf_new = gdf_new_aux

	st.write( '   ')
	# Convert the 'date' column to datetime
	df_ships['date'] = pd.to_datetime(df_ships['date'])
	df_ships = df_ships.sort_values(['id_buque', 'date'])

	# Calculate the time difference between each row
	df_ships['time_diff'] = df_ships.groupby('id_buque')['date'].diff()
	df_ships['time_diff'] = df_ships['time_diff'].dt.total_seconds() / 3600
	# Calculate the total time spent by each ship in seconds
	stay_time = df_ships.groupby(['id_buque', 'latitude', 'longitude'])['time_diff'].sum().reset_index()
	# Convert the longitude and latitude to a geometric point
	df_ships['geometry'] = df_ships.apply(lambda row: Point(row.longitude, row.latitude), axis=1)
	# Convert the DataFrame to a GeoDataFrame
	gdf_ships = gpd.GeoDataFrame(df_ships, geometry='geometry')
	# Create a larger figure and axis
	fig, ax = plt.subplots(1, 1, figsize=(10, 10))
	# Plot the zones
	gdf_new.plot(column='zone_name', legend=True, ax=ax)
	# Plot the total time spent by each ship
	gdf_ships.plot(column='time_diff', legend=True, ax=ax, marker='o', markersize=5, cmap='viridis')

	st.pyplot(fig)

def plot_plotly(data ) :

	# Convert the 'date' column to datetime format
	data['date'] = pd.to_datetime(data['date'])

	# Sort the data by 'id_buque' and 'date'
	data = data.sort_values(['id_buque', 'date'])

	# Calculate the difference in 'date' between each row and the previous row
	data['time_diff'] = data.groupby('id_buque')['date'].diff()

	# Convert the time difference to hours
	data['time_diff'] = data['time_diff'].dt.total_seconds() / 3600

	# Group the data by 'id_buque' and coordinates and calculate the sum of 'time_diff' for each group
	stay_time = data.groupby(['id_buque', 'latitude', 'longitude'])['time_diff'].sum().reset_index()

	# Create a scatter plot on a map, coloring the markers by stay time
	fig = px.scatter_geo(stay_time, lat='latitude', lon='longitude', color='time_diff', hover_name='id_buque', color_continuous_scale=px.colors.sequential.Plasma)

	fig.update_layout(title_text = 'Ship Locations and Stay Time', title_x = 0.5, showlegend = False, geo_scope='world')


	st.plotly_chart(fig)


def grafico_barras(data):
    fig, ax = plt.subplots(figsize=(8, 6))
    data['type'].value_counts().plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title('Cantidad de Barcos por Tipo')
    ax.set_xlabel('Tipo de Barco')
    ax.set_ylabel('Cantidad')
    ax.set_xticklabels(data['type'].value_counts().index, rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Mostrar el gráfico de barras en Streamlit
    st.pyplot(fig)


def tipo_de_barco(data):
    fig = px.scatter_geo(data, lat='latitude', lon='longitude', color='type', hover_name='id_buque',
                         title='Ubicación de Barcos en el Mapa', color_discrete_sequence=px.colors.qualitative.Pastel)

    fig.update_layout(geo_scope='world')

    # Mostrar el gráfico de dispersión geográfico
    st.plotly_chart(fig)


# Filtrar el DataFrame según la opción seleccionada
if seleccion_buques  == "Todas las opciones":

	if seleccion_zonas == "Todas las opciones":

		st.write('''Estos graficos muestran la actividad de los barcos en diferentes zonas geográficas. 
					Las áreas coloreadas son las zonas, y los puntos representan barcos. El color de cada 
					punto indica el tiempo total que un barco ha pasado, con colores más oscuros indicando 
					más tiempo(en horas). El time_diff se calcula como la diferencia en tiempo entre cada 
					registro de ubicación de un barco y el registro anterior de ese mismo barco. Los datos 
					se ordenan por barco y fecha, y luego se calcula esta diferencia en tiempo para cada 
					par de registros consecutivos. La diferencia se convierte a horas para facilitar la 
					interpretación.''')

		plot_velocidad(	df_ships , gdf_new )
		plot_plotly(df_ships )

	else : 

		st.write(f'''Estos graficos muestran la actividad de los barcos con respecto al { seleccion_zonas }.
					Las áreas coloreadas son las zonas, y los puntos representan barcos. El color de cada 
					punto indica el tiempo total que un barco ha pasado, con colores más oscuros indicando 
					más tiempo(en horas). El time_diff se calcula como la diferencia en tiempo entre cada 
					registro de ubicación de un barco y el registro anterior de ese mismo barco. Los datos 
					se ordenan por barco y fecha, y luego se calcula esta diferencia en tiempo para cada
					 par de registros consecutivos. La diferencia se convierte a horas para facilitar la 
					 interpretación.''')

		plot_velocidad(	df_ships , gdf_new[ gdf_new['zone_name'] == seleccion_zonas ] )
		plot_plotly(df_ships )

else:

	if seleccion_zonas == "Todas las opciones":


		st.write( f'''Estos graficos muestran la actividad del barco {seleccion_buques} en diferentes zonas geográficas. 
			Las áreas coloreadas son las zonas, y los puntos representan barcos. El color de cada 
			punto indica el tiempo total que un barco ha pasado, con colores más oscuros indicando 
			más tiempo(en horas). El time_diff se calcula como la diferencia en tiempo entre cada 
			registro de ubicación de un barco y el registro anterior de ese mismo barco. Los datos 
			se ordenan por barco y fecha, y luego se calcula esta diferencia en tiempo para cada par 
			de registros consecutivos. La diferencia se convierte a horas para facilitar la interpretación.''' )


		plot_velocidad(	df_ships[ df_ships['id_buque'] == seleccion_buques]  , gdf_new )
		plot_plotly(df_ships[ df_ships['id_buque'] == seleccion_buques] )


	else : 
		st.write( f'''Estos graficos muestran la actividad del barco {seleccion_buques} con respecto al {seleccion_zonas}
		 	. Las áreas coloreadas son las zonas, y los puntos representan barcos. El color de cada 
			punto indica el tiempo total que un barco ha pasado, con colores más oscuros indicando 
			más tiempo(en horas). El time_diff se calcula como la diferencia en tiempo entre cada 
			registro de ubicación de un barco y el registro anterior de ese mismo barco. Los datos 
			se ordenan por barco y fecha, y luego se calcula esta diferencia en tiempo para cada par 
			de registros consecutivos. La diferencia se convierte a horas para facilitar la interpretación.''' )

		plot_velocidad(	df_ships[ df_ships['id_buque'] == seleccion_buques] , gdf_new[ gdf_new['zone_name'] == seleccion_zonas ])
		plot_plotly(df_ships[ df_ships['id_buque'] == seleccion_buques]  )

st.header('Gráfico de Barras - "Cantidad de Barcos por Tipo"')
st.write('Este gráfico muestra la distribución de la cantidad de barcos según su tipo en el conjunto de datos. Los datos se representan en un gráfico de barras, donde cada barra representa un tipo de barco y su altura indica la cantidad de barcos de ese tipo presentes en el dataset. A través de este gráfico, podemos identificar fácilmente qué tipos de barcos son más comunes y cuáles son menos frecuentes.')
grafico_barras(df_ships)


st.header('Gráfico de Dispersión Geográfico - "Ubicación de Barcos en el Mapa":')
st.write('Este gráfico utiliza una representación geográfica para mostrar la ubicación de los barcos en el mapa. Los puntos de colores en el mapa indican la posición de cada barco, y el color de los puntos está codificado según el tipo de barco. Al pasar el cursor sobre los puntos, podemos obtener información detallada sobre cada barco, incluido su identificador. Este gráfico nos permite visualizar cómo están distribuidos geográficamente los diferentes tipos de barcos y si existen patrones o concentraciones específicas en ciertas áreas.')
tipo_de_barco(df_ships)