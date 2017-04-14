# -*- coding: utf-8 -*-
"""
@author: python273
@contact: https://vk.com/python273
@license Apache License, Version 2.0, see LICENSE file

Copyright (C) 2017
"""


class VkUpload(object):
    def __init__(self, vk):
        """

        :param vk: объект VkApi
        """

        self.vk = vk
        # https://vk.com/dev/upload_files

    def photo(self, photos, album_id,
              latitude=None, longitude=None, caption=None, description=None,
              group_id=None):
        """ Загрузка изображений в альбом пользователя

        :param photos: путь к изображению(ям) или file-like объект(ы)
        :type photos: str, list

        :param album_id: идентификатор альбома
        :param latitude: географическая широта, заданная в градусах
                            (от -90 до 90)
        :param longitude: географическая долгота, заданная в градусах
                            (от -180 до 180)
        :param caption: текст описания изображения
        :param description: текст описания альбома
        :param group_id: идентификатор сообщества (если загрузка идет в группу)
        """

        values = {'album_id': album_id}

        if group_id:
            values['group_id'] = group_id

        # Получаем ссылку для загрузки
        url = self.vk.method('photos.getUploadServer', values)['upload_url']

        # Загружаем
        photo_files = open_files(photos)
        response = self.vk.http.post(url, files=photo_files).json()
        close_files(photo_files)

        # Олег Илларионов:
        # это не могу к сожалению просто пофиксить
        if 'album_id' not in response:
            response['album_id'] = response['aid']

        response.update({
            'latitude': latitude,
            'longitude': longitude,
            'caption': caption,
            'description': description
        })

        values.update(response)

        # Сохраняем фото в альбоме
        response = self.vk.method('photos.save', values)

        return response

    def photo_messages(self, photos):
        """ Загрузка изображений в сообщения

        :param photos: путь к изображению(ям) или file-like объект(ы)
        :type photos: str, list
        """

        url = self.vk.method('photos.getMessagesUploadServer')['upload_url']

        photo_files = open_files(photos)
        response = self.vk.http.post(url, files=photo_files)
        close_files(photo_files)

        response = self.vk.method('photos.saveMessagesPhoto', response.json())

        return response

    def photo_profile(self, photo, owner_id=None, crop_x=None, crop_y=None,
                      crop_width=None):
        """ Загрузка изображения профиля

        :param photo: путь к изображению или file-like объект
        :param owner_id: идентификатор сообщества или текущего пользователя.
                По умолчанию загрузка идет в профиль текущего пользователя.
                При отрицательном значении загрузка идет в группу.
        :param crop_x: координата X верхнего правого угла миниатюры.
        :param crop_y: координата Y верхнего правого угла миниатюры.
        :param crop_width: сторона квадрата миниатюры.
                При передаче всех crop_* для фотографии также будет
                подготовлена квадратная миниатюра.
        """

        values = {}

        if owner_id:
            values['owner_id'] = owner_id

        crop_params = {}

        if crop_x is not None and crop_y is not None and crop_width is not None:
            crop_params['_square_crop'] = '{},{},{}'.format(
                crop_x, crop_y, crop_width
            )

        response = self.vk.method('photos.getOwnerPhotoUploadServer', values)
        url = response['upload_url']

        photo_files = open_files(photo, key_format='file')
        response = self.vk.http.post(url, data=crop_params, files=photo_files)
        close_files(photo_files)

        response = self.vk.method('photos.saveOwnerPhoto', response.json())

        return response
    
    def photo_chat(self, photo, chat_id):
        """ Загрузка и смена обложки в беседе

        :param photo: путь к изображению или file-like объект
        :param chat_id: ID беседы
        """

        values = {'chat_id': chat_id}
        url = self.vk.method('photos.getChatUploadServer', values)['upload_url']

        photo_file = open_files(photo)
        response = self.vk.http.post(url, files=photo_file)
        close_files(photo_file)

        response = self.vk.method('messages.setChatPhoto', response.json())

        return response

    def photo_wall(self, photos, user_id=None, group_id=None):
        """ Загрузка изображений на стену пользователя или в группу

        :param photos: путь к изображению(ям) или file-like объект(ы)
        :type photos: str, list

        :param user_id: идентификатор пользователя
        :param group_id: идентификатор сообщества (если загрузка идет в группу)
        """

        values = {}

        if user_id:
            values['user_id'] = user_id
        elif group_id:
            values['group_id'] = group_id

        response = self.vk.method('photos.getWallUploadServer', values)
        url = response['upload_url']

        photos_files = open_files(photos)
        response = self.vk.http.post(url, files=photos_files)
        close_files(photos_files)

        values.update(response.json())

        response = self.vk.method('photos.saveWallPhoto', values)

        return response

    def audio(self, audio, artist, title):
        """ Загрузка аудио

        :param audio: путь к аудиофайлу или file-like объект
        :param artist: исполнитель
        :param title: название
        """

        url = self.vk.method('audio.getUploadServer')['upload_url']

        f = open_files(audio, key_format='file')
        response = self.vk.http.post(url, files=f).json()
        close_files(f)

        response.update({
            'artist': artist,
            'title': title
        })

        response = self.vk.method('audio.save', response)

        return response

    def document(self, doc, title=None, tags=None, group_id=None,
                 to_wall=False):
        """ Загрузка документа

        :param doc: путь к документу или file-like объект
        :param title: название документа
        :param tags: метки для поиска
        :param group_id: идентификатор сообщества (если загрузка идет в группу)
        :param to_wall: загрузить на стену
        """

        values = {'group_id': group_id}

        if to_wall:
            method = 'docs.getWallUploadServer'
        else:
            method = 'docs.getUploadServer'

        url = self.vk.method(method, values)['upload_url']

        files = open_files(doc, 'file')
        response = self.vk.http.post(url, files=files).json()

        response.update({
            'title': title,
            'tags': tags
        })

        response = self.vk.method('docs.save', response)

        return response

    def document_wall(self, doc, title=None, tags=None, group_id=None):
        """ Загрузка документа в папку Отправленные,
            для последующей отправки документа на стену
            или личным сообщением.

        :param doc: путь к документу или file-like объект
        :param title: название документа
        :param tags: метки для поиска
        :param group_id: идентификатор сообщества (если загрузка идет в группу)
        """

        return self.document(doc, title, tags, group_id, True)


def open_files(paths, key_format='file{}'):
    if not isinstance(paths, list):
        paths = [paths]

    files = []

    for x, file in enumerate(paths):
        if hasattr(file, 'read'):
            f = file

            if hasattr(file, 'name'):
                filename = file.name
            else:
                filename = '.jpg'
        else:
            filename = file
            f = open(filename, 'rb')

        ext = filename.split('.')[-1]
        files.append(
            (key_format.format(x), ('file{}.{}'.format(x, ext), f))
        )

    return files


def close_files(files):
    for f in files:
        f[1][1].close()
