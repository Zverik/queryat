# Query Admin/Towns

A simple API for querying administrative entities and towns for a point. Call
it a geocoder if you like. Works on the OpenStreetMap software stack.

## Setup

* Download [a planet](http://planet.openstreetmap.org/).
* Install osmctools (you know, osmconvert and such).
* `osmconvert planet-latest.osm.pbf -o=planet-latest.o5m`
* `osmfilter planet-latest.o5m --keep="admin_level=2 =4 place=city =town =village =hamlet" -o=at.o5m`
* `osm2pgsql -d gis --slim --drop -S at.style --number-processes 6 -p at -l -C 8000 at.o5m`
* Did I mention to install PostgreSQL, PostGIS and osm2pgsql? No?

The database would be around 3 GB. You can do a little cleanup:

* `psql gis`
* `drop table at_roads; drop table at_line;`
* `delete from at_point where place is null;`
* `\q`

Now set up the API. You can just run `queryat.py`, which creates a server at `localhost:5000`,
but it's better to learn WSGI and use the supplied `queryat.wsgi` file.

## API

`localhost/queryat/q?lat=12.345&lon=67.890` would give you a JSON with names (and translations,
see the source code and `at.style`) for each administrative division and town that have that point.

## Author and License

This script was written by Ilya Zverev and published under WTFPL.
