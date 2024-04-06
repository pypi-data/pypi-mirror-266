import os
from dotenv import load_dotenv
from enum import Enum, auto

current_script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_script_dir, "..", ".env")
load_dotenv(env_path)


class LocationProviderType(Enum):
    ASTRAL = auto()
    MEERKAT = auto()


class LogLevel(Enum):
    DEBUG = auto()
    INFO = auto()
    WARN = auto()


class Conf:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Conf, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._log_level = os.environ.get("LOG_LEVEL", LogLevel.INFO)
        self._latitude = os.environ.get("LATITUDE", "-30:42:39.8")
        self._longitude = os.environ.get("LONGITUDE", "21:26:38.0")
        self._py_env = os.environ.get("PY_ENV", "development")

        if os.environ.get("LOC_PROVIDER"):
            self._loc_provider = LocationProviderType[os.environ.get("LOC_PROVIDER").upper()]
        else:
            self._loc_provider = LocationProviderType.MEERKAT

        test_mode_str = os.environ.get("TEST_MODE", "False")
        if test_mode_str and test_mode_str.lower() in ("0", "false"):
            self._test_mode = False
        else:
            self._test_mode = True

    @property
    def LOC_PROVIDER(self) -> bool:
        return self._loc_provider

    @LOC_PROVIDER.setter
    def LOC_PROVIDER(self, value: LocationProviderType) -> None:
        self._loc_provider = value

    @property
    def TEST_MODE(self) -> bool:
        return self._test_mode

    @TEST_MODE.setter
    def TEST_MODE(self, value: bool) -> None:
        self._test_mode = value

    @property
    def LOG_LEVEL(self):
        return self._log_level

    @LOG_LEVEL.setter
    def LOG_LEVEL(self, value):
        self._log_level = value

    @property
    def LATITUDE(self):
        return self._latitude

    @LATITUDE.setter
    def LATITUDE(self, value):
        self._latitude = value

    @property
    def LONGITUDE(self):
        return self._longitude

    @LONGITUDE.setter
    def LONGITUDE(self, value):
        self._longitude = value

    @property
    def PY_ENV(self):
        return self._py_env

    @PY_ENV.setter
    def PY_ENV(self, value):
        self._py_env = value


__all__ = ["Conf", "LogLevel"]

# Automatically added by katversion
__version__ = '1.5.0'
