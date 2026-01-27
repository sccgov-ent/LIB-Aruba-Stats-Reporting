import smtplib
import database
import mariadb
import os
from dotenv import load_dotenv
from email.message import EmailMessage


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
mail = EmailMessage()
mail.set_content("Daily report for wifi statistics: " + str(results))
mail['Subject'] = "WIFI Stats daily report"
mail['From'] = "ian.may@lib.sccgov.org"
mail['To'] = "ian.may@lib.sccgov.org"
smtpConn = smtplib.SMTP('sccgovapp.sccgov.org')
smtpConn.send_message(mail)
smtpConn.quit()
