import logging

from pyautowire import cache


class Injectable:
    @classmethod
    def get_fully_qualified_name(cls) -> str:
        return f"{cls.__module__}.{cls.__name__}"

    def register(self) -> "Injectable":
        """
        Registers this Injectable instance in the cache.
        Returns itself as a convenience, such that you can call e.g.
        `configuration = MyConfiguration().register()`
        :return:
        """
        logging.debug(f"Registering {self.get_fully_qualified_name()} as singleton.")
        return cache.register(self)
