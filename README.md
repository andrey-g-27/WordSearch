# WordSearch
Simple word search python script with text/curses interface.

Was created for a parent to help with a game.

Inputs:
* Set of letters (repeats allowed) the desired word consists of.
* Mask for the word to match (`*` matches any letter).
* Set of words to search in.

Outputs:
* List of words consisting of letters in the specified set and matching the mask.

## Files
* `words_lib.py` - library with a class for loading a list of words from a file and searching in it.
* `words.py` - simple console program using the library. Exits after one query.
* `words_textui.py` - ncurses-based interface for the library. Allows editing the query.

## Custom files
Should be added by user.
* `wordlist.txt` - contains a list of words to search in (one word per line, should include all desired wordforms). For Russian language this one was used: https://github.com/danakt/russian-words/blob/master/russian.txt.
