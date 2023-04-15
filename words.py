import words_lib

ws = words_lib.WordSearcher()
ws.load_words('wordlist.txt')

letters = input('Enter letters: ')
mask = input('Enter mask: ')
res_words = ws.gen_matching_words(letters, mask)

print('Possible words: ')
for word in res_words:
    print(word)

input('Press Enter to close.')
