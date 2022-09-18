import json
import meshtastic.serial_interface
import meshtastic.node
from pubsub import pub
from pprint import pprint
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

from json_utilities import json_friendly_packet, jsonify_dict, render_components

HEXADECIMAL_STRING_CHARS = "0123456789abcdef"

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


packets = []


def on_receive(packet):
    packet = json_friendly_packet(packet)
    packets.append(packet)


def on_connection(topic=pub.AUTO_TOPIC):
    pprint(topic)


def is_node_id_valid(node_id: str) -> bool:
    return node_id.startswith("!") and \
           len(node_id) == 9 and \
           len([x for x in node_id.lower() if x in HEXADECIMAL_STRING_CHARS]) == 8


def send_message(destination: str, message: str) -> str:
    packet = {"fromId": "", "toId": destination, "decoded": {"text": message, "portnum": "TEXT_MESSAGE_APP"}}
    packets.append(packet)
    print(json.dumps(packets, indent=2))
    return str(interface.sendText(message, destination, True, False, 3))


def save_messages():
    packets_serialized = json.dumps(packets)
    try:
        with open("mesh_msgs.json", "w") as f:
            f.write(packets_serialized)
    except Exception as e:
        print(e)


def load_messages():
    try:
        with open("mesh_msgs.json") as f:
            packets_serialized = f.read()
            packets.append(json.loads(packets_serialized))
    except Exception as e:
        print(e)


@app.route("/")
def flask_main():
    return jsonify({})


@app.route("/get_nodes")
def flast_get_nodes():
    nodes_list = []
    for node_key in interface.nodes:
        try:
            node_value = interface.nodes[node_key]
            node_details = {}

            if "snr" in node_value:
                node_details["snr"] = float(node_value["snr"])

            if "deviceMetrics" in node_value:
                if "batteryLevel" in node_value["deviceMetrics"]:
                    node_details["battery_level"] = float(node_value["deviceMetrics"]["batteryLevel"])
                if "voltage" in node_value["deviceMetrics"]:
                    node_details["voltage"] = float(node_value["deviceMetrics"]["voltage"])

            if "user" in node_value:
                if "id" in node_value["user"]:
                    node_details["node_id"] = node_value["user"]["id"]
                if "longName" in node_value["user"]:
                    node_details["node_name"] = node_value["user"]["longName"]
                if "shortName" in node_value["user"]:
                    node_details["node_short_name"] = node_value["user"]["shortName"]

            try:
                node_details["last_heard"] = str(datetime.utcfromtimestamp(float(node_value["lastHeard"])))
            except Exception as e:
                print(e)

            nodes_list.append(node_details)
        except Exception as e:
            print(e)

    return jsonify(nodes_list)


@app.route("/get_messages")
def flask_get_messages():
    # print(json.dumps(packets, indent=2))

    messages_list = []

    for message in packets:
        message_details = {}
        if "fromId" in message:
            message_details["source"] = message["fromId"]
        if "toId" in message:
            message_details["destination"] = message["toId"]
        if "rxSnr" in message:
            message_details["snr"] = message["rxSnr"]
        if "rxRssi" in message:
            message_details["rssi"] = message["rxRssi"]
        if "decoded" in message:
            if "text" in message["decoded"]:
                message_details["message"] = message["decoded"]["text"]
            if "portnum" in message["decoded"]:
                message_details["portnum"] = message["decoded"]["portnum"]
        messages_list.append(message_details)
    return jsonify(messages_list)


@app.route("/send_message", methods=['POST'])
def flask_send_message():
    if request.method == 'POST':
        if "destination" in request.json and "message" in request.json:
            destination, message = request.json["destination"], request.json["message"]
            if type(destination) != str or type(message) != str:
                return jsonify({"error": "destination or message invalid"})
            if not is_node_id_valid(destination):
                return jsonify({"error": "destination {} not valid".format(destination)})
            result = send_message(destination, message)
            return jsonify({"result": result})
        return jsonify({"error": "destination or message not in request"})
    return jsonify({"error": "use POST requests"})


pub.subscribe(on_receive, "meshtastic.receive")
pub.subscribe(on_connection, "meshtastic.connection.established")

interface = meshtastic.serial_interface.SerialInterface()

if __name__ == '__main__':
    try:
        load_messages()
        node: meshtastic.Node = interface.localNode
        app.run(port=5643)
    except Exception as e:
        print(e)
        print("Got keyboard interrupt, exiting application")
        save_messages()
