from mqttscrobbler import MQTTScrobbler

if __name__ == '__main__':
	scrobbler = MQTTScrobbler()
	print "Starting scrobbler..."
	scrobbler.start()
	print "Scrobbling!"