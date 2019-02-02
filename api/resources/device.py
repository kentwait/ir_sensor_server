from flask import request
from flask_restful import Resource, reqparse
from api.config import SHELVE_PATH, SQLITE_PATH
from ircodec.command import CommandSet
from api.common.util import error
import shelve
import sqlite3 as sq


class Device(Resource):
    def get(self, location_id, device_id):
        pass

    def post(self, device_id=None):
        # Retrieves ir command from local shelve
        # Retrieves state data from local sqlite
        # Sends signal to ir blaster
        # Stores new state data from local sqlite
        # Stores new state data to dynamodb
        parser = reqparse.RequestParser()
        parser.add_argument('device_id', type=str, required=True, location='json', help='Unique device name')
        parser.add_argument('command_id', type=str, required=True, location='json', help='IR command name')
        args = parser.parse_args()
        if device_id is None:
            device_id = args['device_id']
        elif device_id != args['device_id']:
            return error('device_id specified by URL and device_id in JSON are not the same', code=400)
        with shelve.open(SHELVE_PATH) as shl:
            if device_id not in shl.keys():
                return error('device_id not found', code=400)
            if args['command_id'] not in shl[device_id].commands.keys():
                return error('command_id not found', code=400)
            try:
                cmd_set = shl[device_id]
                cmd_set.emit(args['command_id'])
            except Exception as e:
                return error(str(e), code=400)
        return {'status': 'success',
                'device_id': device_id,
                'command_id': args['command_id']}

    def put(self, device_id=None):
        # Stores new command into local shelve
        with shelve.open(SHELVE_PATH) as shl:
            try:
                cmd_set = CommandSet.from_json(request.json)
                if device_id is None:
                    device_id = cmd_set.name
                shl[device_id] = cmd_set
            except Exception as e:
                return error(str(e), code=400)
        return {'status': 'success',
                'device_id': device_id}

    def delete(self, device_id=None):
        if device_id is None:
            return error('device_id not specified', code=400)
            try:
                with shelve.open(SHELVE_PATH) as shl:
                    del shl[device_id]
            except Exception as e:
                return error(str(e), code=400)
        return {'status': 'success',
                'deleted': {
                    'device_id': device_id}
                }
