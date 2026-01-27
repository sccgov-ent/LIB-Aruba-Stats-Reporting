#!/bin/bash

sudo dnf update
sudo dnf install python3.12 -y
sudo dnf install python3.12-pip -y
python -m venv
./venv/Scripts/activate
pip install dotenv
pip install mariadb
pip install requests
deactivate