#!/bin/bash

sudo dnf update
sudo dnf install python3.12 -y
sudo dnf install python3.12-pip -y
curl -LsSO https://r.mariadb.com/downloads/mariadb_repo_setup
chmod +x mariadb_repo_setup
sudo ./mariadb_repo_setup \ --mariadb-server-version="mariadb-10.6"
rm mariadb_repo_setup
sudo dnf install MariaDB-shared MariaDB-devel
python -m venv venv
source ./venv/bin/activate
pip install dotenv
pip install mariadb
pip install requests
deactivate
