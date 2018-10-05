import os
import sys
import cv2
import numpy as np
import gc
import threading


# for windows
# import win32api


os.environ['KIVY_GL_BACKEND'] = 'sdl2'
from kivy.core.window import Window
from kivy import Config
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder, Parser, ParserException
from kivy.graphics.texture import Texture
import tkinter
import tkinter.filedialog

import src.detect_utils as det
import src.draw_utils as draw
from widgets.result_item import ResultItem

Config.read(os.path.expanduser('~/.kivy/config.ini'))
Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'resizeable', 0)
Builder.load_file('./Alpr.kv')
# APP_ROOT = os.path.dirname(__file__)


class AlprScreen(FloatLayout):
    image_path = ""
    top_plate = ""
    img = None

    def __init__(self, **kwargs):
        super(AlprScreen, self).__init__(**kwargs)
        self.result_list = ["asd"]

    def on_btn_open(self):
        tk = tkinter.Tk()
        tk.withdraw()
        select_file = (tkinter.filedialog.askopenfile(initialdir='.', title='select a image file'))
        if select_file is not None:
            self.image_path = select_file.name
            if os.path.splitext(self.image_path)[1].lower() in [".jpg", ".png"]:
                self.img = cv2.imread(self.image_path)
                tk.update()

        tk.destroy()
        self.ids.btn_recog.focus = True
        texture = self.__img2texture(cvimg=self.img, size=self.ids.img_show.size)
        self.ids.img_show.texture = texture

    def __img2texture(self, cvimg, size):
        buf = draw.frame2buf(cvimg=cvimg, size=size)
        texture = Texture.create(size=size)
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture

    #
    def on_btn_recog(self):
        results, cleared_plate = det.proc(plate_image=self.image_path)
        self.__show_result(results=results, cleared_plate=cleared_plate)

    #
    def on_btn_clear(self):
        self.ids.img_show.texture = None
        self.ids.img_crop.texture = None
        self.ids.img_binary.texture = None
        self.ids.img_gray.texture = None
        self.ids.result_box.clear_widgets()

    #
    def __show_result(self, results, cleared_plate):
        cv_img = self.img
        if results is None or len(results["results"]) == 0:
            sys.stdout.write("Can not find number plate!\n")
            self.ids.img_crop.texture = None
            self.ids.img_binary.texture = None
            self.ids.img_gray.texture = None
            self.ids.result_box.clear_widgets()
        else:
            top_plate = results['results'][0]

            plate_number = top_plate['plate']
            plate_confidence = top_plate['confidence']
            plate_coordinates = top_plate['coordinates']
            self.top_plate = "Plate Number: {}\t  Confidence: {}".format(plate_number, plate_confidence)

            proc_time = top_plate['processing_time_ms']
            candidates = top_plate['candidates']

            # gray image
            gray_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            gray_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

            # draw rectangle
            points = [[int(pt['x']), int(pt['y'])] for pt in plate_coordinates]
            contours = [np.array(points, dtype=np.int32)]
            cv2.drawContours(cv_img, contours, 0, (150, 255, 0), 2)

            # crop image
            min_pt = np.amin(contours, axis=1)[0]
            max_pt = np.amax(contours, axis=1)[0]
            crop_img = cv_img[min_pt[1]:max_pt[1], min_pt[0]:max_pt[0], :]

            # put text
            # cv2.putText(cv_img, plate_number + " : " + str(plate_confidence), (min_pt[0], min_pt[1]),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 255, 0), 1, cv2.LINE_AA)

            # binary image
            mask_img = np.zeros((cv_img.shape[0], cv_img.shape[1], 3), dtype=np.uint8)
            cv2.drawContours(mask_img, contours, -1, (255, 255, 255), -1)

            texture = self.__img2texture(cvimg=cv_img, size=self.ids.img_show.size)
            self.ids.img_show.texture = texture

            texture = self.__img2texture(cvimg=crop_img, size=self.ids.img_crop.size)
            self.ids.img_crop.texture = texture

            texture = self.__img2texture(cvimg=mask_img, size=self.ids.img_binary.size)
            self.ids.img_binary.texture = texture

            texture = self.__img2texture(cvimg=gray_img, size=self.ids.img_gray.size)
            self.ids.img_gray.texture = texture

            self.ids.result_box.clear_widgets()
            wid = ResultItem(sn="S/N", chracters="Recognized Characters", confidence="Precision/Confidence (%)",
                             recog_time="Recognition Time (ms)")
            self.ids.result_box.add_widget(wid)

            for i in range(len(candidates)):
                candi = candidates[i]
                candi_txt = " %3s \t\t %24s \t\t %24s \t\t %24s \n" % (i + 1, str(candi['plate']),
                                                                       str(candi['confidence']), str(proc_time))
                sys.stdout.write(candi_txt)

            if cleared_plate != "":
                candi = candidates[0]
                wid = ResultItem(sn=str(1), chracters=str(cleared_plate), confidence=str(candi['confidence']),
                                 recog_time=str(proc_time))
                self.ids.result_box.add_widget(wid)
                for i in range(4):
                    wid = ResultItem(sn=str(i+2), chracters="", confidence="", recog_time="")
                    self.ids.result_box.add_widget(wid)
            else:
                cv2.imshow("Cropped", cv2.resize(crop_img, (1000, 500)))
                key = cv2.waitKey(5)
                cv2.destroyAllWindows()
                for i in range(5):
                    wid = ResultItem(sn=str(i + 1), chracters="", confidence="", recog_time="")
                    self.ids.result_box.add_widget(wid)

    def btn_save(self, *args):
        if self.img is not None and self.top_plate != "":
            base = os.path.split(self.image_path)[0]
            txt_path = os.path.splitext(base)[0] + ".txt"
            with open(txt_path, 'w') as f:
                f.write(self.top_plate)


class AlprSysApp(App):
    title = "A Robust Automatic License Plate Recognition System"

    def build(self):
        return AlprScreen()


if __name__ == '__main__':
    AlprSysApp().run()
