# TODO: Change tuples to lists and back to tuple for appending instead of creating new lists 
import xlsxwriter as xlsw
import sqlite3
from datetime import datetime
# import gpxpy
# import gpxpy.gpx

conn = sqlite3.connect('E:/Antartida 2020/PamGuard/2020_Array_SQlite_Database _Antarctica.sqlite3')
cur = conn.cursor()
data = cur.execute("SELECT Sighting_No,Sighting_Time_GMT__,Visual_Species,Min_Group_Size,Max_Group_Size,Best_Group_Size, Sighting_effort, Distance, Distance_Units, Photograph, Photographer, Comments FROM Sightings ORDER BY Sighting_Time_GMT__ ASC")
#data = cur.execute("SELECT Sighting_No,Sighting_Time_GMT__,Visual_Species,Min_Group_Size,Max_Group_Size,Best_Group_Size,Distance,Distance_Units,Angle_Board,Detector FROM Sightings ORDER BY Sighting_Time_GMT__ ASC")
#data = cur.execute("SELECT Sighting_No, Sighting_Time_GMT__, Visual_Species, Sighting_effort FROM Sightings WHERE Sighting_effort LIKE 'ON%' ORDER BY Sighting_Time_GMT__ ASC")
time_diff = []
results = data.fetchall()
lista = []

for row in results:
	sight_time = row[1] # take date and time
	if sight_time == None:
		continue
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

## Write data to xlsx file

#Create book and sheet
workbook = xlsw.Workbook('D:/Usuario/Documentos/Cethus/antartida/Campaña-2020/Sightings_query.xlsx')
worksheet = workbook.add_worksheet()

# Add a bold format to use to highlight cells.
bold = workbook.add_format({'bold': 1})

# Set starting position
row = 0
col = 0

# Write titles

titles = ['Sighting_No', 'Time', 'Species', 'Min', 'Max', 'Best', 'Effort', 'Distance', 'Distance_Units', 'Photograph', 'Photographer', 'Comments', 'GpsDate', 'Latitude', 'Logitude']
for title in titles:
	worksheet.write(row, col, title, bold)
	col += 1

# Write the data
row = 1
col = 0
for Sighting_No, Time, Species, Min, Max, Best, Effort, Distance, Distance_Units, Photograph, Photographer, Comments, GpsDate, Latitude, Logitude in lista:
	# # Change dot for comma for xcel format
	# if Latitude or Longitude == None:
	# 	pass
	# else:
	# 	lat = list(Latitude)
	# 	lon = list(Longitude)
	# 	lat[3] = ','
	# 	lon[3] = ','
	# 	Latitude = "".join(lat)
	# 	Longitude = "".join(lon)

	# Format columns and write the data
	worksheet.write_string(row, col, Sighting_No)
	worksheet.write(row, col+1, Time)
	worksheet.write_string(row, col+2, Species)
	worksheet.write_number(row, col+3, Min)
	worksheet.write_number(row, col+4, Max)
	worksheet.write_number(row, col+5, Best)
	worksheet.write_string(row, col+6, Effort)
	worksheet.write(row, col+7, Distance)
	worksheet.write(row, col+8, Distance_Units)
	worksheet.write(row, col+9, Photograph)
	worksheet.write(row, col+10, Photographer)
	worksheet.write(row, col+11, Comments)
	worksheet.write(row, col+12, GpsDate)
	worksheet.write(row, col+13, Latitude)
	worksheet.write(row, col+14, Logitude)
	row += 1

workbook.close()
conn.close()
##################################################################################
# with open('D:/Usuario/Documentos/Cethus/antartida/Campaña-2020/python-sqlite3-queries-antarctica/Sightings_query.xlsx', 'w', newline='') as f:
# 	writer = csv.writer(f)
# 	writer.writerow(['Sighting_No', 'Time', 'Species', 'Min', 'Max', 'Best', 'Effort', 'GpsDate', 'Latitude', 'Logitude'])
# 	writer.writerows(lista)

###################################################################################
# gpx_file = open('E:/Antartida 2020/Tracks Garmin (inclompleto)/Track_ 020-01-07 200732.gpx', 'r')
# gpx = gpxpy.parse(gpx_file)

# for track in gpx.tracks:
#     for segment in track.segments:
#         for point in segment.points:
#             print('Point at ({0},{1},{2}) -> {3}'.format(point.latitude, point.longitude, point.elevation, point.time))
###################################################################################
