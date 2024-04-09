from typing import Container


class StringIteratorWithIndex:

    def __iter__(self):
        return self

    def __init__(self, string: str, index=0):
        self.string = string
        self.index = index

    def __next__(self):
        try:
            character = self.string[self.index]
        except IndexError:
            raise StopIteration from None
        self.index += 1
        return character

    def skip_to(self, characters: Container[str]) -> str:
        while True:
            character = next(self)
            if character in characters:
                return character

    def skip(self, characters: Container[str]) -> str:
        while True:
            character = next(self)
            if character not in characters:
                return character

    def collect_to(
            self, characters: Container[str], including_end=False) -> str:
        beginning_index = self.index
        while True:
            if next(self) in characters:
                if not including_end:
                    self.index -= 1
                return self.string[beginning_index:self.index]


class StringIteratorWithNewlinesCounting(StringIteratorWithIndex):

    def __init__(
            self, string: str, index=0, line_number=1, character_number=0):
        super().__init__(string, index)
        self.line_number = line_number
        self.character_number = character_number

    def __next__(self):
        try:
            character = self.string[self.index]
        except IndexError:
            raise StopIteration from None
        if character == "\n":
            self.line_number += 1
            self.character_number = 0
        self.index += 1
        self.character_number += 1
        return character

    @property
    def previous_character_number(self):
        return self.character_number - 1
