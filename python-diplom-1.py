#! /usr/bin/env python3
import json
import os
import requests
from time import sleep
import sys
import logging.config


def get_path(item_name=''):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), item_name)


token = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'

logger = logging.getLogger('errorLog')


def log_conf():
    with open(get_path('conf.json')) as f:
        return json.load(f)


logging.config.dictConfig(log_conf())


def get_user_input():
    user_input = input('Введите данные пользователья: ID(прим. 400362303) или Имя пользователя(прим. i.a.vinogradov): ')
    return user_input


class UserVk:

    TOKEN = token
    error_user = []

    @staticmethod
    def response_param():
        return dict(v='5.92', access_token=UserVk.TOKEN)

    @staticmethod
    def error_handler(resp, par, met):
        if 'error' in resp:
            logger.error(f'{resp["error"]["error_code"]}: {resp["error"]["error_msg"]}')
            if resp["error"]["error_code"] == 6:
                sleep(2)
                resp = UserVk.get_response(par, met)
        return resp

    def __init__(self, user_id):
        self.user_id = user_id

    @staticmethod
    def get_response(param, method):
        return requests.post(f'https://api.vk.com/method/{method}', param).json()

    def get_user_id(self):
        param = UserVk.response_param()
        param['user_ids'] = self.user_id
        method = 'users.get'
        response = UserVk.get_response(param, method)
        response = UserVk.error_handler(response, param, method)
        return response['response'][0]['id']

    def get_friends_list(self):
        if type(self.user_id) is str:
            self.user_id = self.get_user_id()
        param = UserVk.response_param()
        param['user_id'] = self.user_id
        method = 'friends.get'
        response = UserVk.get_response(param, method)['response']
        response = UserVk.error_handler(response, param, method)
        return list(map(UserVk, response['items']))

    def get_groups(self):
        if type(self.user_id) is str:
            self.user_id = self.get_user_id()
        param = UserVk.response_param()
        param['user_id'] = self.user_id
        method = 'groups.get'
        response = UserVk.get_response(param, method)
        response = UserVk.error_handler(response, param, method)
        try:
            return response['response']['items']
        except KeyError:
            return []

    def __repr__(self):
        return f'{self.user_id}'

    user_groups = property(get_groups)
    user_friends = property(get_friends_list)

    def get_description_group(self):
        param = UserVk.response_param()
        param['group_id'] = self.user_id
        method = 'groups.getById'
        response = UserVk.get_response(param, method)
        response = UserVk.error_handler(response, param, method)
        return {'name': response['response'][0]['name'],
                'id': response['response'][0]['id'],
                'members_count': response['response'][0]['members_count']}

    def check_membership(self, verifiable_friends):
        param = UserVk.response_param()
        param['user_ids'] = f'{verifiable_friends}'
        param['group_id'] = self.user_id
        param['extended'] = '1'
        method = 'groups.isMember'
        response = UserVk.get_response(param, method)
        response = UserVk.error_handler(response, param, method)
        return [member for member in response['response']]

    @staticmethod
    def generation_list(gen_list, offset):
        start_index = 0
        end_index = offset
        while end_index <= len(gen_list):
            temp_list = []
            temp_list += gen_list[start_index: end_index]
            start_index = end_index
            end_index += 500
            yield temp_list
        if end_index > len(gen_list):
            temp_list = []
            temp_list += gen_list[start_index: len(gen_list)]
            yield temp_list

    @staticmethod
    def count_members(list_groups):
        temp_dict = {}
        for group in list_groups:
            temp_dict.setdefault(group, 0)
        return temp_dict

    def counting_friends(self):
        current_user_groups = UserVk.count_members(list(map(UserVk, self.user_groups)))
        friends = self.user_friends
        for index, group in enumerate(current_user_groups):
            for friends_list in UserVk.generation_list(friends, 500):
                for friend in group.check_membership(friends_list):
                    if friend['member'] == 1:
                        current_user_groups[group] += 1
            sys.stdout.write('\r')
            sys.stdout.write(f'Обработано групп {index + 1} из {len(current_user_groups)}')
            sys.stdout.flush()
        print('\n')
        return current_user_groups

    @staticmethod
    def filter_groups(dict_groups, number):
        temp_list = []
        for group in dict_groups:
            if dict_groups[group] == number:
                temp_list.append(group)
        return temp_list

    @staticmethod
    def create_dict_groups(list_of_id):
        temp_list = []
        for id_group in list_of_id:
            temp_list.append(id_group.get_description_group())
        return temp_list


if __name__ == "__main__":
    try:
        userint = UserVk(get_user_input())
        result = userint.create_dict_groups(userint.filter_groups(userint.counting_friends(), 50))
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'groups.json')), 'w') as output_file:
            json.dump(result, output_file, ensure_ascii=False, indent=2)
    except IndexError:
        pass
