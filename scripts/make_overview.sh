#!/bin/bash

CSV=/var/www/html/server_list.csv
HTML=/var/www/html/server_list.html

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CMDB_OUT="$BASE_DIR/ansible-cmdb-out"
TPL_DIR="$BASE_DIR/tpl"
LOCAL_IP=$(hostname -I | awk '{print $1}')

ansible -b all -m setup --tree "$CMDB_OUT"

ansible-cmdb -t "$TPL_DIR/csv_custom.tpl" "$CMDB_OUT" > "$CSV"
ansible-cmdb -t "$TPL_DIR/html_fancy_split_overview.tpl" "$CMDB_OUT" > "$HTML"

echo "http://$LOCAL_IP/cmoon/server_list.csv"
echo "http://$LOCAL_IP/cmoon/server_list.html"

