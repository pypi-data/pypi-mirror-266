from enum import Enum


class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    EXPRESS = "express"
    PROD = "prod"

    @property
    def is_debug(self) -> bool:
        return self in (self.LOCAL, self.EXPRESS, self.DEV)
