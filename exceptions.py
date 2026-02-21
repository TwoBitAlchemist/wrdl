class WrdlException:
    def __init__(self, *args, **kw):
        super().__init__(self.default_message, *args, **kw)


class AlreadyGuessed(ValueError, WrdlException):
    default_message = "Already guessed!"


class InvalidGuess(ValueError, WrdlException):
    default_message = "Unrecognized word."


class InvalidGuessChars(InvalidGuess):
    default_message = "Guesses must be letters only."


class InvalidGuessLength(InvalidGuess):
    default_message = "Wrong length for a guess!"


class ImpossibleSolution(RuntimeError, WrdlException):
    default_message = "No plausible words remain but the puzzle is unsolved."


class GameOver(RuntimeError, WrdlException):
    pass


class NoSuchDictionary(OSError, WrdlException):
    pass


class OutOfGuesses(RuntimeError, WrdlException):
    default_message = "Better luck next time!"
