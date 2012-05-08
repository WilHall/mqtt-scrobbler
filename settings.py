import logging
import nyamuk.nyamuk_const as NC

## General
#
# Interval (in seconds) to poll for scrobbled tracks
poll_interval = 30

# Print iformation about scrobbled songs to the console
print_info = True

# Print debug information
print_debug = False
##

## last.fm settings
#
lastfm_apikey = ""
lastfm_user = ""
##

## MQTT settings
#
mqtt_clientid = "mqttscrobbler"
mqtt_username = None
mqtt_password = None
mqtt_server = "localhost"
mqtt_port = 1883
mqtt_keepalive = NC.KEEPALIVE_VAL
mqtt_loglevel = logging.INFO

# List of topics to publish scrobble messages to
mqtt_topics = ["lastfm"]

# Format string for the scrobble messages.
# See: http://docs.python.org/library/stdtypes.html#string-formatting
# 
# Possible values are:
# 
# mqtt_clientid, mqtt_username, mqtt_topic, lastfm_user, track_name, track_album, track_artist, track_duration, track_playcount, track_url, track_scrobbled_time
mqtt_scrobble_string = "%(mqtt_clientid)s just scrobbled '%(track_name)s' by %(track_artist)s at %(track_scrobbled_time)s"
##
