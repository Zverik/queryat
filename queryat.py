#!/usr/bin/python
from flask import Flask, g, request, json, jsonify, abort
from flask.ext.cors import CORS
import psycopg2, config
from psycopg2.extras import DictCursor

app = Flask(__name__)
app.debug=config.DEBUG
CORS(app)

@app.route('/')
def what():
  return 'Query Admin/Towns API.'

def extract_names(row):
  """Returns a dict with names from the database."""
  result = {}
  for col in row.keys():
    if col == 'name':
      result['name'] = row[col]
    elif 'name:' in col and row[col]:
      result[col[5:]] = row[col]
  return result

@app.route('/q')
def query():
  lat = request.args.get('lat')
  lon = request.args.get('lon')
  conn = psycopg2.connect(config.CONNECTION)
  cur = conn.cursor(cursor_factory=DictCursor)
  cur.execute("""SELECT * FROM {}_polygon WHERE ST_Contains(way, ST_SetSRID(ST_Point(%s, %s), 4326));""".format(config.PREFIX), (lon, lat))
  countries = []
  regions = []
  village = None
  town = None
  for row in cur:
    names = extract_names(row)
    if row['admin_level'] == '2':
      countries.append(names)
    elif row['admin_level'] == '4':
      regions.append(names)
    elif row['place'] == 'city' or row['place'] == 'town':
      town = names
    elif row['place']:
      village = names

  if village is None:
    cur.execute("""SELECT *, ST_Distance(way::geography, ST_SetSRID(ST_Point(%s, %s), 4326)::geography) as d FROM {}_point WHERE place not in ('city', 'town') ORDER BY way <#> ST_SetSRID(ST_Point(%s, %s), 4326) LIMIT 1""".format(config.PREFIX), (lon, lat, lon, lat))
    res = cur.fetchone()
    if res and res['d'] < config.MAX_VILLAGE_DISTANCE * 1000:
      village = extract_names(res)
      if res['d'] > config.VILLAGE_RADIUS * 1000:
        village['distance'] = res['d'] / 1000

  if town is None:
    cur.execute("""SELECT *, ST_Distance(way::geography, ST_SetSRID(ST_Point(%s, %s), 4326)::geography) as d FROM {}_point WHERE place in ('city', 'town') ORDER BY way <#> ST_SetSRID(ST_Point(%s, %s), 4326) LIMIT 1""".format(config.PREFIX), (lon, lat, lon, lat))
    res = cur.fetchone()
    if res and res['d'] < config.MAX_TOWN_DISTANCE * 1000:
      town = extract_names(res)
      if (village is None or 'distance' in village) and res['d'] > config.TOWN_RADIUS * 1000:
        town['distance'] = res['d'] / 1000

  conn.close()
  return jsonify(countries=countries, regions=regions, village=village, town=town)

if __name__ == '__main__':
	app.run(threaded=True)