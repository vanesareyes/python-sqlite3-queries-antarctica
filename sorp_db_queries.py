########### arreglar conteo de rows para arreglar condicional cuando no encuentra posicion de gps
import csv
import sqlite3
from datetime import datetime
import gpxpy
import gpxpy.gpx


conn = sqlite3.connect('D:/Usuario/Escritorio/PamGuard/2020_Array_SQlite_Database _Antarctica.sqlite3')
cur = conn.cursor()
# data = cur.execute("SELECT Sighting_No,Sighting_Time_GMT__,Visual_Species,Min_Group_Size,Max_Group_Size,Best_Group_Size,Distance,Distance_Units,Angle_Board,Detector FROM Sightings")
data = cur.execute("SELECT Sighting_No, Sighting_Time_GMT__, Visual_Species, Sighting_effort FROM Sightings WHERE Sighting_effort LIKE 'ON%' ORDER BY Sighting_Time_GMT__ ASC")
time_diff = []
results = data.fetchall()
lista = []
n = 0

for row in results:
	n += 1
	sight_time = row[1] # take date and time
	sight_time_str = sight_time[:16] # take HH:MM for query filtering reference
	sight_time_dt = datetime.strptime(sight_time, '%Y-%m-%d %H:%M:%S.%f') # convert to datetime format for operations
	gps_times = cur.execute("SELECT GpsDate, Latitude, longitude FROM gpsData WHERE GpsDate LIKE (?)", (sight_time_str + '%',))	
	gps_times_ls = gps_times.fetchall()
	
	if len(gps_times_ls) != 0:
		for time in gps_times_ls:
			gps_time_dt = datetime.strptime(time[0], '%Y-%m-%d %H:%M:%S.%f')
			time_diff.append(abs(sight_time_dt - gps_time_dt))
		indice = time_diff.index(min(time_diff))
		time_diff = []
		row_full = row + gps_times_ls[indice]
		lista.append(row_full)
	else: 
		row_full = row + (None,None,None)
		lista.append(row_full)
	if n > 30:
		break

with open('D:/Usuario/Escritorio/PamGuard/query_output.csv', 'w') as f:
	writer = csv.writer(f)
	writer.writerow(['Sighting_No', 'Time', 'Species', 'Effort', 'GpsDate', 'Latitude', 'Logitude'])
	writer.writerows(lista)
	



# gpx_file = open('E:/Antartida 2020/Tracks Garmin (inclompleto)/Track_ 020-01-07 200732.gpx', 'r')
# gpx = gpxpy.parse(gpx_file)

# for track in gpx.tracks:
#     for segment in track.segments:
#         for point in segment.points:
#             print('Point at ({0},{1},{2}) -> {3}'.format(point.latitude, point.longitude, point.elevation, point.time))
###################################################################################

# for row in data:
	# extraer fecha de cada row y pasarlo a datestring
	# extraer AAAA:DD:MM HH:MM
	# hacer query con LIKE extreayendo Id de tabla gpsData comparando GpsDate y meter en una lista de tuples y pasar a datestring
	# comparar usando func neareast
	# imprimir para debug row original: Sighting_No, Sighting_Time_GMT__, Visual_Species, Sighting_effort + GpsIndex, GpsTime, Latitude, longitude, dif temporal
