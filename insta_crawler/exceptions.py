class PrivateProfileError(Exception):
    def __init__(
        self,
        message="The answer is empty. This profile is private. You must first follow it."
    ):
        self.message = message
        super().__init__(self.message)


class BlockedByInstagramError(Exception):
    def __init__(
        self,
        message=""
    ):
        self.message = message
        super().__init__(self.message)


class NoCookieError(Exception):
    def __init__(
        self,
        message="There is no cookie. Use your cookie."
    ):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    def __init__(
        self,
        message="Not found."
    ):
        self.message = message
        super().__init__(self.message)
