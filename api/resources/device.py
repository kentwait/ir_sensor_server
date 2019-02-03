from flask import request
from flask_restful import Resource, reqparse
from api.config import COMMAND_SHELVE_PATH, STATE_SHELVE_PATH
from ircodec.command import CommandSet
from api.common.util import success, error
import shelve
import sqlite3 as sq


class Device(Resource):
    def get(self, device_id=None):
        if device_id is None:
            return self.list_devices()
        return self.list_command_ids(device_id)

    def list_devices(self):
        with shelve.open(COMMAND_SHELVE_PATH) as shl:
            device_ids = list(shl.keys())
        return success({'device_ids': device_ids})

    def list_command_ids(self, device_id):
        with shelve.open(COMMAND_SHELVE_PATH) as shl:
            if device_id not in shl.keys():
                return error('device_id not found', code=400)
            command_ids = list(shl[device_id].commands.keys())
        return success({'command_ids': command_ids})

    def post(self, device_id=None):
        # Parse json payload
        parser = reqparse.RequestParser()
        parser.add_argument('device_id', type=str, required=True, location='json', help='Unique device name')
        parser.add_argument('command_id', type=str, required=True, location='json', help='IR command name')
        args = parser.parse_args()

        # Set device_id
        if device_id is None:
            device_id = args['device_id']
        elif device_id != args['device_id']:
            return error('device_id specified by URL and device_id in JSON are not the same', code=400)
        
        # Retrieves ir command from local shelve
        with shelve.open(COMMAND_SHELVE_PATH) as shl:
            if device_id not in shl.keys():
                return error('device_id not found', code=400)
            if args['command_id'] not in shl[device_id].commands.keys():
                return error('command_id not found', code=400)
            cmd_set = shl[device_id]

        # TODO: Retrieves state data from local sqlite

        # Sends signal using ir blaster
        try:
            cmd_set.emit(args['command_id'])
        except Exception as e:
            return error('Error emitting signal, ' + str(e), code=400)

        # TODO: Stores new state data from local sqlite
        # TODO: Stores new state data to dynamodb

        return success({'device_id': device_id, 'command_id': args['command_id']})

    def delete(self, device_id=None):
        if device_id is None:
            return error('device_id not specified', code=400)
        try:
            with shelve.open(COMMAND_SHELVE_PATH) as shl:
                del shl[device_id]
        except Exception as e:
            return error(str(e), code=400)
        return success({'deleted_device_id': device_id})

class NewDevice(Resource):
    def put(self, device_type, device_id=None):
        # Convert JSON to CommandSet object
        try:
            cmd_set = CommandSet.from_json(request.json)
        except Exception as e:
            return error('Error creating CommandSet from JSON, ' + str(e), code=400)

        # Set device_id
        if device_id is None:
            device_id = cmd_set.name
        elif device_id != cmd_set.name:
            return error('device_id specified by URL and command set name are not the same', code=400)

        # Stores command set into local shelve
        with shelve.open(COMMAND_SHELVE_PATH) as shl:
            try:
                shl[device_id] = cmd_set
            except Exception as e:
                return error(str(e), code=400)
        
        # Stores a new Device state model

        return success({'device_id': device_id})
