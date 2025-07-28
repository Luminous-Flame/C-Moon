#!/bin/bash
set -e

ENV_DIR="$HOME/.c-moon"
REQ_FILE=""

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GSDK_PARENT_DIR="$(dirname "$BASE_DIR")"
GSDK_DIR="$GSDK_PARENT_DIR/google-cloud-sdk"

echo "[+] Detected Python Version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.9" | bc) -eq 1 ]]; then
  echo "[+] Python < 3.9 → Using requirements-py38.txt"
  REQ_FILE="requirements-py38.txt"
else
  echo "[+] Python >= 3.9 → Using requirements.txt"
  REQ_FILE="requirements.txt"
fi

echo "[+] Update apt cache & install system packages..."
apt-get update -y
apt-get install -y python3 python3-venv python3-pip mysql-server curl git bc

echo "[+] Create Python venv: $ENV_DIR"
python3 -m venv "$ENV_DIR"
source "$ENV_DIR/bin/activate"

echo "[+] Upgrade pip..."
pip install --upgrade pip

echo "[+] Install Python packages from $REQ_FILE..."
pip install -r "$REQ_FILE"

if [ ! -d "$GSDK_DIR" ]; then
  echo "[+] Installing Google Cloud SDK in $GSDK_DIR"
  curl -sSL https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-450.0.0-linux-x86_64.tar.gz -o /tmp/google-cloud-sdk.tar.gz
  tar -xzf /tmp/google-cloud-sdk.tar.gz -C "$GSDK_PARENT_DIR"
  "$GSDK_DIR/install.sh" --quiet
else
  echo "[=] Google Cloud SDK already installed at $GSDK_DIR"
fi

export PATH="$GSDK_DIR/bin:$PATH"


echo "[+] Create MySQL Database..."

DB_HOST="localhost"
DB_USER="cmoon"
DB_PASSWORD="cmoonpassword"
DB_NAME="cmoon"
SQL_FILE="$(pwd)/database.sql"

if [ ! -f "$SQL_FILE" ]; then
  echo "Database schema file not found: $SQL_FILE"
  exit 1
fi

echo "[+] Create MySQL Database and User..."
mysql -uroot -e "
  CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
  CREATE USER IF NOT EXISTS '${DB_USER}'@'${DB_HOST}' IDENTIFIED BY '${DB_PASSWORD}';
  GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'${DB_HOST}';
  FLUSH PRIVILEGES;
"

echo "[+] Load schema into DB..."
mysql -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$SQL_FILE"

echo "[+] Install & Database Setup Complete"

echo "======================================"
echo "[*] To activate environment:"
echo "source $ENV_DIR/bin/activate"
echo "======================================"

echo "[*] Version Check"
ansible --version | head -n 1 || echo "ansible not found"
ansible-cmdb --version || echo "ansible-cmdb not found"
python --version

