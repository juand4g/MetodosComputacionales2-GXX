import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from statsmodels.tsa.seasonal import seasonal_decompose
# Cargar los datos
archivo = open('C:/Users/Usuario/Desktop/list_aavso-arssn_daily.txt', 'r')
year = []
month = []
day = []
manchas_sol = []

# Procesar el archivo
for linea in archivo:
    if linea != '':  # Ignorar líneas vacías
        partes = linea.split()  # Separar cada parte de la línea
        if len(partes) == 4:  # Asegurarse de que la línea tenga 4 partes
            if partes[0] != 'Year':  # Ignorar encabezado
                if int(partes[0]) < 2012:  # Filtrar datos hasta 2012
                    num_fltY = int(partes[0])
                    num_fltM = int(partes[1])
                    num_fltD = int(partes[2])
                    num_fltS = int(partes[3])
                    year.append(num_fltY)
                    month.append(num_fltM)
                    day.append(num_fltD)
                    manchas_sol.append(num_fltS)
archivo.close()  # Cerrar el archivo después de leer

fechas = pd.to_datetime([f'{a}-{m}-{d}' for a, m, d in zip(year, month, day)])
datos_manchas = np.array(manchas_sol)
plt.plot(fechas, datos_manchas)
plt.xlabel('Fecha')
plt.ylabel('Número de manchas solares')
plt.title('Manchas solares a lo largo del tiempo')
plt.show()
df = pd.DataFrame({'fecha': fechas, 'manchas': manchas_sol})
df.set_index('fecha', inplace=True)

# Definir un filtro pasa-bajo (Butterworth)
def butter_lowpass(cutoff, fs, order=4):
    nyquist = 0.5 * fs  # Frecuencia de Nyquist
    normal_cutoff = cutoff / nyquist  # Frecuencia de corte normalizada
    b, a = butter(order, normal_cutoff, btype='low', analog=False)  # Coeficientes del filtro
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=4):
    b, a = butter_lowpass(cutoff, fs, order)
    y = filtfilt(b, a, data)  # Aplicar el filtro
    return y

# Filtrar los datos para eliminar el ruido (ajusta el corte según sea necesario)
# cutoff: frecuencia de corte, fs: frecuencia de muestreo (1 día por defecto)
cutoff = 0.01  # Frecuencia de corte (ajústala según el análisis, por ejemplo, 0.01 para eliminar frecuencias altas)
fs = 1  # Frecuencia de muestreo (1 día)
manchas_suavizadas = butter_lowpass_filter(df['manchas'].values, cutoff, fs)

# Visualizar los datos originales y los suavizados
plt.figure(figsize=(10, 6))
plt.plot(df.index, df['manchas'], label='Datos originales')
plt.plot(df.index, manchas_suavizadas, label='Datos suavizados', linestyle='--', color='red')
plt.xlabel('Fecha')
plt.ylabel('Manchas solares')
plt.title('Datos de manchas solares con y sin suavizado')
plt.legend()
plt.show()

# Realizar la transformada de Fourier sobre los datos suavizados
frecuencias = np.fft.rfftfreq(len(manchas_suavizadas), d=1)  # 'd=1' significa separación por 1 día
transformada = np.fft.rfft(manchas_suavizadas)

# Calcular la densidad espectral
densidad_espectral = np.abs(transformada)**2

# Visualizar la densidad espectral en escala log-log
plt.figure(figsize=(8, 6))
plt.loglog(frecuencias, densidad_espectral, label='Densidad espectral')
plt.xlabel('Frecuencia [1/día]', fontsize=12)
plt.ylabel('Densidad espectral', fontsize=12)
plt.title('Transformada de Fourier de las manchas solares (Escala log-log)', fontsize=14)
plt.grid(True)
plt.legend()
plt.show()

# Encontrar la frecuencia dominante y evitamos el indice 0
frecuencia_dominante = frecuencias[np.argmax(np.abs(transformada[1:]))+1]

# Calcular el período (inverso de la frecuencia dominante en días)
if frecuencia_dominante != 0:
    periodo_solar_dias = 1 / frecuencia_dominante
    periodo_solar_anos = periodo_solar_dias / 365.25
    print(f'2.b.a) P_solar = {periodo_solar_anos:.2f} años')
else:
    print("2.b.a) No se detectó una frecuencia dominante significativa.")
