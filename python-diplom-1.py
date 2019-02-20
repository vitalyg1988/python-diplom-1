#! /usr/bin/env python3
import json
import os
import requests
from pprint import pprint
from time import sleep
from urllib.parse import urlencode

PATH = os.path.abspath(os.path.dirname(__file__))


APP_ID = 6866070
AUTH_URL = 'https://oauth.vk.com/authorize'

aut_data = dict(client_id=APP_ID, response_type='token', v='5.92')

print('?'.join((AUTH_URL, urlencode(aut_data))))


def get_user_input():
    user_input = input('Введите данные пользователья: ID(прим. 400362303) или Имя пользователя(прим. i.a.vinogradov): ')
    return user_input


class UserVk:
    TOKEN = 'e7a4b85a9e08dfc28c55cac4886f20fff880450b54324466426155b962825302bc366e3cb9f6c14159bed'
    param = dict(v='5.92', access_token=TOKEN)

    @staticmethod
    def get_response(method):
        return requests.get(f'https://api.vk.com/method/{method}', UserVk.param).json()

    def __init__(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        UserVk.param['user_ids'] = self.user_id
        method = 'users.get'
        return UserVk.get_response(method)['response'][0]['id']

    def get_friends_list(self):
        if type(self.user_id) is str:
            self.user_id = self.get_user_id()
        UserVk.param['user_id'] = self.user_id
        method = 'friends.get'
        return list(map(UserVk, UserVk.get_response(method)['response']['items']))

    def get_groups(self):
        if type(self.user_id) is str:
            self.user_id = self.get_user_id()
        UserVk.param['user_id'] = self.user_id
        method = 'groups.get'
        response = UserVk.get_response(method)
        return list(map(UserVk, response['response']['items']))

    def __repr__(self):
        return f'{self.user_id}'


# class Groups(UserVk):
    def description_groups(self, group_list):
        for group in group_list:
            UserVk.param['group_ids'] = group
            UserVk.param['fields'] = 'members_count'
            method = 'groups.getById'
            response = UserVk.get_response(method)['response'][0]
            descript_groups = {'name': response['name'],
                               'gid': response['id'],
                               'members_count': response['members_count']}
            return descript_groups


if __name__ == "__main__":
    user = UserVk(get_user_input())
    print(user.get_groups())
    print(user.description_groups(user.get_groups()))
