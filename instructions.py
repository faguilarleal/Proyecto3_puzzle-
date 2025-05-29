from algorithm import get_adjacent

# instructions.py

def format_grouped_instructions(grouped):
    """
    grouped: dict donde cada clave es (a,b) y el valor
    es la lista de conexiones (rec dicts) entre pieza a y pieza b.
    """
    steps = []
    for (a, b), recs in grouped.items():
        if len(recs) == 2:
            r1, r2 = recs
            steps.append(
                f"Conecta pieza {a} ↔ pieza {b}: "
                f"{r1['emisor']}→{r1['receptor']} ({r1['posicion']}) y "
                f"{r2['emisor']}→{r2['receptor']} ({r2['posicion']})."
            )
        else:
            r = recs[0]
            steps.append(
                f"Pieza {a}: conecta emisor “{r['emisor']}” "
                f"con receptor “{r['receptor']}” de pieza {b} "
                f"por lado “{r['posicion']}”."
            )
    return steps


def assemble_all_grouped(driver, start_piece_id):
    visited = set()
    all_conns = []

    def dfs(tx, pid):
        if pid in visited:
            return
        visited.add(pid)

        vecinos = get_adjacent(tx, pid)
        for v in vecinos:
            all_conns.append({**v, "from": pid})
            dfs(tx, v["id"])

    with driver.session() as session:
        session.read_transaction(dfs, start_piece_id)

    # Agrupar conexiones por (a,b)
    agrupados = {}
    for conn in all_conns:
        a = conn["from"]
        b = conn["id"]
        key = tuple(sorted([a, b]))
        if key not in agrupados:
            agrupados[key] = []
        agrupados[key].append(conn)

    return format_grouped_instructions(agrupados)