from flask import Blueprint, request, jsonify, current_app

from .db import get_db
from .support_functions import fetchone_by_pattern_attribute_value, \
    check_json_fields_existance

from . import constants

from .auth import validate_token, decode_token


FIELD_STATUS = constants.FIELD_STATUS
FIELD_TOKEN = constants.FIELD_TOKEN
FIELD_MESSAGE = constants.FIELD_MESSAGE

STATUS_OK = constants.STATUS_OK
STATUS_BAD = constants.STATUS_BAD

FIELD_ID = 'id'
FIELD_USER_ID = 'user_id'
FIELD_NAME = 'name'
FIELD_OWNER_ID = 'owner_id'
FIELD_ROOM_ID = 'room_id'

DB_TABLE_ROOMS = 't_room'
DB_TABLE_CHEQUES = 't_cheque'
DB_TABLE_ROOMS_ASSOC = 't_room_associative'
DB_TABLE_USERS = 't_user'


bp = Blueprint('logic', __name__, url_prefix='/api')


@bp.post('/add_room')
def add_room():
    fields = [FIELD_TOKEN, FIELD_NAME]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400
    
    token = str(request.json[FIELD_TOKEN])
    name = str(request.json[FIELD_NAME])

    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
   
    user_id = decode_token(token)[FIELD_ID]
    db = get_db()
    cur = db.cursor()
    cur.execute(
        f"insert into {DB_TABLE_ROOMS} (name, owner_id)"
        "values (%s, %s) returning id",
        (name, user_id)
    )
    new_id = cur.fetchone()[0]
    db.commit()

    response = {
        FIELD_MESSAGE : 'room was added successfully',
        FIELD_ID : new_id,
        FIELD_STATUS : STATUS_OK
    }

    return jsonify(response), 200


@bp.post('/delete_room')
def delete_room():
    fields = [FIELD_TOKEN]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400
    
    token = str(request.json[FIELD_TOKEN])
    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
   
    user_id = decode_token(token)[FIELD_ID]
    db = get_db()
    db.cursor().execute(
        f"delete from {DB_TABLE_ROOMS}\n"
        f"where owner_id = '{user_id}';"
    )
    db.commit()

    response = {
        FIELD_MESSAGE : 'deleted user rooms',
        FIELD_STATUS : STATUS_OK
    }

    return jsonify(response), 200


def get_rooms(query):
    db = get_db()
    cur = db.cursor()
    cur.execute(query)
    rooms = cur.fetchall()
    rooms_list = []
    for room in rooms:
        # get members list
        id = room[0]
        cur = db.cursor()
        cur.execute(
            f"select a.user_id, b.name\n"
            f"from {DB_TABLE_ROOMS_ASSOC} a\n"
            f"join {DB_TABLE_USERS} b on a.user_id = b.id\n"
            f"where a.room_id = {id}"
        )
        members_fetch = cur.fetchall()
        members = []
        for member in members_fetch:
            members.append({
                "id": member[0],
                "name": member[1]
            })

        # get cheque count
        cur = db.cursor()
        cur.execute(
            f"select count(*)\n"
            f"from {DB_TABLE_CHEQUES}"
        )
        cnt = cur.fetchone()[0]

        rooms_list.append({
            "members": members,
            "cheque_cnt": cnt,
            FIELD_ID : id,
            FIELD_NAME : room[1],
            FIELD_OWNER_ID : room[2]
        })
    return rooms_list


@bp.post('/get_rooms_admin')
def get_rooms_admin():
    fields = [FIELD_TOKEN]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400
    
    token = str(request.json[FIELD_TOKEN])
    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400

    user_id = decode_token(token)[FIELD_ID]
    rooms_list = get_rooms(
        f"select *\n"
        f"from {DB_TABLE_ROOMS}\n"
        f"where owner_id = {user_id}"
    )
    response = {
        FIELD_MESSAGE : rooms_list,
        FIELD_STATUS : STATUS_OK
    }
    return jsonify(response), 200


@bp.post('/get_rooms_member')
def get_rooms_member():
    fields = [FIELD_TOKEN]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400
    
    token = str(request.json[FIELD_TOKEN])
    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
   
    
    user_id = decode_token(token)[FIELD_ID]
    rooms_list = get_rooms(
        f"select a.id, a.name, a.owner_id\n"
        f"from {DB_TABLE_ROOMS} a\n"
        f"join {DB_TABLE_ROOMS_ASSOC} b on a.id = b.room_id\n"
        f"where b.user_id = {user_id}"
    )
    response = {
        FIELD_MESSAGE : rooms_list,
        FIELD_STATUS : STATUS_OK
    }
    return jsonify(response), 200


