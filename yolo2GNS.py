import json
import cv2
import os


def yolo_to_rectangle(image_width, image_height, x, y, w, h):
    # Преобразование координат центра объекта в координаты левого верхнего угла
    x1 = int((x - w/2) * image_width)
    y1 = int((y - h/2) * image_height)

    # Вычисление координат правого нижнего угла прямоугольника
    x2 = x1 + int(w * image_width)
    y2 = y1 + int(h * image_height)

    # # Вычисление координат правого нижнего угла прямоугольника
    # x2 = x1 + int(w * image_width)
    # y2 = y1 + int(h * image_height)
    # Возвращаем координаты двух углов и размер прямоугольника
    return (x1, y1, x2, y2)

def get_image_size(path_to_image):
    img = cv2.imread(path_to_image)
    # получаем размеры изображения
    height, width, _ = img.shape
    return height, width

def yolo_to_cxywh(path_to_txt):
    with open(path_to_txt) as f:
        cxywh = list(map(lambda line: [float(x) for x in line.split()],f.readlines()))
    return cxywh

def get_annotation(file):
    annotation = []
    clases = []
    path_to_txt = file.rsplit(".", 1)[0]+'.txt'
    image_height, image_width = get_image_size(file)
    cxywh = yolo_to_cxywh(path_to_txt)
    for det in cxywh:
        c, x, y, w, h = det
        clases.append(int(c))
        annotation.append(yolo_to_rectangle(image_width, image_height, x, y, w, h))
    return annotation, clases

def transform_annotation_to_GNS(annotation,clases):
    gns_annotation= []
    for a,c in zip(annotation,clases):
        head = {
            "description": "ObjectDetection",
            "class": "",
            "shape": {
                "type": "rectangle",
                "exterior": [],
                "interior": []
            }
        }
        head["class"] = str(c)
        head["shape"]["exterior"] = [[a[0], a[1]], [a[2], a[3]]]
        gns_annotation.append(head)
    return gns_annotation

def read_classes(path_to_classes):
    with open(path_to_classes) as f:
        lines = f.read()
        return dict(enumerate(lines.split()))

def save_gns_json(annotation,path_to_gns,file):
    path_to_json = os.path.join(path_to_gns,file.rsplit(".", 1)[0] + '.json')
    head = {
        "version": 1,
        "image": {
            "representation": "",
            "value": ""
        },
        "annotation": []
    }
    head["annotation"] = annotation
    with open(path_to_json, "w") as f:
        json.dump(head, f, indent=4)


def main():
    path_to_yolo = 'yolo'
    path_to_save_gns = 'gns'
    path_to_classes = 'classes.txt'
    if not os.path.exists(path_to_save_gns): os.makedirs(path_to_save_gns)
    classes_dict = read_classes(path_to_classes)
    for filename in os.listdir(path_to_yolo):
        if not filename.endswith('.txt'):
            file_path = os.path.join(path_to_yolo, filename)
            annotation,classes = get_annotation(file_path)
            classes = [classes_dict[c] for c in classes]
            annotation = transform_annotation_to_GNS(annotation,classes)
            save_gns_json(annotation,path_to_save_gns,filename)

if __name__ == "__main__":
    main()


