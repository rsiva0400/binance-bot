from enum import Enum


class BotState(Enum):
    IDLE = "IDLE"
    SCANNING = "SCANNING"
    IN_TRADE = "IN_TRADE"
    COOLDOWN = "COOLDOWN"
    STOPPED = "STOPPED"
