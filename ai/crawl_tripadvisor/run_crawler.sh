#!/bin/bash
cd /home/cseiu/AIOT_lab/MLoPs-study/Travel-project
source /home/cseiu/miniconda3/bin/activate jupyter_env
python tripadvisor_hotel_crawler.py --max 3 --delay 3 --url "https://www.tripadvisor.com/Hotels-g293924-Hanoi-Hotels.html" --output "tripadvisor_Hanoi_hotels_fixed.csv" --debug 