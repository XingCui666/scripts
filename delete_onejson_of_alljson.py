import os,sys
import json

json_file = sys.argv[1]
save_name = sys.argv[2]
root_dir = os.path.dirname(json_file)
with open(json_file) as f:
    json_data = json.load(f)
result = {}
for image_name in json_data:
    if 'UnknownSensorType' in image_name:
        continue
    result[image_name] = json_data[image_name]
with open(os.path.join(root_dir, save_name), 'w') as f:
    json.dump(result, f, indent=4, sort_keys=True)
