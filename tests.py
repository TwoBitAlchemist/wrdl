import string
import pytest

from wrdllib.wrdl import Wrdl
from wrdllib.exceptions import (
    AlreadyGuessed,
    InvalidGuess,
    InvalidGuessChars,
)


def test_wrdl_setup():
    wordle = Wrdl(blind=True)  # word length 5, six guesses, random answer
    assert wordle.auto_solver.dictionary.length == 5
    assert all(len(word) == 5 for word in wordle.auto_solver.dictionary.lexicon)
    assert wordle.max_guesses == 6

    wrdl = Wrdl(length=4, blind=True)
    assert wrdl.auto_solver.dictionary.length == 4
    assert all(len(word) == 4 for word in wrdl.auto_solver.dictionary.lexicon)
    assert wrdl.max_guesses == 6

    easier_wordle = Wrdl(max_guesses=7, blind=True)
    assert easier_wordle.auto_solver.dictionary.length == 5
    assert all(len(word) == 5 for word in easier_wordle.auto_solver.dictionary.lexicon)
    assert easier_wordle.max_guesses == 7

    deterministic_wordle = Wrdl(force_starting_word="CHEAT", blind=True)
    assert deterministic_wordle.auto_solver.dictionary.length == 5
    assert all(
        len(word) == 5 for word in deterministic_wordle.auto_solver.dictionary.lexicon
    )
    assert deterministic_wordle.max_guesses == 6
    deterministic_wordle.enter_guess("CHEAT")
    assert deterministic_wordle.solved

    shortest_wordle = Wrdl(length=2, blind=True)
    assert shortest_wordle.auto_solver.dictionary.length == 2
    assert all(
        len(word) == 2 for word in shortest_wordle.auto_solver.dictionary.lexicon
    )
    assert shortest_wordle.max_guesses == 6

    loooooongest_wordle = Wrdl(length=15, blind=True)
    assert loooooongest_wordle.auto_solver.dictionary.length == 15
    assert all(
        len(word) == 15 for word in loooooongest_wordle.auto_solver.dictionary.lexicon
    )
    assert loooooongest_wordle.max_guesses == 6


def test_guess_handling():
    wordle = Wrdl(force_starting_word="SPILT", blind=True)
    with pytest.raises(InvalidGuess):
        wordle.enter_guess("AAAAA")
    assert len(wordle.checker.valid_guesses) == 0
    assert all(
        wordle.auto_solver.read_from_model(i) == string.ascii_uppercase
        for i in range(5)
    )

    with pytest.raises(InvalidGuessChars):
        wordle.enter_guess("AAA!1")
    assert len(wordle.checker.valid_guesses) == 0
    assert all(
        wordle.auto_solver.read_from_model(i) == string.ascii_uppercase
        for i in range(5)
    )

    wordle.enter_guess("THICK")
    wordle.checker.evaluate()
    assert len(wordle.checker.valid_guesses) == 1
    assert (
        wordle.auto_solver.read_from_model(2) == "I"
    ), wordle.auto_solver.reveal_model()
    assert all(
        letter not in wordle.auto_solver.read_from_model(i)
        for letter in "HCK"
        for i in range(5)
    ), wordle.auto_solver.reveal_model()
    assert "T" not in wordle.auto_solver.read_from_model(
        0
    ), wordle.auto_solver.reveal_model()

    with pytest.raises(AlreadyGuessed):
        wordle.enter_guess("THICK")
    assert len(wordle.checker.valid_guesses) == 1

    wordle = Wrdl(force_starting_word="BLOOM", blind=True)
    assert len(wordle.checker.valid_guesses) == 0
    assert all(
        wordle.auto_solver.read_from_model(i) == string.ascii_uppercase
        for i in range(5)
    )

    wordle.enter_guess("THROW")
    assert len(wordle.checker.valid_guesses) == 1
    assert (
        wordle.auto_solver.read_from_model(3) == "O"
    ), wordle.auto_solver.reveal_model()
    assert all(
        letter not in wordle.auto_solver.read_from_model(i)
        for letter in "THRW"
        for i in range(5)
    ), wordle.auto_solver.reveal_model()

    wordle.enter_guess("OZONE")
    assert len(wordle.checker.valid_guesses) == 2
    assert (
        wordle.auto_solver.read_from_model(2) == "O"
    ), wordle.auto_solver.reveal_model()
    assert (
        wordle.auto_solver.read_from_model(3) == "O"
    ), wordle.auto_solver.reveal_model()
    assert "O" not in wordle.auto_solver.read_from_model(
        0
    ), wordle.auto_solver.reveal_model()
    assert all(
        letter not in wordle.auto_solver.read_from_model(i)
        for letter in "ZE"
        for i in range(5)
    ), wordle.auto_solver.reveal_model()


@pytest.mark.xfail
def test_auto_solver():
    wordle = Wrdl(blind=True)
    wordle.auto_guess()
    assert len(wordle.checker.valid_guesses) == 1
    assert (
        len(wordle.auto_solver.get_plausible_words(wordle.checker.guessed_letters)) > 0
    )
