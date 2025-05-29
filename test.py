# test_adjacent.py

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
from algorithm import get_adjacent

load_dotenv()
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

def main():
    piece_id = 1  # cambia por el ID que tengas en la BD
    with driver.session() as ses:
        vecinos = ses.read_transaction(get_adjacent, piece_id)
    print(f"Vecinos de {piece_id}:", vecinos)
    driver.close()

if __name__ == "__main__":
    main()
