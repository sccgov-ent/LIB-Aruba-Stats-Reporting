import smtplib
from . import database
from . import central
import mariadb
import os
from dotenv import load_dotenv
from email.message import EmailMessage

class error_report:
    def __init__(self):
        flag = False
        mail = EmailMessage()
        mail_body = "Error report for wifi statistics:"
        mail['Subject'] = "WIFI Stats daily report"
        mail['From'] = "ian.may@lib.sccgov.org"
        mail['To'] = "ian.may@lib.sccgov.org"
        smtpConn = smtplib.SMTP('sccgovapp.sccgov.org')

        api = central.Central()
        try:
            load_dotenv(override=True)
            DB_IP = os.getenv("DB_IP")
            DB_LOGIN = os.getenv("DB_LOGIN")
            DB_PASSWORD = os.getenv("DB_PASSWORD")
            DB_NAME = os.getenv("DB_NAME")
            conn = mariadb.connect(host=DB_IP, user=DB_LOGIN, password=DB_PASSWORD, database=DB_NAME)
            cursor = conn.cursor()
            query = "select Max(users) from concurrent_users where day(date) = day(CURRENT_DATE) and month(date) = month(CURRENT_DATE) and Year(date) = YEAR(CURRENT_DATE)"
            cursor.execute(query)
            results = cursor.fetchall()
        except Exception as e:
            flag = True
            mail_body += "\nError: accessing database"
        try:
            api.api_query("https://apigw-uswest4.central.arubanetworks.com/monitoring/v1/clients/wireless?calculate_total=true")
        except Exception as e:
            flag = True
            mail_body += "\nError: calling api"
        try:
            #enter in group queries and check how many aps appear
            result = api.api_query("https://apigw-uswest4.central.arubanetworks.com/monitoring/v2/aps?label=Active%20APs&fields=status&status=Up&calculate_total=true")
            print(str(result['total']))
            if result['total'] != 125:
                print("wrong number")
                raise Exception("wrong number of APs")
        except Exception as e:
            flag = True
            mail_body += "\nError: wrong number of APs"

        if flag:
            mail.set_content(mail_body)
            smtpConn.send_message(mail)
            smtpConn.quit()
