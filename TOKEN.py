from configparser import ConfigParser


parser = ConfigParser()
parser.read('./config.ini')
OWM_TOKEN = "2afe45612bb32f481b11c81e353e6b9f"
#OWM_TOKEN = parser["owm"]["TOKEN"]
