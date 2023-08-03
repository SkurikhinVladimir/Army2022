import os
import shutil
from datetime import datetime

###########################################################################################################################################
class dir_structure():
    """Родительский класс, задает структуру хранения файлов"""
    def __get_list_labels_images(self):
        """Удаляет из папок labels и images папки-исключения"""
        self.labels = self.rm_exceptions(os.listdir(self.lab_path))
        self.images = self.rm_exceptions(os.listdir(self.img_path))

    def __init_paths_and_dirs(self):
        """Создает требуемую структуру, создает переменные класса с именами папок"""
        self.cur_workdir = os.path.join(self.main_folder_path, self.path)
        self.lab_path = os.path.join(self.cur_workdir, 'labels')
        self.img_path = os.path.join(self.cur_workdir, 'images')
        self.trash_path = os.path.join(self.main_folder_path, 'trash', self.path)
        self.mkdir(self.img_path)
        self.mkdir(self.lab_path)
        self.mkdir(os.path.join(self.main_folder_path, 'trash'))
        self.mkdir(self.trash_path)

    def __init__(self, main_folder_path='soldier', path='0'):
        self.main_folder_path = main_folder_path
        self.path = path
        self.except_list = ['.ipynb_checkpoints', 'labels', 'images', 'trash']
        self.__init_paths_and_dirs()
        self.__get_list_labels_images()

    def rm_exceptions(self, orig_list):
        """Удаляет исключения из списка"""
        for e in self.except_list:
            if e in orig_list:
                orig_list.remove(e)
        return orig_list

    def mkdir(self, path):
        """Создает папку по пути"""
        try:
            os.mkdir(path)
        except:
            pass

    def get_name(self, label):
        """Возвращает имя файла с раширением и без"""
        return [label, label[:label.rfind('.')]]


###########################################################################################################################################

class change_labels(dir_structure):
    """Меняет метки в дирректории
    dengerous_change([1, 2], [3, 4]) - меняет в файлай разметки метки 1 на 2, 3 на 4
    del_labels(2,6,7,9) удалит метки из файлов разметки 2,6,7,9
    """
    
    def __get_label_list(self):
        """Считывает метки из файла"""
        self.label_list = []
        with open(self.lp, 'r') as lines:
            for line in lines:
                self.label_list.append(line.split())

    def __dengerous_change(self):
        """Проводит замену меток на заданные"""
        labels = []
        for label in self.label_list:
            for i, j in self.label_pairs:
                if int(label[0]) == i:
                    label[0] = str(j)
                    break
            labels.append((' ').join(label))
        self.label_list = labels

    def __remove_labels(self):
        """Удаляет заданные метки"""
        labels = []
        for label in self.label_list:
            if label[0] not in self.rm_labels:
                labels.append((' ').join(label))
        self.label_list = labels

    def __write_labels(self):
        """Записывает метки в файл разметки"""
        with open(self.lp, 'w') as f:
            for line in self.label_list:
                f.write(line + '\n')

    def dengerous_change(self, *label_pairs):
        """Заменяет метки на заданные в указанной дирректории"""
        self.label_pairs = list(label_pairs)
        for label in self.labels:
            self.lp = os.path.join(self.lab_path, label)
            self.__get_label_list()
            self.__dengerous_change()
            self.__write_labels()

    def del_labels(self, *rm_labels):
        """Удаляет заданные метки в указанной дирректории"""
        self.rm_labels = [str(i) for i in rm_labels]
        for label in self.labels:
            self.lp = os.path.join(self.lab_path, label)
            self.__get_label_list()
            self.__remove_labels()
            self.__write_labels()


###########################################################################################################################################

