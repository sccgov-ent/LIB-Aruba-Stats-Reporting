import os
from dotenv import load_dotenv, set_key
import requests
import json
import time as t
from . import database
from datetime import *

class Central:
    def __init__(self):
        load_dotenv(override=True)
        self.log_path = "/home/yam/dev1/WhoFi/logs/" + datetime.now().strftime("%y-%m-%d-%H:%M") + ".log"
        set_key("/home/yam/dev1/.env", "LOG_PATH", self.log_path)
        os.environ["LOG_PATH"] = self.log_path
        self.db = database.Database()
        self.logging_level = int(os.getenv("LOGGING_LEVEL"))

    # This is a version of api_query that handles paginated data, it returns an array of json data. Any processing should be done for each entry as if they were all a part of the same dataset
    def paginated_api_query(self, url, pagination_limit=1000):
        if(self.logging_level > 0):
            with open(self.log_path, "a") as log:
                log.write("Starting paginated API query\n")
        counter = 0
        results = []
        results.insert(0, self.api_query(url + "&limit=" + str(pagination_limit) + "&offset=" + str(counter * pagination_limit)))
        total = results[0]["count"]
        counter += 1
        while(counter * pagination_limit < total):
            results.insert(counter, self.api_query(url + "&limit=" + str(pagination_limit) + "&offset=" + str(counter * pagination_limit)))
            counter += 1
        query_results = None
        for result in results:
            if query_results == None:
                query_results = result
            else:
                query_results["clients"] = query_results["clients"] + result["clients"]
        if(self.logging_level > 0):
            with open(self.log_path, "a") as log:
                log.write("Completed paginated API query\n")
        return query_results

    def api_query(self, url, pagination_limit=1000, indexing=False):
        if(self.logging_level > 0):
            with open(self.log_path, "a") as log:
                log.write("Starting API query\n")
        # token is stored in json, need to convert it
        token = self.db.get_token()
        token = json.loads(token)
        # print(token)

        if(self.is_token_invalid(token)):
            print("refreshing token")
            try:
                token = self.refresh_token(token)
                self.db.update_token(json.dumps(token))
            except Exception as e:
                print(e)
                raise e
        else:
            print("valid token")
        try:
            results = requests.get(url + "&limit=" + str(pagination_limit), headers= {"content-type":"application/json", "Authorization": f"Bearer {token["access_token"]}"}, timeout=30)
            print(results)
            obj = results.json()
            if(self.logging_level > 0):
                with open(self.log_path, "a") as log:
                    log.write("Completed API query\n")
            return obj
        except Exception as e:
            if(self.logging_level > 0):
                with open(self.log_path, "a") as log:
                    log.write("Failed API query with exception:" + repr(e) + "\n")
            raise e
        
    def gather_data(self):
        try:
            obj = self.api_query("https://apigw-uswest4.central.arubanetworks.com/monitoring/v1/clients/wireless?calculate_total=true")
            # print(obj)
            #print(obj["clients"][1])
            print(obj["total"])
            #key = set()
            for client in obj["clients"]:
                #for k in client.keys():
                    # this loop is used to gather all attributes an object being returned may have
                    #key.add(k)
                self.db.insert_test_data(client)
            #print(sorted(key))
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()
            raise e
        
    def gather_paginated_data(self):
        try:
            obj = self.paginated_api_query("https://apigw-uswest4.central.arubanetworks.com/monitoring/v1/clients/wireless?calculate_total=true")
            print(obj)
            for val in obj:
                for client in val["clients"]:
                    self.db.insert_test_data(client)
                self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()
            raise e

    # We check if a token is invalid, returns true if token will soon be invalid and false otherwise
    def is_token_invalid(self, token):
        if(self.logging_level > 0):
            with open(self.log_path, "a") as log:
                log.write("Checking token valididty\n")
        # created_at uses unix timestamp at ms resolution, but gives time till expiry in second resolution, we need to convert seconds to ms
        expires = token["created_at"] + (token["expires_in"] * 1000)
        # there isn't a time ms so we grab time in ns and convert by using lossy division, this is probably bad practice and should be changed
        now = int(t.time_ns() / 1000000)
        #if we just check if the token is valid now, it may be expiring soon. We want to refresh it if it has less than 5 minutes remaining so we have added 5 minutes in ms
        safe_time = 300000 + now
        if expires <= safe_time:
            if(self.logging_level > 0):
                with open(self.log_path, "a") as log:
                    log.write("Token is invalid\n")
            return True
        else:
            if(self.logging_level > 0):
                with open(self.log_path, "a") as log:
                    log.write("Token is valid\n")
            return False

    # We take a token and return a refreshed version of that token, allowing for 2 hours of access
    def refresh_token(self, token):
        if(self.logging_level > 0):
            with open(self.log_path, "a") as log:
                log.write("Refreshing token\n")
        try:
            CLIENT_ID = os.getenv("CLIENT_ID")
            CLIENT_SECRET = os.getenv("CLIENT_SECRET")
            response = requests.post(f"https://apigw-uswest4.central.arubanetworks.com/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=refresh_token&refresh_token={token["refresh_token"]}", headers={"content-type" : "application/json", "Authorization": f"Bearer {token["access_token"]}"}, json={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "grant_type": "refresh_token", "refresh_token": token["refresh_token"]})

            # Set the fields of token then use that to set the ENV, as we aren't actually given a full new token in response, just some new information about the token
            if(self.logging_level > 0):
                with open(self.log_path, "a") as log:
                    log.write(str(response))
                    log.write("\n")
                    log.write(str(response.content))
                    log.write("\n")
            token["access_token"] = response.json()["access_token"] #NOTE: If this is erroring out, and the request is a 400 error, try restarting your client, your env var is probably cached and you are using the wrong access token to authenticate
            token["refresh_token"] = response.json()["refresh_token"]
            token["expires_in"] = response.json()["expires_in"]
            token["created_at"] = int(t.time_ns() / 1000000)
            set_key("/home/yam/dev1/.env", "ARUBA_TOKEN", json.dumps(token))
            os.environ["ARUBA_TOKEN"] = json.dumps(token)
            if(self.logging_level > 0):
                with open(self.log_path, "a") as log:
                    log.write("Completed token refresh\n")
            return token
        except Exception as e:
            if(self.logging_level > 0):
                with open(self.log_path, "a") as log:
                    log.write("Failed refreshing token with exception: " + repr(e) + "\n")
            raise e

# print(os.getenv("STAGE"))
# set_key(".env", "testing", "test1")
#api = Central()
#api.gather_data()
#token = json.loads(os.getenv("ARUBA_TOKEN"))
#print(token)
