def format_instructions(piece_id, adjacent_list):
    """
    Dada la pieza de inicio y la lista de vecinos con
    detalles de relación, devuelve una lista de strings
    con los pasos de montaje.
    """
    steps = []
    for rec in adjacent_list:
        # ejemplo:
        steps.append(
            f"Pieza {piece_id}: conecta tu emisor “{rec['emisor']}” "
            f"con el receptor “{rec['receptor']}” de la pieza {rec['id']} "
            f"por el lado “{rec['posicion']}”."
        )
    return steps
