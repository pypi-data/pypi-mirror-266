import logging
from pathlib import Path

from cfitall.registry import ConfigurationRegistry


CREDENTIALS_FILE = Path.home() / ".local" / "etc" / "auth" / "google" / "client_credentials.json"
TOKEN_FILE = Path.home() / ".local" / "etc" / "auth" / "google" / "md2gdocs_token.json"

config = ConfigurationRegistry("md2gdocs")
config.set_default("log.level", "error")
config.set_default("google.oauth.client_credentials", str(CREDENTIALS_FILE))
config.set_default("google.oauth.server_port", 9999)
config.set_default("google.oauth.open_browser", True)
config.set_default("google.oauth.token", str(TOKEN_FILE))
config.set_default("markdown.extensions", [])
config.update()

level = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}.get(config.get("log.level"), logging.ERROR)

logging.basicConfig(level=level, format="[%(levelname)s]  %(module)s  -  %(message)s")
