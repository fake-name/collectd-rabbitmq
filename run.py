
import logging
import time
import statsd_rabbitmq


def go():
	conf = statsd_rabbitmq.load_config("./statsd.json")
	instance = statsd_rabbitmq.StatsdPlugin(conf)
	while 1:
		instance.read()
		time.sleep(10)


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	go()
