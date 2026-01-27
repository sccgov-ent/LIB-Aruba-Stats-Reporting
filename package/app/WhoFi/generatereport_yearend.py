import os
import csv
from dotenv import load_dotenv
import calendar
from datetime import *
import mariadb

load_dotenv(override=True)
DB_IP = os.getenv("DB_IP")
DB_LOGIN = os.getenv("DB_LOGIN")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
conn = mariadb.connect(host=DB_IP, user=DB_LOGIN, password=DB_PASSWORD, database=DB_NAME)
cursor = conn.cursor()
# headers = ["date", "group name", "count"]
query = "select date, group_name, SUM(session_count) from `Daily_stats` where Year(date) = YEAR(ADD_MONTHS(date, -1)) group by date, group_name order by date;"
cursor.execute(query)
results = cursor.fetchall()
compiled = [[0 for a in range(14)] for b in range(31)]
for entry in results:
    match entry[1]:
        case "Campbell_Library":
            compiled[entry[0].day-1][0] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "Campbell Library":
            compiled[entry[0].day-1][1] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "CampbellExpress_Library":
            compiled[entry[0].day-1][2] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "Cupertino_Library":
            compiled[entry[0].day-1][3] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "default":
            compiled[entry[0].day-1][4] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "Gilroy_Library":
            compiled[entry[0].day-1][5] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "LosAltos_Library":
            compiled[entry[0].day-1][6] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "Milpitas_Library":
            compiled[entry[0].day-1][7] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "MorganHill_Library":
            compiled[entry[0].day-1][8] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "SantaClaraHQ":
            compiled[entry[0].day-1][9] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "Saratoga_Library":
            compiled[entry[0].day-1][10] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "SCCLD-Wireless":
            compiled[entry[0].day-1][11] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case "Woodland_Library":
            compiled[entry[0].day-1][12] = entry[2]
            compiled[entry[0].day-1][13] = entry[0]
        case _:
            raise KeyError("Unexpected Group Value: " + entry[1])
labels = ["Campbell_Library", "Campbell Library", "CampbellExpress_Library", "Cupertino_Library", "default", "Gilroy_Library", "LosAltos_Library", "Milpitas_Library", "MorganHill_Library", "SantaClaraHQ", "Saratoga_Library", "SCCLD-Wireless", "Woodland_Library", "date"]
with open("/home/reports/" + DB_NAME + " Report Year End" + ".csv", "w") as file:
    writer = csv.writer(file)
    writer.writerow(labels)
    writer.writerows(compiled)
print(compiled)

query = "select avg(visits) as visits, group_name, dayname(date) from (select count(macaddr) as visits, group_name, date from Daily_stats where Year(date) = YEAR(ADD_MONTHS(date, -1)) group by group_name, date) as stats group by group_name, dayname(date);"
cursor.execute(query)
results = cursor.fetchall()
with open("/home/reports/" + DB_NAME + " Average Daily Visits Report Year End" + ".csv", "w") as file:
    writer = csv.writer(file)
    writer.writerows(results)
print(results)

query = "select max(visits) as visits, group_name, date from (select connection_count as visits, group_name, Hour(time) as date from Connection_Counts where Year(time) = YEAR(ADD_MONTHS(time, -1)) group by group_name, hour(time)) as stats group by group_name, date;"
cursor.execute(query)
results = cursor.fetchall()
with open("/home/reports/" + DB_NAME + " Average Peak Hourly Report Year End" + ".csv", "w") as file:
    writer = csv.writer(file)
    writer.writerows(results)
print(results)

query = "select sum(session_count), group_name as monthly_sessions from Daily_stats where Year(date) = YEAR(ADD_MONTHS(date, -1)) group by group_name;"
cursor.execute(query)
results = cursor.fetchall()
with open("/home/reports/" + DB_NAME + " Monthly Sessions Report Year End" + ".csv", "w") as file:
    writer = csv.writer(file)
    writer.writerows(results)
print(results)

query = "select count(*) as Total_Visits, group_name from Daily_stats where Year(date) = YEAR(ADD_MONTHS(date, -1)) group by group_name;"
cursor.execute(query)
results = cursor.fetchall()
with open("/home/reports/" + DB_NAME + " Total Visits Report Year End" + ".csv", "w") as file:
    writer = csv.writer(file)
    writer.writerows(results)
print(results)

query = "select group_name, count(*) as unique_visits from (select distinct macaddr, group_name from Daily_stats where Year(date) = YEAR(ADD_MONTHS(date, -1))) as stats group by group_name;"
cursor.execute(query)
results = cursor.fetchall()
with open("/home/reports/" + DB_NAME + " Unique Visitors Report Year End" + ".csv", "w") as file:
    writer = csv.writer(file)
    writer.writerows(results)
print(results)

query = "select group_name, Total_Visits / unique_visits from (select group_name, count(*) as Total_Visits from Daily_stats where Year(date) = YEAR(ADD_MONTHS(date, -1)) group by group_name) as A natural join (select group_name, count(*) as unique_visits from (select distinct macaddr, group_name from Daily_stats where month(date) = month(CURRENT_DATE) and Year(date) = YEAR(ADD_MONTHS(date, -1))) as C group by group_name) as B;"
cursor.execute(query)
results = cursor.fetchall()
with open("/home/reports/" + DB_NAME + " Average Return Rate Report Year End" + ".csv", "w") as file:
    writer = csv.writer(file)
    writer.writerows(results)
print(results)

query = "select Max(users) from concurrent_users where Year(date) = YEAR(ADD_MONTHS(date, -1))"
cursor.execute(query)
results = cursor.fetchall()
with open("/home/reports/" + DB_NAME + " Max Concurrent Users Report Year End" + ".csv", "w") as file:
    writer = csv.writer(file)
    writer.writerows(results)
print(results)

