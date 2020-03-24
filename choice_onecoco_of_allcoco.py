import os,sys
import json

coco_file = sys.argv[1]
images = []
annotations = []
categories = []
with open(coco_file) as f:
    coco_data = json.load(f)
for image_data in coco_data['images']:
    image_name = image_data['file_name']
    if 'bswd' in image_name:
        images.append(image_data)
idx = 0
for anno_data in coco_data['annotations']:
    image_name = anno_data['image_id']
    if 'bswd' in image_name:
        anno_data['id'] = idx
        annotations.append(anno_data)
        idx += 1
for category in coco_data['categories']:
    categories.append(category)

result = {"images": images,
          "annotations": annotations,
          "categories": categories
         }
with open('bswd.coco', 'w') as f:
    json.dump(result, f, indent=4)

