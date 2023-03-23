# app.py
from flask import Flask, request, jsonify, render_template, abort
from functools import partial
import wikipediaapi
import hashlib
from graph import Node, ValueLink, Graph
import uuid
import datetime
import requests
import urllib.parse
import time
import wikipedia
import random

app = Flask(__name__)
graph = Graph()
wiki_wiki = wikipediaapi.Wikipedia('en')

def get_wikipedia_image(title):
    try:
        page = wikipedia.page(title, auto_suggest=False)
        images = page.images
        for image in images:
            if image.endswith(".jpg") or image.endswith(".png"):
                return image
    except wikipedia.exceptions.PageError:
        print(f"Page for '{title}' not found")
    except wikipedia.exceptions.DisambiguationError:
        print(f"'{title}' is ambiguous")
    return None


def get_wikipedia_content(title):
    page = wiki_wiki.page(title)
    if page.exists():
        return page.text, page.fullurl
    else:
        return None, None


def hash_node(wiki_title, base_currency):
    return str(uuid.uuid4())


def hash_wikipedia_content_image_url():
    content_hash = str(uuid.uuid4())
    image_hash = str(uuid.uuid4())
    url_hash = str(uuid.uuid4())
    return content_hash, image_hash, url_hash


@app.route('/add_nodes_from_links', methods=['POST'])
def add_nodes_from_links():
    token_hash = request.json.get("token_hash")
    node = graph.nodes.get(token_hash)
    if not node:
        return jsonify({"error": "Node not found"}), 404

    new_nodes = []

    wiki_links = get_wikipedia_links(node.wiki_title)
    for link in wiki_links[:5]:
        wiki_content, wiki_url = get_wikipedia_content(link)
        if wiki_content:
            content_hash, image_hash, url_hash = hash_wikipedia_content_image_url()
            link_hash = hash_node(link, node.base_currency)
            new_node = Node(token_hash=link_hash, wiki_title=link, base_currency=node.base_currency, wiki_content=wiki_content)
            new_node.image_url = get_wikipedia_image(link)
            graph.add_node(new_node)
            valuelink = ValueLink(node, new_node)
            graph.add_valuelink(valuelink)
            new_nodes.append(new_node)

            quest_and_factory_items = [
                {
                    "quest_id": link_hash,
                    "kind": "TITLE",
                    "content": link,
                    "following_id": None,
                },
                {
                    "quest_id": content_hash,
                    "kind": "BODY",
                    "content": wiki_content,
                    "following_id": link_hash,
                },
                {
                    "quest_id": image_hash,
                    "kind": "IMAGE",
                    "content": new_node.image_url or "",
                    "following_id": link_hash,
                },
            ]

            quest_headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }

            factory_headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }

            for item in quest_and_factory_items:
                quest_data = {
                    "quest": {
                        "id": item["quest_id"],
                        "kind": item["kind"],
                        "content": item["content"]
                    }
                }

                if item["following_id"]:
                    quest_data["followingId"] = item["following_id"]

                quest_response = requests.post('https://quests-staging-alt.fly.dev:3000/quest', headers=quest_headers, json=quest_data)

                # Check if the quest request was successful
                if quest_response.status_code != 200:
                    print("Error in quest_response:")
                    print("URL: https://quests-staging-alt.fly.dev:3000/quest")
                    print("Status code:", quest_response.status_code)
                    print("Content:", quest_response.text)
                    return "Error: Failed to add quest"

                # Generate a random account name
                account_name = str(uuid.uuid4())

                factory_data = {
                    "id": item["quest_id"],
                    "account": account_name
                }

                factory_response = requests.post('https://quests-staging-alt.fly.dev:3000/factory', headers=factory_headers, json=factory_data)

                if factory_response.status_code != 200:
                    print("Error in quest_response:")
                    print("URL: https://quests-staging-alt.fly.dev:3000/factory")
                    print("Status code:", factory_response.status_code)
                    print("Content:", factory_response.text)
                    return "Error: Failed to add quest"

            # Create value links between nodes
            valuelink_data = {
                "followerId": new_node.token_hash,
                "followingId": node.token_hash
            }
            valuelink_headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
            valuelink_response = requests.post('https://quests-staging-alt.fly.dev:3000/value_link', headers=valuelink_headers, json=valuelink_data)

            if valuelink_response.status_code != 200:
                print("Error in quest_response:")
                print("URL: https://quests-staging-alt.fly.dev:3000/value_link")
                print("Status code:", valuelink_response.status_code)
                print("Content:", valuelink_response.text)
                print("Follower ID:", node.token_hash)
                print("Following ID:", new_node.token_hash)
                return "Error: Failed to add quest"


    return jsonify({"message": "Nodes and edges added from links", "nodes": [node.serialize() for node in new_nodes]})


