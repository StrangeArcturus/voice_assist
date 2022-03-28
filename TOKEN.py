from configparser import ConfigParser


parser = ConfigParser()
parser.read('./config.ini')
OWM_TOKEN = parser["owm"]["TOKEN"]
