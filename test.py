
import logging
import statsd_rabbitmq


def go():
	print(statsd_rabbitmq)
	conf = statsd_rabbitmq.load_config("./statsd.json")

	print("Config:")
	print(conf)
	print(conf.is_ignored("exchange", 'amq.direct'))

	instance = statsd_rabbitmq.StatsdPlugin(conf)
	print(instance)
	print(instance.read())

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	go()
