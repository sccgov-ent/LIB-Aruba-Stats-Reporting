import os
from dotenv import load_dotenv
import mariadb

class Database:
    def __init__(self):
        load_dotenv(override=True)
        self.create_connection()
        self.execute("CREATE TABLE IF NOT EXISTS concurrent_users(date DATETIME NOT NULL PRIMARY KEY DEFAULT CURRENT_TIMESTAMP, users INT NOT NULL);")
        #self.update_token('{"access_token":"2XKtOMM6fckQLGBFMz2EIr3ZTnjrT5rj","appname":"nms","authenticated_userid":"imay@sccl.org","created_at":1762207269846,"credential_id":"005a0b08-0750-47f3-be5e-91569e233797","expires_in":7200,"id":"7ff51c39-c41e-45a0-946c-59fff7a34c8b","refresh_token":"9jnjvgJJuSwyEDdtjat2QWjnVkYvpZZW","scope":"all","token_type":"bearer"}')

    def rollback(self):
        self.conn.rollback()

    def commit(self):
        self.conn.commit()

    def create_connection(self):
        DB_IP = os.getenv("DB_IP")
        DB_LOGIN = os.getenv("DB_LOGIN")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = os.getenv("DB_NAME")
        conn = mariadb.connect(host=DB_IP, user=DB_LOGIN, password=DB_PASSWORD, database=DB_NAME)
        self.conn = conn

    def test_select(self):
        cursor = self.conn.cursor()
        query = "select * from test"
        cursor.execute(query)
        return cursor.fetchall()

    def get_token(self):
        DB_IP = os.getenv("DB_IP")
        DB_LOGIN = os.getenv("DB_LOGIN")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = "TOKEN"
        db = mariadb.connect(host=DB_IP, user=DB_LOGIN, password=DB_PASSWORD, database=DB_NAME)
        cursor = db.cursor()
        query = "select * from TOKEN"
        cursor.execute(query)
        return cursor.fetchone()[0]

    def update_token(self, token):
        DB_IP = os.getenv("DB_IP")
        DB_LOGIN = os.getenv("DB_LOGIN")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_NAME = "TOKEN"
        print("connecting")
        db = mariadb.connect(host=DB_IP, user=DB_LOGIN, password=DB_PASSWORD, database=DB_NAME)
        cursor = db.cursor()
        query = "delete from TOKEN"
        print("Old token deleted")
        cursor.execute(query)
        query = "insert into TOKEN (TOKEN) values (%s)"
        cursor.execute(query, [token])
        db.commit()
        print("New token inserted")
        print(token)
    
    def update(self, session):
        cursor = self.conn.cursor()
        #query = "insert into Daily_stats (macaddr, network, group_name, session_count, date) values (%s, %s, %s, 1, %s) on DUPLICATE KEY update session_count = session_count + 1"
        query = "insert into Daily_stats (macaddr, network, group_name, session_count, Session_Duration, date) values (%s, %s, %s, 1, %d, %s) on DUPLICATE KEY update session_count = session_count + 1, Session_Duration = Session_Duration + VALUES(Session_Duration)"
        #values = (session.macaddr, session.network, session.group_name, session.date)
        values = (session.macaddr, session.network, session.group_name, session.lastseen - session.starttime, session.date)
        cursor.execute(query, values)

    def execute(self, query, values = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, values)

    def insert_sessions_count(self, count, group_name="all"):
        cursor = self.conn.cursor()
        query = "insert into Connection_Counts (connection_count, group_name) values (%d, %s)"
        values = (count, group_name)
        cursor.execute(query, values)

    def insert_test_data(self, client):
        cursor = self.conn.cursor()
        query = "insert into test_stats (associated_device, associated_device_mac, associated_device_name, authentication_type, band, `channel`, client_category, client_type, connected_device_type, `connection`, encryption_method, failure_reason, failure_stage, group_id, group_name, health, ht_type, ip_address, label_id, labels, last_connection_time, `macaddr`, manufacturer, maxspeed, `name`, network, os_type, phy_type, radio_mac, radio_number, signal_db, signal_strength, `site`, snr, speed, swarm_id, `usage`, user_role, username, vlan) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (client.get("associated_device", "NULL"), client.get("associated_device_mac", "NULL"), client.get("associated_device_name", "NULL"), client.get("authentication_type", "NULL"), client.get("band", "NULL"), client.get("channel", "NULL"), client.get("client_category", "NULL"), client.get("client_type", "NULL"), client.get("connected_device_type", "NULL"), client.get("connection", "NULL"), client.get("encryption_method", "NULL"), client.get("failure_reason", "NULL"), client.get("failure_stage", "NULL"), client.get("group_id", "NULL"), client.get("group_name", "NULL"), client.get("health", "NULL"), client.get("ht_type", "NULL"), client.get("ip_address", "NULL"), ",".join(client.get("label_id", "NULL")), ",".join(client.get("labels", "NULL")), client.get("last_connection_time", "NULL"), client.get("macaddr", "NULL"), client.get("manufacturer", "NULL"), client.get("maxspeed", "NULL"), client.get("name", "NULL"), client.get("network", "NULL"), client.get("os_type", "NULL"), client.get("phy_type", "NULL"), client.get("radio_mac", "NULL"), client.get("radio_number", "NULL"), client.get("signal_db", "NULL"), client.get("signal_strength", "NULL"), client.get("site", "NULL"), client.get("snr", "NULL"), client.get("speed", "NULL"), client.get("swarm_id", "NULL"), client.get("usage", "NULL"), client.get("user_role", "NULL"), client.get("username", "NULL"), client.get("vlan", "NULL"))
        #print((type(client.get("associated_device", "NULL")), type(client.get("associated_device_mac", "NULL")), type(client.get("associated_device_name", "NULL")), type(client.get("authentication_type", "NULL")), type(client.get("band", "NULL")), type(client.get("channel", "NULL")), type(client.get("client_category", "NULL")), type(client.get("client_type", "NULL")), type(client.get("connected_device_type", "NULL")), type(client.get("connection", "NULL")), type(client.get("encryption_method", "NULL")), type(client.get("failiure_reason", "NULL")), type(client.get("failiure_stage", "NULL")), type(client.get("group_id", "NULL")), type(client.get("group_name", "NULL")), type(client.get("health", "NULL")), type(client.get("ht_type", "NULL")), type(client.get("ip_address", "NULL")), type(client.get("label_id", "NULL")), type(client.get("labels", "NULL")), type(client.get("last_connection_time", "NULL")), type(client.get("macaddr", "NULL")), type(client.get("manufacturer", "NULL")), type(client.get("maxspeed", "NULL")), type(client.get("name", "NULL")), type(client.get("network", "NULL")), type(client.get("os_type", "NULL")), type(client.get("phy_type", "NULL")), type(client.get("radio_mac", "NULL")), type(client.get("radio_number", "NULL")), type(client.get("signal_db", "NULL")), type(client.get("site", "NULL")), type(client.get("snr", "NULL")), type(client.get("speed", "NULL")), type(client.get("swarm_id", "NULL")), type(client.get("usage", "NULL")), type(client.get("user_role", "NULL")), type(client.get("username", "NULL")), type(client.get("vlan", "NULL"))))
        cursor.execute(query, values)
