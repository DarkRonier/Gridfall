# ChessLike/game/logic.py

from .constants import FILAS, COLUMNAS # Importación relativa

# --- FUNCIONES DE CÁLCULO DE MOVIMIENTO ---

def es_valida(fila, col):
    """Comprueba si una coordenada está dentro del tablero."""
    return 0 <= fila < FILAS and 0 <= col < COLUMNAS

def _buscar_pasos(pieza, n, tablero, is_attack=False):
    if n == 0:
        return set()
    
    fila_origen, col_origen = pieza.posicion
    casillas_inrange = set()
    cola = [((fila_origen, col_origen), 0)]
    visitados = {(fila_origen, col_origen)}

    while cola:
        (f, c), pasos = cola.pop(0)
        if pasos >= n:
            continue
        for df, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nf, nc = f + df, c + dc
            if es_valida(nf, nc) and (nf, nc) not in visitados:
                visitados.add((nf, nc))
                casillas_inrange.add((nf, nc))

                pieza_en_casilla = tablero[nf][nc]

                if pieza_en_casilla is None:  # Si la casilla está vacía, seguimos explorando.
                    cola.append(((nf, nc), pasos + 1))
                elif is_attack and pieza_en_casilla.jugador == pieza.jugador:
                    cola.append(((nf, nc), pasos + 1))  # Si es un ataque, seguimos si es aliado.                    
    return casillas_inrange


def calcular_mov_rect(pieza, n, tablero, is_attack=False):
    """
    Calcula el movimiento rectilíneo.
    - Si es un movimiento, se detiene ante cualquier pieza.
    - Si es un ataque, pasa a través de aliados y se detiene en enemigos.
    """
    casillas = set()
    fila_origen, col_origen = pieza.posicion
    if pieza.puede_saltar:
        # Si puede saltar, consideramos que puede moverse hasta n casillas en línea recta.
        for i in range(1, n + 1):
            posiciones = [(fila_origen - i, col_origen), (fila_origen + i, col_origen),
                          (fila_origen, col_origen - i), (fila_origen, col_origen + i)]
            for f, c in posiciones:
                if es_valida(f, c):
                    casillas.add((f, c))
        pass
    else:
        direcciones = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for df, dc in direcciones:
            for i in range(1, n + 1):
                nf, nc = fila_origen + i*df, col_origen + i*dc
                if not es_valida(nf, nc):
                    break

                pieza_bloqueante = tablero[nf][nc]
                if pieza_bloqueante is not None:
                    if is_attack:
                        if pieza_bloqueante.jugador != pieza.jugador:
                            casillas.add((nf, nc))
                            break
                    else:
                        break  # Si hay una pieza, no podemos seguir en esa dirección.
                casillas.add((nf, nc))
    return list(casillas)

def calcular_mov_diag(pieza, n, tablero, is_attack=False):
    casillas = set()
    fila_origen, col_origen = pieza.posicion
    if pieza.puede_saltar:
        # Si puede saltar, consideramos que puede moverse hasta n casillas en diagonal.
        for i in range(1, n + 1):
            posiciones = [(fila_origen - i, col_origen - i), (fila_origen - i, col_origen + i),
                          (fila_origen + i, col_origen - i), (fila_origen + i, col_origen + i)]
            for f, c in posiciones:
                if es_valida(f, c):
                    casillas.add((f, c))
        pass
    else:
        direcciones = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for df, dc in direcciones:
            for i in range(1, n + 1):
                nf, nc = fila_origen + i*df, col_origen + i*dc
                if not es_valida(nf, nc):
                    break

                pieza_bloqueante = tablero[nf][nc]
                if pieza_bloqueante is not None:
                    if is_attack:
                        if pieza_bloqueante.jugador != pieza.jugador:
                            casillas.add((nf, nc))
                            break
                    else:
                        break
                casillas.add((nf, nc))
    return list(casillas)

