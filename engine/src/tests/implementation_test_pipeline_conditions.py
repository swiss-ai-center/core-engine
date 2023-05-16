import json
import re

# Test raw text
raw_data = b'image/jpg'
data = raw_data.decode("utf-8")
condition = "data == 'image/jpg'"

condition_passes = eval(condition, {}, {"data": data})

print(condition_passes)  # noqa: T201

# Test JSON object
raw_data = b'{"a": 1}'
data = raw_data.decode("utf-8")
condition = "data['a'] == 1"

condition_passes = eval(condition, {}, {"data": json.loads(data)})

print(condition_passes)  # noqa: T201

# Test from pipeline execution example
raw_data = b'{"areas": [[165, 64, 382, 383]]}'
condition = "len(face-detection.result['areas']) > 0"
inputs = ['pipeline.image', 'face-detection.result']
files = [
    {'reference': 'pipeline.image', 'file_key': 'd4fc5e03-6f5a-4e11-b8af-20ea21aafcc1.jpg'},
    {'reference': 'face-detection.result', 'file_key': json.loads(raw_data)},
]

files_mapping = {}

for file_input in inputs:
    # Change input formatted as `<service>.<input>` to `<service>_<input>` and replace all `.` to `_`
    file_input_one_word = re.sub(r"[-.]", "_", file_input)

    # Replace in the condition the formatted input
    condition = condition.replace(file_input, file_input_one_word)

    # Map the new formatted input with the downloaded file
    for file in files:
        if file["reference"] == file_input:
            files_mapping[file_input_one_word] = file["file_key"]
            break

# Check the condition based on the files mapping
condition_passes = eval(condition, {}, files_mapping)

print(condition_passes)  # noqa: T201
