# coding: utf-8
from __future__ import unicode_literals

from time import sleep
from weakref import proxy
from random import randint, choice
from types import NoneType

import helpers


class NightClub(object):
    """ Ночной клуб
    """
    capacity = 0  # Максимальная вместительность клуба
    party_time = 0  # Продолжительность вечеринки

    playlist = []  # Список композиций вечеринки

    dancers = []  # Список посетителей

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NightClub, cls).__new__(cls)
        return cls.instance

    def __init__(self, capacity, party_time, styles, **kwargs):
        """
        :param capacity: Вместимость клуба, чел.
        :type capacity: int
        :param party_time: Продолжительность вечеринки, мин.
        :type party_time: int
        """
        assert capacity, 'Необходимо задать максимальную вместимость клуба'
        assert party_time, 'Необходимо задать продолжительность вечеринки'
        assert isinstance(styles, list), 'Необходимо задать словарь стилей'

        self.capacity = capacity
        self.party_time = party_time

        # Подберем композиции на вечер
        timer = 0  # Сумма продолжительностей уже добавленных композиций, сек.
        while timer < self.party_time * 60:
            track = Track(styles[randint(0, len(styles) - 1)],
                          min_duration=kwargs.get('min_track_length', 2),
                          max_duration=kwargs.get('max_track_length', 10))
            self.playlist.append(track)
            timer += track.duration

        # Заполняем ночной клуб посетителями
        for i in range(0, randint(0, self.capacity)):
            self.dancers.append(Dancer(styles=styles))

    def play_songs(self):
        """ Генератор трэков
        """
        for track in self.playlist:
            yield track

    def dance_peoples(self):
        """ Генератор танцоров
        """
        for dancer in self.dancers:
            yield dancer

    def start_work(self):
        """ It's Party Time!
        """
        # Вывесим рекламный баннер на входе
        print 'Ночной клуб открыт!'

        for song in self.play_songs():
            print 'Играет {0}'.format(song.style.name)

            for dancer in self.dance_peoples():
                dancer.move_it(song.style)

            sleep(song.duration)

            print

        print 'Ночной клуб закрывается! До новых встреч!'


class Dancer(object):
    """ Танцор
    """
    sex = None
    name = None
    abilities = {}

    def __init__(self, sex=None, name=None, styles=None):
        """
        :type name: basestring
        :type sex: int
        """
        assert isinstance(styles, (NoneType, list)), (
            'Танцевальные стили должны быть списком')
        self.sex = sex or randint(0, 1)
        self.name = name or helpers.NAMES[self.sex][
            randint(0, len(helpers.NAMES[self.sex])) - 1]

        self.abilities = {
            x.name: randint(0, 1) for x in styles
        }

    def move_it(self, style):
        """ I like to move it, move it!
        """
        do_nothing = '{0} идёт в бар пить водку'.format(self.name)
        if self.abilities.get(style.name):
            moves = style.get_moves()
            try:
                print '{0} {1}'.format(self.name, moves[choice(moves.keys())])
            except IndexError or KeyError:
                print do_nothing
        else:
            print do_nothing


class Style(object):
    """ Танцевальный стиль
    """
    instances = {}

    name = ''
    parent_style = None
    config = {}

    def __init__(self, name, parent=None, config=None):
        assert isinstance(name, basestring), (
            'Название стиля задано некорректно.')

        self.__class__.instances.update({
            name: proxy(self)
        })

        self.name = name
        self.parent_style = parent or None
        self.config = config or {}

    def get_moves(self):
        """ Получить движения для данного стиля
        """
        config = self.config or {}
        if not config:
            parent = self.__class__.instances.get(self.parent_style, None)
            config = getattr(parent, 'config', {})

        return config


class Track(object):
    """ Музыкальная композиция
    """
    style = None
    _duration = 0

    def __init__(self, style, duration=0, min_duration=0, max_duration=0):
        assert isinstance(style, Style), (
            'Не задан танцевальный стиль')

        self.style = style
        self.duration = duration or randint(min_duration, max_duration)

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        err_msg = ('Продолжительность композиции должна быть целым '
                   'количеством секунд либо временем в формате ММ:СС')
        assert isinstance(value, (int, basestring)), err_msg

        if isinstance(value, int):
            self._duration = value
        elif isinstance(value, basestring):
            try:
                m, s = value.split(':')
            except ValueError:
                raise ValueError(err_msg)
            self._duration = m * 60 + s


def get_param(ptype, prompt='Введите параметр: ',
              err_msg="Значение должно быть типа '{0}'"):
    """ Ввод параметра с проверкой типа
    """
    assert isinstance(ptype, type), 'Некорректное значение типа данных.'
    assert isinstance(prompt, basestring), 'Сообщение должно быть строкой'

    if not prompt.endswith(': '):
        prompt += ': '

    while True:
        try:
            param = ptype(raw_input(prompt))
        except ValueError:
            print err_msg.format(ptype.__name__)
            continue
        else:
            return param


def main():
    print "*** Добро пожаловать в Ночной Клуб! ***"

    club_capacity = get_param(int, 'Введите максимальную вместимость клуба')
    party_time = get_param(int, 'Введите продолжительность работы клуба, мин')
    min_track_length = get_param(int, 'Введите минимальную '
                                      'продолжительность трека, сек')
    max_track_length = get_param(int, 'Введите максимальную '
                                      'продолжительность трека, сек')
    assert min_track_length <= max_track_length, (
        'Минимальная продолжительность больше максимальной')

    print

    # Составляем список танцевальных стилей
    styles = []
    for k, v in helpers.STYLE_CONFIG.items():
        assert isinstance(v, list), 'Ошибка конфигурации стилей'
        styles.extend([
            Style(x, parent=k, config=helpers.DANCE_CONFIG.get(x)) for x in v
        ])

    # Создаём ночной клуб
    club = NightClub(club_capacity, party_time, styles,
                     min_track_length=min_track_length,
                     max_track_length=max_track_length)
    club.start_work()

if __name__ == '__main__':
    main()