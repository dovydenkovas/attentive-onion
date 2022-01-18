"""
    Основной файл программы
    Создает веб сервер и поток с техн. зрением.
"""


import os
import shutil
from flask import Flask, render_template, redirect
from loguru import logger

import compvision
import timemgr

SITE_VERSION = "1.0.4"


logger.add("static/data/logs.log", format="{time} {level} {message}", level="INFO",
           rotation="500 KB", compression="zip")


def update_info():
    pass

app = Flask(__name__)
camera_controller = compvision.CameraController()
tm = timemgr.TimeManager([
    timemgr.Event(15*60, camera_controller.update),
    timemgr.Event(5*60, update_info)
])
tm.start_mainloop()



@logger.catch
@app.route('/')
def index():
    return render_template('index.html', title="Главная", tab_number=0, last_frame=camera_controller.get_last_frame())

@logger.catch
@app.route('/i')
def show_images():
    return render_template('im.html', title="Изображения", tab_number=1, images=camera_controller.get_filenames())

@logger.catch
@app.route('/l')
def show_logs():
    total, used, free = shutil.disk_usage("/")
    total = round(10 * total / (2**30)) / 10
    free = round(10 * free / (2**30)) / 10
    return render_template('logs.html', settings=camera_controller.__dict__,
                           title="Настройки", tab_number=2, total_memory=total,
                           free_memory=free, version=SITE_VERSION)

@logger.catch
@app.route('/da')
def download_archive():
    return redirect("static/data/images.zip")


@logger.catch
@app.route('/dv')
def download_video():
    return redirect("static/data/video.webm")


@logger.catch
@app.errorhandler(404)
def err_404(err):
    return render_template('error/404.html', title="404")


@logger.catch
@app.errorhandler(500)
def err_500(err):
    return render_template('error/404.html', title="500")


if __name__ == '__main__':
    app.run(port=8880, debug=False, host="0.0.0.0")

