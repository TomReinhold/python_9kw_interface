import requests
import os


class nine_kw:
    API_URL = "https://www.9kw.eu/index.cgi"
    API_SOURCE = "pythonapi"
    BASE_COST = 10
    
    
    def __init__(self, API_KEY, API_SOURCE="pythonapi", priority=0, timeout=300):
        self.API_KEY = API_KEY
        self.API_SOURCE = API_SOURCE
        self.base_payload = {
            "apikey": self.API_KEY,
            "source": self.API_SOURCE
        }
        self.cost = self.BASE_COST
        self.priority = priority
        self.timeout = timeout
        self._id=None
        
    def reset(self):
        self._id=None
        
    @property
    def credits(self):
        payload = self.base_payload
        payload["action"] = "usercaptchaguthaben"
        r = requests.get(self.API_URL, params=payload)
        r.raise_for_status()
        return int(r.text)

    @property
    def priority(self):
        return self.__priority

    @priority.setter
    def priority(self, val):
        if val < 0 or val > 10:
            raise ValueError(
                "priority value should be between 0 and 10"
                )
        self.__priority = val
        self.cost = self.BASE_COST + val
        
    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, val):
        if val < 60 or val > 3999:
            raise ValueError(
                "timeout value should be between 60 and 3999"
                )
        self.__timeout = val
        
    def submit(self, file):
        if self._id is not None:
            raise ValueError("get result od last submit before adding new Submit")
        
        if self.cost > self.credits:
            raise UserWarning("not enough credits available")
        payload = self.base_payload
        payload["action"] = "usercaptchaupload"
        payload["maxtimeout"] = str(self.timeout)
        payload["prio"] = str(self.priority)
        
        if isinstance(file, str):
            #check if file is valid
            if not os.path.isfile(file):
                raise FileNotFoundError("File not fount @ %s" % file)
            files = {'file-upload-01': open(file, "rb")}
        elif isinstance(file, bytes):
            files = {'file-upload-01': (file)}# wahrscheinlich fehlt hier filename
        else:
            raise ValueError("unknown type")
        
        r = requests.post(self.API_URL, params=payload, files=files)
        r.raise_for_status()
        self._id=int(r.text)
        # start timer for timeout
        return self._id
    
    def result(self):
        if self._id is None:
            raise ValueError("Unkown id for captcha")
        payload = self.base_payload
        payload["action"] = "usercaptchacorrectdata"
        payload["id"] = self._id
        payload["info"] = 1
        
        r = requests.get(self.API_URL, params=payload)
        r.raise_for_status()
        if r.text == "NO DATA":
            return None
        else:
            return r.text
        
    def result_loop(self):
        # wait a minimum amount of time (5 sec)
        # then request a result in loop with waits
        pass
    
    def result_feedback(self, correct):
        payload = self.base_payload
        payload["action"] = "usercaptchacorrectback"
        payload["id"] = self._id
        
        if correct == True:
            payload["correct"] = 1
        elif correct == False:
            payload["correct"] = 2
        elif correct == None:
            payload["correct"] = 3
        else:
            ValueError("Unknown type of correct")
            
        r = requests.get(self.API_URL, params=payload)
        
        if r.text == 'OK':
            self._id = None
            return True
        else:
            return False
        
        
        
        
        
if __name__ == "__main__":
    solver = nine_kw("API-KEY", priority=10, timeout=300)
    print(solver.credits)
    solver.submit("test.gif")
    print()