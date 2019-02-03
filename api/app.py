from flask import Flask
from flask_restful import Api
from api.resources.device import Device, NewDevice
from api.resources.sensor import Sensor

app = Flask(__name__)
api = Api(app)

api.add_resource(Device, '/device', '/device/<string:device_id>')
api.add_resource(NewDevice, '/device/<string:device_type>', '/device/<string:device_type>/<string:device_id>')
api.add_resource(Sensor, '/sensor', '/sensor/<string:sensor_id>')