def calcular_mov_allsides(pieza, n, tablero, is_attack=False):
    rectas = set(calcular_mov_rect(pieza, n, tablero, is_attack))
    diagonales = set(calcular_mov_diag(pieza, n, tablero, is_attack))
    return list(rectas.union(diagonales))
    
def calcular_mov_steps(pieza, n, tablero):
    casillas_accesibles = _buscar_pasos(pieza, n, tablero, is_attack=False)
    movimientos_validos = set()
    for f, c in casillas_accesibles:
        if tablero[f][c] is None:
            movimientos_validos.add((f, c))
    return list(movimientos_validos)

def calcular_ran_steps(pieza, a, b, tablero):
    zona_maxima = _buscar_pasos(pieza, b, tablero, is_attack=True)
    if a <= 0:
        return zona_maxima
    zona_muerta = _buscar_pasos(pieza, a, tablero, is_attack=True)
    zona_valida = zona_maxima - zona_muerta
    return list(zona_valida)

def calcular_casillas_posibles(pieza, tablero):
    casillas_en_rango = set()

    for tipo_mov, valor_mov in pieza.movimientos:
        casillas_calculadas = []
        if tipo_mov == 'rect':
            casillas_calculadas = calcular_mov_rect(pieza, valor_mov, tablero)
        elif tipo_mov == 'diag':
            casillas_calculadas = calcular_mov_diag(pieza, valor_mov, tablero)
        elif tipo_mov == 'allsides':
            casillas_calculadas = calcular_mov_allsides(pieza, valor_mov, tablero)
        elif tipo_mov == 'steps':
            casillas_calculadas = calcular_mov_steps(pieza, valor_mov, tablero)

        casillas_en_rango.update(casillas_calculadas)
    
    movimientos_validos = set()
    for fila, col in casillas_en_rango:
        if tablero[fila][col] is None:
            movimientos_validos.add((fila, col))

    return list(movimientos_validos)

def calcular_ataques_posibles(pieza, tablero):
    """
    Calcula las casillas que contienen un enemigo y están en el rango de ataque.
    """
    casillas_en_rango = set()

    # 1. Obtenemos todas las casillas en rango de ataque.
    for tipo_ran, valor_ran in pieza.rango_ataque:
        casillas_calculadas = []
        if tipo_ran == 'rect':
            casillas_calculadas = calcular_mov_rect(pieza, valor_ran, tablero, is_attack=True)
        elif tipo_ran == 'diag':
            casillas_calculadas = calcular_mov_diag(pieza, valor_ran, tablero, is_attack=True)
        elif tipo_ran == 'allsides':
            casillas_calculadas = calcular_mov_allsides(pieza, valor_ran, tablero, is_attack=True)
        elif tipo_ran == 'steps':
            min_ran, max_ran = valor_ran
            casillas_calculadas = calcular_ran_steps(pieza, min_ran, max_ran, tablero)
        
        casillas_en_rango.update(casillas_calculadas)

    # 2. Filtramos para quedarnos solo con las que tienen un enemigo.
    ataques_validos = set()
    for fila, col in casillas_en_rango:
        pieza_en_casilla = tablero[fila][col]
        if pieza_en_casilla is not None and pieza_en_casilla.jugador != pieza.jugador:
            ataques_validos.add((fila, col))
            
    return list(ataques_validos)

def verificar_ganador(piezas_en_juego):
    """
    Comprueba si algún jugador se ha quedado sin piezas.
    Devuelve 1 si gana el jugador 1, 2 si gana el jugador 2, o None si el juego continúa.
    """
    p1_vivas = 0
    p2_vivas = 0
    for pieza in piezas_en_juego:
        if pieza.jugador == 1:
            p1_vivas += 1
        else:
            p2_vivas += 1
    
    if p1_vivas == 0 and p2_vivas > 0:
        return 2
    if p2_vivas == 0 and p1_vivas > 0:
        return 1
    
    return None