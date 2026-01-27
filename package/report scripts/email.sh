#!/bin/bash

echo dev1
source /home/{user}/rep1/venv/bin/activate
python3 /home/{user}/rep1/WhoFi/dailymail.py
echo dev2
source /home/{user}/rep2/venv/bin/activate
python3 /home/{user}/rep2/WhoFi/dailymail.py