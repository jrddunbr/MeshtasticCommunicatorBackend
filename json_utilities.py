import meshtastic


def _spaces(count=0) -> str:
    return "".join([" " for _ in range(count)])


def json_friendly_packet(packet: dict) -> dict:
    raw: meshtastic.mesh_pb2.MeshPacket = packet.pop("raw")
    packet["raw"] = str(raw)
    decoded = packet.pop("decoded")
    packet["decoded"] = jsonify_dict(decoded)
    return packet
    # raw_admin: meshtastic.admin_pb2.AdminMessage = decoded["admin"]["raw"]


def jsonify_set(input_set: set) -> set:
    return set(jsonify_list(list(input_set)))


def jsonify_list(input_list: list) -> list:
    result = []
    for item in input_list:
        item_type = type(item)
        if item_type == dict:
            result.append(jsonify_dict(item))
        elif item_type == list:
            result.append(jsonify_list(item))
        elif item_type == set:
            result.append(jsonify_set(item))
        elif item_type != str or item_type != int or item_type != float:
            result.append(str(item))
        else:
            result.append(item)
    return result


def jsonify_dict(input_dict: dict) -> dict:
    result = {}
    for key in input_dict:
        value_type = type(input_dict[key])
        value = input_dict[key]
        if value_type == dict:
            result[key] = jsonify_dict(value)
        elif value_type == list:
            result[key] = jsonify_list(value)
        elif value_type == set:
            result[key] = jsonify_set(value)
        elif value_type != str or value_type != int or value_type != float:
            result[key] = str(value)
        else:
            result[key] = value
    return result


def render_components(input_dict: dict, level=0):
    if level == 0:
        print("[ Rendering Components ]")
    for component in input_dict:
        level_string = _spaces(level * 4)
        if type(input_dict[component]) == dict:
            print("{}[{} {}:]".format(level_string, component, str(type(input_dict[component]))))
            render_components(input_dict[component], level + 1)
        else:
            print("{}[{} {}:] {}".format(
                level_string,
                component,
                str(type(input_dict[component])),
                input_dict[component]
            ))
    if level == 0:
        print("[ Rendered Components ]")
