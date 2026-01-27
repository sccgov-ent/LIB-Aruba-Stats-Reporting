#!/bin/bash

echo dev1
source /home/{user}/rep1/venv/bin/activate
python3 -m rep1.WhoFi
echo dev2
source /home/{user}/rep2/venv/bin/activate
python3 -m rep2.WhoFi