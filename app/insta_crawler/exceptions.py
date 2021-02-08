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
        message="""The request returns a non-JSON response.
There are some reasons of that:
1) Instagram blocked access to your page; 
2) Your cookie string is expired. Try to visit cookie user`s profile
and check this out."""
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
