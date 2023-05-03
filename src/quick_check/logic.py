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
    db.cursor().execute(
        f"insert into {DB_TABLE_ROOMS} (name, owner_id)"
        "values (%s, %s)",
        (name, user_id)
    )
    db.commit()

    response = {
        FIELD_MESSAGE : 'room was added successfully',
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


@bp.post('/get_rooms')
def get_rooms():
    fields = [FIELD_TOKEN]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400
    
    token = str(request.json[FIELD_TOKEN])
    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
   
    user_id = decode_token(token)[FIELD_ID]
    cur = get_db().cursor()
    cur.execute(
        f"select a.id, a.name, a.owner_id\n"
        f"from {DB_TABLE_ROOMS} a\n"
        f"join {DB_TABLE_ROOMS_ASSOC} b on a.id = b.room_id"
        f"where b.user_id = {user_id}"
    )
    rooms = cur.fetchall()
    rooms_list = []
    for room in rooms:
        rooms_list.append({
            FIELD_ID : room[0],
            FIELD_NAME : room[1],
            FIELD_OWNER_ID : room[2]
        })

    response = {
        FIELD_MESSAGE : rooms_list,
        FIELD_STATUS : STATUS_OK
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
