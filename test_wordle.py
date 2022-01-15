from contextlib import contextmanager

import pytest as pytest

from wordle import LetterState, GameState, Wordle, GameOverError, InvalidWordError, word_list


@contextmanager
def augment_word_list(new_words):
    word_list.extend(new_words)
    yield
    for _ in new_words:
        word_list.pop()


@pytest.mark.parametrize('word,guess_list,expected', [
    ('apple', [], GameState.IN_PROGRESS),
    ('apple', ['chair', 'puppy'], GameState.IN_PROGRESS),
    ('apple', ['apple'], GameState.WIN),
    ('apple', ['chair', 'puppy', 'laugh', 'plane', 'rhino', 'apple'], GameState.WIN),
    ('apple', ['chair', 'puppy', 'laugh', 'plane', 'rhino', 'novel'], GameState.LOSS),
])
def test_wordle_state(word, guess_list, expected):
    wordle = Wordle(word)
    for guess_word in guess_list:
        wordle.guess(guess_word)
    assert wordle.state == expected


@pytest.mark.parametrize('word,guess_list,letters_in,letters_not_in', [
    ('abcde', ['defgh', 'efghi'], 'de', 'fghi'),
    ('abcba', ['cbabc'], 'abc', ''),
    ('abcde', ['fghij', 'ghijk'], '', 'fghijk'),
    ('abcde', ['efghi', 'jklma'], 'ae', 'fghijklm'),
    ('abcde', [], '', '')
])
def test_wordle_letter_states(word, guess_list, letters_in, letters_not_in):
    with augment_word_list([word] + guess_list):
        wordle = Wordle(word)
        for guess_word in guess_list:
            wordle.guess(guess_word)
        expected = {
            chr(i): LetterState.UNKNOWN
            for i in range(ord('a'), ord('z') + 1)
        }
        for letter in letters_in:
            expected[letter] = LetterState.IN_WORD
        for letter in letters_not_in:
            expected[letter] = LetterState.NOT_IN_WORD
        assert wordle.letter_states == expected


@pytest.mark.parametrize('word,prev_guesses,new_guess', [
    ('apple', ['mango', 'apple'], 'peach'),
    ('apple', ['mango', 'grape', 'plums', 'berry', 'pears', 'guava'], 'apple')
])
def test_wordle_guess__game_over(word, prev_guesses, new_guess):
    wordle = Wordle(word)
    for guess_word in prev_guesses:
        wordle.guess(guess_word)
    with pytest.raises(GameOverError):
        wordle.guess(new_guess)


@pytest.mark.parametrize('length', [0, 1, 2, 3, 4, 6, 7, 100, 1000, 10000])
def test_wordle_guess__invalid_length(length):
    wordle = Wordle('apple')
    with pytest.raises(InvalidWordError):
        wordle.guess('a' * length)


@pytest.mark.parametrize('guess_word', ['aaaaa', '12345', '🤔hmm🤔', '     ', 'ok.ay'])
def test_wordle_guess__invalid_word(guess_word):
    wordle = Wordle('apple')
    with pytest.raises(InvalidWordError):
        wordle.guess(guess_word)
