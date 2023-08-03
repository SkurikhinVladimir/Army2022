import cv2
import yaml
import os
import numpy as np


class FramePostprocessing:
    def __init__(self, filename='config.yaml'):
        with open(filename, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        self.__names = config['names']
        self.__path_to_detections_file = config['path_to_detections_file']
        self.__path_to_image_file = config['path_to_image_file']
        self.__image_size = tuple(config['image_size'])
        self.__hide_labels = config['hide_labels']
        self.__hide_conf = config['hide_conf']
        self.__line_thickness = config['line_thickness']
        self.__path_to_save_frames = config['path_to_save_frames']
        self.__path_to_save_videos = config['path_to_save_videos']
        self.__fps = config['result_fps']
        self.__save_annotated_image_used = False
        if not os.path.isdir(self.__path_to_save_videos): os.makedirs(self.__path_to_save_videos)
        if not os.path.isdir(self.__path_to_save_frames): os.makedirs(self.__path_to_save_frames)

    @staticmethod
    def __get_filename(path_to_save):
        names = os.listdir(path_to_save)
        names = ['.'.join(name.split('.')[:-1]) if len(name.split('.')) > 1 else name for name in names]
        if len(names) > 0:
            names = [int(name) for name in names if name.isdigit()]
            return str(max(names) + 1)
        else:
            return '1'

    @staticmethod
    def __read_detections_from_txt(path_to_detections_file):
        with open(path_to_detections_file, 'r') as f:
            lines = f.readlines()
        return [line.split() for line in lines]

    @staticmethod
    def __read_image(path_to_image_file, size=(1920, 1088)):
        img = cv2.imread(path_to_image_file)
        return cv2.resize(img, size)

    def __annotate_frame(self, img, detections):
        annotator = Annotator(img, line_width=self.__line_thickness, example=str(self.__names))
        for det in detections:
            x1, y1, w, h = [round(float(i), 2) for i in det[1:5]]
            x2, y2 = x1 + w, y1 + h
            c = int(det[0])
            conf = float(det[5])
            label = None if self.__hide_labels else (self.__names[c] if self.__hide_conf
                                                     else f'{self.__names[c]} {conf:.2f}')
            annotator.box_label([x1, y1, x2, y2], label, color=colors(c, True))
        return annotator.result()

    def __chek_save_annotated_image_used(self):
        if self.__save_annotated_image_used == False:
            name = self.__get_filename(self.__path_to_save_frames)
            self.__path_to_save_frames = os.path.join(self.__path_to_save_frames, name)
            os.makedirs(self.__path_to_save_frames)
            self.__save_annotated_image_used = True

    def save_annotated_image(self):
        self.__chek_save_annotated_image_used()
        img = self.__read_image(self.__path_to_image_file)
        detections = self.__read_detections_from_txt(self.__path_to_detections_file)
        new_name = self.__get_filename(self.__path_to_save_frames) + '.jpeg'
        an_img = self.__annotate_frame(img, detections)
        filename = os.path.join(self.__path_to_save_frames, new_name)
        cv2.imwrite(filename, an_img, [cv2.IMWRITE_JPEG_QUALITY, 100])

    def make_video(self):
        if self.__save_annotated_image_used == False:
            name = str(int(self.__get_filename(self.__path_to_save_frames)) - 1)
            self.__path_to_save_frames = os.path.join(self.__path_to_save_frames, name)
        new_name = self.__get_filename(self.__path_to_save_videos) + '.mp4'
        output_file = os.path.join(self.__path_to_save_videos, new_name)
        filenames = [filename for filename in os.listdir(self.__path_to_save_frames) if filename.endswith('.jpeg')]
        filenames = sorted(filenames, key=lambda x: int(x.split('.jpeg')[0]))
        frames = []
        for filename in filenames:
            frames.append(os.path.join(self.__path_to_save_frames, filename))
        frame = cv2.imread(frames[0])
        height, width, channels = frame.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, self.__fps, (width, height))
        for frame in frames:
            img = cv2.imread(frame)
            out.write(img)
        out.release()


class Colors:
    def __init__(self):
        hex = ('FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
               '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')
        self.palette = [self.hex2rgb('#' + c) for c in hex]
        self.n = len(self.palette)

    def __call__(self, i, bgr=False):
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):  # rgb order (PIL)
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))


class Annotator:

    # YOLOv5 Annotator for train/val mosaics and jpgs and detect/hub inference annotations
    def __init__(self, im, line_width=None, font_size=None, font='Arial.ttf', pil=False, example='abc'):
        assert im.data.contiguous, 'Image not contiguous. Apply np.ascontiguousarray(im) to Annotator() input images.'
        self.im = im
        self.lw = line_width or max(round(sum(im.shape) / 2 * 0.003), 2)  # line width

    def box_label(self, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
        p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
        cv2.rectangle(self.im, p1, p2, color, thickness=self.lw, lineType=cv2.LINE_AA)
        if label:
            tf = max(self.lw - 1, 1)  # font thickness
            w, h = cv2.getTextSize(label, 0, fontScale=self.lw / 3, thickness=tf)[0]  # text width, height
            outside = p1[1] - h - 3 >= 0  # label fits outside box
            p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
            cv2.rectangle(self.im, p1, p2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(self.im, label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2), 0, self.lw / 3, txt_color,
                        thickness=tf, lineType=cv2.LINE_AA)

    def result(self):
        # Return annotated image as array
        return np.asarray(self.im)


colors = Colors()

