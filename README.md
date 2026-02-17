Configurable play Wordle. Must have dictionaries loaded at
`dictionaries/n_letter_words.txt` to play `Wrdl(length=n)`.
The max for `max_guesses` is given only by your patience.

```bash
└──╼ python3 wrdl --help
usage: Wrdl [-h] [-l LENGTH] [-m MAX_GUESSES] [-i]

A small Wordle clone that can vary the board size somewhat.

options:
  -h, --help            show this help message and exit
  -l, --length LENGTH
  -m, --max-guesses MAX_GUESSES
  -i, --interactive

Enjoy Wrdl! :)
```

```python
>>> from wrdl import Wrdl; Wrdl(length=4, max_guesses=2).play()
[   ][   ][   ][   ]
[   ][   ][   ][   ]

[ Q ][ W ][ E ][ R ][ T ][ Y ][ U ][ I ][ O ][ P ]
   [ A ][ S ][ D ][ F ][ G ][ H ][ J ][ K ][ L ]
      [ Z ][ X ][ C ][ V ][ B ][ N ][ M ]

Enter a 4-letter guess:
```

Example full game with default settings below. Pretend the color feedback
is like the NYT one because on an ANSI console (Vs GitHub Markdown) it is:

```python
>>> from wrdl import Wrdl; Wrdl().play()
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]

[ Q ][ W ][ E ][ R ][ T ][ Y ][ U ][ I ][ O ][ P ]
   [ A ][ S ][ D ][ F ][ G ][ H ][ J ][ K ][ L ]
      [ Z ][ X ][ C ][ V ][ B ][ N ][ M ]

Enter a 5-letter guess: adieu

[ A ][ D ][ I ][ E ][ U ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]

[ Q ][ W ][ E ][ R ][ T ][ Y ][ U ][ I ][ O ][ P ]
   [ A ][ S ][ D ][ F ][ G ][ H ][ J ][ K ][ L ]
      [ Z ][ X ][ C ][ V ][ B ][ N ][ M ]

Enter a 5-letter guess: bleak

[ A ][ D ][ I ][ E ][ U ]
[ B ][ L ][ E ][ A ][ K ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]

[ Q ][ W ][ E ][ R ][ T ][ Y ][ U ][ I ][ O ][ P ]
   [ A ][ S ][ D ][ F ][ G ][ H ][ J ][ K ][ L ]
      [ Z ][ X ][ C ][ V ][ B ][ N ][ M ]

Enter a 5-letter guess: leach

[ A ][ D ][ I ][ E ][ U ]
[ B ][ L ][ E ][ A ][ K ]
[ L ][ E ][ A ][ C ][ H ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]

[ Q ][ W ][ E ][ R ][ T ][ Y ][ U ][ I ][ O ][ P ]
   [ A ][ S ][ D ][ F ][ G ][ H ][ J ][ K ][ L ]
      [ Z ][ X ][ C ][ V ][ B ][ N ][ M ]

Enter a 5-letter guess: gavel

[ A ][ D ][ I ][ E ][ U ]
[ B ][ L ][ E ][ A ][ K ]
[ L ][ E ][ A ][ C ][ H ]
[ G ][ A ][ V ][ E ][ L ]
[   ][   ][   ][   ][   ]
[   ][   ][   ][   ][   ]

[ Q ][ W ][ E ][ R ][ T ][ Y ][ U ][ I ][ O ][ P ]
   [ A ][ S ][ D ][ F ][ G ][ H ][ J ][ K ][ L ]
      [ Z ][ X ][ C ][ V ][ B ][ N ][ M ]

Enter a 5-letter guess: pales

[ A ][ D ][ I ][ E ][ U ]
[ B ][ L ][ E ][ A ][ K ]
[ L ][ E ][ A ][ C ][ H ]
[ G ][ A ][ V ][ E ][ L ]
[ P ][ A ][ L ][ E ][ S ]
[   ][   ][   ][   ][   ]

[ Q ][ W ][ E ][ R ][ T ][ Y ][ U ][ I ][ O ][ P ]
   [ A ][ S ][ D ][ F ][ G ][ H ][ J ][ K ][ L ]
      [ Z ][ X ][ C ][ V ][ B ][ N ][ M ]

Enter a 5-letter guess: false

[ A ][ D ][ I ][ E ][ U ]
[ B ][ L ][ E ][ A ][ K ]
[ L ][ E ][ A ][ C ][ H ]
[ G ][ A ][ V ][ E ][ L ]
[ P ][ A ][ L ][ E ][ S ]
[ F ][ A ][ L ][ S ][ E ]

[ Q ][ W ][ E ][ R ][ T ][ Y ][ U ][ I ][ O ][ P ]
   [ A ][ S ][ D ][ F ][ G ][ H ][ J ][ K ][ L ]
      [ Z ][ X ][ C ][ V ][ B ][ N ][ M ]

Phew...
```
