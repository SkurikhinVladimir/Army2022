import json


def coco2GNS(coco_ann):
    new_ann = {
        "version": 1,
        "image": {
            "representation": "",
            "value": ""
        },
        "annotation": []
    }

    categories = {cat['id']: cat['name'] for cat in coco_ann['categories']}
    for ann in coco_ann['annotations']:
        new_shape = {
            'type': 'rectangle',
            'exterior': [[round(ann['bbox'][0]), round(ann['bbox'][1])],
                         [round(ann['bbox'][0] + ann['bbox'][2]), round(ann['bbox'][1] + ann['bbox'][3])]],
            'interior': []
        }
        new_ann['annotation'].append({
            'description': 'ObjectDetection',
            'class': categories[ann['category_id']],
            'shape': new_shape
        })

    return new_ann


with open('coco/output.json', 'r') as f:
    coco_ann = json.load(f)
new_ann = coco2GNS(coco_ann)

with open('new_annotation.json', 'w') as f:
    json.dump(new_ann, f, indent=4)