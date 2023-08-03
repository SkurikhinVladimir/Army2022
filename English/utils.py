import pandas as pd
from copy import deepcopy
import os
import pickle


class Utils:
    @staticmethod
    def save_dict_to_excel(name, dict, sort=True):
        df = pd.DataFrame(data=dict, index=[0])
        df = df.T
        if sort is True:
            df = df.sort_values(by=df.columns[0], ascending=False)
        df.to_excel(os.path.join('his', '{}.xlsx'.format(name)), header=False)

    @staticmethod
    def save_list_to_excel(name, list):
        df = pd.DataFrame(data=list)
        df.to_excel(os.path.join('his', '{}.xlsx'.format(name)), header=False,index = False)

    @staticmethod
    def open_excel(name):
        return pd.read_excel(os.path.join('his', '{}.xlsx'.format(name)), index_col=None, header=None)

    @staticmethod
    def import_dict_from_excel(name):
        df = pd.read_excel(os.path.join('his', '{}.xlsx'.format(name)), index_col=None, header=None)
        return dict(zip(list(df[0]), list(df[1])))

    @staticmethod
    def get_unknown_words(all_words, known_words):
        counter = deepcopy(all_words)
        unknown_words = counter.keys() - known_words.keys()
        for word in list(counter.keys()):
            if word not in unknown_words:
                del counter[word]
        return counter

    @staticmethod
    def save_to_pickle(name, counter):
        with open(os.path.join('his', '{}.pickle'.format(name)), 'wb') as handle:
            pickle.dump(counter, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load_from_pickle(name):
        with open(os.path.join('his', '{}.pickle'.format(name)), 'rb') as handle:
            return pickle.load(handle)
