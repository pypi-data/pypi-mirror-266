import re
from dataclasses import dataclass
from typing import Union, Optional, List, Dict

from eazzyformat.string_iterators import StringIteratorWithNewlinesCounting


class BaseEazzyFormatSyntaxError(Exception):
    character_state: str

    def __init__(self, character_number: int, character: str, line_number: int):
        self.character_number = character_number
        self.character = character
        self.line_number = line_number

    def __str__(self):
        return (
            f"{self.character_state} character '{self.character}' on line "
            f"{self.line_number}, character number {self.character_number}"
        )


class UnexpectedCharacter(BaseEazzyFormatSyntaxError):
    character_state = "Unexpected"


class UnclosedCharacter(BaseEazzyFormatSyntaxError):
    character_state = "Unclosed"


class NothingToParse(Exception):
    pass


class ListEnded(Exception):
    pass


EazzyObject = Union[str, List["EazzyObject"]]


@dataclass
class ParsingResult:
    parsed_object: EazzyObject
    rest_index: Optional[int]


REMOVE_INDENTATION_REGEX = re.compile(r"\n[^\S\r\n]+")


def _parse_eazzyformat_object(
        string_iterator: StringIteratorWithNewlinesCounting,
        cached_strings: Dict[str, str]) -> EazzyObject:
    try:
        character = string_iterator.skip(" \n\t")
    except StopIteration:
        raise NothingToParse from None
    else:
        if character == "[":
            parsed_objects_list = []
            character_number = string_iterator.previous_character_number
            line_number = string_iterator.line_number
            while True:
                try:
                    parsed_object = _parse_eazzyformat_object(
                        string_iterator, cached_strings
                    )
                except NothingToParse:
                    raise UnclosedCharacter(
                        character_number, "[", line_number
                    ) from None
                except ListEnded:
                    break
                else:
                    parsed_objects_list.append(parsed_object)
            return parsed_objects_list
        elif character == "]":
            raise ListEnded
        elif character == '"':
            character_number = string_iterator.previous_character_number
            line_number = string_iterator.line_number
            try:
                string = ""
                while True:
                    string += string_iterator.collect_to('"\\')
                    if next(string_iterator) == '"':
                        string = REMOVE_INDENTATION_REGEX.sub("\n", string)
                        return cached_strings.setdefault(string, string)
                    else:  # \
                        string += next(string_iterator)
            except StopIteration:
                raise UnclosedCharacter(
                    character_number, '"', line_number
                ) from None
        else:
            raise UnexpectedCharacter(
                string_iterator.previous_character_number,
                character, string_iterator.line_number
            )


def parse_eazzyformat(string: str) -> ParsingResult:
    """
    Returns a string or list. Every list can contain other lists or strings
    Can raise NothingToParse
    """
    string_iterator = StringIteratorWithNewlinesCounting(string)
    parsed_object = _parse_eazzyformat_object(
        string_iterator, cached_strings={}
    )
    text_after_object_index = string_iterator.index
    try:
        string_iterator.skip(" \n\t")
    except StopIteration:
        return ParsingResult(parsed_object, rest_index=None)
    else:
        return ParsingResult(parsed_object, rest_index=text_after_object_index)
