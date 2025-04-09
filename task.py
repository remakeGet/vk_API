

import os
from pprint import pprint
import requests
import json
import configparser


class ydAPIclient:

    API_YD_BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, yd_token):
        self.yd_token = yd_token

    def get_common_params(self):
        return {
    'path': 'Images'
        }
    
    def create_upload_folder(self, path_for_upload):
        headers = self.get_common_headers()
        params = {
            'path':path_for_upload
        }
        print('Создание папки Images на сервере Яндекс Диска...')
        response = requests.put(self.API_YD_BASE_URL, params=params, headers=headers)
        return path_for_upload
    
    def get_common_headers(self):
        return {
    'Authorization' : self.yd_token
        }

    def _build_url_(self, api_method):
        return f'{self.API_YD_BASE_URL}/{api_method}'

    def list_files(self, images_path):
            print('Получение информации о файлах, хранящихся в папке images...')
            files = os.listdir(images_path)
            return [f for f in files if os.path.isfile(os.path.join(images_path, f))]
        
    def upload_photo(self):
        print('Получение основных параметров для запроса на загрузку фотографий на сервер...')
        headers = self.get_common_headers()
        upload_folder = self.create_upload_folder('Images')
        params = self.get_common_params()
        files_list = self.list_files('images')
        try:
            print('Загрузка фотографий на сервер Яндекс Диска...')
            for file in files_list:
                params.update({'path':f'{upload_folder}/{file}'})
                response = requests.get(self._build_url_('upload'), params=params, headers=headers)
                url_for_upload = response.json()['href']
                with open(f'images/{file}', 'rb') as f:
                    requests.put(url_for_upload, files={'file':f})
            return 'Файлы успешно загружены на Яндекс Диск.'
        except:
            return 'Ошибка, файлы не были загружены.'


class vkAPIclient:
    API_BASE_URL = 'https://api.vk.com/method'

    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_common_params(self):
        return {
            'access_token': self.token,
            'v': '5.131'
        }
    
    def _build_url_(self, api_method):
        return f'{self.API_BASE_URL}/{api_method}'
    
    def get_photos(self):
        params = self.get_common_params()
        params.update({'owner_id': self.user_id, 'album_id':'profile','extended': 1})
        response = requests.get(self._build_url_('photos.get'), params=params)
        return response.json()
    
    def download_photo(self):
        print('Получение фотографий со страницы пользователя...')
        response = self.get_photos()
        json_files_list = []
        print('Скачивание фотографий на компьютер в папку images...')
        for resp in response['response']['items']:
            url = (resp['orig_photo']['url'])
            file_name = resp['likes']['count']
            picture_response = requests.get(url)
            json_files_list.append({'file_name': f'{file_name}.jpg',
                                     'size': 
                                     f"{resp['orig_photo']['height']}x{resp['orig_photo']['width']}"
                                     })
            with open(f'images/{file_name}.jpg','wb') as f:
                f.write(picture_response.content)

        with open('data.json', 'w', encoding='utf-8') as json_file:
            json.dump(json_files_list, json_file, ensure_ascii=False, indent=4)
        print('Вывод информации о файлах, записанной в json-файл:')
        return json_files_list


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    vk_token = config['Tokens']['vk_token']
    vk_id = config['Tokens']['vk_id']
    print(vk_token)
    
    yd_token = config['Tokens']['yd_token']
    vk_client = vkAPIclient(vk_token, vk_id)
    yd_client = ydAPIclient(yd_token)
    pprint(vk_client.download_photo())
    print(yd_client.upload_photo())




