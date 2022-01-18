"""
    Осуществляет управление камерой в соответствии с расписанием.
    Задача системы:
    * Включаться по расписанию, например каждые 15 минут.
    * Получать изображения с камеры
    * Если уровень освещенности ниже порогового значения, то кадр отбрасывается (ночь)
    * Кадры сохраняются на диск
    * Если количество новых кадров достигло заданного количества,
      необходимо сохранить их на диске и добавить в конец видео.

    Система реализована в виде класса.

"""


import os
from datetime import datetime
import threading
import time
from os import listdir
import threading

import cv2
from loguru import logger

from timemgr import Timer 


class CameraController:
    def __init__(self, delay=15, light_level=60, buffer_size=50):
        """
            Осуществляет все операции с изображениями.
        :param delay: время между кадрами
        :param light_level: Пороговый уровень освещенности
        :param buffer_size: Количество кадров перед обновлением архива и видео
        """

        self.n_frames = 0
        self.delay_between_frames = delay
        self.light_level = min(100, max(0, light_level)) / 100
        self.buffer_size = buffer_size
        self.filenames = ''
        self.update_filenames()
        self.timer = Timer(delay)
        self.last_frame_time = ""

        self.cap = cv2.VideoCapture(0)
        while self.cap is None:
            logger.error("Fail connecting to camera!")
            time.sleep(1)
            self.cap = cv2.VideoCapture(0)

        self.cap.set(3, 1280.0)
        self.cap.set(4, 720.0)
        time.sleep(2)

        self.cap.set(cv2.CAP_PROP_EXPOSURE, -150)  


    def __str__(self):
        return f"CameraController with:\n\t{self.delay_between_frames}\n\t{self.light_level}\n\t"\
               f"{self.buffer_size}\n\t{len(self.n_frames)} frames in buffer\n"

    def get_last_frame(self):
        return self.last_frame_time

    def update_filenames(self):
        """ Обновляет список имен сохраненных картинок. """
        self.filenames = sorted([f for f in listdir("static/data/imgs") if '.jpg' in f])

    def get_filenames(self):
        """ Возвращает список имен сохраненных картинок. """
        return self.filenames

    @logger.catch
    def get_light_level(self, frame):
        """ Возвращает процент освещенности изображения. """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        w, h = gray.shape
        n = cv2.countNonZero(thresh)
        return n / (w*h)

    @logger.catch
    def make_frame(self):
        """ Создает кадр, считывает кадр с камеры. """
        for i in range(10):
            ret, frame = self.cap.read()
            if ret:
                return frame
            time.sleep(1)

        logger.error("Can't make frame!")
        return False

    @logger.catch
    def get_filename(self):
        """ Возвращает имя файла в соответствии с текущим временем. """
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d_%H:%M:%S")
        self.last_frame_time = dt_string
        result = "img_" + dt_string + ".jpg"
        return result

    @logger.catch
    def rebuild_video(self):
        """ добавление кадров в видео. """
        os.system("rm static/data/video.webm; cat static/data/imgs/*.jpg | ffmpeg -framerate 25 -f image2pipe -i - -c:v libvpx-vp9 -pix_fmt yuva420p static/data/video.webm &")

    @logger.catch
    def rebuild_zip(self):
        """ сохранение кадров в архив. """
        os.system("zip -rj static/data/images.zip static/data/imgs/ &")

    @logger.catch
    def mainloop(self):
        """
            Главный цикл.
            Реализует работу по расписанию, связывает весь функционал
        """

        logger.info("Start mainloop")
        while True:
            if self.timer.is_time():
                self.timer.update()
                # Создать новый кадр
                frame = self.make_frame()
                if type(frame) != bool:
                    if self.get_light_level(frame) >= self.light_level:
                        logger.info("Make frame")
                        self.n_frames += 1
                        cv2.imwrite("static/data/imgs/" + self.get_filename(), frame)
                        self.update_filenames()
                        self.last_frame_time += ", состояние: день"
                    else: 
                        if not "ночь" in self.last_frame_time:
                            self.last_frame_time += ", состояние: ночь"

                if self.n_frames >= self.buffer_size:
                    logger.info("Rebuild archive and video")
                    self.rebuild_zip()
                    self.rebuild_video()
                    self.n_frames = 0
                
            time.sleep(60)


@logger.catch
def start():
    """ Запускает CameraController в отдельном потоке. """
    cc = CameraController()
    th = threading.Thread(target=cc.mainloop, args=tuple(), daemon=True)
    th.start()
    return cc


if __name__ == "__main__":
    pass
    #print(get_filenames())

    # start()
    # input()

    # cc = CameraController()
    # print("Test filename generator")
    # for i in range(10):
    #     print(cc.get_filename())
    #     time.sleep(0.5)

    # print("Test make frame function")
    # for i in range(10):
    #     frame = cc.make_frame()
    #     if frame is not None:
    #         cv2.imshow("video", frame)
    #     else:
    #         print("Error")
    #     cv2.waitKey(500)

    # print("Test get_light_level function")
    # for i in range(100):
    #     frame = cc.make_frame()
    #     if frame is not None:
    #         print(cc.get_light_level(frame))
    #     else:
    #         print("Error")
    #     cv2.waitKey(20)

    #print("Test zip function")
    #cc.rebuild_zip()

    # print("Test rebuild video function")
    # cc.rebuild_video()

