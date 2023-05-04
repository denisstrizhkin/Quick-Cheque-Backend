#!/bin/python

import requests
import json


API_URL = "http://localhost:8080/api"

REGISTER_URL = API_URL + "/register"
LOGIN_URL= API_URL + "/login"
DELETE_URL= API_URL + "/delete_user"

ADD_ROOM_URL = API_URL + "/add_room"
GET_ROOMS_ADMIN_URL = API_URL + "/get_rooms_admin"
GET_ROOMS_MEMBER_URL = API_URL + "/get_rooms_member"
DELETE_ROOMS_URL = API_URL + "/delete_room"

ADD_CHEQUE_URL = API_URL + "/add_cheque"
GET_CHEQUES_URL = API_URL + "/get_cheques"
DELETE_CHEQUE_URL = API_URL + "/delete_cheque"


#MAX_USERNAME = 32
#MIN_USERNAME = 4
#
#MAX_PASSWORD = 16
#MIN_PASSWORD = 8
#
#MAX_EMAIL = 40


def test_wrong_password():
    print('### test wrong password ###')

    password1 = '123'
    password2 = '432143214214321431243124'
    password3 = '44444оооо'

    def do_request(password):
        data = {
            'email': 'admin@example.com',
            'username': 'admin',
            'password': password
        }
        x = requests.post(REGISTER_URL, json=data)
        print(x.status_code, x.text)

    do_request(password1)
    do_request(password2)
    do_request(password3)


def test_wrong_username():
    print('### test wrong username ###')

    username1 = '123'
    username2 = 'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj'
    username3 = 'равыаывфаыфв'

    def do_request(username):
        data = {
            'email': 'admin@example.com',
            'username': username,
            'password': 'adminadmin'
        }
        x = requests.post(REGISTER_URL, json=data)
        print(x.status_code, x.text)

    do_request(username1)
    do_request(username2)
    do_request(username3)


def test_wrong_email():
    print('### test wrong email ###')

    email1 = ''
    email2 = 'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj'
    email3 = 'равыаывфаыфв'

    def do_request(email):
        data = {
            'email': email,
            'username': 'admin',
            'password': 'adminadmin'
        }
        x = requests.post(REGISTER_URL, json=data)
        print(x.status_code, x.text)

    do_request(email1)
    do_request(email2)
    do_request(email3)


def test_register_and_login():
    print('### test_register_and_login ###')

    data = {
        'email': 'admin@test.com',
        'username': 'admin',
        'password': 'adminadmin'
    }
    x = requests.post(REGISTER_URL, json=data)
    print(x.status_code, x.text)
    
    data = {
        'email': 'admin@test.com',
        'password': 'adminadmin'
    }
    x = requests.post(LOGIN_URL, json=data)
    print(x.status_code, x.text)
    
    info = json.loads(x.text)
    data = {
        'token': info['token'],
        'id' : info['id']
    }
    x = requests.post(DELETE_URL, json=data)
    print(x.status_code, x.text)


def test_add_rooms():
    print('### test_add_rooms (get_rooms_admin) ###')

    data = {
        'email': 'admin@test.com',
        'username': 'admin',
        'password': 'adminadmin'
    }
    requests.post(REGISTER_URL, json=data)
    
    data = {
        'email': 'admin@test.com',
        'password': 'adminadmin'
    }
    x = requests.post(LOGIN_URL, json=data)
    info = json.loads(x.text)

    data = {
        'token': info['token'],
        'name': 'room1'
    }
    x = requests.post(ADD_ROOM_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
        'name': 'room2'
    }
    x = requests.post(ADD_ROOM_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
    }
    x = requests.post(GET_ROOMS_ADMIN_URL, json=data)
    print(x.status_code, x.text)
    x = requests.post(DELETE_ROOMS_URL, json=data)
    print(x.status_code, x.text)
    
    data = {
        'token': info['token'],
        'id' : info['id']
    }
    requests.post(DELETE_URL, json=data)


def test_join_room():
    print('### test_join_rooms (get_rooms_member) ###')

    data = {
        'email': 'admin@test.com',
        'username': 'admin',
        'password': 'adminadmin'
    }
    requests.post(REGISTER_URL, json=data)
    
    data = {
        'email': 'admin@test.com',
        'password': 'adminadmin'
    }
    x = requests.post(LOGIN_URL, json=data)
    info = json.loads(x.text)

    data = {
        'token': info['token'],
        'name': 'room1'
    }
    x = requests.post(ADD_ROOM_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
        'name': 'room2'
    }
    x = requests.post(ADD_ROOM_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
    }
    x = requests.post(GET_ROOMS_ADMIN_URL, json=data)
    print(x.status_code, x.text)
    x = requests.post(DELETE_ROOMS_URL, json=data)
    print(x.status_code, x.text)
    
    data = {
        'token': info['token'],
        'id' : info['id']
    }
    requests.post(DELETE_URL, json=data)

def test_add_cheques():
    print('### test_add_cheques ###')

    data = {
        'email': 'admin@test.com',
        'username': 'admin',
        'password': 'adminadmin'
    }
    requests.post(REGISTER_URL, json=data)
    
    data = {
        'email': 'admin@test.com',
        'password': 'adminadmin'
    }
    x = requests.post(LOGIN_URL, json=data)
    info = json.loads(x.text)

    data = {
        'token': info['token'],
        'name': 'room1'
    }
    x = requests.post(ADD_ROOM_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
    }
    x = requests.post(GET_ROOMS_ADMIN_URL, json=data)
    room_id = json.loads(x.text)['message'][0]['id']
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
        'name': 'cheque1',
        'room_id': room_id
    }
    x = requests.post(ADD_CHEQUE_URL, json=data)
    print(x.status_code, x.text)
    
    data = {
        'token': info['token'],
        'room_id': room_id
    }
    x = requests.post(GET_CHEQUES_URL, json=data)
    print(x.status_code, x.text)

    data = {
        'token': info['token'],
        'room_id': room_id
    }
    x = requests.post(DELETE_CHEQUE_URL, json=data)
    print(x.status_code, x.text)

    x = requests.post(DELETE_ROOMS_URL, json=data)
    print(x.status_code, x.text)
    
    data = {
        'token': info['token'],
        'id' : info['id']
    }
    requests.post(DELETE_URL, json=data)


def main():
    test_wrong_password()
    test_wrong_username()
    test_wrong_email()
    test_register_and_login()

    test_add_rooms()
    test_join_room()
    #test_add_cheques()


if __name__ == '__main__':
    main()
