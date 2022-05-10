from logging import exception
from os import stat
from urllib import request, response
import requests
from flask import Blueprint
from flask import request
import redis
from datetime import timedelta

api_bp = Blueprint('api_bp', __name__)

def send_request(code):
    code = code.upper()
    response = requests.get(url = f'http://tgftp.nws.noaa.gov/data/observations/metar/stations/{code}.TXT')
    if response.status_code == 200:
        data = response.text.split()
        return data
    else:
        return "404, Not Found."

def celsius_to_farenheit(celsius):
    farenheit = (celsius * 1.8) + 32
    return "{:0.2f}".format(farenheit)

def knots_to_miles(knots):
    miles = int(knots) * 1.151
    return "{:0.2f}".format(miles)

def handle_response(response):
    if response == "404, Not Found.":
        return [{
            "error": "Invalid scode"
        }, 400]
    degrees_to_direction = {
        "N": {
            "min": 348.75,
            "max": 11.25
        },
        "NNE": {
            "min": 11.25,
            "max": 33.75
        },
        "NE": {
            "min": 33.75,
            "max": 56.25
        },
        "ENE": {
            "min": 56.25,
            "max": 78.75
        },
        "E": {
            "min": 78.75,
            "max": 101.25
        },
        "ESE": {
            "min": 101.25,
            "max": 123.75
        },
        "SE": {
            "min": 123.75,
            "max": 146.25
        },
        "SSE": {
            "min": 146.25,
            "max": 168.75
        },
        "S": {
            "min": 168.75,
            "max": 191.25
        },
        "SSW": {
            "min": 191.25,
            "max": 213.75
        },
        "SW": {
            "min": 213.75,
            "max": 236.25
        },
        "WSW": {
            "min": 236.25,
            "max": 258.75
        },
        "W": {
            "min": 258.75,
            "max": 281.25
        },
        "WNW": {
            "min": 281.25,
            "max": 303.75
        },
        "NW": {
            "min": 303.75,
            "max": 326.25
        },
        "NNW": {
            "min": 326.25,
            "max": 348.75
        },
    }
    temp = []
    station = response[2]
    last_observation_date = response[0]
    last_observation_time = response[1]
    for i in response:
        if '/' in i:
            temp.append(i)
        elif 'KT' in i:
            wind_group = i
    wind_degree_direction = float(wind_group[:3])
    for i in degrees_to_direction.keys():
        if wind_degree_direction > degrees_to_direction[i]['min'] and wind_degree_direction < degrees_to_direction[i]['max']:
            wind_cardinal_direction = i
    if 'G' in wind_group:
        wind = f'{wind_cardinal_direction} at {knots_to_miles(wind_group[6:-2])} mph ({wind_group[3:5]} gusting to {wind_group[6:-2]} knots)'
    else:
        wind = f'{wind_cardinal_direction} at {knots_to_miles(wind_group[3:-2])} mph ({wind_group[3:-2]} knots)'  
    temperature = temp[1].split('/')[0]
    if temperature[0] == 'M':
        celsius = float(temperature[1:]) * -1 
    else:
        celsius = float(temperature)
    farenheit = celsius_to_farenheit(celsius)
    current_temperature = f'{celsius} C ({farenheit} F)'
    data = {
            'data': {
                'station': f'{station}',
                'last_observation': f'{last_observation_date} at {last_observation_time} GMT',
                'temperature': f'{current_temperature}',
                'wind': f'{wind}'
            }
        }
    return [data, 200]

def get_result(scode, redis, nocache):
    if nocache:    
        accepted_cache = [1, 2]
        if nocache not in accepted_cache:
            return [{
                "error": "Invalid value for nocache"
            }, 400]
        if nocache in accepted_cache:
            if nocache == 1:
                response = send_request(scode)
                redis.set(scode, f'{response}', 10)
                redis.expire(scode, timedelta(seconds=10))
            elif nocache == 2:
                cache = redis.get(scode)
                if cache: 
                    response = eval(cache.decode('utf-8'))
                    print(f'response if cache: {response}')
                else:
                    response = send_request(scode)
                    if response != "404, Not Found.":
                        print(f'response if not cache: {response}')
                        redis.set(scode, f'{response}', ex=300000)
    try:
        response_to_the_client = handle_response(response)
        print(f'response to the client: {response_to_the_client}')
        return response_to_the_client
    except Exception as e:
        print(f'error: {e}')
        return [{
            "error": f'{e}'
        }, 500]

@api_bp.route('/ping', methods=['GET'])
def ping():
    data = {
        "data": "pong"
    }
    return data, 200

@api_bp.route('/', methods=['GET'])
def home():
    r = redis.Redis(host='127.0.0.1', port=6379)
    scode = request.args.to_dict()['scode']
    try:
        nocache = request.args.to_dict()['nocache']
    except:
        nocache = 2
    result = get_result(scode, r, int(nocache))
    return result[0], result[1]