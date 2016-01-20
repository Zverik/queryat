# postgresql connection string
CONNECTION = 'dbname=gis'
# prefix to tables
PREFIX='at'
# passed to flask.Debug
DEBUG = False

# max distance to centres in kilometers
MAX_TOWN_DISTANCE = 25
MAX_VILLAGE_DISTANCE = 5
# now distances for which a point is considered inside
TOWN_RADIUS = 2
VILLAGE_RADIUS = 0.4
