#! /usr/bin/python3
import argparse
import collections
import os
from pathlib import Path
import random
import string
import time


ANSI_DARK_GRAY = "\033[1;30m"
ANSI_GREEN = "\033[0;32m"
ANSI_YELLOW = "\033[0;33m"
ANSI_WHITE = "\033[1;37m"
ANSI_BOLD = "\033[1m"
ANSI_RED = "\033[0;31m"


class WrdlException:
    def __init__(self, *args, **kw):
        super().__init__(self.default_message, *args, **kw)


class AlreadyGuessed(ValueError, WrdlException):
    default_message = "Already guessed!"


class InvalidGuess(ValueError, WrdlException):
    default_message = "Invalid guess."


class ImpossibleSolution(RuntimeError, WrdlException):
    default_message = "No plausible words remain but the puzzle is unsolved."


class GameOver(RuntimeError, WrdlException):
    pass


class NoSuchDictionary(OSError, WrdlException):
    pass


class OutOfGuesses(RuntimeError, WrdlException):
    default_message = "Better luck next time!"


class WrdlDictionary:
    def __init__(self, length):
        self.__length = int(length)

        def validate_word(word, checker=GuessChecker(self.__length)):
            try:
                return checker.validate(word)
            except (AlreadyGuessed, InvalidGuess):
                return None

        with open(
            Path(__file__).parent.joinpath("dictionary.txt").resolve()
        ) as wordfile:
            self.__lexicon = list(
                filter(
                    None,
                    set(
                        validate_word(word, length=length, fail_silently=True)
                        for word in wordfile
                    ),
                )
            )

    @property
    def length(self):
        return self.__length

    @property
    def lexicon(self):
        return tuple(self.__lexicon)


class WrdlSolver:
    def __init__(self, length):
        self.dictionary = WrdlDictionary(length)
        self.__auto_guess_model = [string.ascii_uppercase] * self.dictionary.length

    def plausible_words(self):
        words = tuple(
            word
            for word in self.dictionary.lexicon
            if all(
                letter in self.__auto_guess_model[position]
                for position, letter in enumerate(word)
            )
            and all(
                misplaced_letter in word
                for misplaced_letter in "".join(
                    char
                    for char in string.ascii_uppercase
                    if self.__guessed_letters.get(char) == -1
                )
            )
        )
        if not words:
            raise ImpossibleSolution()
        else:
            return words

    def read_from_model(self, index):
        return self.__auto_guess_model[index]

    def remove_from_model(self, index, letter):
        self.update_model(
            index,
            "".join(
                char
                for char in self.__auto_guess_model[index]
                if char != letter
            )
        )

    def update_model(self, index, plausible_letters):
        self.__auto_guess_model[index] = str(plausible_letters)


class GuessChecker:
    def __init__(self, length, force_starting_word=None):
        self.dictionary = WrdlDictionary(length)
        self.auto_solver = WrdlSolver(length)
        self.reset(force_starting_word)

    def evaluate(self, index=-1):
        letter_counts = collections.Counter(self.__secret_word)
        guess_letter_counts = collections.defaultdict(int)
        for position, letter in enumerate(self.__valid_guesses[int(index)]):
            guess_letter_counts[letter] += 1
            if self.__secret_word[position] == letter:
                self.__guessed_letters[letter] = 1
                self.auto_solver.update_model(position, letter)
            elif letter in self.__secret_word:
                if letter_counts[letter] >= guess_letter_counts[letter]:
                    self.__guessed_letters[letter] = -1
                    self.auto_solver.remove_from_model(position, letter)
                else:
                    self.__guessed_letters[letter] = 0
            else:
                self.__guessed_letters[letter] = 0
            yield self.__guessed_letters[letter]
        possible_letters = "".join(
            (
                letter
                for letter in string.ascii_uppercase
                if self.__guessed_letters.get(letter) != 0
            )
        )
        for i in range(self.dictionary.length):
            letter_set = self.auto_solver.read_from_model(i)
            if len(letter_set) > len(possible_letters):
                self.auto_solver.update_model(i, possible_letters)

    @property
    def guessed_letters(self):
        return self.__guessed_letters.copy()

    def reset(self, force_starting_word=None):
        self.__secret_word = None
        if force_starting_word is not None:
            force_starting_word = force_starting_word.upper()
            if force_starting_word in self.dictionary.lexicon:
                self.__secret_word = force_starting_word
        if self.__secret_word is None:
            self.__secret_word = random.choice(self.dictionary.lexicon)
        self.__guessed_letters = dict()
        self.__valid_guesses = list()

    def reveal_answer(self):
        print(f"Answer: {ANSI_BOLD}{ANSI_RED}{self.__secret_word}")

    def validate(self, guess):
        guess = str(guess).upper().strip()

        if len(guess) != len(self.dictionary.length):
            raise InvalidGuess("Wrong length for a guess!")

        if any(not char.isalpha() for char in guess):
            raise InvalidGuess("Guesses must be letters only.")

        if self.dictionary.lexicon is not None:
            if guess not in self.dictionary.lexicon:
                raise InvalidGuess("Unrecognized word.")
            if guess in self.__valid_guesses:
                raise AlreadyGuessed()

        self.__valid_guesses.append(guess)
        return guess

    @property
    def valid_guesses(self):
        return tuple(self.__valid_guesses)


