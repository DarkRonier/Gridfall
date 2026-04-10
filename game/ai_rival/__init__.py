from .simple_ai import SimpleAI
# Importamos las funciones de lógica del juego para pasárselas a la IA
from game.logic import calcular_casillas_posibles, calcular_ataques_posibles

class AIController:
    """
    Clase adaptadora que conecta el sistema del juego con SimpleAI.
    """
    def __init__(self, team_id):
        self.team_id = team_id
        self.cerebro = SimpleAI()

    def calcular_turno(self, tablero, pieza_activa, movimientos_resaltados=None, ataques_resaltados=None):
        """
        Método estandarizado que llama main.py.
        Adapta los datos del juego a lo que necesita SimpleAI.
        """

        def obtener_movimientos():
            if movimientos_resaltados is not None:
                return movimientos_resaltados
            return calcular_casillas_posibles(pieza_activa, tablero)

        def obtener_ataques():
            if ataques_resaltados is not None:
                return ataques_resaltados
            return calcular_ataques_posibles(pieza_activa, tablero)

        def elegir_mejor_movimiento(movimientos):
            if not movimientos:
                return None
            objetivo = self.cerebro.encontrar_objetivo(pieza_activa, tablero)
            if objetivo:
                return min(movimientos, key=lambda mov: self.cerebro.distancia(mov, objetivo.posicion))
            return movimientos[0]

        def elegir_mejor_objetivo(ataques):
            if not ataques:
                return None
            return max(ataques, key=lambda pos: self.cerebro.valor_pieza(tablero[pos[0]][pos[1]]))

        # Si ya atacó, no puede volver a atacar en este turno.
        if pieza_activa.ha_atacado:
            if pieza_activa.tipo_turno == 2 and not pieza_activa.ha_movido:
                movimientos = obtener_movimientos()
                destino = elegir_mejor_movimiento(movimientos)
                if destino is not None:
                    return {'tipo': 'mover', 'destino': destino}
            return {'tipo': 'pasar'}

        # Si ya se movió, puede atacar solo si su tipo de turno lo permite.
        if pieza_activa.ha_movido:
            if pieza_activa.tipo_turno > 0 and not pieza_activa.ha_atacado:
                ataques = obtener_ataques()
                objetivo = elegir_mejor_objetivo(ataques)
                if objetivo is not None:
                    return {'tipo': 'atacar', 'objetivo': objetivo}
            return {'tipo': 'pasar'}

        accion, valor = self.cerebro.elegir_accion(
            pieza_activa,
            tablero,
            calcular_casillas_posibles,
            calcular_ataques_posibles
        )
        
        # Convertimos la respuesta de tupla (SimpleAI) a diccionario (Juego)
        if accion == 'atacar':
            return {'tipo': 'atacar', 'objetivo': valor}
        
        elif accion == 'mover':
            return {'tipo': 'mover', 'destino': valor}
            
        else:
            return {'tipo': 'pasar'}