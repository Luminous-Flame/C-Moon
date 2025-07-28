#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
import sys
import argparse
from prettytable import PrettyTable

parser = argparse.ArgumentParser(
    description='''CMDB Search Tool

- 대/소문자 구분 없음
- 자원 값 검색 시, 복수 입력하여 검색 가능

- 호스트 네임을 기준으로 서버의 모든 자원 값을 검색
Ex) cview ade-01

- 호스트 네임을 기준으로 서버의 입력한 자원 값 검색 
Ex) cview ade-01 os,memory...

- 호스트 그룹을 기준으로 서버들의 모든 자원 값을 검색
Ex) cview ade

- 호스트 그룹을 기준으로 서버들의 입력한 자원 값 검색
Ex) cview ade os,memory...

- 자원 값 검색 (구분자는 ','로 중첩 검색 가능)
Ex) os=ubuntu,memory=64,vendor=FUJITSU...

''',
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument('-i', action='store_true', help='인덱스 값 조회')
parser.add_argument('-t', action='store_true', help='조회 결과 값들을 Table 형식이 아닌, Tab으로 구분하여 출력')
parser.add_argument('search_criteria', nargs='*', default='', help='HostName, OS, IP, MAC, CPU, CPUCore, CPUCount, TotalCore, ThreadsPerCore, ThreadsTotal, Memory, Vendor, ProductName, SerialNo')
args = parser.parse_args()

def display_result(result, headers=None):
    if not result:
        print("No data found.")
        return
    if args.t:
        filtered_headers = [header for i, header in enumerate(headers) if not headers[i] == 'IndexValue']
        for row in result:
            filtered_row = [val for i, val in enumerate(row) if not headers[i] == 'IndexValue']
            print("\t".join(str(val) for val in filtered_row))
    else:
        filtered_headers = [header for header in headers if not header == 'IndexValue']
        table = PrettyTable(filtered_headers)
        for row in result:
            filtered_row = [value for i, value in enumerate(row) if not headers[i] == 'IndexValue']
            table.add_row(filtered_row)

        print(table)
        print("Number of rows:", len(result))

db = mysql.connector.connect(
    host="localhost",
    user="cmoon",
    password="cmoonpassword",
    database="cmoon"
)
cursor = db.cursor()

if args.i:
    query = "SELECT HostName, IndexValue FROM Serverdata ORDER BY HostName"
    cursor.execute(query)
    result = cursor.fetchall()
    headers = ["HostName", "IndexValue"]
    table = PrettyTable(headers)
    for row in result:
        table.add_row([row[0], row[1]])
    print(table)

elif not args.search_criteria:
    query = "SELECT * FROM Serverdata ORDER BY HostName"
    cursor.execute(query)
    result = cursor.fetchall()
    headers = [i[0] for i in cursor.description] if cursor.description else None
    display_result(result, headers)

elif args.search_criteria and "=" in args.search_criteria[0]:
    properties = args.search_criteria[0].split(",")
    conditions = []
    values = []
    for prop in properties:
        prop_parts = prop.split("=")
        if len(prop_parts) == 2:
            prop_name = prop_parts[0]
            prop_value = "%" + prop_parts[1] + "%"
            conditions.append("{} LIKE %s".format(prop_name))
            values.append(prop_value)

    if conditions:
        query = "SELECT * FROM Serverdata WHERE {} ORDER BY HostName".format(" AND ".join(conditions))
        cursor.execute(query, tuple(values))

        result = cursor.fetchall()
        headers = [i[0] for i in cursor.description] if cursor.description else None
        display_result(result, headers)
    else:
        print("Invalid search criteria.")

elif len(args.search_criteria) >= 2 and (not args.search_criteria[0][-1].isdigit()):

    host_group = args.search_criteria[0]
    properties = args.search_criteria[1].split(",")
    placeholders = ",".join(["%s"] * len(properties))

    query = "SELECT HostName, {} FROM Serverdata WHERE HostName LIKE %s ORDER BY HostName".format(",".join(properties))
    cursor.execute(query, (host_group + "%",))

    result = cursor.fetchall()
    headers = ["HostName"] + properties
    filtered_result = []
    for row in result:
        if row[0].replace(row[0][row[0].rfind("-"):], "") == host_group:
            filtered_result.append(row)

    display_result(filtered_result, headers)

elif len(args.search_criteria) >= 2 and args.search_criteria[0][-1].isdigit():

    host_names = args.search_criteria[0].split(",")
    properties = args.search_criteria[1].split(",")
    placeholders = ",".join(["%s"] * len(host_names))

    query = "SELECT HostName, {} FROM Serverdata WHERE HostName IN ({}) ORDER BY HostName".format(",".join(properties), placeholders)
    cursor.execute(query, host_names)

    result = cursor.fetchall()
    headers = ["HostName"] + properties
    display_result(result, headers)

elif args.search_criteria and (not args.search_criteria[0][-1].isdigit()):
    host_group = args.search_criteria[0]
    properties = []

    query = "SELECT HostName FROM Serverdata WHERE HostName LIKE %s ORDER BY HostName"
    cursor.execute(query, (host_group + "%",))

    result = cursor.fetchall()
    headers = [i[0] for i in cursor.description] if cursor.description else None

    filtered_result = []
    for row in result:
        if row[0].startswith(host_group + "-") and row[0][len(host_group)+1:].isdigit():
            filtered_result.append(row)

    if filtered_result:
        host_names = [row[0] for row in filtered_result]
        placeholders = ",".join(["%s"] * len(host_names))

        query = "SELECT * FROM Serverdata WHERE HostName IN ({}) ORDER BY HostName".format(placeholders)
        cursor.execute(query, tuple(host_names))

        result = cursor.fetchall()
        headers = [i[0] for i in cursor.description] if cursor.description else None
        display_result(result, headers)

elif args.search_criteria and (args.search_criteria[0][-1].isdigit()):
    host_names = args.search_criteria[0].split(",")

    placeholders = ",".join(["%s"] * len(host_names))

    query = "SELECT * FROM Serverdata WHERE HostName IN ({}) ORDER BY HostName".format(placeholders)
    cursor.execute(query, host_names)

    result = cursor.fetchall()
    headers = [i[0] for i in cursor.description] if cursor.description else None
    display_result(result, headers)

db.close()
