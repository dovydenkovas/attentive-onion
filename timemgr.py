"""
    Модуль для управления периодическими событиями.
    Позволяет запускать функции через заданные промежутки времени.
    Функции необходимо обернуть в класс события Event с указанием периодичности вызовов в секундах.


    Примеры использования:
    # Вызывать функию foo(1, 2, 'zzz') каждые 10 секунд
    >>> def foo(x, y, z): print(z * (x + y) / 0)
    >>> event = Event(1, foo, (1, 2, 'zzz'))  # Создайте событие
    >>> tmanager = TimeManager([event])  # Создайте "повелителя времени"
    >>> tmanager.mainloop()  # Для запуска главного цикла в текущем потоке


"""


from datetime import datetime
from time import sleep
from math import gcd
import threading
import json
from loguru import logger

class Event:
    def __init__(self, delay, function, args=None):
        """
        delay: задержка между вызывами функции в секундах
        function: вызываемая функия
        args: аргументы функции
        """
        self.delay = delay
        self.function = function
        self.args = args if args else tuple()
        self.last_active = 0


class TimeManager:
    def __init__(self, events=None):
        self.events = events if type(events) == list else []
        self.events.append(Event(15*60, self.save))
        self.delay = 10

    def calculate_delay(self):
        """ Расчет оптимального времени задержки исходя из требуемой задержки каждого события. """
        delays = [event.delay for event in self.events]
        for i in range(1, len(self.events)):
            delays[i] = gcd(delays[i-1], delays[i])
        self.delay = delays[-1]

    def add_event(self, event):
        self.events.append(event)
        self.calculate_delay()

    def run_event(self, id):
        try:
            self.events[id].function(*self.events[id].args)
        except Exception as e:
            print(f"Error at {self.events[id].function.__name__}{self.events[id].args}:", e)

        self.events[id].last_active = datetime.now().timestamp()

    def save(self):
        res = [[e.function.__name__, e.last_active] for e in self.events]
        with open("events.txt", 'w') as f:
            json.dump(res, f)

    def load(self):
        with open("events.txt", 'r') as f:
            events = json.load(f)
            for i in range(len(self.events)):
                name = self.events[i].function.__name__
                for ev in events:
                    if ev[0] == name:
                        self.events[i].last_active = ev[1]
                        break


    def mainloop(self):
        self.calculate_delay()
        self.load()
        print("Set delay to", self.delay, "seconds")

        while True:
            now = datetime.now().timestamp()
            for i in range(len(self.events)):
                if now - self.events[i].last_active >=  self.events[i].delay:
                    th = threading.Thread(target=self.run_event, args=(i,), daemon=True)
                    th.start()
            sleep(self.delay)

    def start_mainloop(self):
        th = threading.Thread(target=self.mainloop, args=tuple(), daemon=True)
        th.start()
        return th


if __name__ == "__main__":
    def foo(x, y, z): print(z * (x + y) / 0)

    event = Event(1, foo, (1, 2, 'zzz'))  # Создайте событие
    tmanager = TimeManager([event])  # Создайте "повелителя времени"
    tmanager.mainloop()  # Для запуска главного цикла в текущем потоке
