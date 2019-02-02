from flask import Flask
from flask_restful import Api
from api.resources.device import Device
from api.resources.sensor import Sensor

app = Flask(__name__)
api = Api(app)

api.add_resource(Device, '/device', '/device/<str:id>')
api.add_resource(Sensor, '/sensor', '/sensor/<str:id>')
