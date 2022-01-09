import json
import random
from enum import Enum

import colorama
from colorama import Fore, Back


class MatchType(Enum):

    MISS = 0
    WRONG_POS = 1
    HIT = 2


class GameState(Enum):

    IN_PROGRESS = 0
    LOSS = 1
    WIN = 2


class LetterState(Enum):

    UNKNOWN = 0
    IN_WORD = 1
    NOT_IN_WORD = 2


class GameOverError(Exception):
    pass


class InvalidWordError(Exception):
    pass


with open("wordlist_short.json") as fp:
    word_list_short = json.load(fp)

with open("wordlist_extra.json") as fp:
    word_list_extra = json.load(fp)

word_list = word_list_short + word_list_extra


class Wordle:

    def __init__(self, word: str):
        self.word = word.strip().lower()
        if len(self.word) != 5:
            raise InvalidWordError("Length of word must be exactly 5")
        if self.word not in word_list:
            raise InvalidWordError("Word not in valid word list")
        self.guess_list = []
        self.results = []

    @property
    def state(self) -> GameState:
        if len(self.guess_list) == 6 and self.guess_list[-1] != self.word:
            return GameState.LOSS
        elif len(self.guess_list) == 0 or self.guess_list[-1] != self.word:
            return GameState.IN_PROGRESS
        else:
            return GameState.WIN

    @property
    def letter_states(self):
        states = {
            chr(i): LetterState.UNKNOWN
            for i in range(ord('a'), ord('z') + 1)
        }
        for guess_word, result in zip(self.guess_list, self.results):
            for letter, match in zip(guess_word, result):
                if match == MatchType.MISS:
                    states[letter] = LetterState.NOT_IN_WORD
                else:
                    states[letter] = LetterState.IN_WORD
        return sorted(states.items())

    def guess(self, guess_word: str):
        guess_word = guess_word.strip().lower()
        if self.state != GameState.IN_PROGRESS:
            raise GameOverError("game is over")
        if len(guess_word) != 5:
            raise InvalidWordError("Length of guess must be exactly 5")
        if guess_word not in word_list:
            raise InvalidWordError("Guess not in valid word list")
        self.guess_list.append(guess_word)
        result = [
            MatchType.HIT if guess_letter == word_letter
            else MatchType.WRONG_POS if guess_letter in self.word
            else MatchType.MISS
            for (guess_letter, word_letter) in zip(guess_word, self.word)
        ]
        self.results.append(result)
        return result


class WordleCli:

    def __init__(self):
        colorama.init(autoreset=True)

    def new_game(self):
        game = Wordle(random.choice(word_list_short))
        while game.state == GameState.IN_PROGRESS:
            while True:
                try:
                    game.guess(input("Guess: "))
                except InvalidWordError as e:
                    print(e.args[0])
                    print()
                else:
                    break
            #os.system('cls')
            for word, result in zip(game.guess_list, game.results):
                self.print_result(word, result)
            print()
            self.print_letter_states(game.letter_states)
            print()
        if game.state == GameState.WIN:
            print("You won!")
        else:
            print("Game over")
        self.print_share_code(game.results)

        input()

    def print_result(self, guess_word, result):
        strs = []
        for letter, match_type in zip(guess_word, result):
            if match_type == MatchType.MISS:
                prefix = Fore.WHITE + Back.BLACK
            elif match_type == MatchType.HIT:
                prefix = Fore.BLACK + Back.GREEN
            else:
                prefix = Fore.BLACK + Back.YELLOW
            strs.append(prefix + letter)
        print(''.join(strs))

    def print_letter_states(self, letter_states):
        strs = []
        for letter, state in letter_states:
            if state == LetterState.UNKNOWN:
                prefix = Fore.WHITE + Back.BLACK
            elif state == LetterState.IN_WORD:
                prefix = Fore.BLACK + Back.GREEN
            else:
                prefix = Fore.LIGHTBLACK_EX + Back.BLACK
            strs.append(prefix + letter)
        print(''.join(strs))

    def print_share_code(self, results):
        print(f"pbwordle {len(results)}/6")
        for result in results:
            print(''.join(
                '⬛' if match_type == MatchType.MISS
                else '🟨' if match_type == MatchType.WRONG_POS
                else '🟩'
                for match_type in result
            ))


if __name__ == "__main__":
    cli = WordleCli()
    cli.new_game()
