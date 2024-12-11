import json

def read_json():
    # Read max level achieved and eroded levels
    with open("info.json", 'r') as file:
        json_dict = json.loads(file.read())
        return json_dict['max level achieved'], json_dict['eroded']

def update_json(max_level_achieved, eroded):
    # Store max level achieved and eroded levels
    with open("info.json", 'w') as file:
        json_dict = {"max level achieved":max_level_achieved, "eroded":eroded}
        json_string = json.dumps(json_dict)
        file.write(json_string)
