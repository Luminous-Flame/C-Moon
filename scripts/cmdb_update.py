#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import hashlib
import mysql.connector
import argparse
import os
from datetime import datetime

db = mysql.connector.connect(
    host="localhost",
    user="cmoon",
    password="cmoonpassword",
    database="cmoon"
)

filename = "/var/www/html/cmoon/server_list.csv"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

parser = argparse.ArgumentParser(description='CMDB Input Window')
parser.add_argument('option', choices=['a', 'n', 'd'], help='Select option (a: Full data input, n: New server data input, d: Delete data)')
args = parser.parse_args()

not_updated_file = os.path.join(BASE_DIR, 'scripts', 'not_updated.list')
not_updated_hosts = [line.strip() for line in open(not_updated_file).readlines()]

def get_user_input():
    print("Enter server data (Ctrl+C to cancel):")
    hostname = input("Hostname: ")
    os = input("OS: ")
    ip = input("IP: ")
    mac = input("MAC: ")
    cpu = input("CPU: ")
    cpu_core = int(input("CPU Core: "))
    cpu_count = int(input("CPU Count: "))
    total_core = int(input("Total Core: "))
    threads_per_core = int(input("Threads Per Core: "))
    threads_total = int(input("Threads Total: "))
    memory = input("Memory: ")
    vendor = input("Vendor: ")
    product_name = input("Product Name: ")
    serial_no = input("Serial No: ")
    return [hostname, os, ip, mac, cpu, cpu_core, cpu_count, total_core, threads_per_core, threads_total, memory, vendor, product_name, serial_no]

def delete_data(index_value):
    cursor = db.cursor()
    cursor.execute("DELETE FROM Serverdata WHERE IndexValue = %s", (index_value,))
    db.commit()
    print("Data deleted: ", index_value)

if args.option == "a":

    with open(filename, "r") as file:
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            mac = row[3]
            serial_no = row[13]
            product_name = row[12]
            index_value = hashlib.md5((mac + serial_no + product_name).encode()).hexdigest()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Serverdata WHERE IndexValue = %s", (index_value,))
            result = cursor.fetchone()

            if row[0] in not_updated_hosts:
                print(f"Skipping data input for host {row[0]} (found in not_updated.list).")
                continue

            elif result is None:
                query = "INSERT INTO Serverdata (IndexValue, HostName, OS, IP, MAC, CPU, CPUCore, CPUCount, TotalCore, ThreadsPerCore, ThreadsTotal, Memory, Vendor, ProductName, SerialNo, Status, Update_time, Strike) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'On', NOW(), 0)"
                data = (index_value, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
                cursor.execute(query, data)
                db.commit()
                print("New data inserted.")
            else:
                if result[1:] != row:
                    query = "UPDATE Serverdata SET HostName = %s, BeforeHost = %s, OS = %s, IP = %s, MAC = %s, CPU = %s, CPUCore = %s, CPUCount = %s, TotalCore = %s, ThreadsPerCore = %s, ThreadsTotal = %s, Memory = %s, Vendor = %s, ProductName = %s, SerialNo = %s, Status = 'On', Update_time = NOW(), Strike = 0 WHERE IndexValue = %s"
                    before_host = result[1]
                    data = (row[0], before_host, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], index_value)
                    cursor.execute(query, data)
                    db.commit()
                    print(f"Data updated: {row[0]}")
    print("\nFull data input completed.")

elif args.option == "n":
    server_data = get_user_input()
    mac = server_data[3]
    serial_no = server_data[13]
    product_name = server_data[12]
    index_value = hashlib.md5((mac + serial_no + product_name).encode()).hexdigest()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Serverdata WHERE IndexValue = %s", (index_value,))
    result = cursor.fetchone()

    if server_data[0] in not_updated_hosts:
        print(f"Skipping data input for host {server_data[0]} (found in not_updated.list).")

    elif result is None:
        query = "INSERT INTO Serverdata (IndexValue, HostName, OS, IP, MAC, CPU, CPUCore, CPUCount, TotalCore, ThreadsPerCore, ThreadsTotal, Memory, Vendor, ProductName, SerialNo, Status, Update_time, Strike) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'On', NOW(), 0)"

        data = (index_value, server_data[0], server_data[1], server_data[2], server_data[3], server_data[4], server_data[5], server_data[6], server_data[7], server_data[8], server_data[9], server_data[10], server_data[11], server_data[12], server_data[13])

        cursor.execute(query, data)
        db.commit()
        print("New data inserted: ", server_data[0])

    else:
        before_host = result[1]

        query = "UPDATE Serverdata SET HostName = %s, BeforeHost = %s, OS = %s, IP = %s, MAC = %s, CPU = %s, CPUCore = %s, CPUCount = %s, TotalCore = %s, ThreadsPerCore = %s, ThreadsTotal = %s, Memory = %s, Vendor = %s, ProductName = %s, SerialNo = %s, Status = 'On', Update_time = NOW(), Strike = 0 WHERE IndexValue = %s"
        data = (*server_data[:2], before_host, *server_data[2:], index_value)

        cursor.execute(query, data)
        db.commit()
        print(f"Data updated: {server_data[0]}")
    print("Server data input completed.")

elif args.option == "d":
    index_value = input("Enter IndexValue to delete: ")
    delete_data(index_value)

else:
    print("Invalid option. Please enter a, n, d, or q.")

db.close()
