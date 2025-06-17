#SpaceX Falcon 9 primera etapa Predicción de aterrizaje
#Laboratorio 1: Recogida de datos

#En este laboratorio, predeciremos si la primera etapa del Falcon 9 aterrizará con éxito.
#  SpaceX anuncia lanzamientos de cohetes Falcon 9 en su sitio web con un coste de 62 millones de dólares;
#  otros proveedores cuestan más de 165 millones de dólares cada uno, 
# gran parte del ahorro se debe a que SpaceX puede reutilizar la primera etapa. Por lo tanto, 
# si podemos determinar si la primera etapa aterrizará, podemos determinar el coste de un lanzamiento.
#  Esta información se puede utilizar si una empresa alternativa quiere pujar contra SpaceX por el lanzamiento de un cohete.
#  En este laboratorio, recopilarás datos de una API y te asegurarás de que estén en el formato correcto. 
# El siguiente es un ejemplo de un lanzamiento exitoso.

# 1. Importar bibliotecas y definir funciones auxiliares
# Requests nos permite hacer peticiones HTTP que utilizaremos para obtener datos de una API
import requests
# Pandas es una biblioteca de software escrita para el lenguaje de programación Python para la manipulación y análisis de datos.
import pandas as pd
# NumPy es una librería para el lenguaje de programación Python, que añade soporte para matrices y arrays multidimensionales de gran tamaño, junto con una gran colección de funciones matemáticas de alto nivel para operar sobre estos arrays
import numpy as np
# Datetime es una librería que nos permite representar fechas
import datetime

# Esta opción imprimirá todas las columnas de un marco de datos
pd.set_option('display.max_columns', None)
# Configurando esta opción se imprimirán todos los datos de una característica
pd.set_option('display.max_colwidth', None)

# A continuación definiremos una serie de funciones helper que nos ayudarán a utilizar la API
#  para extraer información utilizando números de identificación en los datos de lanzamiento.

# De la columna cohete queremos saber el nombre del propulsor.

# 2.Toma el conjunto de datos y utiliza la columna rocket para llamar a la API y añadir los datos a la lista
def getBoosterVersion(data):
    for x in data['rocket']:
       if x:
        response = requests.get("https://api.spacexdata.com/v4/rockets/"+str(x)).json()
        BoosterVersion.append(response['name'])
# 3.De la plataforma de lanzamiento nos gustaría saber el nombre del lugar de lanzamiento utilizado, la logitud y la latitud.
def getLaunchSite(data):
    for x in data['launchpad']:
       if x:
        response = requests.get("https://api.spacexdata.com/v4/launchpads/"+str(x)).json()
        Longitude.append(response['longitude'])
        Latitude.append(response['latitude'])
        LaunchSite.append(response['name'])
# 4.De la carga útil queremos saber su masa y la órbita a la que se dirige.
def getPayloadData(data):
    for load in data['payloads']:
       if load:
        response = requests.get("https://api.spacexdata.com/v4/payloads/"+load).json()
        PayloadMass.append(response['mass_kg'])
        Orbit.append(response['orbit'])

# 5.# De los núcleos nos gustaría saber el resultado del aterrizaje, el tipo de aterrizaje, el número de vuelos con ese núcleo,
# si se utilizaron aletas de rejilla, si se reutilizó el núcleo, si se utilizaron patas, la pista de aterrizaje utilizada, 
# el bloque del núcleo que es un número utilizado para separar la versión de los núcleos, 
# el número de veces que este núcleo específico ha sido reutilizado, y la serie del núcleo.
def getCoreData(data):
    for core in data['cores']:
            if core['core'] != None:
                response = requests.get("https://api.spacexdata.com/v4/cores/"+core['core']).json()
                Block.append(response['block'])
                ReusedCount.append(response['reuse_count'])
                Serial.append(response['serial'])
            else:
                Block.append(None)
                ReusedCount.append(None)
                Serial.append(None)
            Outcome.append(str(core['landing_success'])+' '+str(core['landing_type']))
            Flights.append(core['flight'])
            GridFins.append(core['gridfins'])
            Reused.append(core['reused'])
            Legs.append(core['legs'])
            LandingPad.append(core['landpad'])
# 6 Ahora vamos a empezar a solicitar datos de lanzamiento de cohetes a la API de SpaceX con la siguiente URL:
spacex_url="https://api.spacexdata.com/v4/launches/past"
response = requests.get(spacex_url)
print(response.content)

#Deberías ver que la respuesta contiene información masiva sobre los lanzamientos de SpaceX.
#  A continuación, vamos a intentar descubrir más información relevante para este proyecto.

#Tarea 1: Solicitar y analizar los datos de lanzamiento de SpaceX utilizando la solicitud GET
# Para que los resultados JSON solicitados sean más consistentes, utilizaremos el siguiente objeto de respuesta estática para este proyecto:
static_json_url='https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json'
response=requests.get(static_json_url)
response.status_code
# Utilice json_normalize meethod para convertir el resultado json en un dataframe
data = pd.json_normalize(response.json())
# Imprimir las primeras filas del dataframe
print(data.head())
# Observará que muchos de los datos son ID. Por ejemplo, la columna del cohete no contiene información sobre el cohete,
#  sólo un número de identificación.
# Ahora usaremos la API de nuevo para obtener información sobre los lanzamientos usando los IDs dados para cada lanzamiento. 
# En concreto, utilizaremos las columnas cohete, cargas útiles, plataforma de lanzamiento y núcleos.
# Tomemos un subconjunto de nuestro dataframe manteniendo sólo las características que queremos y el número de vuelo, y date_utc.
data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]