def get_wikipedia_links(title):
    page = wiki_wiki.page(title)
    if page.exists():
        links = list(page.links)
        random.shuffle(links)  # Shuffle the links randomly
        return links[:5]  # Return only the first 5 links
    else:
        return []


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/add_node', methods=['POST'])
def add_node():
    wiki_title = request.json.get("wiki_title")
    base_currency = request.json.get("base_currency")

    if wiki_title:
        wiki_content, wiki_url = get_wikipedia_content(wiki_title)
        if not wiki_content:
            return jsonify({"error": "Wikipedia content not found"}), 404
        image_url = get_wikipedia_image(wiki_title)
        token_hash = hash_node(wiki_title, base_currency)
        content_hash, image_hash, url_hash = hash_wikipedia_content_image_url()
        new_node = Node(token_hash=token_hash, wiki_title=wiki_title, base_currency=base_currency, wiki_content=wiki_content, image_url=image_url)
        graph.add_node(new_node)

    quest_and_factory_items = [
        {
            "quest_id": token_hash,
            "kind": "TITLE",
            "content": wiki_title,
            "following_id": None,
        },
        {
            "quest_id": content_hash,
            "kind": "BODY",
            "content": wiki_content,
            "following_id": token_hash,
        },
        {
            "quest_id": image_hash,
            "kind": "IMAGE",
            "content": image_url,
            "following_id": token_hash,
        },
    ]

    quest_headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    factory_headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Generate a random account name
    account_name = str(uuid.uuid4())

    for item in quest_and_factory_items:
        quest_data = {
            "quest": {
                "id": item["quest_id"],
                "kind": item["kind"],
                "content": item["content"]
            }
        }

        if item["following_id"]:
            quest_data["followingId"] = item["following_id"]

        quest_response = requests.post('https://quests-staging-alt.fly.dev:3000/quest', headers=quest_headers, json=quest_data)

        # Check if the quest request was successful
        if quest_response.status_code != 200:
            return "Error: Failed to add quest"

        factory_data = {
            "id": item["quest_id"],
            "account": account_name
        }

        factory_response = requests.post('https://quests-staging-alt.fly.dev:3000/factory', headers=factory_headers, json=factory_data)

        if factory_response.status_code != 200:
            print("Factory response status code:", factory_response.status_code)
            print("Factory response content:", factory_response.text)
            return "Error: Failed to add factory"

    return jsonify({"message": "Nodes added and posted to the endpoints"})


@app.route("/valuelink", methods=["POST"])
def add_link():
    token_hash_1 = request.json.get("token_hash_1")
    token_hash_2 = request.json.get("token_hash_2")
    if not token_hash_1 or not token_hash_2:
        return jsonify({"error": "Missing required fields"}), 400
    node_1 = graph.nodes.get(token_hash_1)
    node_2 = graph.nodes.get(token_hash_2)
    if not node_1 or not node_2:
        return jsonify({"error": "Node(s) not found"}), 404
    valuelink = ValueLink(node_1, node_2)
    node_1.valuelinks.add(valuelink)  # Add the valuelink to node_1
    node_2.valuelinks.add(valuelink)  # Add the valuelink to node_2
    graph.add_valuelink(valuelink)
    return jsonify({"link_id": valuelink.id})


@app.route("/query", methods=["GET"])
def query_node():
    query_hash = request.args.get("hash")
    if query_hash is not None:
        matching_nodes = [node for node in graph.nodes.values() if query_hash and node.token_hash.startswith(query_hash)]
        return jsonify({"nodes": [node.serialize() for node in matching_nodes]})
    else:
        return jsonify({"nodes": [node.serialize() for node in graph.nodes.values()]})

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "An internal server error occurred."}), 500

@app.route("/valuelink", methods=["GET"])
def get_valuelinks():
   return jsonify({"valuelinks": [valuelink.serialize() for valuelink in graph.valuelinks.values()]})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
