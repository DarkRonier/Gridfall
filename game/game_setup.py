# ChessLike/game/game_setup.py

from .piece import (crear_soldado, crear_paladin, crear_mago,
                    crear_dragon, crear_destructor)
from .constants import FILAS, COLUMNAS

def crear_nuevo_juego():
    """Crea y devuelve un tablero con todas las piezas iniciales."""
    tablero = [[None for _ in range(COLUMNAS)] for _ in range(FILAS)]

    soldados = ([0, 1, 2, 3, 4, 5, 6, 7])  # Posiciones de los soldados
    for i, pos in enumerate(soldados):
        for j in range(2):
            if j == 0:
                soldado = crear_soldado(jugador=1)
                soldado.posicion = (6, pos)
                tablero[6][pos] = soldado
            else:
                soldado = crear_soldado(jugador=2)
                soldado.posicion = (1, pos)
                tablero[1][pos] = soldado

    paladins = ([2, 5])  # Posiciones de los paladines
    for i, pos in enumerate(paladins):
        for j in range(2):
            if j == 0:
                paladin = crear_paladin(jugador=1)
                paladin.posicion = (7, pos)
                tablero[7][pos] = paladin
            else:
                paladin = crear_paladin(jugador=2)
                paladin.posicion = (0, pos)
                tablero[0][pos] = paladin
    
    magos = ([1, 6])  # Posiciones de los magos
    for i, pos in enumerate(magos):
        for j in range(2):
            if j == 0:
                mago = crear_mago(jugador=1)
                mago.posicion = (7, pos)
                tablero[7][pos] = mago
            else:
                mago = crear_mago(jugador=2)
                mago.posicion = (0, pos)
                tablero[0][pos] = mago

    for i in range(2):
        if i == 0:
            dragon = crear_dragon(jugador=1)
            dragon.posicion = (7, 3)
            tablero[7][3] = dragon
        else:
            dragon = crear_dragon(jugador=2)
            dragon.posicion = (0, 3)
            tablero[0][3] = dragon
    
    for i in range(2):
        if i == 0:
            destructor = crear_destructor(jugador=1)
            destructor.posicion = (7, 4)
            tablero[7][4] = destructor
        else:
            destructor = crear_destructor(jugador=2)
            destructor.posicion = (0, 4)
            tablero[0][4] = destructor
    
    return tablero