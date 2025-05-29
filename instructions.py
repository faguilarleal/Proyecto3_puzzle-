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
