from flask import Flask, jsonify
from neo4j import GraphDatabase
from dotenv import load_dotenv
import json
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


# Method for inserting node
def create_nodes(tx, nodes):
    for node in nodes:
        tx.run(
            """
            MERGE (n:Piece {id: $id})
            SET n.emisores = $emisores, n.receptores = $receptores, n.activa = $active
            """,
            id=node["id"],
            emisores=node["emisores"],
            receptores=node["receptores"],
            active=node["active"]
        )

def create_relationship(tx, relationships):
    for rel in relationships:
        tx.run(
            """
            MATCH(a:Piece {id: $start}), (b:Piece {id: $end})
            MERGE (a)-[r:es_adj_a]->(b)
            SET r.emisor = $emisor, r.receptor = $receptor, r.posicion = $pos
            """,
            start=rel["pieceID"],
            end=rel["pieceAdjID"],
            emisor=rel["emisor"],
            receptor=rel["receptor"],
            pos=rel["posicion"]
        )


# Method for inserting relationship



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

@app.route("/load-json", methods=["POST"])
def load_json_to_neo4j():
    try:
        with open("neo4j_data.json", "r") as f:
            data = json.load(f)

        with driver.session() as session:
            session.execute_write(create_nodes, data["nodes"])
            session.execute_write(create_relationship, data["relationships"])

        return jsonify(message="Datos cargados a Neo4J")
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)
