# EazzyFormat
Format made by me, megahomyak. Used to store states in FAQ telegram bot for Eazzy (scooter rental company).

This library has no dependencies and can be installed as `pip install eazzyformat`.

List is `[element element element]`. Element can be a `"string"` or `["another" "list"]`.

You can insert quotes in strings by escaping them: `"quote -> \" <- quote "`. Also, you can add \ to a string by escaping it with another \: `"backslash -> \\ <- backslash"`. Actually, you can escape any other character, and it will produce no result: `"\a"` (in eazzyformat) will become `"a"` (in Python).

Spaces at the beginning of a new line in a string will be trimmed.

Maybe I'll add numbers later.

EazzyFormat objects are being translated to Python objects: lists and strings.