import onnx
from onnx.tools import update_model_dims
from onnxsim import simplify

input_path = '1088x1920_yolov5n.onnx'
output_path = '1088x1920_yolov5n_modified.onnx'
input_names = ['images']
output_names = ['392', '458', '326']
BATCH = 1
CHANNEL = 3
HEIGHT = 1088
WIDTH = 1920

onnx.checker.check_model(input_path)
model = onnx.load(input_path)

e = onnx.utils.Extractor(model)
extracted = e.extract_model(input_names, output_names)
onnx.checker.check_model(extracted)

static_length_model = update_model_dims.update_inputs_outputs_dims(extracted, {input_names[0]: [int(BATCH), int(CHANNEL), int(HEIGHT), int(WIDTH)]}, {output_names[0]: ['B', 'C','H','W'], output_names[1]: ['B', 'C','H','W'], output_names[2]: ['B', 'C','H','W']})
onnx.checker.check_model(static_length_model)

model_simp, check = simplify(static_length_model)
assert check, "Simplified ONNX model could not be validated"

# Save the ONNX model
onnx.save(model_simp, output_path)


