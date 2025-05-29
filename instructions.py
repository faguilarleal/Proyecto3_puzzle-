from algorithm import get_adjacent

# instructions.py


def format_grouped_instructions(grouped):
    """
    grouped: dict { (a,b): [ {emisor, receptor, posicion}, … ] }
    Devuelve una lista de strings combinando A↔B cuando haya
    dos mitades de la misma conexión.
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

def format_missing_instructions(missing):
    """
    missing: lista de dicts { from:a, to:b, pos:posición }
    Devuelve avisos claros de huecos por piezas inactivas.
    """
    steps = ["\n---\nADVERTENCIAS (PIEZAS FALTANTES):"]
    # Agrupamos todos los huecos por pieza faltante
    holes = {}
    for m in missing:
        holes.setdefault(m["to"], []).append(m)

    for hole_id, infos in holes.items():
        vecinos = [str(i["from"]) for i in infos]
        lados   = [i["pos"]    for i in infos]
        steps.append(
            f"Tenga en cuenta que la pieza {hole_id} NO está disponible; "
            f"quedará un hueco conectado a la(s) pieza(s) "
            f"{', '.join(vecinos)} por el/los lado(s) {', '.join(lados)}."
        )
    return steps