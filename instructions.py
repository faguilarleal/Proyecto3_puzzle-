from algorithm import get_adjacent

# instructions.py

def format_grouped_instructions(grouped):
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

def format_missing_instructions(missing):
    """
    missing: lista de dicts {"from":a,"to":b,"pos":posicion}
    """
    steps = ["\n---\nADVERTENCIAS (PIEZAS FALTANTES):"]
    # agrupamos por pieza faltante para un mensaje más compacto
    holes = {}
    for m in missing:
        holes.setdefault(m["to"], []).append(m)
    for hole_id, infos in holes.items():
        vecinos = [str(i["from"]) for i in infos]
        lados   = [i["pos"] for i in infos]
        steps.append(
            f"Tenga en cuenta que la pieza {hole_id} NO está disponible; "
            f"quedará un hueco conectado a la(s) pieza(s) {', '.join(vecinos)} "
            f"por el/los lado(s) {', '.join(lados)}."
        )
    return steps
