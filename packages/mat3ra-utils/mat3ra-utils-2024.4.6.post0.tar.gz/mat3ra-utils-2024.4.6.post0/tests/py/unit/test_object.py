from mat3ra.utils import object as utils

REFERENCE_OBJECT_1 = {"key1": "value1", "key2": "value2"}
REFERENCE_OBJECT_1_WITHOUT_KEY1 = {"key2": "value2"}
REFERENCE_OBJECT_1_WITH_KEY3 = {"key1": "value1", "key2": "value2", "key3": "value3"}
# Using 3 different objects to avoid clashes between tests
REFERENCE_OBJECT_2_CLONE_SHALLOW = {"key2": {"nested_key1": "nested_value1"}}
REFERENCE_OBJECT_2_CLONE_DEEP = {"key2": {"nested_key1": "nested_value1"}}
REFERENCE_OBJECT_2_GET = {"key2": {"nested_key1": "nested_value1"}}


def test_omit():
    object_without_key1 = utils.omit(REFERENCE_OBJECT_1, ["key1"])
    assert object_without_key1 == REFERENCE_OBJECT_1_WITHOUT_KEY1


def test_set():
    object_with_key3 = utils.clone_deep(REFERENCE_OBJECT_1)
    utils.set(object_with_key3, "key3", "value3")
    assert object_with_key3 == REFERENCE_OBJECT_1_WITH_KEY3


def test_clone_shallow():
    object_2_clone_shallow = utils.clone_shallow(REFERENCE_OBJECT_2_CLONE_SHALLOW)
    REFERENCE_OBJECT_2_CLONE_SHALLOW["key2"]["nested_key1"] = "nested_value2"
    assert object_2_clone_shallow["key2"]["nested_key1"] == "nested_value2"


def test_clone_deep():
    object_2_clone_deep = utils.clone_deep(REFERENCE_OBJECT_2_CLONE_DEEP)
    REFERENCE_OBJECT_2_CLONE_DEEP["key2"]["nested_key1"] = "nested_value2"
    assert object_2_clone_deep["key2"]["nested_key1"] == "nested_value1"


def test_get():
    nested_value1 = utils.get(REFERENCE_OBJECT_2_GET, "key2/nested_key1")
    assert nested_value1 == "nested_value1"
    assert nested_value1 == utils.get(REFERENCE_OBJECT_2_GET, "/key2/nested_key1")
    assert nested_value1 == utils.get(REFERENCE_OBJECT_2_GET, "key2.nested_key1", ".")
