from TDhelper.network.http.REST_HTTP import POST, GET
from datetime import datetime, timedelta, timezone
import json


class token_manage:
    __token = None
    __expire = None
    __token_service_uri = None
    __service_key = None
    __service_secret = None
    __time_cls = None
    __status= False
    __err_msg= ""
    
    @property
    def Status(self):
        return self.__status
    
    @property
    def ErrMsg(self):
        return self.__err_msg
    
    @property
    def Token(self):
        if self.__status:
            try:
                if not self.__token:
                    self.__get_token__()
                if self.__expire:
                    if datetime.strptime(self.__expire,"%Y-%m-%d %H:%M:%S.%f") < self.__time_cls.now():
                        self.__get_token__()
                return self.__token
            except Exception as e:
                self.__status= False
                self.__err_msg= e.args[0]
        else:
            return self.__err_msg

    def __init__(self, token_uri:str, svr_key:str, secret:str, time_cls=None, path:str= None, post_data:dict={}) -> None:
        self.__time_cls = datetime if not time_cls else time_cls
        self.__service_key = svr_key
        self.__service_secret = secret
        token_uri= token_uri.rstrip('/')
        self.__token_service_uri = "/".join([token_uri, path if path else "api/rpc_token"])
        self.__post_data= post_data if post_data else {
                "svr_key": self.__service_key.upper(),
                "secret": self.__service_secret
                }
        self.__status= False
        #self.__get_token__()

    def __get_token__(self):
        try:
            state, body = GET(
                self.__token_service_uri,
                self.__post_data,
                time_out=5
            )
            if state:
                data = json.loads(body)
                if data.get("state")==200:
                    self.__token = data.get("msg").get("token", None)
                    self.__expire = data.get("msg").get("expire", None).replace("T"," ")
                    self.__status= True
                else:
                    self.__status= False
                    self.__err_msg= data.get('msg')
            else:
                self.__status= False
                self.__err_msg= data.get('msg')
        except Exception as e:
            self.__status= False
            self.__err_msg= e.args[0]
