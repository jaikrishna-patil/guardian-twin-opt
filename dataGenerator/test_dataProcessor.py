import pytest
from dataProcessor import Process

@pytest.fixture
def process():
    return Process()

def test_process_node_dict(process):
    node_dict = {
        "key1": "value1",
        "key2": {
            "nested_key1": "nested_value1",
            "nested_key2": "nested_value2"
        },
        "key3": ["item1", "item2", "item3"]
    }
    processed_node = process.process_node(node_dict)
    assert processed_node == {
        "key1": "value1",
        "key2": {
            "nested_key1": "nested_value1",
            "nested_key2": "nested_value2"
        },
        "key3": ["item1", "item2", "item3"]
    }

def test_process_node_list(process):
    node_list = ["item1", "item2", "item3"]
    processed_node = process.process_node(node_list)
    assert processed_node == ["item1", "item2", "item3"]

def test_process_node_other(process):
    node = "value"
    processed_node = process.process_node(node)
    assert processed_node == "value"
    
def test_process_node_dict_empty(process):
    node_dict = {}
    processed_node = process.process_node(node_dict)
    assert processed_node == {}

def test_process_node_list_empty(process):
    node_list = []
    processed_node = process.process_node(node_list)
    assert processed_node == []

def test_process_node_str(process):
    node_str = "value"
    processed_node = process.process_node(node_str)
    assert processed_node == "value"

def test_process_node_nested_dict(process):
    node_dict = {
        "key1": {
            "nested_key1": {
                "nested_nested_key1": "nested_nested_value1"
            }
        }
    }
    processed_node = process.process_node(node_dict)
    assert processed_node == {
        "key1": {
            "nested_key1": {
                "nested_nested_key1": "nested_nested_value1"
            }
        }
    }

def test_process_node_nested_list(process):
    node_list = [
        ["item1", "item2"],
        ["item3", "item4"]
    ]
    processed_node = process.process_node(node_list)
    assert processed_node == [
        ["item1", "item2"],
        ["item3", "item4"]
    ]