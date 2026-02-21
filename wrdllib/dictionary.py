from pathlib import Path

from .exceptions import (
    InvalidGuess,
    InvalidGuessChars,
    InvalidGuessLength,
)


class WrdlDictionary:
    def __init__(self, length):
        self.__length = int(length)

        with open(
            Path(__file__).parent.joinpath("dictionary.txt").resolve()
        ) as wordfile:
            self.__lexicon = list(
                filter(
                    None,
                    set(self.validate(word, fail_silently=True) for word in wordfile),
                )
            )

    @property
    def length(self):
        return self.__length

    @property
    def lexicon(self):
        try:
            return tuple(self.__lexicon)
        except AttributeError:
            return None

    def validate(self, word, fail_silently=False):
        word = str(word).upper().strip()

        try:
            if len(word) != self.length:
                raise InvalidGuessLength()

            if any(not char.isalpha() for char in word):
                raise InvalidGuessChars()

            if self.lexicon is not None and word not in self.lexicon:
                raise InvalidGuess()
        except InvalidGuess:
            if fail_silently:
                return None
            else:
                raise
        else:
            return word
