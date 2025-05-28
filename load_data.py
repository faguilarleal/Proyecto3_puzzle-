import json
import requests

nodes = []
relationships = []

def add_piece(piece_id, senders, receivers):
    nodes.append({
        "id": piece_id,
        "emisores": senders,
        "receptores": receivers,
        "active": False
    })

def add_adjacence(piece_id, piece_adj_id, sender, receiver, position):
    relationships.append({
        "pieceID": piece_id,
        "pieceAdjID": piece_adj_id,
        "emisor": sender,
        "receptor": receiver,
        "posicion": position,
    })

if __name__ == "__main__":
    print("------------------PUZZLE GENERATOR-----------------------\n\n")
    total_pieces = int(input("Ingrese cuantas piezas tiene el puzzle: "))
    print()
    for i in range(total_pieces):
        print(f"PIEZA {i+1}:\n")
        senders = []
        receivers = []

        total_senders = int(input("Total de emisores: "))
        for k in range(total_senders):
            sender_name = str(input("Nombre del emisor: "))
            senders.append(sender_name)

        total_receiver = int(input("Total de receptores: "))
        for k in range(total_receiver):
            receiver_name = str(input("Nombre del receptor: "))
            receivers.append(receiver_name)

        add_piece(i+1, senders, receivers)

        total_adjacents = int(input("Total de piezas adyacentes: "))
        for k in range(total_adjacents):
            adj_piece = int(input("Pieza adyacente: "))
            position = str(input("Posición: "))
            sender = str(input("Emisor: "))
            receiver = str(input("Receptor: "))
            
            add_adjacence(i+1, adj_piece, sender, receiver, position)

    data = {
        "nodes": nodes,
        "relationships": relationships
    }

    with open('neo4j_data.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    response = requests.post("http://localhost:5000/load-json")
    print(response.json())
