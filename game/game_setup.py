# ChessLike/game/game_setup.py

from .piece import crear_soldado, crear_paladin, crear_mago
from .constants import FILAS, COLUMNAS

def crear_nuevo_juego():
    """Crea y devuelve un tablero con todas las piezas iniciales."""
    tablero = [[None for _ in range(COLUMNAS)] for _ in range(FILAS)]
    
    # Jugador 1 (abajo)

    for i in range(8):
        soldado_j1 = crear_soldado(jugador=1)
        soldado_j1.posicion = (6, i)
        tablero[6][i] = soldado_j1

    paladins = ([2, 5])  # Posiciones de los paladines
    for i, pos in enumerate(paladins):
        for j in range(2):
            if i == 0:
                paladin = crear_paladin(jugador=1)
                paladin.posicion = (7, pos)
                tablero[7][pos] = paladin
            else:
                paladin = crear_paladin(jugador=2)
                paladin.posicion = (0, pos)
                tablero[0][pos] = paladin


    paladin2_j1 = crear_paladin(jugador=1)
    paladin2_j1.posicion = (7, 5)
    tablero[7][5] = paladin2_j1

    mago1_j1 = crear_mago(jugador=1)
    mago1_j1.posicion = (7, 1)
    tablero[7][1] = mago1_j1

    mago2_j1 = crear_mago(jugador=1)
    mago2_j1.posicion = (7, 6)
    tablero[7][6] = mago2_j1

    # Jugador 2 (arriba)
    for i in range(8):
        soldado_j2 = crear_soldado(jugador=2)
        soldado_j2.posicion = (1, i)
        tablero[1][i] = soldado_j2

    paladin1_j2 = crear_paladin(jugador=2)
    paladin1_j2.posicion = (0, 2)
    tablero[0][2] = paladin1_j2
    paladin2_j2 = crear_paladin(jugador=2)
    paladin2_j2.posicion = (0, 5)
    tablero[0][5] = paladin2_j2

    mago1_j2 = crear_mago(jugador=2)
    mago1_j2.posicion = (0, 1)
    tablero[0][1] = mago1_j2
    mago2_j2 = crear_mago(jugador=2)
    mago2_j2.posicion = (0, 6)
    tablero[0][6] = mago2_j2
    
    return tablero