import random

class SimpleAI:
    """
    IA básica para Gridfall. Prioriza ataques útiles y mueve hacia piezas rivales.
    """
    def elegir_accion(self, pieza, tablero, calcular_casillas_posibles, calcular_ataques_posibles):
        ataques = calcular_ataques_posibles(pieza, tablero)
        if ataques:
            # Prioriza atacar la pieza con mayor valor (ejemplo: mayor atk o hp)
            mejor_objetivo = max(ataques, key=lambda pos: self.valor_pieza(tablero[pos[0]][pos[1]]))
            return ('atacar', mejor_objetivo)
        movimientos = calcular_casillas_posibles(pieza, tablero)
        if movimientos:
            # Mueve hacia la pieza rival más cercana
            objetivo = self.encontrar_objetivo(pieza, tablero)
            if objetivo:
                mejor_mov = min(movimientos, key=lambda mov: self.distancia(mov, objetivo.posicion))
                return ('mover', mejor_mov)
            return ('mover', random.choice(movimientos))
        return ('pasar', None)

    def valor_pieza(self, pieza):
        # Puedes mejorar este criterio según el juego
        if pieza is None:
            return -1
        return getattr(pieza, 'atk', 1) + getattr(pieza, 'hp', 1)

    def encontrar_objetivo(self, pieza, tablero):
        # Busca la pieza rival más cercana
        rivales = [p for fila in tablero for p in fila if p and p.jugador != pieza.jugador]
        if not rivales:
            return None
        return min(rivales, key=lambda p: self.distancia(pieza.posicion, p.posicion))

    def distancia(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
