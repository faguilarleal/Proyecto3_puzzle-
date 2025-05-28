from flask import Flask, jsonify
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os


load_dotenv()  # take environment variables


neo4j_uri = os.getenv('NEO4J_URI')
user = os.getenv('NEO4J_USERNAME')
password = os.getenv("NEO4J_PASSWORD")

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
AUTH = (user, password)

driver = GraphDatabase.driver(neo4j_uri, auth=AUTH)





# Methods to get all nodes from databasedef get_all_nodes():
def get_all_nodes():
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN n LIMIT 100")
        nodes = []
        for record in result:
            node = record["n"]
            nodes.append({
                "id": node.id,
                "labels": list(node.labels),
                "properties": dict(node)
            })
        return nodes





app = Flask(__name__)

# Access NEO4J_URI
NEO4J_URI = os.getenv("NEO4J_URI", "not set")

@app.route("/", methods=["GET"])
def home():
    return jsonify(message="Welcome to the Flask API!")

@app.route("/nodes", methods=["GET"])
def fetch_nodes():
    try:
        nodes = get_all_nodes()
        return jsonify(nodes)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)