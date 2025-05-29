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


def assemble_all(driver, start_piece_id):
    visited = set()
    steps = []

    def dfs(tx, pid):
        if pid in visited:
            return
        visited.add(pid)

        neighbors = get_adjacent(tx, pid)
        for rec in neighbors:
            steps.append(
                f"Pieza {pid}: conecta tu emisor “{rec['emisor']}” "
                f"con el receptor “{rec['receptor']}” de la pieza {rec['id']} "
                f"por el lado “{rec['posicion']}”."
            )
            dfs(tx, rec['id'])

    with driver.session() as session:
        session.read_transaction(dfs, start_piece_id)

    return steps



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
