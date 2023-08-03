from PyPDF2 import PdfReader
from collections import Counter
import os
import pandas as pd
import pickle
from copy import deepcopy
import translators as ts
from threading import Thread
import enchant
from utils import Utils


class WordsExtractor:
    def __init__(self, path):
        self.files = os.listdir(path)
        self.path = path
        self.all_words = Counter()

    def __check_grammar(self):
        dictionary = enchant.Dict("en_US")
        for word in list(self.all_words.keys()):
            if dictionary.check(word) is False:
                self.all_words.pop(word)

    def __open_pdf(self, file):
        reader = PdfReader(os.path.join(self.path, file))
        text = ''
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            text += page.extract_text() + ' '
        self.text = text

    def __remove_no_letter(self):
        e = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' \
            'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ '
        text = list(self.text)
        for i, t in enumerate(text):
            if t in e:
                continue
            else:
                if text[i] == '-' and text[i + 1] == '\n':
                    del text[i + 1], text[i]
                else:
                    text[i] = ' '
        self.text = ''.join(text)

    def __remove_short_words(self):
        for c in list(self.all_words):
            if len(c) < 3:
                self.all_words.pop(c)

    def translate(self):
        import random
        your_proxy_pool = [{'http': '123.123'}, {'http': '456.456'}]
        all_words_translated = deepcopy(self.all_words)
        splitter = '; '
        string = splitter.join(all_words_translated.keys())
        i = 0
        sum = ''
        while i < len(string):
            stride = 4999
            if i + stride < len(string):
                temp = string[i:i + stride]
                a = temp.rfind(splitter)
                temp = string[i:i + a]
                i = i + a
            else:
                temp = string[i:]
                i = i + stride
            sum += ts.translate_text(temp, translator='google', from_language='en', to_language='ru',
                                    proxies=random.choice(your_proxy_pool))
            #sum += ts.translate_text(temp, translator='google', to_language='ru')
            #sum += ts.translate_text(temp, translator='deepl', from_language='en', to_language='ru')
            print('1')
        sum = sum.split(splitter)
        for i, v in enumerate(all_words_translated.keys()):
            all_words_translated[v] = sum[i]
        return all_words_translated

    @staticmethod
    def dicts_to_list(a, b):
        c = []
        for i in a.keys():
            c.append([i, a[i], b[i]])
        c = sorted(c, key=lambda x: x[2], reverse=True)
        return c

    def extract(self):
        for file in self.files:
            self.__open_pdf(file)
            self.__remove_no_letter()
            self.text = self.text.lower()
            self.all_words += Counter(self.text.split())
        self.__remove_short_words()
        self.__check_grammar()
        self.known_words = Utils.import_dict_from_excel('known_words')
        self.unknown_words = Utils.get_unknown_words(self.all_words, self.known_words)
        self.all_words_translated = self.translate()
        self.unknown_words_translated = Utils.get_unknown_words(self.all_words_translated, self.known_words)
        all_words = self.dicts_to_list(self.all_words_translated, self.all_words)
        unknown_words = self.dicts_to_list(self.unknown_words_translated, self.unknown_words)
        Utils.save_list_to_excel('all_words', all_words)
        Utils.save_list_to_excel('unknown_words', unknown_words)


WordsExtractor('pdf').extract()
