import json
import meshtastic.serial_interface
import meshtastic.node
from pubsub import pub
from pprint import pprint


from json_utilities import json_friendly_packet


def on_receive(packet):
    packet = json_friendly_packet(packet)
    print(json.dumps(packet, indent=2))


def on_connection(topic=pub.AUTO_TOPIC):
    pprint(topic)


pub.subscribe(on_receive, "meshtastic.receive")
pub.subscribe(on_connection, "meshtastic.connection.established")

interface = meshtastic.serial_interface.SerialInterface()

if __name__ == '__main__':
    node: meshtastic.Node = interface.localNode
    node.showInfo()
