from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,
                             QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
                             QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
                             QVBoxLayout, QProgressBar, QMessageBox)

from PyQt5.QtCore import *

import pandas as pd
import random
from functools import partial
import PyQt5_stylesheets
from copy import deepcopy
import os
from utils import Utils


class Dialog(QDialog):
    def __init__(self):
        super(Dialog, self).__init__()
        self.setStyleSheet(PyQt5_stylesheets.load_stylesheet_pyqt5(style="style_DarkOrange"))
        self.init_Grid_size()
        self.createLabelBox()
        self.createGridGroupBox()
        self.createProgressBarBox()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.gridGroupBox)
        main_layout.addWidget(self.ProgressBarBox)
        self.setLayout(main_layout)
        self.setWindowTitle("English")

        self.number_of_words_to_study = 20
        self.init_new_part_words_to_learn()

    def init_new_part_words_to_learn(self):
        self.progress.setValue(0)
        self.__get_all_unknown_word_dict()
        self.__get_word_dict()
        self.__fill_in_the_buttons()

    def init_Grid_size(self, x=2, y=5):
        self.NumGridRows = x
        self.NumGridCols = y

    def createGridGroupBox(self):
        self.gridGroupBox = QGroupBox()
        layout = QGridLayout()
        self.buttons = []
        for i in range(self.NumGridCols):
            for j in range(self.NumGridRows):
                self.buttons.append(self.make_button())
                layout.addWidget(self.buttons[len(self.buttons) - 1], i, j)
        self.gridGroupBox.setLayout(layout)

    def createLabelBox(self):
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignHCenter)
        self.formGroupBox = QGroupBox()
        layout = QFormLayout()
        layout.addRow(self.label)
        self.formGroupBox.setLayout(layout)

        # layout = QGridLayout()
        # self.ok_button = self.make_button()
        # self.ok_button1 = self.make_button()
        # layout.addWidget(self.label,0,0,0,6)
        # layout.addWidget(self.ok_button,0,6)
        # layout.addWidget(self.ok_button1,0,8)
        # self.formGroupBox.setLayout(layout)

    def createProgressBarBox(self):
        self.progress = QProgressBar()
        self.ProgressBarBox = QGroupBox()
        layout = QFormLayout()
        layout.addRow(self.progress)
        self.progress.setStyleSheet('text-align: center;')
        self.ProgressBarBox.setLayout(layout)

    def show_end_box(self):
        end_box = QMessageBox.question(self, 'MessageBox', "Сохранить изученные слова?",
                                       QMessageBox.Yes | QMessageBox.No)
        if end_box == QMessageBox.Yes:
            self.__save_words()
            self.init_new_part_words_to_learn()
        if end_box == QMessageBox.No:
            self.init_new_part_words_to_learn()

    def make_button(self):
        qbtn = QPushButton('Quit', self)
        qbtn.clicked.connect(partial(self.__on_click, qbtn))
        return qbtn

    #####################################################################################
    def __on_click(self, qbtn):
        if len(self.word_dict.keys()) > 0:
            if qbtn == self.right_button:
                self.word_dict.pop(self.current_word)
                self.progress.setValue(100 - round(len(self.word_dict.keys()) / self.len_word_dict * 100))
                if len(self.word_dict.keys()) > 0:
                    self.__fill_in_the_buttons()
                else:
                    self.show_end_box()
            else:
                self.word_dict.pop(self.current_word)
                self.word_dict.update({self.current_word: self.current_word_translation})
                self.__fill_in_the_buttons()

    def __get_all_unknown_word_dict(self):
        df = pd.read_excel(os.path.join('his', 'unknown_words.xlsx'), index_col=None, header=None)
        df1 = pd.read_excel(os.path.join('his', 'known_words.xlsx'), index_col=None, header=None)
        unknown_words = dict(zip(list(df[0]), list(df[1])))
        self.known_words = dict(zip(list(df1[0]), list(df1[1])))
        self.unknown_words = Utils.get_unknown_words(unknown_words,self.known_words)

    def __get_word_dict(self):
        self.word_dict = dict(list(self.unknown_words.items())[:self.number_of_words_to_study])
        self.learned_words = deepcopy(self.word_dict)
        d = {v: k for k, v in self.word_dict.items()}
        self.word_dict.update(d)
        self.len_word_dict = len(self.word_dict)

    def __fill_in_the_buttons(self):
        self.current_word = list(self.word_dict.keys())[0]
        self.current_word_translation = self.word_dict[self.current_word]
        if self.current_word[0] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            unknown_words = random.sample(list(self.unknown_words.values()), len(self.buttons) - 1)
        else:
            unknown_words = random.sample(list(self.unknown_words.keys()), len(self.buttons) - 1)
        unknown_words.append(self.current_word_translation)
        random.shuffle(unknown_words)

        self.label.setText(self.current_word)
        for button, word in zip(self.buttons, unknown_words):
            button.setText(word)
            if word == self.current_word_translation:
                self.right_button = button

    def __save_words(self):
        known_words = deepcopy(self.known_words)
        known_words.update(self.learned_words)
        Utils.save_dict_to_excel('known_words',known_words)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    dialog = Dialog()
    sys.exit(dialog.exec_())
