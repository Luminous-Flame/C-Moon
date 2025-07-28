#!/bin/bash

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

DATE=$(date +%Y%m%d)

WWW_ROOT="/var/www/html/cmoon"
DATE_DIR="$WWW_ROOT/$DATE"

CSV="$DATE_DIR/server_list.csv"
XLSX="$DATE_DIR/server_list.xlsx"
HTML="$DATE_DIR/server_list.html"

DEST_CSV="$WWW_ROOT/server_list.csv"
DEST_XLSX="$WWW_ROOT/server_list.xlsx"
DEST_HTML="$WWW_ROOT/server_list.html"

DB_HOST="localhost"
DB_USER="cmoon"
DB_PASSWORD="cmoonpassword"
DB_NAME="cmoon"

ANSIBLE_CMDB_OUT_DIR="$BASE_DIR/ansible-cmdb-out"
TPL_DIR="$BASE_DIR/tpl"

if [ -f "$CSV" ]; then
  echo "CSV file already exists: $CSV"
  exit 0
fi

mkdir -p "$DATE_DIR"

ansible -b -i /etc/ansible/hosts all -m setup --tree "$ANSIBLE_CMDB_OUT_DIR"

ansible-cmdb -t "$TPL_DIR/csv_custom.tpl" "$ANSIBLE_CMDB_OUT_DIR" > "$CSV"
ansible-cmdb -t "$TPL_DIR/html_fancy_split_overview.tpl" "$ANSIBLE_CMDB_OUT_DIR" > "$HTML"

SQL_QUERY="SELECT HostName, OS, IP, MAC, CPU, CPUCore, CPUCount, TotalCore, ThreadsPerCore, ThreadsTotal, Memory, Vendor, ProductName, SerialNo, Status, Update_time, Strike, BeforeHost FROM Serverdata"

mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "$SQL_QUERY" | sed 's/\t/","/g;s/^/"/;s/$/"/;s/\n//g' > data.csv
cat data.csv > "$XLSX"

rm data.csv header.csv
rm -rf "$ANSIBLE_CMDB_OUT_DIR"

cp "$CSV" "$DEST_CSV"
cp "$XLSX" "$DEST_XLSX"
cp "$HTML" "$DEST_HTML"

LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "http://${LOCAL_IP}/cmoon/server_list.xlsx"
echo "http://${LOCAL_IP}/cmoon/server_list.csv"
echo "http://${LOCAL_IP}/cmoon/server_list.html"

