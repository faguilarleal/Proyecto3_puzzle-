from flask import Flask, jsonify
from neo4j import GraphDatabase
from dotenv import load_dotenv
import json
import os
import random

def get_random(driver):
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN n LIMIT 100")
        nodes = [record["n"] for record in result]
        if nodes:
            return random.choice(nodes)
        



def get_adjacent(tx, piece_id):
    query = """
    MATCH (p:Piece {id: $piece_id})-[r:es_adj_a]->(adj:Piece)
    RETURN DISTINCT
      adj.id        AS id,
      adj.emisores  AS emisores,
      adj.receptores AS receptores,
      adj.activa    AS activa,
      r.emisor      AS emisor,
      r.receptor    AS receptor,
      r.posicion    AS posicion
    """
    result = tx.run(query, {"piece_id": piece_id})
    return [record.data() for record in result]


# algorithm.py

def assemble_all(driver, start_piece_id):
    visited_nodes = set()
    processed_edges = set()   # aquí guardaremos tuplas (min_id, max_id)
    steps = []

    def dfs(tx, pid):
        if pid in visited_nodes:
            return
        visited_nodes.add(pid)

        # obtenemos únicamente relaciones activas (no visitadas en BD, opcional)
        neighbors = tx.run("""
            MATCH (p:Piece {id: $pid})-[r:es_adj_a]->(adj:Piece)
            WHERE r.visitado = false  // si quieres filtrar en BD
            RETURN adj.id   AS id,
                   r.emisor AS emisor,
                   r.receptor AS receptor,
                   r.posicion AS posicion
        """, {"pid": pid})
        recs = [rec.data() for rec in neighbors]

        for rec in recs:
            a, b = pid, rec["id"]
            edge_key = tuple(sorted((a, b)))

            # si ya procesamos A<->B, saltamos
            if edge_key in processed_edges:
                continue

            # marcamos en memoria (y opcionalmente en BD) como procesado
            processed_edges.add(edge_key)
            # session.write / tx.run(...)
            tx.run("""
                MATCH (x:Piece {id:$a})-[r]-(y:Piece {id:$b})
                SET r.visitado = true
            """, {"a": a, "b": b})

            # buscamos la relación inversa (B->A) para combinar
            inverse = next(
                (x for x in recs
                 if x["id"] == a and x["emisor"] == rec["receptor"] and x["receptor"] == rec["emisor"]),
                None
            )

            if inverse:
                # si existe la mitad inversa en la misma llamada, la combinamos
                steps.append(
                    f"Conecta pieza {a} ↔ pieza {b}: "
                    f"{rec['emisor']}→{rec['receptor']} ({rec['posicion']}) y "
                    f"{inverse['emisor']}→{inverse['receptor']} ({inverse['posicion']})."
                )
            else:
                # si no, emitimos la instrucción normal
                steps.append(
                    f"Pieza {a}: conecta tu emisor “{rec['emisor']}” "
                    f"con el receptor “{rec['receptor']}” de la pieza {b} "
                    f"por el lado “{rec['posicion']}”."
                )

            # seguimos DFS desde el vecino (sólo por el lado A→B)
            dfs(tx, b)

    with driver.session() as session:
        # usamos write_transaction porque vamos a actualizar r.visitado
        session.write_transaction(lambda tx: dfs(tx, start_piece_id))

    return steps


def group_connections(pieza_id, conexiones):

    grouped = {}

    for rec in conexiones:
        a = pieza_id
        b = rec["id"]
        key = (min(a, b), max(a, b))  # Ignora orden (↔)

        if key not in grouped:
            grouped[key] = []
        grouped[key].append(rec)

    return grouped

def mark_visited(tx, piece_id):
    tx.run(
        """
        MATCH (p:Pieza {id: $piece_id})
        SET p.visitado = true
        """,
        piece_id=piece_id
    )


def solve_puzzle(driver, piece_id):
    with driver.session() as session:

        # 0.verificar si ya esta visitado
        is_visited = session.run(
            "MATCH (p:Pieza {id: $piece_id}) RETURN p.visitado AS visitado", 
            piece_id = piece_id
        ).single()["visitado"]

        if is_visited == True:
            return
        
        #marcar como visitado si no lo esta
        session.write_transaction(mark_visited, piece_id)
        
        # 1. tomar las piezas adyacentes de la pieza inicial
        # query para tomar las piezas adyacentes    
        adjacent_nodes = session.read_transaction(get_adjacent, piece_id)
        print("piezas adyacentes:")
        for node in adjacent_nodes:
            print(node['id'])

        # 2. conectar cada emisor con su receptor 



    # 3. jalar las piezas adyacentes de unas de las que conecto
    #visitar recursivamente las piezas adyacentes
    for node in adjacent_nodes:
        next_id = node["id"]
        solve_puzzle(driver, next_id)
