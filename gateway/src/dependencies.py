from functools import lru_cache

from config.config import GatewaySettings

@lru_cache
def get_settings():
    return GatewaySettings()