import collections
import random


class Wrdl:
    ANSI_DARK_GRAY = "\033[1;30m"
    ANSI_GREEN = "\033[0;32m"
    ANSI_YELLOW = "\033[0;33m"
    ANSI_WHITE = "\033[1;37m"
    ANSI_BOLD = "\033[1m"
    ANSI_RED = "\033[0;31m"

    MARKERS = {
        -1: f" {ANSI_YELLOW}",
        0: f" {ANSI_DARK_GRAY}",
        1: f" {ANSI_GREEN}",
        None: " ",
    }

    class AlreadyGuessed(ValueError):
        pass

    class InvalidGuess(ValueError):
        pass

    class OutOfGuesses(Exception):
        pass

    class NoSuchDictionary(OSError):
        pass

    def __init__(self, length=5, max_guesses=6, force_starting_word=None):
        length = max(int(length), 1)
        self.__dictionary = None
        try:
            self.read_dictionary(length)
        except OSError:
            raise self.NoSuchDictionary(
                f"No dictionary loaded for {length}-letter words."
            )
        if force_starting_word is not None:
            force_starting_word = force_starting_word.upper()
            if force_starting_word in self.__dictionary:
                self.__secret_word = force_starting_word
            else:
                self.__secret_word = random.choice(self.__dictionary)
        else:
            self.__secret_word = random.choice(self.__dictionary)
        self.__completed_games = 0
        self.__max_guesses = max(int(max_guesses), 1)
        self.__guessed_letters = dict()
        self.__scores = list()
        self.__streak = 0
        self.__valid_guesses = list()

    def draw(self):
        for i, guess in enumerate(self.__valid_guesses):
            print(self.ANSI_BOLD, end="")
            for grade, letter in zip(self._evaluate_guess(i), guess):
                print(f"[{self.MARKERS[grade]}{letter}{self.ANSI_WHITE} ]", end="")
            print()
        for _ in range(self.max_guesses - len(self.__valid_guesses)):
            print(self.ANSI_BOLD, end="")
            print("[   ]" * len(self.secret_word))
        print()
        self.draw_keyboard()

    def draw_keyboard(self):
        for i, row in enumerate(("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")):
            print(self.ANSI_BOLD, end="")
            print(" " * 3 * i, end="")
            for letter in row:
                marker = self.MARKERS[self.__guessed_letters.get(letter)]
                print(f"[{marker}{letter}{self.ANSI_WHITE} ]", end="")
            print()
        print()

    def guess(self, word):
        self.__valid_guesses.append(self._validate_guess(word))
        if not self.solved and len(self.__valid_guesses) >= self.max_guesses:
            raise self.OutOfGuesses("Better luck next time!")
        return self.solved

    def play(self, console_mode=True):
        if console_mode:
            try:
                while not self.solved:
                    self.draw()
                    try:
                        self.guess(
                            input(f"Enter a {len(self.secret_word)}-letter guess: ")
                        )
                        print()
                    except (self.AlreadyGuessed, self.InvalidGuess) as e:
                        print(e)
                    except self.OutOfGuesses as e:
                        self.__streak = 0
                        self.__completed_games += 1
                        self.draw()
                        print(e)
                        print(
                            f"Answer: {self.ANSI_BOLD}{self.ANSI_RED}{self.secret_word}"
                        )
                        break
            except (EOFError, KeyboardInterrupt):
                print("\nGame ended prematurely. Thanks for playing!")
                self.__streak = 0
            else:
                if self.solved:
                    self.__streak += 1
                    self.__completed_games += 1
                    self.__scores.append(len(self.__valid_guesses))
                    self.draw()
                    print(f"{self.ANSI_BOLD}{self.win_message}")

    def read_dictionary(self, length, save=True):
        with open(f"dictionaries/{length}_letter_words.txt") as wordfile:
            self.__dictionary = list(
                set(
                    self._validate_guess(word, length=length, fail_silently=True)
                    for word in wordfile
                )
            )
        if save:
            self.save_dictionary(length)

    def save_dictionary(self, length):
        if not self.__dictionary:
            return
        with open(f"dictionaries/{length}_letter_words.txt", "w") as wordfile:
            for word in sorted(self.__dictionary):
                print(word, file=wordfile)

    def _evaluate_guess(self, index=-1):
        letter_counts = collections.Counter(self.secret_word)
        guess_letter_counts = collections.defaultdict(int)
        for position, letter in enumerate(self.__valid_guesses[int(index)]):
            guess_letter_counts[letter] += 1
            if self.secret_word[position] == letter:
                self.__guessed_letters[letter] = 1
            elif letter in self.secret_word:
                if letter_counts[letter] > guess_letter_counts[letter]:
                    self.__guessed_letters[letter] = -1
                else:
                    self.__guessed_letters[letter] = 0
            else:
                self.__guessed_letters[letter] = 0
            yield self.__guessed_letters[letter]

    def _validate_guess(self, guess, length=None, fail_silently=False):
        guess = str(guess).upper().strip()
        try:
            if len(guess) != (length or len(self.secret_word)):
                raise self.InvalidGuess("Wrong length for a guess!")
            if any(not char.isalpha() for char in guess):
                raise self.InvalidGuess("Guesses must be letters only.")
            if self.__dictionary is not None:
                if guess not in self.__dictionary:
                    raise self.InvalidGuess("Unrecognized word.")
                if guess in self.__valid_guesses:
                    raise self.AlreadyGuessed("Already guessed!")
        except (self.InvalidGuess, self.AlreadyGuessed):
            if not fail_silently:
                raise
        return guess

    @property
    def completed_games(self):
        return self.__completed_games

    @property
    def guessed_letters(self):
        return tuple(self.__guessed_letters)

    @property
    def max_guesses(self):
        return self.__max_guesses

    @property
    def scores(self):
        score_counts = collections.Counter(self.__scores)

        def percent(s):
            return f"{round((score_counts[s] / len(self.__scores)) * 100, 1)}%"

        return {s: percent(s) for s in range(1, 7)}

    @property
    def secret_word(self):
        return self.__secret_word

    @property
    def solved(self):
        return bool(self.__valid_guesses) and sum(self._evaluate_guess()) == len(
            self.secret_word
        )

    def stats(self):
        print("Total games played:", self.completed_games)
        print("Longest win streak:", self.streak)
        if self.completed_games:
            print(
                "Win Rate:",
                f"{round((len(self.__scores) / self.completed_games) * 100, 1)}%",
            )
        if self.scores:
            print()
            scores = self.scores
            for score in range(1, 7):
                print(f"{score}: {self.scores[score]}")

    @property
    def streak(self):
        return self.__streak

    @property
    def valid_guesses(self):
        return tuple(self.__valid_guesses)

    @property
    def win_message(self):
        match len(self.__valid_guesses):
            case 0:
                return "Unbelievable!"
            case 1:
                return "Genius!"
            case 2:
                return "Magnificent!"
            case 3:
                return "Impressive."
            case 4:
                return "Splendid."
            case 5:
                return "Great."
            case 6:
                return "Phew..."
