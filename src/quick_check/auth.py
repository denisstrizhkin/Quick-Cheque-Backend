import jwt
import re
import datetime

from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db
from .support_functions import fetchone_by_pattern_attribute_value, \
    check_json_fields_existance

from . import constants


bp = Blueprint('auth', __name__, url_prefix='/api')

JWT_ALGORITHM = 'HS256'

FIELD_STATUS = constants.FIELD_STATUS
FIELD_TOKEN = constants.FIELD_TOKEN
FIELD_MESSAGE = constants.FIELD_MESSAGE

FIELD_USERNAME = 'username'
FIELD_ID = 'id'
FIELD_PASSWORD = 'password'
FIELD_EMAIL = 'email'
FIELD_EXPIRES = 'expires'

STATUS_OK = constants.STATUS_OK
STATUS_BAD = constants.STATUS_BAD

MAX_USERNAME = 32
MIN_USERNAME = 4

MAX_PASSWORD = 16
MIN_PASSWORD = 8

MAX_EMAIL = 40
MIN_EMAIL = 3

REGEX_PASSWORD = re.compile(r'[A-za-z0-9]+')
REGEX_USERNAME = re.compile(r'[a-zA-z0-9]+')
REGEX_EMAIL = re.compile(
    r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
)

TOKEN_VALID = {
    FIELD_STATUS: STATUS_OK,
    FIELD_MESSAGE: 'authentication confirmed'
}
TOKEN_INVALID = {
    FIELD_STATUS: STATUS_BAD,
    FIELD_MESSAGE: 'token invalid'
}
TOKEN_EXPIRED = {
    FIELD_STATUS: STATUS_BAD,
    FIELD_MESSAGE: 'token expired'
}

DB_TABLE_USERS = 't_user'


def create_jwt_token(user_id, user_email):
    return jwt.encode(
        {
            FIELD_ID: user_id,
            FIELD_EMAIL: user_email,
            FIELD_EXPIRES: str(datetime.datetime.utcnow() +
                               datetime.timedelta(minutes=10000))
        },
        current_app.config['SECRET_KEY'],
        JWT_ALGORITHM
    )


def decode_token(token):
    return jwt.decode(
        token,
        current_app.config['SECRET_KEY'],
        JWT_ALGORITHM
    )


@bp.post('/register')
def register():
    fields = [FIELD_USERNAME, FIELD_PASSWORD, FIELD_EMAIL]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400

    username = str(request.json[FIELD_USERNAME])
    password = str(request.json[FIELD_PASSWORD])
    email = str(request.json[FIELD_EMAIL])

    def check_field(field, fregx, fmin, fmax, fname):
      if not re.fullmatch(fregx, field) or len(field) < fmin or len(field) > fmax:
        response = {
          FIELD_STATUS: STATUS_BAD,
          FIELD_MESSAGE: f'{fname} is not valid'
        }
        return jsonify(response), 400

    response = check_field(password, REGEX_PASSWORD, MIN_PASSWORD, MAX_PASSWORD, FIELD_PASSWORD)
    if not response is None:
        return response
    response = check_field(username, REGEX_USERNAME, MIN_USERNAME, MAX_USERNAME, FIELD_USERNAME);
    if not response is None:
        return response
    response = check_field(email, REGEX_EMAIL, MIN_EMAIL, MAX_EMAIL, FIELD_EMAIL);
    if not response is None:
        return response

    db = get_db()
    try:
        db.cursor().execute(
            f"insert into {DB_TABLE_USERS} (name, password, email)"
            "values (%s, %s, %s)",
            (username, generate_password_hash(password), email)
        )
        db.commit()
    except db.IntegrityError:
        response = {
            FIELD_STATUS: STATUS_BAD,
            FIELD_MESSAGE: 'username already exists'
        }
        return jsonify(response), 400


    user = fetchone_by_pattern_attribute_value(
        DB_TABLE_USERS,
        f"SELECT * FROM {DB_TABLE_USERS} WHERE email = '{email}';"
    )
    user_id = user[FIELD_ID]
    response = {
        FIELD_STATUS: STATUS_OK,
        FIELD_MESSAGE: 'user created, try to login now',
    }
    return jsonify(response), 200


@bp.post('/login')
def login():
    fields = [FIELD_EMAIL, FIELD_PASSWORD]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400

    email = str(request.json[FIELD_EMAIL])
    password = str(request.json[FIELD_PASSWORD])

    user = fetchone_by_pattern_attribute_value(
        DB_TABLE_USERS,
        f"SELECT * FROM {DB_TABLE_USERS} WHERE email = '{email}';"
    )
    current_app.logger.warning(user)

    if not user:
        response = {
            FIELD_STATUS: STATUS_BAD,
            FIELD_MESSAGE: 'user does not exist'
        }
        return jsonify(response), 400

    if not check_password_hash(user[FIELD_PASSWORD], password):
        response = {
            FIELD_STATUS: STATUS_BAD,
            FIELD_MESSAGE: 'wrong password'
        }
        return jsonify(response), 400

    token = create_jwt_token(user[FIELD_ID], email)
    response = {
        FIELD_STATUS: STATUS_OK,
        FIELD_MESSAGE: 'logged in, token generated',
        FIELD_TOKEN: token,
        FIELD_ID: user[FIELD_ID]
    }
    return jsonify(response), 200


def validate_token(token):
    try:
    	jwt_body = decode_token(token)
    except jwt.exceptions.InvalidTokenError as e:
        current_app.logger.warning(e)
        return TOKEN_INVALID

    fields = [FIELD_EMAIL, FIELD_EXPIRES]
    if not check_json_fields_existance(fields, jwt_body):
        return TOKEN_INVALID

    query = (
        f"SELECT * FROM {DB_TABLE_USERS} "
        f"WHERE email = '{jwt_body[FIELD_EMAIL]}';"
    )
    user = fetchone_by_pattern_attribute_value(DB_TABLE_USERS, query)

    if not user:
        return TOKEN_INVALID

    permitted_time = datetime.datetime.strptime(
        jwt_body[FIELD_EXPIRES],
        "%Y-%m-%d %H:%M:%S.%f"
    )

    current_time = datetime.datetime.utcnow()

    if permitted_time < current_time:
        return TOKEN_EXPIRED

    return TOKEN_VALID


@bp.post('/delete_user')
def delete_user():
    fields = [FIELD_TOKEN]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400

    token = str(request.json[FIELD_TOKEN])
    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
  
    user_id = decode_token(token)[FIELD_ID]
    current_app.logger.warning(user_id)
    
    db = get_db()
    db.cursor().execute(
        f"delete from {DB_TABLE_USERS}\n"
        f"where id = '{user_id}';"
    )
    db.commit()

    return jsonify(token_status), 200


@bp.post('/auth_test')
def auth_test():
    fields = [FIELD_TOKEN]
    if not check_json_fields_existance(fields, request.json):
        return jsonify(constants.WRONG_FORMAT), 400

    token = str(request.json[FIELD_TOKEN])
    token_status = validate_token(token)
    if token_status[FIELD_STATUS] == STATUS_BAD:
        return jsonify(token_status), 400
    
    return jsonify(token_status), 200
