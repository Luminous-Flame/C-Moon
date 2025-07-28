#!/usr/bin/env python
# -*- coding: utf-8 -*-
import mysql.connector
import subprocess
import logging
from datetime import datetime

logging.basicConfig(filename='/tmp/cmdb_clean.log', level=logging.INFO, format='%(asctime)s %(message)s')
logging.info("Script started")

db = mysql.connector.connect(
    host="localhost",
    user="cmoon",
    password="cmoonpassword",
    database="cmoon"
)

def check_ip_reachability(ip):
    try:
        result = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2, text=True)
        if result.returncode == 0:
            return True
        else:
            return False
    except subprocess.TimeoutExpired:
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

cursor = db.cursor()

cursor.execute("SELECT IndexValue, IP, Strike, HostName, Status, ProductName, Vendor FROM Serverdata")
data = cursor.fetchall()

for row in data:
    index_value = row[0]
    ip = row[1]
    strike = row[2]
    hostname = row[3]
    status = row[4]
    product_name = row[5]
    vendor = row[6]

    if strike is None:
        strike = 0

    if product_name is not None:
        if product_name.startswith("S1200"):
            cursor.execute("UPDATE Serverdata SET ProductName = 'White Box', Vendor = 'Intel' WHERE IndexValue = %s", (index_value,))
        elif product_name.startswith("PRIMERGY"):
            cursor.execute("UPDATE Serverdata SET Vendor = 'FUJITSU' WHERE IndexValue = %s", (index_value,))
        elif vendor and (vendor.startswith("Amazon") or vendor == "QEMU"):
            cursor.execute("UPDATE Serverdata SET ProductName = 'VM' WHERE IndexValue = %s", (index_value,))

    if strike < 30 and ip is None:
        strike += 1
        cursor.execute("UPDATE Serverdata SET Strike = %s, Status = 'Off' WHERE IndexValue = %s", (strike, index_value))
        continue

    is_reachable = check_ip_reachability(ip)

    if strike < 30 and not is_reachable:
        strike += 1
        cursor.execute("UPDATE Serverdata SET Strike = %s, Status = 'Off' WHERE IndexValue = %s", (strike, index_value))
    elif strike == 30 and not is_reachable:
        continue
    else:
        strike = 0
        cursor.execute("UPDATE Serverdata SET Strike = %s, Status = 'On' WHERE IndexValue = %s", (strike, index_value))

    if strike >= 30 and hostname != "temp-server":
        cursor.execute("UPDATE Serverdata SET HostName = 'temp' WHERE IndexValue = %s", (index_value,))


cursor.execute("SELECT HostName, MAX(Update_time) FROM Serverdata GROUP BY HostName HAVING COUNT(*) > 1")
duplicate_hostnames = cursor.fetchall()

for hostname, max_time in duplicate_hostnames:
    cursor.execute("SELECT IndexValue, IP, Strike, HostName, Status, Update_time FROM Serverdata WHERE HostName = %s ORDER BY Update_time ASC", (hostname,))
    data = cursor.fetchall()

    for row in data[:-1]:
        index_value = row[0]
        ip = row[1]

        cursor.execute("UPDATE Serverdata SET HostName = 'temp-server', IP = NULL WHERE IndexValue = %s", (index_value,))

db.commit()

db.close()

print("CMDB clean script executed")
