import logging
import sys
from DLMS_SPODES.config_parser import get_values


_log_config = {
    """logging configuration according with config.toml:[DLMSClient.logging] by default"""
    "disabled": False,
    "name": "DLMSClient",
    "level": logging.INFO,
    "format": "%(id)s: %(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%d.%m %H:%M",
    "handlers": [
        {"type": "Stream"}
    ]
}
logger = logging.getLogger(name=F"{_log_config['name']}.{__name__}")
is_file_handler_exist: bool = False
if __log_config_toml := get_values("DLMSClient", "logging"):
    _log_config.update(__log_config_toml)
    logger.disabled = _log_config.get("disabled", False)
    logger.setLevel(level=_log_config["level"])
    formatter = logging.Formatter(
        fmt=_log_config["format"],
        datefmt=_log_config["date_format"])
    for h in _log_config["handlers"]:
        match h.get("type"):
            case "Stream":
                handler = logging.StreamHandler(stream=sys.stdout)
            case "File":
                is_file_handler_exist = True
                handler = logging.FileHandler(
                    filename=h.get("filename", "client_log.txt"),
                    mode=h.get("mode", "a"),
                    encoding="utf-8")
            case err:
                raise ValueError(F"got error logger type Handler: {err}")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.debug(F"Start {logger}", extra={"id": "#common"})
else:
    logger.disabled = True
