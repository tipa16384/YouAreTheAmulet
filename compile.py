import json
import yaml

yaml_fn = 'amulet.yaml'
json_fn = 'amulet.dat'

with open(yaml_fn, "r", encoding="utf-8") as stream:
    try:
        game_yaml = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

with open(json_fn, "w", encoding="utf-8") as stream:
    json.dump(game_yaml, stream)
