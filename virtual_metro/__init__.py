#!/usr/bin/env python3

import flask
app = flask.Flask(__name__)

from . import config

import hashlib
import hmac
import json
import pytz
from binascii import hexlify
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def do_request(endpoint, args=None):
	url = endpoint + '?devid=' + config.PTV_USER_ID
	if args:
		url += '&' + urlencode(args)
	
	# Generate signature
	signature = hexlify(hmac.digest(config.PTV_API_KEY.encode('ascii'), url.encode('ascii'), 'sha1')).decode('ascii')
	
	req = Request('https://timetableapi.ptv.vic.gov.au' + url + '&signature=' + signature, headers={'User-Agent': 'virtual-metro/0.1'})
	resp = urlopen(req)
	return json.load(resp)

def parse_date(dtstring):
	return pytz.utc.localize(datetime.strptime(dtstring, '%Y-%m-%dT%H:%M:%SZ')).astimezone(timezone)

ROUTE_TYPE = 0
LOOP_STATIONS = ['Parliament', 'Melbourne Central', 'Flagstaff', 'Southern Cross', 'Flinders Street']

timezone = pytz.timezone('Australia/Melbourne')

@app.route('/')
@app.route('/index')
def index():
	return flask.render_template('index.html')

def stop_to_name(stop, route_id):
	name = stop['stop_name']
	if name.endswith(' Station'):
		name = name[:-8]
	if name == 'Flemington Racecourse' and route_id and route_id != 16 and route_id != 17 and route_id != 1482:
		# PTV bug??
		name = 'South Kensington'
	return name

route_stops = {} # Cache lookup
def parse_departure(departure, departures, timenow):
	result = {}
	result['dest'] = departures['runs'][str(departure['run_id'])]['destination_name']
	result['sch'] = parse_date(departure['scheduled_departure_utc']).strftime('%I:%M').lstrip('0')
	mins = (parse_date(departure['estimated_departure_utc'] or departure['scheduled_departure_utc']) - timenow).total_seconds() / 60
	if mins < 0.5:
		result['now'] = 'NOW'
	else:
		result['min'] = round(mins)
	
	# Get stopping pattern
	result['stops'] = []
	pattern = do_request('/v3/pattern/run/{}/route_type/{}'.format(departure['run_id'], ROUTE_TYPE), {'expand': 'all'})
	pattern_stops = set(x['stop_id'] for x in pattern['departures'])
	
	# Get all stops on route
	if (departure['route_id'], departure['direction_id']) not in route_stops:
		stops = do_request('/v3/stops/route/{}/route_type/{}'.format(departure['route_id'], ROUTE_TYPE), {'direction_id': departure['direction_id']})
		stops['stops'].sort(key=lambda x: x['stop_sequence'])
		route_stops[(departure['route_id'], departure['direction_id'])] = stops['stops']
	
	route_stops_dir = route_stops[(departure['route_id'], departure['direction_id'])]
	
	# Calculate stopping pattern
	express_stops = [] # express_stop_count is unreliable for the city loop
	num_city_loop = 0
	done_city_loop = False
	for j, stop in enumerate(route_stops_dir):
		if stop['stop_id'] == int(flask.request.args['stop_id']):
			break
	for stop in route_stops_dir[j+1:]:
		if stop['stop_name'].replace(' Station', '') in LOOP_STATIONS:
			# Calculate stopping pattern in city loop
			if done_city_loop:
				continue
			
			pattern['departures'].sort(key=lambda x: x['scheduled_departure_utc'])
			for k, stop2 in enumerate(pattern['departures']):
				if stop2['stop_id'] == stop['stop_id']:
					break
			for stop in pattern['departures'][k:]:
				result['stops'].append(pattern['stops'][str(stop['stop_id'])]['stop_name'].replace(' Station', ''))
				num_city_loop += 1
			
			done_city_loop = True
		elif stop['stop_id'] in pattern_stops:
			result['stops'].append(stop['stop_name'].replace(' Station', ''))
		else:
			result['stops'].append('   ---')
			express_stops.append(stop['stop_name'].replace(' Station', ''))
		if stop['stop_id'] == departures['runs'][str(departure['run_id'])]['final_stop_id']:
			break
	
	# Impute remainder of journey
	if result['stops'][-1] == 'Parliament':
		result['stops'].append('Melbourne Central')
		result['stops'].append('Flagstaff')
		result['stops'].append('Southern Cross')
		result['stops'].append('Flinders Street')
		num_city_loop += 4
	
	result['dest'] = result['stops'][-1]
	if result['dest'] in LOOP_STATIONS:
		# Up train
		# Is this a City Loop train?
		if num_city_loop >= 3:
			result['dest'] = 'City Loop'
		result['desc'] = 'All Except {}'.format(express_stops[0]) if len(express_stops) == 1 else 'Limited Express' if len(express_stops) > 1 else 'Stops All Stations'
	else:
		# Down train
		# Is this a via City Loop train?
		if num_city_loop >= 3:
			result['desc'] = 'Ltd Express via City Loop' if len(express_stops) > 1 else 'Stops All via City Loop'
		else:
			result['desc'] = 'All Except {}'.format(express_stops[0]) if len(express_stops) == 1 else 'Limited Express' if len(express_stops) > 1 else 'Stops All Stations'
	
	return result

@app.route('/latest')
def latest():
	timenow = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
	result = {}
	result['time_offset'] = timenow.utcoffset().total_seconds()
	
	departures = do_request('/v3/departures/route_type/{}/stop/{}'.format(ROUTE_TYPE, flask.request.args['stop_id']), {'platform_numbers': flask.request.args['plat_id'], 'max_results': '5', 'expand': 'all'})
	departures['departures'].sort(key=lambda x: x['scheduled_departure_utc'])
	
	if len(departures['departures']) == 0:
		# Invalid stop ID, platform ID, no departures, etc.
		return flask.jsonify(result)
	
	result['stop_name'] = departures['stops'][flask.request.args['stop_id']]['stop_name'].replace(' Station', '')
	
	# Next train
	
	for i, departure in enumerate(departures['departures']):
		if parse_date(departure['estimated_departure_utc'] or departure['scheduled_departure_utc']) < timenow:
			continue
		
		# This is the next train
		result.update(parse_departure(departure, departures, timenow))
		
		break
	
	# Next trains
	
	result['next'] = []
	for departure in departures['departures'][i+1:i+3]:
		result['next'].append(parse_departure(departure, departures, timenow))
	
	return flask.jsonify(result)

# Cache list of stations
stns = None

def get_station_list():
	global stns
	if not stns:
		stn_list = {}
		
		routes = do_request('/v3/routes', {'route_types': ROUTE_TYPE})
		for route in routes['routes']:
			stops = do_request('/v3/stops/route/{}/route_type/{}'.format(route['route_id'], ROUTE_TYPE), {})
			for stop in stops['stops']:
				stn_list[stop['stop_id']] = stop['stop_name'].replace(' Station', '')
		
		stns = [(k, v) for k, v in stn_list.items()]
		stns.sort(key=lambda x: x[1])

if not app.debug:
	get_station_list()

@app.route('/stations')
def stations():
	get_station_list()
	return flask.render_template('stations.html', stations=stns)
