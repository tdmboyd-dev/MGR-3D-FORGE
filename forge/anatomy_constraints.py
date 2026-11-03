"""Small explicit English anatomy contract for the native CPU creature builder.

This is deliberately bounded syntax, not general language comprehension. Hard
constraints override species guesses and remain fixed across design variants.
"""
import re

NUMBERS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
           "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
           "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
           "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
           "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
           "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
           "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000,
           "dozen": 12}
NOUN = r"(?:wings?|horns?|tails?|armou?r|eyes?|legs?)"
KEYS = {"wing": "wing_pairs", "horn": "horn_count", "tail": "tail",
        "armor": "armor", "armour": "armor", "eye": "eye_count", "leg": "legs"}


def parse_anatomy_constraints(prompt):
    text = prompt.casefold()
    constraints = {}
    negative_spans = []

    def put(key, value):
        if key in constraints and constraints[key] != value:
            # Unquantified positive horns and an explicit nonzero count agree.
            old = constraints[key]
            if key == "horn_count" and (old == "present" or value == "present"):
                count = value if old == "present" else old
                if type(count) is int and count > 0:
                    constraints[key] = count
                    return
            raise ValueError(f"conflicting explicit creature anatomy: {key}")
        constraints[key] = value

    # Negation owns only its listed nouns; it never consumes a later 'with'.
    for match in re.finditer(rf"\b(?:no|without|not with)\s+(?:any\s+)?({NOUN}(?:\s+(?:and|or|nor)\s+{NOUN})*)\b", text):
        negative_spans.append(match.span())
        for noun in re.findall(NOUN, match.group(1)):
            key = KEYS[noun.rstrip("s")]
            put(key, False if key in ("tail", "armor") else 0)
    absent_words = {"wingless": ("wing_pairs", 0), "hornless": ("horn_count", 0),
                    "tailless": ("tail", False), "unarmored": ("armor", False),
                    "unarmoured": ("armor", False), "eyeless": ("eye_count", 0),
                    "legless": ("legs", 0)}
    for word, (key, value) in absent_words.items():
        if re.search(rf"\b{word}\b", text):
            put(key, value)
    # Remove negated lists before counting explicit positives.
    chars = list(text)
    for start, end in negative_spans:
        chars[start:end] = " " * (end - start)
    positive = "".join(chars)
    # Reject whole signed/fractional/scientific/grouped numeric tokens before a
    # word-boundary match can silently interpret only their last digit(s).
    for match in re.finditer(r"(?<![\w])([+-]?(?:\d[\d.,/eE+-]*|\.\d+))[ -]+(?:legs?|legged|eyes?|eyed|horns?|horned|wings?|winged)\b", positive):
        if not match.group(1).isdigit():
            raise ValueError("creature anatomy counts must be whole unsigned integers")
    count_pattern = "|".join(NUMBERS)
    units = "one|two|three|four|five|six|seven|eight|nine"
    tens = "twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
    counted = []
    for match in re.finditer(rf"\b((?:{tens})[ -](?:{units})|{count_pattern}|[0-9]+)[ -]+(legs?|legged|eyes?|eyed|horns?|horned|wings?|winged)\b", positive):
        token, noun = match.groups()
        if token in NUMBERS:count = NUMBERS[token]
        elif token.isdigit():count = int(token)
        else:count = sum(NUMBERS[word] for word in re.split(r"[ -]", token))
        key = "legs" if noun.startswith("leg") else "eye_count" if noun.startswith("eye") else "horn_count" if noun.startswith("horn") else "wing_pairs"
        supported = {"legs": (0, 2, 4, 8), "eye_count": range(9),
                     "horn_count": range(7), "wing_pairs": (0, 2)}[key]
        if count not in supported:
            raise ValueError(f"unsupported explicit creature anatomy: {count} {noun}")
        put(key, count // 2 if key == "wing_pairs" else count)
        counted.append(match.span())
    # Counted zero features are not positive presence claims. Mask those phrases
    # before resolving remaining explicit nouns/adjectives against exclusions.
    chars = list(positive)
    for start, end in counted:chars[start:end] = " " * (end - start)
    presence = "".join(chars)
    if re.search(r"\b(?:winged|wings?)\b", presence):
        put("wing_pairs", 1)
    if re.search(r"\b(?:horned|horns?)\b", presence):
        put("horn_count", "present")
    if re.search(r"\b(?:tails?|tailed)\b", presence):
        put("tail", True)
    if re.search(r"\b(?:armored|armoured|armor|armour)\b", presence):
        put("armor", True)
    return constraints
