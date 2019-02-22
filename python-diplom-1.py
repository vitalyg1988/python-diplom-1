#! /usr/bin/env python3
import json
import os
import requests
from pprint import pprint
from time import sleep

PATH = os.path.abspath(os.path.dirname(__file__))

token = 'ed1271af9e8883f7a7c2cefbfddfcbc61563029666c487b2f71a5227cce0d1b533c4af4c5b888633c06ae'


def get_user_input():
    user_input = input('Введите данные пользователья: ID(прим. 400362303) или Имя пользователя(прим. i.a.vinogradov): ')
    return user_input


class UserVk:

    TOKEN = token
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
        try:
            if 'error' in response:
                assert response['error']['error_code'] != 6
                response = response['response'][0]
        except AssertionError:
            sleep(0.5)
            self.get_groups()
        try:
            return response['response']['items']
        except KeyError:
            return list

    def __repr__(self):
        return f'{self.user_id}'

    # Эта функция пока никак не нужна и не работает как нужно (цикл For), но оставлю как есть
    def description_group(self, groups_list):
        descript_list = []
        for group in groups_list:
            UserVk.param['group_ids'] = group
            UserVk.param['fields'] = 'members_count'
            method = 'groups.getById'
            response = UserVk.get_response(method)
            try:
                if 'error' in response:
                    assert response['error']['error_code'] != 6
            except AssertionError:
                sleep(0.5)
                self.description_group(groups_list)
            response = UserVk.get_response(method)['response'][0]
            descript_group = {'name': response['name'],
                              'gid': response['id'],
                              'members_count': response['members_count']}
            descript_list.append(descript_group)
            return descript_list

    # вот здесь вся моя проблема и кроется
    def get_friends_groups_list(self, friends_list):
        friends_groups_list = []
        for friend in friends_list:
            UserVk.param['user_id'] = friend
            UserVk.param['extended'] = '1'
            UserVk.param['fields'] = 'id'
            method = 'groups.get'
            response = UserVk.get_response(method)
            try:
                if 'error' in response:
                    assert response['error']['error_code'] != 6
                    response = response['response'][0]
            except AssertionError:
                sleep(0.5)
                self.get_friends_groups_list(friends_list)
            try:
                friends_groups_list.append(response['response']['items'])
                return friends_groups_list
            except KeyError:
                return friends_groups_list

    user_groups = property(get_groups)
    user_friends = property(get_friends_list)


if __name__ == "__main__":
    user = UserVk(get_user_input())
    print(f'список друзей пользователя: {user.user_friends}')
    print(f'список групп пользователя: {user.user_groups}')
    pprint(user.get_friends_groups_list(user.get_friends_list))