class Wrdl:
    MARKERS = {
        -1: f" {ANSI_YELLOW}",
        0: f" {ANSI_DARK_GRAY}",
        1: f" {ANSI_GREEN}",
        None: " ",
    }

    def __init__(self, length=5, max_guesses=6, force_starting_word=None):
        length = min(max(int(length), 2), 15)
        try:
            self.dictionary = WrdlDictionary(length)
        except OSError:
            raise NoSuchDictionary(
                f"No dictionary loaded for {length}-letter words."
            )
        self.__completed_games = 0
        self.__max_guesses = max(int(max_guesses), 1)
        self.__scores = list()
        self.__streak = 0
        self.checker = GuessChecker(length, force_starting_word)

    def auto_guess(self):
        try:
            self.enter_guess(random.choice(self.checker.auto_solver.plausible_words()))
        except GameOver as message:
            print(message)

    def demo(self):
        self.play(demo=True)

    def draw(self):
        os.system("clear")
        print(
            f"Playing Wrdl:\nYou have {self.max_guesses} guesses to find a "
            f"{self.dictionary.length}-letter word.\n"
        )
        for i, guess in enumerate(self.checker.valid_guesses):
            print(ANSI_BOLD, end="")
            for grade, letter in zip(self.checker.evaluate(i), guess):
                print(f"[{self.MARKERS[grade]}{letter}{ANSI_WHITE} ]", end="")
            print()
        for _ in range(self.max_guesses - len(self.checker.valid_guesses)):
            print(ANSI_BOLD, end="")
            print("[   ]" * self.dictionary.length)
        print()
        self.draw_keyboard()

    def draw_keyboard(self):
        guessed_letters = self.checker.guessed_letters
        for i, row in enumerate(("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")):
            print(ANSI_BOLD, end="")
            print(" " * 3 * i, end="")
            for letter in row:
                marker = self.MARKERS[guessed_letters.get(letter)]
                print(f"[{marker}{letter}{ANSI_WHITE} ]", end="")
            print()
        print()

    def enter_guess(self, guess=None):
        try:
            if guess is None:
                guess = input(f"Enter a {self.dictionary.length}-letter guess: ")
            guess = self.checker.validate(guess)
            print()
        except (AlreadyGuessed,InvalidGuess) as message:
            print(message)
        except OutOfGuesses as message:
            self.you_lose(message)
        except (EOFError, KeyboardInterrupt) as message:
            self.you_quit()

        if self.solved:
            self.you_win()
        else:
            self.draw()

    def play(self, demo=True, simulations=1):
        if self.checker.valid_guesses:
            self.checker.reset()
        self.draw()
        for iteration in range(simulations if demo else 1):
            while not self.solved:
                try:
                    if demo:
                        time.sleep(3)
                        self.auto_guess()
                    else:
                        self.enter_guess()
                except GameOver:
                    break
        if not demo:
            self.play_again()

    def play_again(self):
        again = input("Play again? (Y/n) - ").upper()
        if again == "N":
            print("Thanks for playing Wrdl!")
        else:
            self.play()

    def you_lose(self, message):
        self.__streak = 0
        self.__completed_games += 1
        self.draw()
        print(message)
        raise GameOver(message)

    def you_quit(self):
        message = "Game ended prematurely. Thanks for playing!"
        print()
        print(message)
        self.__streak = 0
        raise GameOver(message)

    def you_win(self):
        self.__streak += 1
        self.__completed_games += 1
        self.__scores.append(len(self.checker.valid_guesses))
        self.draw()
        print(f"{ANSI_BOLD}{self.win_message}")
        self.stats()

    @property
    def completed_games(self):
        return self.__completed_games

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
    def solved(self):
        return bool(self.checker.valid_guesses) and sum(self.checker.evaluate()) == self.dictionary.length

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Wrdl",
        description="A small Wordle clone that can vary the board size somewhat.",
        epilog="Enjoy Wrdl! :)",
    )
    parser.add_argument("-l", "--length", default=5)
    parser.add_argument("-m", "--max-guesses", default=6)
    parser.add_argument("-d", "--demo", action="store_true")
    parser.add_argument("-s", "--simulations", default=1)
    args = parser.parse_args()
    game_engine = Wrdl(length=args.length, max_guesses=args.max_guesses)
    game_engine.play(demo=args.demo, simulations=int(args.simulations))
