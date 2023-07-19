from pprint import pprint
from datetime import datetime
import vk_api
from vk_api.exceptions import ApiError

from config import acces_token


class VkTools:
    def __init__(self, access_token):
        self.vk_api = vk_api.VkApi(token=access_token)

    def get_profile_info(self, user_id):    # Метод для получения информации о профиле пользователя
        try:
            info = self.vk_api.method('users.get', {
                'user_id': user_id,
                'fields': 'city,sex,relation,bdate'
            })[0]
        except ApiError as e:
            info = {}
            print(f'Error: {e}')

        result = {'name': (info['first_name'] + ' ' + info['last_name']) if
                  'first_name' in info and 'last_name' in info else None,
                  'sex': info.get('sex'),
                  'city': info.get('city')['title'] if info.get('city') is not None else None,
                  'year': datetime.now().year - int(info.get('bdate').split('.')[2])
                  if info.get('bdate') is not None else None
                  }
        return result

    def search_worksheet(self, params, offset):    # Метод для поиска пользователей по заданным параметрам
        try:
            users = self.vk_api.method('users.search', {
                'count': 10,
                'offset': offset,
                'hometown': params['city'],
                'sex': 1 if params['sex'] == 2 else 2,
                'has_photo': True,
                'age_from': params['year'] - 3,
                'age_to': params['year'] + 3,
            })
        except ApiError as e:
            users = []
            print('Error in search_worksheet():')
            print(f'Error: {e}')

        result = [
            {
                'name': f"{item['first_name']} {item['last_name']}",
                'id': item['id']
            }
            for item in users['items']
            if not item['is_closed']
        ]
        return result

    def get_photos(self, user_id):    # Метод для получения информации о фотографиях пользователя
        try:
            photos = self.vk_api.method('photos.get', {
                'owner_id': user_id,
                'album_id': 'profile',
                'extended': 1
            })
        except ApiError as e:
            photos = {}
            print(f'Error: {e}')

        result = [
            {
                'owner_id': item['owner_id'],
                'id': item['id'],
                'likes': item['likes']['count'],
                'comments': item['comments']['count']
            }
            for item in photos['items']
        ]

        result.sort(key=lambda x: (x['likes'], x['comments']), reverse=True)
        return result[:3]


if __name__ == '__main__':
    user_id = 18629760
    vk_tools = VkTools(acces_token)
    params = vk_tools.get_profile_info(user_id)
    worksheets = vk_tools.search_worksheet(params, 20)
    worksheet = worksheets.pop()

    pprint(worksheets)
