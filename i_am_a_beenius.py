# NYT Spelling Bee Auto-Answers

letters = ""
while len(letters) != 7 or not all(char.isalpha() for char in letters):
    letters = input("What are today's letters, in any order? (e.g. UOCIRYT)\n").upper()

required_letter = ""
while len(required_letter) != 1 or required_letter not in letters:
    required_letter = input("And which letter is in the middle (required)?\n").upper()

with open("wrdllib/dictionary.txt") as dictionary_file:
    solutions = [
        word.strip()
        for word in dictionary_file
        if required_letter in word and all((char in letters) for char in word[:-1])
    ]

sort_key = lambda word: (len(word), word)
previous_length = -1
for word in sorted(solutions, key=sort_key, reverse=True):
    length = len(word)
    if length < 4:
        break
    if length != previous_length:
        print("\n")
        print(f"{length}-letter solutions:")
        print("===================")
        previous_length = length
        line_length = 0
    print(word.lower(), end="  ")
    line_length += length + 2
    if line_length > 80:
        print()
        line_length = 0
print("\n\nSo, did I get Genius rank or what?")
