# ChessLike/game/turn_manager.py

import random

class TurnManager:
    def __init__(self, tablero):
        self.reloj = 0
        self.piezas_en_juego = []
        # Recolectamos todas las piezas del tablero
        for fila in tablero:
            for pieza in fila:
                if pieza is not None:
                    self.piezas_en_juego.append(pieza)
                    # Calculamos su primer turno al iniciar
                    pieza.calcular_siguiente_turno(0)
    
    def avanzar_reloj_y_obtener_pieza(self):
        self.piezas_en_juego = [p for p in self.piezas_en_juego if p.esta_viva()]

        self.reloj += 1
        piezas_con_turno = []
        for pieza in self.piezas_en_juego:
            if pieza.proximo_turno == self.reloj:
                piezas_con_turno.append(pieza)
        
        if not piezas_con_turno:
            return None
        
        if len(piezas_con_turno) == 1:
            return piezas_con_turno[0]
        else:
            random.shuffle(piezas_con_turno)
            pieza_afortunada = piezas_con_turno.pop(0)
            for pieza_retrasada in piezas_con_turno:
                pieza_retrasada.proximo_turno += 1
            return pieza_afortunada

    def obtener_siguiente_pieza_activa(self):
        """Avanza el reloj hasta encontrar la siguiente pieza que debe actuar."""
        while True:
            self.reloj += 1
            piezas_con_turno = []
            for pieza in self.piezas_en_juego:
                if pieza.proximo_turno == self.reloj:
                    piezas_con_turno.append(pieza)

            if not piezas_con_turno:
                continue # Nadie tiene turno, el reloj sigue avanzando

            # --- Resolución de Conflictos ---
            if len(piezas_con_turno) == 1:
                return piezas_con_turno[0] # Solo una pieza tiene turno, la devolvemos
            else:
                # ¡Conflicto! Múltiples piezas en el mismo tic.
                random.shuffle(piezas_con_turno)
                pieza_afortunada = piezas_con_turno.pop(0) # La primera es la elegida
                
                # Retrasamos a las demás
                for pieza_retrasada in piezas_con_turno:
                    pieza_retrasada.proximo_turno += 1
                
                return pieza_afortunada