from datetime import datetime
import lastfm as _lastfm
from nyamuk import nyamuk
import nyamuk.nyamuk_const as NC
from nyamuk import event

import settings

class MQTTConnectionError(Exception):
	pass

def timestamp(dtobj=None):
	if not dtobj:
		return datetime.strftime(datetime.now(), "%H:%M:%S")
	else:
		return dtobj.strftime("%H:%M:%S")

class MQTTScrobbler():

	def __init__(self):

		# Nyamuk MQTT client instance
		self.mqtt = nyamuk.Nyamuk(	settings.mqtt_clientid,
									username=settings.mqtt_username,
									password=settings.mqtt_password,
									server=settings.mqtt_server,
									port=settings.mqtt_port,
									keepalive=settings.mqtt_keepalive,
									log_level=settings.mqtt_loglevel
									)

		# lastfm API wrapper instance
		self.lastfm = _lastfm.Api("be8771910e590930c2fc25bea9a8fc25")

		self.lastfm_user = self.lastfm.get_user(settings.lastfm_user)

		self.last_track_id = 0
		self.last_poll = datetime.now()
		self.connected = False
		self.rc = None

	def start(self):
		self.rc = self.mqtt.connect()
		if self.rc != NC.ERR_SUCCESS:
			raise MQTTConnectionError("Could not connect to MQTT server (%s)" % rc)
		self.loop()

	def poll_interval_elapsed(self):
		if (datetime.now() - self.last_poll).seconds < 60:
			return False
		else:
			return True

	def poll(self):
		track = self.lastfm_user.most_recent_track

		if track is not None:
			track._fill_info()

			if track.id != self.last_track_id:
				if settings.print_debug:
					print "DEBUG: Scrobbling replay"
				self.scrobble(track)

	def scrobble(self, track):
		self.last_track_id = track.id

		for topic in settings.mqtt_topics:
			mins = (track.duration / 1000) / 60
			secs = track.duration - (60 * mins)

			scrobble_payload = settings.mqtt_scrobble_string % \
						{	'mqtt_clientid': settings.mqtt_clientid,
							'mqtt_username': settings.mqtt_username,
							'mqtt_topic': topic,
							'lastfm_user': settings.lastfm_user,
							'track_name': track.name,
							'track_album': track.album,
							'track_artist': track.artist.name,
							'track_duration': "%s:%s" % (mins, secs),
							'track_playcount': track.stats.playcount,
							'track_url': track.url,
							'track_scrobbled_time': timestamp(track.played_on)
							}

			if settings.print_info:
				print "Published: ", scrobble_payload

			self.mqtt.publish(topic, scrobble_payload)

	def loop(self):
		while self.rc == NC.ERR_SUCCESS:
			event = self.mqtt.pop_event()
			if event != None:
				if event.type == NC.CMD_CONNACK:
					if event.ret_code == NC.CONNECT_ACCEPTED:
						self.poll()
						self.connected = True
					else:
						raise MQTTConnectionError("MQTT connection was refused by the server (%s)" % event.ret_code)
			
			if self.connected:
				if self.poll_interval_elapsed():
					self.poll()
					self.last_poll = datetime.now()
			
			self.mqtt.loop()