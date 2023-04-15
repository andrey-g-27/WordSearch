import locale
import itertools

class WordSearcher:
    def __init__(self):
        self._words = set()
    
    def load_words(self, filename):
        self._words = set()
        with open(filename, 'rt') as file:
            for line in file:
                parts = line.split(None, 1)
                if (len(parts) > 0):
                    word = parts[0]
                    self._words.add(word)
    
    def gen_matching_words(self, letters, mask):
        gen_words = itertools.permutations(letters, len(mask))
        cand_words = set()
        for gen_word in gen_words:
            gen_word_str = ''.join(gen_word)
            cur_word_ok = True
            for idx, char in enumerate(mask):
                if (char == '*'):
                    continue
                if (char != gen_word_str[idx]):
                    cur_word_ok = False
                    break
            if (cur_word_ok):
                cand_words.add(gen_word_str)
        res_words = list(self._words & cand_words)
        res_words.sort(key = locale.strxfrm)
        return res_words
