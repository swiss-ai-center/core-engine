import json

# Test raw text
raw_data = b'image/jpeg'
data = raw_data.decode("utf-8")
condition = "data == 'image/jpg'"

print(eval(condition, {}, {"data": data}))


# Test JSON object
raw_data = b'{"a": 1}'
data = raw_data.decode("utf-8")
condition = "data['a'] == 1"

print(eval(condition, {}, {"data": json.loads(data)}))
