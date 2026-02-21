#! /usr/bin/python3
import argparse
import collections
import os
import time

from wrdllib.ansi import ANSI
from wrdllib.exceptions import (
    AlreadyGuessed,
    GameOver,
    ImpossibleSolution,
    InvalidGuess,
    NoSuchDictionary,
    OutOfGuesses,
)
from wrdllib.guesses import GuessChecker


class Wrdl:
    MARKERS = {
        -1: f" {ANSI.YELLOW}",
        0: f" {ANSI.DARK_GRAY}",
        1: f" {ANSI.GREEN}",
        None: " ",
    }

    def __init__(self, length=5, max_guesses=6, force_starting_word=None, blind=False):
        self.blind = bool(blind)
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
            f"{self.auto_solver.dictionary.length}-letter word.\n"
        )
        for i, guess in enumerate(self.checker.valid_guesses):
            print(ANSI.BOLD, end="")
            for grade, letter in zip(self.checker.evaluate(i), guess):
                print(f"[{self.MARKERS[grade]}{letter}{ANSI.WHITE} ]", end="")
            print()
        for _ in range(self.max_guesses - len(self.checker.valid_guesses)):
            print(ANSI.BOLD, end="")
            print("[   ]" * self.auto_solver.dictionary.length)
        print()
        self.draw_keyboard()

    def draw_keyboard(self):  # pragma: no cover
        guessed_letters = self.checker.guessed_letters
        for i, row in enumerate(("QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM")):
            print(ANSI.BOLD, end="")
            print(" " * 3 * i, end="")
            for letter in row:
                marker = self.MARKERS[guessed_letters.get(letter)]
                print(f"[{marker}{letter}{ANSI.WHITE} ]", end="")
            print()
        print()

    def enter_guess(self, guess=None):
        try:
            if guess is None:  # pragma: no cover
                guess = input(
                    f"Enter a {self.auto_solver.dictionary.length}-letter guess: "
                )
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
        print(f"{ANSI.BOLD}{self.checker.win_message}")
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
            and sum(self.checker.evaluate()) == self.auto_solver.dictionary.length
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
