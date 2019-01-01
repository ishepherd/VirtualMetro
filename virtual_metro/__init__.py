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

def dest_to_service_name(dest):
	if dest == 'Parliament':
		return 'City Loop'
	return dest

def parse_date(dtstring):
	return pytz.utc.localize(datetime.strptime(dtstring, '%Y-%m-%dT%H:%M:%SZ')).astimezone(timezone)

ROUTE_TYPE = 0

timezone = pytz.timezone('Australia/Melbourne')

@app.route('/')
@app.route('/index')
def index():
	return flask.render_template('index.html')

@app.route('/latest')
def latest():
	timenow = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
	result = {}
	result['time_offset'] = timenow.utcoffset().total_seconds()
	
	departures = do_request('/v3/departures/route_type/{}/stop/{}'.format(ROUTE_TYPE, flask.request.args['stop_id']), {'platform_numbers': flask.request.args['plat_id'], 'max_results': '5', 'expand': 'all'})
	departures['departures'].sort(key=lambda x: x['scheduled_departure_utc'])
	
	result['stop_name'] = departures['stops'][flask.request.args['stop_id']]['stop_name'].replace(' Station', '')
	
	# Next train
	
	for i, departure in enumerate(departures['departures']):
		if parse_date(departure['estimated_departure_utc'] or departure['scheduled_departure_utc']) < timenow:
			continue
		
		# This is the next train
		result['dest'] = dest_to_service_name(departures['runs'][str(departure['run_id'])]['destination_name'])
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
		stops = do_request('/v3/stops/route/{}/route_type/{}'.format(departure['route_id'], ROUTE_TYPE), {'direction_id': departure['direction_id']})
		stops['stops'].sort(key=lambda x: x['stop_sequence'])
		
		# Calculate stopping pattern until city loop
		num_express = 0 # express_stop_count is unreliable for the city loop
		for j, stop in enumerate(stops['stops']):
			if stop['stop_id'] == int(flask.request.args['stop_id']):
				break
		for stop in stops['stops'][j+1:]:
			if stop['stop_id'] == 1155 or stop['stop_id'] == 1120 or stop['stop_id'] == 1068 or stop['stop_id'] == 1181 or stop['stop_id'] == 1071: # Parliament, MCS, Flagstaff, SXS, Flinders St
				# Calculate stopping pattern in city loop
				pattern['departures'].sort(key=lambda x: x['scheduled_departure_utc'])
				for k, stop2 in enumerate(pattern['departures']):
					if stop2['stop_id'] == stop['stop_id']:
						break
				for stop in pattern['departures'][k:]:
					result['stops'].append(pattern['stops'][str(stop['stop_id'])]['stop_name'].replace(' Station', ''))
				break
			if stop['stop_id'] in pattern_stops:
				result['stops'].append(stop['stop_name'].replace(' Station', ''))
			else:
				result['stops'].append('---')
				num_express += 1
			if stop['stop_id'] == departures['runs'][str(departure['run_id'])]['final_stop_id']:
				break
		
		break
	
	# Next trains
	
	result['next'] = []
	for departure in departures['departures'][i+1:i+3]:
		result['next'].append({})
		result['next'][-1]['dest'] = dest_to_service_name(departures['runs'][str(departure['run_id'])]['destination_name'])
		result['next'][-1]['desc'] = 'Stops All Stations' if num_express == 0 else 'Limited Express'
		result['next'][-1]['sch'] = parse_date(departure['scheduled_departure_utc']).strftime('%I:%M').lstrip('0')
		result['next'][-1]['min'] = '{} min'.format(round((parse_date(departure['estimated_departure_utc'] or departure['scheduled_departure_utc']) - timenow).total_seconds() / 60))
	
	return flask.jsonify(result)

# Cache list of stations
stns = None

@app.route('/stations')
def stations():
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
	
	return flask.render_template('stations.html', stations=stns)
