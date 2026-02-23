from . import central
from . import database
import os
from dotenv import load_dotenv, set_key
import json
from datetime import *
import time as t

cutoff_time_in_seconds = 7200

class Session:
    def __init__(self, macaddr, network, group_name, date, starttime, lastseen=None):
        self.macaddr = macaddr
        self.network = network
        self.group_name = group_name
        self.date = date
        if self.date == None:
            self.date = datetime.now().date()
        self.starttime = starttime
        self.lastseen = lastseen
        if lastseen == None:
            self.lastseen = starttime

    @classmethod
    def fromString(cls, string):
        arr = json.loads(string)
        return cls(arr["macaddr"], arr["network"], arr["group_name"], datetime.fromisoformat(arr["date"]), datetime.strptime(arr["starttime"], "%y/%m/%d %H:%M").timestamp(), datetime.strptime(arr["lastseen"], "%y/%m/%d %H:%M").timestamp())
    
    def stringify(self):
        return json.dumps({"macaddr":self.macaddr, "network":self.network, "group_name":self.group_name, "date":self.date.isoformat(), "starttime":datetime.fromtimestamp(self.starttime).strftime("%y/%m/%d %H:%M"), "lastseen":datetime.fromtimestamp(self.lastseen).strftime("%y/%m/%d %H:%M")})
    #self.macaddr + "|" + str(self.starttime) + "|" + str(self.lastseen) + "|" + str(self.sessioncount)

    def processrecord(self, json):
        if json.get("failiure_reason") == "NULL" or json.get("failiure_reason") == None:
            now = datetime.now()
            self.lastseen = now.timestamp()

load_dotenv("/home/{user}/wifi/Rep1/package/.env", override=True)
log_path = os.getenv("LOG_PATH")
logging_level = int(os.getenv("LOGGING_LEVEL"))

def load_sessions():
    if(logging_level > 0):
            with open(log_path, "a") as log:
                log.write("Loading stored sessions\n")
    load_dotenv("/home/{user}/wifi/Rep1/package/.env", override=True)
    result = {}
    if os.getenv("SESSION_LIST") == "":
        print("EMPTY")
        if(logging_level > 0):
            with open(log_path, "a") as log:
                log.write("Session list empty\n")
        return result
    listsessions = json.loads(os.getenv("SESSION_LIST"))
    for session in listsessions:
        temp = Session.fromString(listsessions[session])
        result[temp.macaddr] = temp
    if(logging_level > 0):
            with open(log_path, "a") as log:
                log.write("Finished loading stored sessions\n")
    return result

def dump_sessions(list):
    if(logging_level > 0):
            with open(log_path, "a") as log:
                log.write("Storing sessions\n")
    result = {}
    for entry in list:
        if list[entry] != None:
            result[list[entry].macaddr] = list[entry].stringify()
    set_key("/home/yam/dev1/.env", "SESSION_LIST", json.dumps(result))
    #print(result)
    if(logging_level > 0):
            with open(log_path, "a") as log:
                log.write("Sessions stored\n")
    return result

def gather_test_data():
    db = database.Database()
    api = central.Central()
    sessionlist = load_sessions()
    if(logging_level > 1):
            with open(log_path, "a") as log:
                log.write(sessionlist)
    if(logging_level > 0):
            with open(log_path, "a") as log:
                log.write("Beginning gathering Group Counts\n")
    try:
        load_dotenv(override=True)
        groups = json.loads(os.getenv("GROUPS"))
        concurrent_total = 0
        for group in groups:
            obj = api.paginated_api_query("https://us4.api.central.arubanetworks.com/network-monitoring/v1alpha1/clients?site-name=" + group + "&filter=status%20eq%20%27Connected%27%3B")
            total = obj.get("total")
            concurrent_total += total
            print(total)
            db.insert_sessions_count(total, group)
        db.execute("insert into concurrent_users (users) values (%d)", (concurrent_total,))
        db.commit()
    except Exception as e:
        if(logging_level > 0):
            with open(log_path, "a") as log:
                log.write("Failed gathering Group Counts with exception: " + repr(e) + "\n")
                log.write("Rolling back database")
        db.rollback()
        raise e
    
    if(logging_level > 0):
            with open(log_path, "a") as log:
                log.write("Beginning data collection\n")
    try:
        obj = api.paginated_api_query("https://us4.api.central.arubanetworks.com/network-monitoring/v1alpha1/clients?filter=status%20eq%20%27Connected%27%3B")
        # print(obj)
        #print(obj["clients"][1])
        # print(obj.get("total"))
        # load_dotenv(override=True)
        # groups = json.loads(os.getenv("GROUPS"))
        
        # for group in groups:
        #     obj = api.paginated_api_query("https://apigw-uswest4.central.arubanetworks.com/monitoring/v1/clients/wireless?group=" + group + "&calculate_total=true")
        #     total = obj.get("total")
        #     print(total)
        #     db.insert_sessions_count(total, group)
        #key = set()
        for client in obj.get("clients"):
            #for k in client.keys():
                # this loop is used to gather all attributes an object being returned may have
                #key.add(k)
            #db.insert_test_data(client)

            # Begin handling session objects
            mac = client.get("macaddr")
            current = sessionlist.get(mac)
            if client.get("last_connection_time") != None:
                if current == None:
                    current = Session(mac, client.get("network"), client.get("group_name"), None, datetime.now().timestamp(), datetime.now().timestamp())
                    sessionlist[mac] = current
                else:
                    current.processrecord(client)
        for session in sessionlist:
            # Check if a client was last seen over 2 hours ago. If they were, remove them from the list
            session = sessionlist.get(session)
            #print("start: " + str(datetime.fromtimestamp(session.starttime)))
            #print("end: " + str(datetime.fromtimestamp(session.lastseen)))
            cutoff_time = (int(t.time_ns() / 1000000000) - cutoff_time_in_seconds)
            if session.lastseen <= cutoff_time:
                db.update(session)
                sessionlist[session.macaddr] = None
        dump_sessions(sessionlist)
            
        #print(sorted(key))
        db.commit()
        if(logging_level > 0):
            with open(log_path, "a") as log:
                log.write("Completed data gathering\n")
    except Exception as e:
        if(logging_level > 0):
            with open(log_path, "a") as log:
                log.write("Failed data gathering with exception: " + repr(e) + "\n")
                log.write("Rolling back database\n")
        db.rollback()
        raise e
    
#l = load_sessions()
#print(l)
#dump_sessions(l)
