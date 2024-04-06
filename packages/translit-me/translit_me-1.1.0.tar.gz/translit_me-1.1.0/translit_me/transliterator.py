class CharTrie:

    def __init__(self):
        self.common = ""  # common part of the tree reduced to a string
        self.trie = []  # list of deviations (also CharTries)

    def add(self, s: str):
        """
        Add string, will be added to all variants
        :param s: string to add to current Trie
        :return: nothing
        """
        if len(self.trie) == 0:
            self.common += s
        else:
            for t in self.trie:
                t.add(s)

    def split(self, strings: list):
        """
        Split trie by multiple options
        :param strings: list of strings to be used to create the split
        :return: nothing
        """
        if len(self.trie) == 0:  # no sub-tries yet
            for s in strings:
                c = CharTrie()
                c.add(s)
                self.trie.append(c)
        else:
            t: CharTrie
            for t in self.trie:
                t.split(strings)

    def get_all(self):
        """
        Traverses the trie and returns all words that cover a path from the root to the leaves
        :return: list of words
        """
        if len(self.trie) == 0:  # Leaf node
            return [self.common]

        else:
            res = []
            t: CharTrie
            for t in self.trie:
                name: str
                for name in t.get_all():
                    res.append(self.common + name)
            return res


def transliterate(source_list, table: dict):
    """
    Transliterates names using a supplied transliteration table.
    :param source_list: list of names to transliterate
    :param table: conversion table as dictionary where each character in
                  each name of source_list has a corresponding entry
    :return: list of transliterated names in the same order
    """

    # print("[INFO] received: {}".format(source_list))
    res = []
    for name in source_list:
        word_arrays = []
        for word in name.split():
            word_arrays.append(transliterate_word(word, table))

        if len(word_arrays) == 1:
            res += word_arrays[0]
        else:
            for word in word_arrays[0]:
                res += recursive_word_assembler(word, word_arrays[1:])

    return res


def recursive_word_assembler(current_word, remaining_arrays):
    res = []
    arr = []
    if len(remaining_arrays) == 1:
        arr = remaining_arrays[0]
    else:
        for word in remaining_arrays[0]:
            arr += recursive_word_assembler(word, remaining_arrays[1:])

    for word in arr:
        res.append(current_word + " " + word)

    return res


def transliterate_word(name: str, table):
    new_name_trie = CharTrie()
    skip = 0
    for i in range(len(name)):  # ToDo split words on spaces
        if skip > 0:  # need to skip one or more characters due to character combinations
            skip -= 1
            continue
        if name[i: i + 4] in table.keys() and i + 3 < len(name):
            to_add = table[name[i: i + 4]]
            if callable(to_add):  # resolved by a function
                to_add = table[name[i:i+4]](name, i)
            if type(to_add) is list:
                new_name_trie.split(to_add)
            else:
                new_name_trie.add(to_add)
            # if callable(to_add): # resolved by a function
            skip = 3
        elif name[i: i + 3] in table.keys() and i + 2 < len(name):
            to_add = table[name[i: i + 3]]
            if callable(to_add):  # resolved by a function
                to_add = table[name[i:i+3]](name, i)
            if type(to_add) is list:
                new_name_trie.split(to_add)
            else:
                new_name_trie.add(to_add)
            # if callable(to_add): # resolved by a function
            skip = 2
        elif name[i: i + 2] in table.keys() and i + 1 < len(name):
            to_add = table[name[i: i + 2]]
            if callable(to_add):  # resolved by a function
                to_add = table[name[i:i+2]](name, i)
            if type(to_add) is list:
                new_name_trie.split(to_add)
            else:
                new_name_trie.add(to_add)
            skip = 1
        elif name[i] in table.keys():
            to_add = table[name[i]]
            if callable(to_add):  # resolved by a function
                to_add = table[name[i]](name, i)
            if type(to_add) is list:
                new_name_trie.split(to_add)
            else:
                new_name_trie.add(to_add)
            skip = 0
        else:
            # Assign  name[i] into a new string as a unicode string and send error message
            try:
                print("[WARN] {} not found in language table for {}".format(name[i], name))
            except UnicodeEncodeError:
                print("[WARN] {} not found in language table for {}".format(name[i].encode('utf-8'), name.encode('utf-8')))
            skip = 0
    words = []
    for nn in new_name_trie.get_all():
        words.append(nn)
    return words


def remove_vowels(in_name: str, table):
    res = []
    for word in in_name.split(' '):  # split words on spaces
        new_word = ""
        skip = 0
        for i in range(len(word)):
            if skip > 0:  # need to skip one or more characters due to character combinations
                skip -= 1
                continue
            if word[i: i + 3] in table.keys() and i + 2 < len(word):
                to_remove = table[word[i: i + 3]]
                if not to_remove:
                    new_word += word[i: i + 3]
                # if callable(to_remove): # resolved by a function
                skip = 2
            elif word[i: i + 2] in table.keys() and i + 1 < len(word):
                to_remove = table[word[i: i + 2]]
                if not to_remove:
                    new_word += word[i: i + 2]
                skip = 1
            elif word[i] in table.keys():
                to_remove = table[word[i]]
                if callable(to_remove):  # resolved by a function
                    to_remove = table[word[i]](word, i)
                    if not to_remove:
                        new_word += word[i]
            else:
                new_word += word[i]  # print("[WARN] {} not found in language table for {}".format(word[i], word))
                skip = 0
        res.append(new_word)
    return " ".join(res)
