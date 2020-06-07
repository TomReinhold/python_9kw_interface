import requests


class nine_kw:
    API_URL = "https://www.9kw.eu/index.cgi"
    API_SOURCE = "pythonapi"
    
    
    def __init__(self, API_KEY, API_SOURCE="pythonapi"):
        self.API_KEY = API_KEY
        self.API_SOURCE = API_SOURCE
        self.base_payload = {
            "apikey": self.API_KEY,
            "source": self.API_SOURCE
        }
        
        
    @property
    def credits(self):
        getdata = {
            "action": "usercaptchaguthaben",
            "apikey": self.API_KEY,
            "source": self.API_SOURCE
        }
        r = requests.get(self.API_URL, params=getdata)
        r.raise_for_status()
        return int(r.text)
        
if __name__ == "__main__":
    solver = nine_kw("api-key")
    solver.credits