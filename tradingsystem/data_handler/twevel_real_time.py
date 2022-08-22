from data_handler.base import AbstractDataHandler
import queue
import time
import requests


class TwelveRealTimeBarHandler(AbstractDataHandler):
    """
    Get real time bar data using twelve data api
    https://rapidapi.com/twelvedata/api/twelve-data1/
    """
    def __init__(self, timeframe, event_queue, 
                 db_client=None
        ):
        self.db_client = db_client

                
    def get_next(self):
        pass
    
    
with open("/home/ron/Desktop/apikey", "r") as f:
    api_key = f.read()[:-1]
  

url = "https://twelve-data1.p.rapidapi.com/time_series"

querystring = {"symbol":"AMZN","interval":"1day","outputsize":"30","format":"json"}

headers = {
	"X-RapidAPI-Key": api_key,
	"X-RapidAPI-Host": "twelve-data1.p.rapidapi.com"
}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
    
    
    


                                   
      