class potom(dir_structure):
    """Класс предназначен для предобработки набора данных
    preprocessig() - создает типовую структуру дирректорий, переносит непарные файлы в папку trash
    удаляет пустые файлы разметки, создает уникальные имена файлов. 
    preprocessig_no_ren() тоже, что и preprocessig() только не переименновывает
    """
    def __init__(self, main_folder_path='soldier', path='0'):
        super().__init__(main_folder_path, path)

    def __check_dataset(self):
        """ Проверяет наличие изображений и разметки в папке
        """
        labels = dict(map(self.get_name, self.labels))
        images = dict(map(self.get_name, self.images))
        temp = set([i for i in images.values() if list(images.values()).count(i) > 1])
        dif = []
        for k, v in list(images.items()):
            if v in temp:
                dif.append(k)
                images.pop(k)
        labels = {v: k for k, v in labels.items()}
        images = {v: k for k, v in images.items()}
        sym_dif = set(labels.keys()).symmetric_difference(set(images.keys()))
        union = {**labels, **images}  # python 3.9 -
        # union = labels|images python 3.9+
        for i in sym_dif:
            dif.append(union[i])
        return dif

    def __mkdirs_img_lab(self):
        """Создает папки images и labels, перемещает в них изображения и
        разметку из папки path
        """
        files = os.listdir(self.cur_workdir)
        files = self.rm_exceptions(files)
        for file in files:
            if not file.endswith('.txt'):
                shutil.move(os.path.join(self.cur_workdir, file), os.path.join(self.img_path, file))
            else:
                shutil.move(os.path.join(self.cur_workdir, file), os.path.join(self.lab_path, file))
        self._dir_structure__get_list_labels_images()

    def __clear_txt(self):
        """Удаляет лишние файлы и пустые txt из папки labels"""
        count = 0
        for label in self.labels:
            if not label.endswith('.txt'):
                print('В папке с разметкой был посторонний файл ', label)
                os.remove(os.path.join(self.lab_path, label))
            if (os.path.getsize(os.path.join(self.lab_path, label)) == 0):
                os.remove(os.path.join(self.lab_path, label))
                count += 1
        if count > 0:
            print('Удалено {} пустых файлов, осталось файлов разметки - {}'.format(count, len(self.labels) - count))
        self._dir_structure__get_list_labels_images()

    def __move_to_trash(self):
        """ Переносит непарные файлы из дирректорий labels и images
        в trash
        """
        diff = self.__check_dataset()
        for d in diff:
            if d.endswith('.txt'):
                shutil.move(os.path.join(self.lab_path, d), os.path.join(self.trash_path, d))
            else:
                shutil.move(os.path.join(self.img_path, d), os.path.join(self.trash_path, d))
        if len(diff) > 0:
            print('В папку {} перемещенно {} файлов'.format(self.trash_path, len(diff)))
        self._dir_structure__get_list_labels_images()

    def __rename_all(self):
        """ Переименовывает файлы в дирректориях images и labels в формат:
        curdir_datetimenow_i.* для любых расширений фото
        curdir_datetimenow_i.txt для разметки
        """
        for i, image in enumerate(self.images):
            ext = image[image.rfind('.'):]
            now = datetime.now().strftime('%d%m%y%H%M%S')
            name = '{}_{}_{}'.format(self.path, now, i)
            os.rename(os.path.join(self.img_path, image), os.path.join(self.img_path, name + ext))
            os.rename(os.path.join(self.lab_path, image[:image.rfind('.')] + '.txt'),
                      os.path.join(self.lab_path, name + '.txt'))
        # print('Переименовано {} файлов.'.format(i+1))
        self._dir_structure__get_list_labels_images()

    def preprocessig(self):
        self.__mkdirs_img_lab()
        self.__clear_txt()
        self.__move_to_trash()
        self.__rename_all()

    def preprocessig_no_ren(self):
        self.__mkdirs_img_lab()
        self.__clear_txt()
        self.__move_to_trash()


############################################################################################################################################
class posle_potom_0(dir_structure):
    """Применяет скрипты ко всем папкам в наборе данных
       preprocessig() - создает типовую структуру дирректорий, переносит непарные файлы в папку trash
    удаляет пустые файлы разметки, создает уникальные имена файлов. 
       preprocessig_no_ren() тоже, что и preprocessig() только не переименновывает
       dengerous_change([1, 2], [3, 4]) - меняет в файлай разметки метки 1 на 2, 3 на 4
       del_labels(2,6,7,9) удалит метки из файлов разметки 2,6,7,9
       """
    def __init__(self, main_folder_path):
        self.main_folder_path = main_folder_path
        self.except_list = ['.ipynb_checkpoints', 'labels', 'images', 'trash']
        self.folders = self.rm_exceptions(os.listdir(main_folder_path))

    def preprocessig_no_ren(self):
        count = 0
        for folder in self.folders:
            count += 1
            new = potom(self.main_folder_path, folder).preprocessig_no_ren()
        print('Предобработка {} папок с сохранением имен файлов закончена'.format(count))

    def preprocessig(self):
        count = 0
        for folder in self.folders:
            count += 1
            new = potom(self.main_folder_path, folder).preprocessig()
        print('Предобработка {} папок с изменением имен файлов закончена'.format(count))

    def del_labels(self, *rm_labels):
        count = 0
        for folder in self.folders:
            count += 1
            new = change_labels(self.main_folder_path, folder).del_labels(*rm_labels)
        print('Удаление меток в {} папках закончено'.format(count))

    def dengerous_change(self, *label_pairs):
        count = 0
        for folder in self.folders:
            count += 1
            new = change_labels(self.main_folder_path, folder).dengerous_change(*label_pairs)
        print('Изменение меток в {} папках закончено'.format(count))


###########################################################################################################################################
def show_amount(main_folder_path='drones_and_birds'):
    """ Показывает имена паппок и количество изображений в папке
    (не проверяет соответствие labels и images)
    """
    count = 0
    exceptions = ['.ipynb_checkpoints', 'trash']
    folders = os.listdir(main_folder_path)
    for e in exceptions:
        if e in folders:
            folders.remove(e)
    for folder in folders:
        images_path = os.path.join(main_folder_path, folder, 'images')
        amount = len(os.listdir(images_path))
        count += amount
        # print('В папке {} {} изображений'.format(folder,amount))
    print('Всего изображений - {}'.format(count))
