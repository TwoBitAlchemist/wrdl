import collections
import random
import string

from .dictionary import WrdlDictionary
from .exceptions import AlreadyGuessed, ImpossibleSolution, NoSuchDictionary


class WrdlSolver:
    def __init__(self, length):
        length = min(max(int(length), 2), 15)
        try:
            self.dictionary = WrdlDictionary(length)
        except OSError:  # pragma: no cover
            raise NoSuchDictionary(f"No dictionary loaded for {length}-letter words.")
        self.__auto_guess_model = [string.ascii_uppercase] * self.dictionary.length

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
                key=self.grade_guess,
                reverse=True,
            )[0]
        else:
            raise ValueError("one of modes 'random_guess' or 'best_guess' is required")

    def grade_guess(self, guess):
        return sum(
            GuessChecker.evaluate_single_guess(str(guess), possible_secret_word)
            for possible_secret_word in self.dictionary.lexicon
        )

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
                        char
                        for char in self.__auto_guess_model[index]
                        if char != letter
                    )
            else:
                self.__auto_guess_model[index] = "".join(
                    char for char in self.__auto_guess_model[index] if char != letter
                )


class GuessChecker:
    def __init__(self, length, force_starting_word=None):
        self.auto_solver = WrdlSolver(length)
        self.reset(force_starting_word)

    @classmethod
    def evaluate_single_guess(cls, guess, secret_word):
        guess, secret_word = map(str, (guess, secret_word))
        checker = cls(len(secret_word), force_starting_word=secret_word)
        checker.validate(guess)
        return sum(checker.evaluate())

    def evaluate(self, index=-1):
        guess = self.__valid_guesses[int(index)]
        evaluations = [None] * self.auto_solver.dictionary.length
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
            if force_starting_word in self.auto_solver.dictionary.lexicon:
                self.__secret_word = force_starting_word
        if self.__secret_word is None:
            self.__secret_word = random.choice(self.auto_solver.dictionary.lexicon)
        self.__guessed_letters = dict()
        self.__valid_guesses = list()

    def reveal_answer(self):  # pragma: no cover
        print(f"Answer: {ANSI.BOLD}{ANSI.RED}{self.__secret_word}")

    def validate(self, guess):
        guess = self.auto_solver.dictionary.validate(guess)
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
