from core.enums import BotState


class StateMachine:
    def __init__(self) -> None:
        self._state: BotState = BotState.IDLE

    @property
    def state(self) -> BotState:
        return self._state

    def transition(self, new_state: BotState) -> None:
        self._state = new_state
