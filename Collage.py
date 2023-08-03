import random

from PIL import Image
import os

# определяем папку, в которой находятся фотографии
path_to_images = 'images'
path_to_labels = 'labels'
save_dir = 'output'
os.makedirs(save_dir,exist_ok=True)


def gen_params():
    size = 2**random.randint(6,10)
    img_width, img_height = size,size
    num_rows = int(1024/size)
    num_cols = int(1024/size)
    return num_rows, num_cols, img_width, img_height
# определяем количество рядов и колонок в коллаже
num_rows = 4
num_cols = 4

# определяем ширину и высоту каждого изображения
img_width = 256
img_height = 256

collage_width = img_width*num_cols
collage_height = img_height*num_rows
# создаем пустой холст для коллажа
collage = Image.new('RGB', (num_cols * img_width, num_rows * img_height), (255, 255, 255))

def read_label(image_name,path_to_labels):
    label_name = image_name.rsplit('.', 1)[0]+'.txt'
    with open(os.path.join(path_to_labels,label_name),'r') as f:
        lines = f.readlines()
    lines = [list(map(float,l.split())) for l in lines]
    return lines

def calculate_labels(x,y,collage_width,collage_height, img_width, img_height,labels):
    l = []
    for label in labels:
        new_x = round((x + img_width * label[1])/collage_width,6)
        new_y = round((y + img_height * label[2])/collage_height,6)
        new_w = round((img_width * label[3])/collage_width,6)
        new_h = round((img_height * label[4])/collage_height,6)
        l.append([int(label[0]),new_x,new_y,new_w,new_h])
    return l

def save_collage(name,result,collage,save_dir = 'output'):
    collage.save(os.path.join(save_dir,(f"collage{name}.jpg")))
    with open(os.path.join(save_dir,f"collage{name}.txt"),'w') as f:
        for row in result:
            line = " ".join(str(x) for x in row)
            f.write(line + "\n")

# перебираем все файлы в папке, ищем только изображения
result = []
i,j = 0,0
for filename in os.listdir(path_to_images):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        # загружаем изображение и изменяем размер до заданных ширины и высоты
        img = Image.open(os.path.join(path_to_images, filename))
        img = img.resize((img_width, img_height))
        # определяем координаты для размещения изображения на холсте
        row = (i // num_cols)%num_rows
        col = i % num_cols
        x = col * img_width
        y = row * img_height
        labels = read_label(filename,path_to_labels)
        result += calculate_labels(x,y,collage_width,collage_height, img_width, img_height,labels)
        # добавляем изображение на холст
        collage.paste(img, (x, y))

        # выходим из цикла, если коллаж содержит нужное количество фотографий
        if (i + 1) % (num_rows * num_cols) == 0:
            save_collage(j, result,collage, save_dir)
            print("Коллаж сохранен!")
            j += 1
            result = []
            collage = Image.new('RGB', (num_cols * img_width, num_rows * img_height), (255, 255, 255))
            num_rows, num_cols, img_width, img_height = gen_params()
            print(num_rows, num_cols, img_width, img_height)
            i = 0
            continue
        i += 1
save_collage(j, result,collage, save_dir)

# сохраняем коллаж в файл
# save_collage('1',result,save_dir)
# print("Коллаж сохранен!")