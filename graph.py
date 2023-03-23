import uuid
import wikipediaapi


class Graph:
    def __init__(self):
        self.nodes = {}
        self.valuelinks = {}

    def add_node(self, node):
        self.nodes[node.token_hash] = node

    def add_valuelink(self, valuelink):
        self.valuelinks[valuelink.id] = valuelink

    def query_nodes(self, query_hash=None):
        if query_hash is not None:
            matching_nodes = [
                node for node in self.nodes.values()
                if node.token_hash.startswith(query_hash)
            ]
            return [node.serialize() for node in matching_nodes]
        else:
            return [node.serialize() for node in self.nodes.values()]

    def serialize_valuelinks(self):
        return [valuelink.serialize() for valuelink in self.valuelinks.values()]


class Node:
    def __init__(self, token_hash, wiki_title, base_currency, wiki_content=None, image_url=None):
        self.token_hash = token_hash
        self.wiki_title = wiki_title
        self.base_currency = base_currency
        self.wiki_content = wiki_content
        self.valuelinks = set()
        self.image_url = image_url  # added image_url attribute

    def serialize(self):
        return {
            "token_hash": self.token_hash,
            "wiki_title": self.wiki_title,
            "base_currency": self.base_currency,
            "wiki_content": self.wiki_content,
            "image_url": self.image_url,  # added image_url to serialized output
            "valuelinks": [valuelink.id for valuelink in self.valuelinks]
        }




class ValueLink:
    def __init__(self, node_1, node_2):
        self.id = str(uuid.uuid4())
        self.node_1 = node_1
        self.node_2 = node_2

    def serialize(self):
        return {
            "id": self.id,
            "node_1": self.node_1.serialize(),
            "node_2": self.node_2.serialize()
        }
