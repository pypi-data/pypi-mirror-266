
from typing import Any
from selenium.webdriver import ActionChains


class Action:
    x: int = None
    y: int = None
    action_chain: ActionChains = None

    def __init__(self,
                 x: int,
                 y: int,
                 driver: Any):
        self.x = x
        self.y = y
        self.action_chain = ActionChains(driver)

    def click(self):
        self.action_chain.w3c_actions.pointer_action.move_to_location(self.x, self.y).click()
        self.action_chain.perform()

    def input(self, value: str):
        self.click()

        self.action_chain.w3c_actions.key_action.send_keys(value)
        self.action_chain.perform()
