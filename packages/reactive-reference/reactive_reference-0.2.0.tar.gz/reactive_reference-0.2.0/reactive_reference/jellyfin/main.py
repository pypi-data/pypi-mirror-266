from pprint import pprint

from requests import get

from reactive_reference.jellyfin.common import Jellyfin
from reactive_reference.jellyfin.data import Constants
from reactive_reference.jellyfin.data.Server import Server

API_KEY = "9951ef78de554cfe82231fa416e3a0ba"

server = Server(8096, "192.168.1.168", Constants.Protocols.HTTP, API_KEY)

jellyfin = Jellyfin(server)

res = get(jellyfin.artists_by_name("Blasted Mechanism"))

pprint(res.json())