# Eliminaremos las filas con múltiples núcleos porque esos son cohetes falcon con 2 cohetes propulsores extra y filas que tienen múltiples cargas útiles en un solo cohete.
data = data[data['cores'].map(len)==1]
data = data[data['payloads'].map(len)==1]

# Dado que payloads y cores son listas de tamaño 1 también extraeremos el único valor de la lista y reemplazaremos la característica.
data['cores'] = data['cores'].map(lambda x : x[0])
data['payloads'] = data['payloads'].map(lambda x : x[0])

# También queremos convertir el date_utc a un datetime datatype y luego extraer la fecha dejando la hora
data['date'] = pd.to_datetime(data['date_utc']).dt.date

# Usando la fecha restringiremos las fechas de los lanzamientos
data = data[data['date'] <= datetime.date(2020, 11, 13)]

# Del cohete queremos saber el nombre del propulsor.

#De la carga útil nos gustaría saber su masa y la órbita a la que se dirige.

#De la plataforma de lanzamiento nos gustaría saber el nombre del lugar de lanzamiento utilizado, la longitud y la latitud.

#De los núcleos nos gustaría saber el resultado del aterrizaje, el tipo de aterrizaje, 
# el número de vuelos con ese núcleo, si se utilizaron aletas de rejilla, si se reutilizó el núcleo, si se utilizaron patas, 
# la pista de aterrizaje utilizada, el bloque del núcleo, que es un número utilizado para separar la versión de los núcleos,
#  el número de veces que se ha reutilizado este núcleo específico y la serie del núcleo.

#Los datos de estas solicitudes se almacenarán en listas y se utilizarán para crear un nuevo marco de datos
#Global variables 
BoosterVersion = []
PayloadMass = []
Orbit = []
LaunchSite = []
Outcome = []
Flights = []
GridFins = []
Reused = []
Legs = []
LandingPad = []
Block = []
ReusedCount = []
Serial = []
Longitude = []
Latitude = []
#Estas funciones aplicarán las salidas globalmente a las variables anteriores. Echemos un vistazo a la variable BoosterVersion.
#  Antes de aplicar getBoosterVersion la lista está vacía:
print(BoosterVersion)
#Ahora, apliquemos el método de la función getBoosterVersion para obtener la versión del booster
getBoosterVersion(data)
# Ahora la lista contiene los nombres de los propulsores de los cohetes.
print(BoosterVersion[0:5])  # Imprime los primeros 5 nombres de propulsores
#podemos aplicar el resto de las funciones aquí:
getLaunchSite(data)
getPayloadData(data)
getCoreData(data)
#Finalmente vamos a construir nuestro conjunto de datos utilizando los datos que hemos obtenido. Combinamos las columnas en un diccionario.
launch_dict = {'FlightNumber': list(data['flight_number']),
'Date': list(data['date']),
'BoosterVersion':BoosterVersion,
'PayloadMass':PayloadMass,
'Orbit':Orbit,
'LaunchSite':LaunchSite,
'Outcome':Outcome,
'Flights':Flights,
'GridFins':GridFins,
'Reused':Reused,
'Legs':Legs,
'LandingPad':LandingPad,
'Block':Block,
'ReusedCount':ReusedCount,
'Serial':Serial,
'Longitude': Longitude,
'Latitude': Latitude}

# Ahora creamos un marco de datos a partir del diccionario
launch_df = pd.DataFrame(launch_dict)

# Muestra el sumario del marco de datos
print(launch_df.info())

#Tarea 2: Filtrar el marco de datos para incluir sólo los lanzamientos del Falcon 9
# Finalmente eliminaremos los lanzamientos del Falcon 1 manteniendo sólo los lanzamientos del Falcon 9.
#  Filtra los datos usando la columna BoosterVersion para mantener sólo los lanzamientos de Falcon 9. 
# Guarde los datos filtrados en un nuevo marco de datos llamado data_falcon9.
# Hint data['BoosterVersion']!='Falcon 1'
data_falcon9 = launch_df[launch_df['BoosterVersion'] != 'Falcon 1']
#Ahora que hemos eliminado algunos valores debemos restablecer la columna FlgihtNumber
data_falcon9.loc[:,'FlightNumber'] = list(range(1, data_falcon9.shape[0]+1))
print(data_falcon9) 

# Gestión de datos
# A continuación podemos ver que en nuestro conjunto de datos faltan valores en algunas de las filas.
data_falcon9.isnull().sum()

#Tarea 3: Tratar con valores perdidos
# Calcule a continuación la media de PayloadMass utilizando la función .mean(). 
mean_payload_mass = data_falcon9['PayloadMass'].mean()
print("Media de PayloadMass:", mean_payload_mass)

# A continuación, utilice la media y la función .replace() para reemplazar los valores np.nan de los datos por la media calculada.
data_falcon9['PayloadMass'].replace(np.nan, mean_payload_mass, inplace=True)
# Ahora podemos comprobar que no hay valores perdidos en la columna PayloadMass
print(data_falcon9['PayloadMass'].isnull().sum())




#Debería ver que el número de valores perdidos de PayLoadMass cambia a cero.

#Ahora no deberíamos tener valores perdidos en nuestro conjunto de datos, excepto en LandingPad.

#Ahora podemos exportarlo a un CSV para la siguiente sección, pero para que las respuestas sean coherentes,
#  en el próximo laboratorio proporcionaremos datos en un intervalo de fechas preseleccionado.







data_falcon9.to_csv("dataset_part_1.csv", index=False)