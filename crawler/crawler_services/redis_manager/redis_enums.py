from enum import Enum


class REDIS_CONNECTIONS:
  S_DATABASE_IP = 'localhost'
  S_DATABASE_PORT = 6379
  S_DATABASE_PASSWORD = ""


class CUSTOM_SCRIPT_REDIS_KEYS(Enum):
  URL_PARSED = "URL_PARSED_"

class REDIS_COMMANDS:
  S_SET_BOOL = 1
  S_GET_BOOL = 2
  S_SET_INT = 3
  S_GET_INT = 4
  S_SET_STRING = 5
  S_GET_STRING = 6
  S_SET_LIST = 7
  S_GET_LIST = 8
  S_GET_KEYS = 9
  S_GET_FLOAT = 10
  S_SET_FLOAT = 11
  S_FLUSH_ALL = 12
  S_ACQUIRE_LOCK = 13
  S_RELEASE_LOCK = 14
