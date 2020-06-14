import requests
import os
import time


class nine_kw:
    """Cass to solve captchas using 9kw

    setup you 9kw-account and get a API-key
    choose 'pythonapi' as api-source or
    input you'r own api-source.
    """
    API_URL = "https://www.9kw.eu/index.cgi"
    API_SOURCE = "pythonapi"
    BASE_COST = 10

    def __init__(self,
                 API_KEY,
                 API_SOURCE="pythonapi",
                 priority=0,
                 timeout=300):
        """Initialize the Class

        Args:
            API_KEY (str): your API-Key
            API_SOURCE (str, optional): your API-source. 
                Defaults to "pythonapi".
            priority (int, optional): Priority of submits. Defaults to 0.
                maximum is 10. Note, each priority-level costs one
                additional credit per submit.
            timeout (int, optional): maximum time to solve captchas. Defaults to 300.
        """
        self.API_KEY = API_KEY
        self.API_SOURCE = API_SOURCE
        self.base_payload = {
            "apikey": self.API_KEY,
            "source": self.API_SOURCE
        }
        self.cost = self.BASE_COST
        self.priority = priority
        self.min_wait_time = 10
        self.timeout = timeout
        self._id = None

    def reset(self):
        self._id = None

    @property
    def credits(self):
        """get your credits

        Returns:
            int: cedits
        """
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

    def submit(self, captcha):
        """
        Submit a captcha.

        Args:
            captcha (str, bytes): Submit your captcha as
            filepath,
            binary file or
            url.
        """
        
        if self._id is not None:
            raise ValueError(
                "get result od last submit before adding new Submit")

        if self.cost > self.credits:
            raise UserWarning("not enough credits available")
        payload = self.base_payload
        payload["action"] = "usercaptchaupload"
        payload["maxtimeout"] = str(self.timeout)
        payload["prio"] = str(self.priority)

        if isinstance(captcha, str):
            # check if file is valid
            if captcha.startswith("http"):
                img = requests.get(captcha, allow_redirects=True)
                if img.status_code != 200:
                    raise FileNotFoundError("can't open url")
                else:
                    files = {'file-upload-01': (img.content)}

            elif not os.path.isfile(captcha):
                raise FileNotFoundError("File not fount @ %s" % captcha)
            else:
                files = {'file-upload-01': open(captcha, "rb")}
        elif isinstance(captcha, bytes):
            # wahrscheinlich fehlt hier filename
            files = {'file-upload-01': (captcha)}
        else:
            raise ValueError("unknown type")

        r = requests.post(self.API_URL, params=payload, files=files)
        r.raise_for_status()
        self._id = int(r.text)
        self._submit_time = time.time()
        # start timer for timeout
        return self._id

    def result(self):
        """Get the resukt of your catcha

        Raises:
            ValueError: When there is not captcha-id (no active captcha)

        Returns:
            (None, str): returns None if not solved or
                solitions as str if solved.
        """
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
        """loop funtion to get result

        Returns:
            (None, str): None if not solved or solution as str.
        """
        wait_for = self.min_wait_time\
            - (self._submit_time - time.time())
        if wait_for > 0:
            time.sleep(wait_for)

        while((self._submit_time - time.time()) < self.timeout):
            result = self.result()
            if result is not None:
                return result
            else:
                time.sleep(5)

        return None

    def result_feedback(self, correct):
        """Give feedback of result

        Args:
            correct (Bool, None):
                True = correct
                False = incorrect
                None = unknown

        Returns:
            bool: True if successfull
        """
        payload = self.base_payload
        payload["action"] = "usercaptchacorrectback"
        payload["id"] = self._id

        if correct is True:
            payload["correct"] = 1
        elif correct is False:
            payload["correct"] = 2
        elif correct is None:
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
    solver = nine_kw("API-key", priority=0, timeout=300)
    print(solver.credits)
    # solver.submit("test.gif")
    solver.submit("https://opfcaptcha-prod.s3.amazonaws.com/03b1c1052b6d4d1eb62a1fbdee9740bc.gif?AWSAccessKeyId=AKIA5WBBRBBBWROUAICF&Expires=1592143542&Signature=Yqxs2g4M18%2FswSBreVaRX7W97wo%3D")
    result = solver.result_loop()
    print(result)
    if result is None:
        solver.result_feedback(None)
    else:
        # correct = (result == "kM7wuT")
        print(correct)
        solver.result_feedback(correct)
