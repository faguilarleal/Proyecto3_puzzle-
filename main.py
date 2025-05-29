from flask import Flask, jsonify
from neo4j import GraphDatabase
from dotenv import load_dotenv
from algorithm import get_adjacent
from instructions import format_grouped_instructions
from algorithm import assemble_all, group_connections



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
    
# Methods to get a node by id
def get_node_byID(node_id):
     with driver.session() as session:
        result = session.run(
            "MATCH (n) WHERE id(n) = $id RETURN n",
            id=node_id
        )
        record = result.single()
        if record:
            return record["n"]
        else:
            return None
    


# Method for inserting node
def create_nodes(tx, nodes):
    for node in nodes:
        tx.run(
            """
            MERGE (n:Piece {id: $id})
            SET n.emisores = $emisores, n.receptores = $receptores, n.activa = $active, n.visitado = $visitado
            """,
            id=node["id"],
            emisores=node["emisores"],
            receptores=node["receptores"],
            active=node["active"],
            visitado=node["visitado"],
        )



# Method for inserting relationship
def create_relationship(tx, relationships):
    for rel in relationships:
        tx.run(
            """
            MATCH(a:Piece {id: $start}), (b:Piece {id: $end})
            MERGE (a)-[r:es_adj_a]->(b)
            SET r.emisor = $emisor, r.receptor = $receptor, r.posicion = $pos, r.visitado = $visitado
            """,
            start=rel["pieceID"],
            end=rel["pieceAdjID"],
            emisor=rel["emisor"],
            receptor=rel["receptor"],
            pos=rel["posicion"],
            visitado=rel["visitado"],
        )

# Method for deleting all nodes
def delete_all(tx):
    tx.run(
        """
        MATCH (n)
        DETACH DELETE n
        """
    )

def update_relationship_visitado(id1, id2):
    with driver.session() as session:
        session.run(
            """
            MATCH (a {id: $id1})-[r]-(b {id: $id2})
            SET r.visitado = true
            """,
            id1=id1,
            id2=id2
        )


# Method for update visitado in node
def update_node_visitado(node_id):
    with driver.session() as session:
        r = session.run(
            """
            MATCH (n {id: $id})
            SET n.visitado = true
            """,
            id=node_id
        )

# Method for update visitado in node
def update_node_existente(node_id):
    with driver.session() as session:
        r = session.run(
            """
            MATCH (n {id: $id})
            SET n.activa = false
            """,
            id=node_id
        )
        


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
    
@app.route("/nodes/<int:piece_id>", methods=["GET"])
def getNode(piece_id):
    node = get_node_byID(piece_id)
    if node:
        return jsonify(dict(node)), 200
    else:
        return jsonify({"error": "Nodo no encontrado"}), 404
    
@app.route("/", methods=["DELETE"])
def delete_nodes():
    with driver.session() as session:
        session.execute_write(delete_all)
    return jsonify(message="DB Clear")

@app.route("/load-json", methods=["POST"])
def load_json_to_neo4j():
    try:
        with open("neo4j_data.json", "r") as f:
            data = json.load(f)
        print(data)

        with driver.session() as session:
            session.execute_write(create_nodes, data["nodes"])
            session.execute_write(create_relationship, data["relationships"])

        return jsonify(message="Datos cargados a Neo4J")
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route("/assemble/<int:piece_id>", methods=["GET"])
def assemble(piece_id):
    try:
        with driver.session() as session:
            vecinos = session.execute_read(get_adjacent, piece_id)

        return jsonify(vecinos), 200

    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/assemble/<int:piece_id>/steps", methods=["GET"])
def assemble_steps(piece_id):
    with driver.session() as session:
        vecinos = session.execute_read(get_adjacent, piece_id)
    
    agrupados = group_connections(piece_id, vecinos)
    pasos = format_grouped_instructions(agrupados)
    return jsonify(pasos), 200

@app.route("/assemble/full/<int:piece_id>", methods=["GET"])
def assemble_full(piece_id):
    try:
        steps = assemble_all(driver, piece_id)
        return jsonify(steps), 200
    except Exception as e:
        return jsonify(error=str(e)), 500
    
@app.route("/relaciones/<int:id1>/<int:id2>", methods=["PUT"])
def marcar_relaciones_visitadas(id1, id2):
    try:
        update_relationship_visitado(id1, id2)
        return jsonify({"mensaje": f"Relaciones entre {id1} y {id2} actualizadas con visitado=true"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/nodes/<int:node_id>", methods=["PUT"])
def marcar_nodo_visitado(node_id):
    try:
        update_node_visitado(node_id)
        return jsonify({"mensaje": f"Nodo {node_id} actualizado con visitado=true"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/nodes/activo/<int:node_id>", methods=["PUT"])
def marcar_nodo_inactivo(node_id):
    try:
        update_node_existente(node_id)
        return jsonify({"mensaje": f"Nodo {node_id} actualizado con activo=false"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
