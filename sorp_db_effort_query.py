# TODO: Change tuples to lists and back to tuple for appending instead of creating new lists 
import csv
import sqlite3
from datetime import datetime, timedelta
import xlsxwriter as xlsw

# Connect to Databse and query data
conn = sqlite3.connect('E:/Antartida 2020/PamGuard/2020_Array_SQlite_Database _Antarctica.sqlite3')
cur = conn.cursor()
#data = cur.execute("SELECT Time, Visual_Effort FROM Environment ORDER BY Time ASC")
data = cur.execute("SELECT Time, Visual_Effort FROM Environment ORDER BY Time ASC")
time_diff = [] # Temporal calculation of closest date and time
query_output = data.fetchall() # Time and status of every log
status_ls = [] # Storage of all status
effort_change = [] # Storage of datetime and status effort log where status changed  
status_change = [] # Storage of full effort and position log status only where status changed
total_eff = [] # Effort type and duration

# Get all status
for row in query_output:
	status = row[1]
	status_ls.append(status[:2]) # ON for ON, OF for OFF, IC for ICE

temp_stat = 'OF' # Temporal variable to look only for changes in status

# Keep only status changes
for i, v in enumerate(status_ls):	
	if temp_stat != v:
		effort_change.append(query_output[i])
		temp_stat = v

# Get closest date and time from GpsData to status change and request GPS position
for row in effort_change:
	eff_time = row[0] # take date and time
	if eff_time == None:
		continue
	eff_time_str = eff_time[:16] # take HH:MM for query filtering reference
	eff_time_dt = datetime.strptime(eff_time, '%Y-%m-%d %H:%M:%S.%f') # convert to datetime format for operations
	gps_times = cur.execute("SELECT GpsDate, Latitude, longitude FROM gpsData WHERE GpsDate LIKE (?)", (eff_time_str + '%',))	
	gps_times_ls = gps_times.fetchall()
	
	if len(gps_times_ls) != 0:
		for time in gps_times_ls:
			gps_time_dt = datetime.strptime(time[0], '%Y-%m-%d %H:%M:%S.%f')
			time_diff.append(abs(eff_time_dt - gps_time_dt))
		indice = time_diff.index(min(time_diff))
		full_row = row + gps_times_ls[indice]
		status_change.append(full_row)
		time_diff = []
	else: 
		full_row = row + (None,None,None)
		status_change.append(full_row)	

# Resultado final status_change
# for row in status_change:
# 	print(row)
# Calculate time differences por total effort
seconds_in_day = 24 * 60 * 60

for row, items in enumerate(status_change):
	try:	
		if not items[1].startswith('OFF'):	
			ini_time = datetime.strptime(items[0], '%Y-%m-%d %H:%M:%S.%f')
			end_time = datetime.strptime(status_change[row+1][0], '%Y-%m-%d %H:%M:%S.%f')
			time_delta = end_time-ini_time
			total_eff.append((items[1], str(time_delta)))	
			row_ls = list(items)
			row_ls.append(str(time_delta))
			status_change[row] = tuple(row_ls)
		else:
			row_ls = list(items)
			row_ls.append(None)
			status_change[row] = tuple(row_ls)
	except:
		print('error en: ', row, items)
		row_ls = list(items)
		row_ls.append(None)
		status_change[row] = tuple(row_ls)

for i in status_change:
	print(i)

## Write data to xlsx file

#Create book and sheet
workbook = xlsw.Workbook('D:/Usuario/Documentos/Cethus/antartida/Campaña-2020/Effort_query.xlsx')
worksheet1 = workbook.add_worksheet('Esfuerzo visual completo')
worksheet2 = workbook.add_worksheet('Calculo esfuerzo visual')

# Add a bold format to use to highlight cells.
bold = workbook.add_format({'bold': 1})

# Set starting position
row = 0
col = 0

# Write titles

titles = ['Time', 'Effort Status', 'GpsDate', 'Latitude', 'Logitude', 'Effort duration']
for title in titles:
	worksheet2.write(row, col, title, bold)
	col += 1

# Write the data
row = 1
col = 0
for Time, Effort, GpsDate, Latitude, Longitude, Effort_dur in status_change:
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
	worksheet2.write(row, col, Time)
	worksheet2.write(row, col+1, Effort)
	worksheet2.write(row, col+2, GpsDate)
	worksheet2.write(row, col+3, Latitude)
	worksheet2.write(row, col+4, Longitude)
	worksheet2.write(row, col+5, Effort_dur)

	row += 1

workbook.close()
conn.close()