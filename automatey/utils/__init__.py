
import random
import string

class Random:

    @staticmethod
    def getRandomText(len:int) -> str:
        """Generate random text, consisting only of upper-case letter(s) and digit(s).

        Parameters
        ----------
        len : int
            Expected length of text.

        Returns
        -------
        txt : string
            Random text.
        """
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(len))