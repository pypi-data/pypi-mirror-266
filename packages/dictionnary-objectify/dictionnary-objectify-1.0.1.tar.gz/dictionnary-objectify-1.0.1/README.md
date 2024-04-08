# Objectify

### Common Usage

```py
from dictionnary_objectify import to_object

dictionnary = {
    "some_key": "some_value",
    "some_other_key": {
        "some_sub_key": "some_sub_value"
    }
}

object = dictionnary.to_object()

print(object.some_key)
# output : "some_value"

print(object.some_other_key.some_sub_key)
# output : "some_sub_value"
```