@bp.post('/join_room')
def join_room():
    fields = [FIELD_TOKEN, FIELD_ID]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400
    
    token = str(request.json[FIELD_TOKEN])
    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
   
    user_id = int(decode_token(token)[FIELD_ID])
    room_id = int(request.json[FIELD_ID])

    try:
        get_db().cursor().execute(
            f"insert into {DB_TABLE_ROOMS_ASSOC}\n"
            f"(user_id, room_id)\n"
            f"values ({user_id}, {room_id});"
        )
        get_db().commit();
        response = {
            FIELD_MESSAGE : "joined room successfuly",
            FIELD_STATUS : STATUS_OK
        }
    except Exception as e:
        response = {
            FIELD_MESSAGE : "join failed",
            FIELD_STATUS : STATUS_BAD
        }
    
    return jsonify(response), 200


@bp.post('/delete_member')
def delete_member():
    fields = [FIELD_TOKEN, FIELD_ROOM_ID, FIELD_USER_ID]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400
    
    token = str(request.json[FIELD_TOKEN])
    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
   
    user_id = int(decode_token(token)[FIELD_ID])
    room_id = int(request.json[FIELD_ROOM_ID])
    delete_id = int(request.json[FIELD_USER_ID])

    try:
        get_db().cursor().execute(
            f"delete from {DB_TABLE_ROOMS_ASSOC}\n"
            f"where room_id = {room_id} and user_id = {user_id};"
        )
        get_db().commit();
        response = {
            FIELD_MESSAGE : "deleted member successfuly",
            FIELD_STATUS : STATUS_OK
        }
    except Exception as e:
        response = {
            FIELD_MESSAGE : "delete failed",
            FIELD_STATUS : STATUS_BAD
        }
    
    return jsonify(response), 200


@bp.post('/add_cheque')
def add_cheque():
    fields = [FIELD_TOKEN, FIELD_ROOM_ID, FIELD_NAME]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400
    
    token = str(request.json[FIELD_TOKEN])
    room_id = str(request.json[FIELD_ROOM_ID])
    name = str(request.json[FIELD_NAME])

    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
   
    user_id = decode_token(token)[FIELD_ID]
    db = get_db()
    db.cursor().execute(
        f"insert into {DB_TABLE_CHEQUES} (name, room_id, owner_id)"
        "values (%s, %s, %s)",
        (name, room_id, user_id)
    )
    db.commit()

    response = {
        FIELD_MESSAGE : 'cheque was added successfully',
        FIELD_STATUS : STATUS_OK
    }

    return jsonify(response), 200


@bp.post('/delete_cheque')
def delete_cheque():
    fields = [FIELD_TOKEN, FIELD_ROOM_ID]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400
    
    token = str(request.json[FIELD_TOKEN])
    room_id = str(request.json[FIELD_ROOM_ID])

    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
   
    user_id = decode_token(token)[FIELD_ID]
    db = get_db()
    db.cursor().execute(
        f"delete from {DB_TABLE_CHEQUES}\n"
        f"where owner_id = '{user_id}' and room_id = '{room_id}';"
    )
    db.commit()

    response = {
        FIELD_MESSAGE : f'deleted room {room_id} cheques',
        FIELD_STATUS : STATUS_OK
    }

    return jsonify(response), 200


@bp.post('/get_cheques')
def get_cheques():
    fields = [FIELD_TOKEN, FIELD_ROOM_ID]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400
    
    token = str(request.json[FIELD_TOKEN])
    room_id = str(request.json[FIELD_ROOM_ID])
    
    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
   
    user_id = decode_token(token)[FIELD_ID]
    cur = get_db().cursor()
    cur.execute(
        f"select * from {DB_TABLE_CHEQUES};\n",
        f"where owner_id = '{user_id}' and room_id = '{room_id}';"
    )
    cheques = cur.fetchall()
    cheques_list = []
    for cheque in cheques:
        cheques_list.append({
            FIELD_ID : cheque[0],
            FIELD_ROOM_ID : cheque[1],
            FIELD_OWNER_ID : cheque[2],
            FIELD_NAME : cheque[3]
        })

    response = {
        FIELD_MESSAGE : cheques_list,
        FIELD_STATUS : STATUS_OK
    }

    return jsonify(response), 200
