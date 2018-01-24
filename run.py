
import logging
import time
import traceback
import statsd_rabbitmq


def go():
	conf = statsd_rabbitmq.load_config("/etc/statsd-rabbitmq/statsd-rabbitmq-conf.json")
	instance = statsd_rabbitmq.StatsdPlugin(conf)
	while 1:
		try:
			instance.read()
		except Exception:
			traceback.print_exc()
		time.sleep(10)


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	go()
