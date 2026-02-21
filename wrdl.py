#! /usr/bin/python3
import argparse
import collections
import os
from pathlib import Path
import random
import string
import time

from exceptions import *

ANSI_DARK_GRAY = "\033[1;30m"
ANSI_GREEN = "\033[0;32m"
ANSI_YELLOW = "\033[0;33m"
ANSI_WHITE = "\033[1;37m"
ANSI_BOLD = "\033[1m"
ANSI_RED = "\033[0;31m"


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


class WrdlSolver:
    def __init__(self, length):
        self.dictionary = WrdlDictionary(length)
        self.__auto_guess_model = [string.ascii_uppercase] * self.dictionary.length
        self.__letter_frequency = collections.Counter("".join(self.dictionary.lexicon))

    def get_plausible_words(self, guessed_letters):
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
                    if guessed_letters.get(char) == -1
                )
            )
        )
        if not words:  # pragma: no cover
            raise ImpossibleSolution()
        else:
            return words

    def generate_guess(self, guessed_letters, random_guess=True, best_guess=False):
        if random_guess and best_guess:
            raise ValueError(
                "random_guess and best_guess are mutually exclusive arguments"
            )
        elif random_guess:
            return random.choice(self.get_plausible_words(guessed_letters))
        elif best_guess:
            return sorted(
                self.get_plausible_words(guessed_letters),
                key=self.grade_letter_probability,
                reverse=True,
            )[0]
        else:
            raise ValueError("one of modes 'random_guess' or 'best_guess' is required")

    def grade_letter_probability(self, word):
        return sum(self.__letter_frequency[char] for char in word)

    def read_from_model(self, index):
        return self.__auto_guess_model[int(index)]

    def reveal_model(self):  # pragma: no cover
        for position in range(self.dictionary.length):
            print(f"{position}: {self.read_from_model(position)}")

    def update_model(self, index, letter, evaluation):
        index, letter, evaluation = int(index), str(letter), int(evaluation)
        if evaluation == 1:
            self.__auto_guess_model[index] = letter
        else:
            if evaluation == 0:
                for index, _ in enumerate(self.__auto_guess_model):
                    self.__auto_guess_model[index] = "".join(
                        char for char in self.__auto_guess_model[index] if char != letter
                    )
            else:
                self.__auto_guess_model[index] = "".join(
                    char for char in self.__auto_guess_model[index] if char != letter
                )


class GuessChecker:
    def __init__(self, length, force_starting_word=None):
        self.dictionary = WrdlDictionary(length)
        self.auto_solver = WrdlSolver(length)
        self.reset(force_starting_word)

    def evaluate(self, index=-1):
        guess = self.__valid_guesses[int(index)]
        evaluations = [None] * self.dictionary.length
        guessed_letter_counts = collections.defaultdict(int)
        letter_counts = collections.Counter(self.__secret_word)

        for position, letter in enumerate(guess):
            if self.__secret_word[position] == letter:
                evaluation = 1
            elif letter not in self.__secret_word:
                evaluation = 0
            else:
                continue
            evaluations[position] = evaluation
            guessed_letter_counts[letter] += evaluation

        for position, evaluation in enumerate(evaluations):
            if evaluation is not None:
                continue
            guessed_letter = guess[position]
            if guessed_letter_counts[guessed_letter] >= letter_counts[guessed_letter]:
                evaluations[position] = 0
            else:
                evaluations[position] = -1
            guessed_letter_counts[guessed_letter] += 1

        position = 0
        for letter, evaluation in zip(guess, evaluations):
            self.__guessed_letters[letter] = evaluation
            self.auto_solver.update_model(position, letter, evaluation)
            yield evaluation
            position += 1

    @property
    def guessed_letters(self):
        return dict(self.__guessed_letters)

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

    def reveal_answer(self):  # pragma: no cover
        print(f"Answer: {ANSI_BOLD}{ANSI_RED}{self.__secret_word}")

    def validate(self, guess):
        guess = self.dictionary.validate(guess)
        if guess in self.__valid_guesses:
            raise AlreadyGuessed()
        self.__valid_guesses.append(guess)
        return guess

    @property
    def valid_guesses(self):
        return tuple(self.__valid_guesses)

    @property
    def win_message(self):  # pragma: no cover
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


class Wrdl:
    MARKERS = {
        -1: f" {ANSI_YELLOW}",
        0: f" {ANSI_DARK_GRAY}",
        1: f" {ANSI_GREEN}",
        None: " ",
    }

    def __init__(self, length=5, max_guesses=6, force_starting_word=None, blind=False):
        length = min(max(int(length), 2), 15)
        self.blind = bool(blind)
        try:
            self.dictionary = WrdlDictionary(length)
        except OSError:  # pragma: no cover
            raise NoSuchDictionary(f"No dictionary loaded for {length}-letter words.")
        self.__completed_games = 0
        self.__max_guesses = max(int(max_guesses), 1)
        self.__scores = list()
        self.__streak = 0
        self.checker = GuessChecker(length, force_starting_word)
        self.auto_solver = self.checker.auto_solver

    def auto_guess(self, best_guess=True, random_guess=False):
        try:
            self.enter_guess(
                self.auto_solver.generate_guess(
                    self.checker.guessed_letters,
                    best_guess=best_guess,
                    random_guess=random_guess,
                )
            )
        except ImpossibleSolution as e:  # pragma: no cover
            print(e)
            self.checker.reveal_answer()
            raise GameOver("Impossible Solution")

    def demo(self):  # pragma: no cover
        self.play(demo=True)

    def draw(self):  # pragma: no cover
        if self.blind:
            return
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

    def draw_keyboard(self):  # pragma: no cover
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
            if guess is None:  # pragma: no cover
                guess = input(f"Enter a {self.dictionary.length}-letter guess: ")
            guess = self.checker.validate(guess)
            print()
        except (AlreadyGuessed, InvalidGuess) as message:
            if self.blind:
                raise
            else:  # pragma: no cover
                print(message)
        except OutOfGuesses as message:
            self.you_lose(message)
        except (EOFError, KeyboardInterrupt) as message:
            self.you_quit()

        if self.solved:
            self.you_win()
        else:
            self.draw()

    def play(self, demo=True, simulations=1):  # pragma: no cover
        for iteration in range(simulations if demo else 1):
            if self.checker.valid_guesses:
                self.checker.reset()
            self.draw()
            while not self.solved:
                try:
                    if demo:
                        time.sleep(3)
                        self.auto_guess()
                    else:
                        self.enter_guess()
                except GameOver as message:
                    print(message)
                    break
        if not demo:
            self.play_again()

    def play_again(self):  # pragma: no cover
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
        print(f"{ANSI_BOLD}{self.checker.win_message}")
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
        return (
            bool(self.checker.valid_guesses)
            and sum(self.checker.evaluate()) == self.dictionary.length
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


if __name__ == "__main__":  # pragma: no cover
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
