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
    """
    Recupera vecinos no visitados junto con su estado 'activa'
    y los datos de la relación.
    """
    query = """
    MATCH (p:Piece {id: $piece_id})-[r:es_adj_a]->(adj:Piece)
    WHERE r.visitado = false
    RETURN
      adj.id       AS id,
      adj.activa   AS activa,
      r.emisor     AS emisor,
      r.receptor   AS receptor,
      r.posicion   AS posicion
    """
    result = tx.run(query, {"piece_id": piece_id})
    return [record.data() for record in result]


def assemble_all(driver, start_piece_id):
    """
    Recorre en DFS el ensamblaje completo desde start_piece_id,
    agrupando conexiones activas y registrando huecos por piezas inactivas.
    """
    visited = set()
    processed_edges = set()
    grouped_edges = {}    # {(a,b): [ {emisor,receptor,posicion}, … ]}
    missing_edges = []    # [ {from:a, to:b, pos:posición}, … ]

    def dfs(tx, pid):
        if pid in visited:
            return
        visited.add(pid)

        for rec in tx.run(
            """
            MATCH (p:Piece {id: $pid})-[r:es_adj_a]->(adj:Piece)
            WHERE r.visitado = false
            RETURN
              adj.id       AS id,
              adj.activa   AS activa,
              r.emisor     AS emisor,
              r.receptor   AS receptor,
              r.posicion   AS posicion
            """,
            {"pid": pid}
        ):
            a, b = pid, rec["id"]
            edge_key = tuple(sorted((a, b)))
            if edge_key in processed_edges:
                continue
            processed_edges.add(edge_key)

            # Marcamos la relación como visitada en la DB
            tx.run(
                """
                MATCH (x:Piece {id:$a})-[r]-(y:Piece {id:$b})
                SET r.visitado = true
                """,
                {"a": a, "b": b}
            )

            if not rec["activa"]:
                # Pieza b faltante → registrar hueco
                missing_edges.append({
                    "from": a,
                    "to": b,
                    "pos": rec["posicion"]
                })
            else:
                # Pieza b activa → agrupar conexión y seguir DFS
                grouped_edges.setdefault(edge_key, []).append({
                    "emisor":   rec["emisor"],
                    "receptor": rec["receptor"],
                    "posicion": rec["posicion"]
                })
                dfs(tx, b)

    # Ejecutamos el DFS desde el driver
    with driver.session() as session:
        session.write_transaction(lambda tx: dfs(tx, start_piece_id))

    # Formateamos las instrucciones
    from instructions import (
        format_grouped_instructions,
        format_missing_instructions
    )
    steps = format_grouped_instructions(grouped_edges)
    if missing_edges:
        steps += format_missing_instructions(missing_edges)
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
