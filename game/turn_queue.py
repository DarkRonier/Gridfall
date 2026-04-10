"""
Clase TurnQueue - Maneja la cola de 5 piezas que van a mover
"""

class TurnQueue:
    def __init__(self, turn_manager):
        """
        Inicializa la cola de turnos.
        
        Args:
            turn_manager: Instancia de TurnManager que proporciona las piezas
        """
        self.turn_manager = turn_manager
        self.queue = []  # Cola de piezas activas
        self.max_size = 5
        
        # Llenar la cola inicial
        self._fill_queue()
    
    def get_max_size(self):
        """Devuelve el tamaño máximo dinámico de la cola.
        Es el menor entre 5 y el número de piezas activas.
        """
        piezas_activas = [p for p in self.turn_manager.piezas_en_juego if p and p.esta_viva() and hasattr(p, 'posicion')]
        return min(self.max_size, len(piezas_activas))

    def _fill_queue(self):
        """Llena la cola hasta tener el número dinámico de piezas válidas."""
        while len(self.queue) < self.get_max_size():
            # CRÍTICO: Limpiar piezas muertas o inválidas de la cola
            self.queue = [p for p in self.queue if p and p.esta_viva() and hasattr(p, 'posicion')]
            
            # Obtener siguiente pieza del turn_manager
            siguiente = self.turn_manager.obtener_siguiente_pieza_activa()
            
            if siguiente is None:
                # No hay más piezas disponibles
                break
            
            # Validar que la pieza esté viva y tenga posición antes de agregar
            if siguiente.esta_viva() and hasattr(siguiente, 'posicion'):
                # Agregar a la cola si no está ya presente
                if siguiente not in self.queue:
                    self.queue.append(siguiente)
            else:
                # Si la pieza no es válida, continuar buscando
                continue
    
    def get_current_piece(self):
        """
        Retorna la pieza que tiene el turno actual (primera de la cola).
        Limpia piezas muertas antes de retornar.
        """
        # CRÍTICO: Filtrar piezas que no están vivas o no tienen posición válida
        self.queue = [p for p in self.queue if p and p.esta_viva() and hasattr(p, 'posicion')]
        
        # Rellenar si es necesario
        if len(self.queue) < self.get_max_size():
            self._fill_queue()
        
        # Retornar primera pieza o None
        return self.queue[0] if self.queue else None
    
    def advance_turn(self):
        """
        Avanza al siguiente turno: remueve la primera pieza de la cola
        y llena el espacio vacío solicitando una nueva pieza al turn_manager.
        """
        if not self.queue:
            return None
        
        # Remover la primera pieza (turno completado)
        pieza_completada = self.queue.pop(0)
        
        # CRÍTICO: Limpiar piezas muertas o inválidas de la cola
        self.queue = [p for p in self.queue if p and p.esta_viva() and hasattr(p, 'posicion')]
        
        # Llenar la cola de nuevo
        self._fill_queue()
        
        # Retornar la nueva pieza activa
        return self.get_current_piece()
    
    def get_queue(self):
        """
        Retorna una copia de la cola actual.
        Útil para la visualización.
        """
        # CRÍTICO: Filtrar piezas que no están vivas o no tienen posición válida
        self.queue = [p for p in self.queue if p and p.esta_viva() and hasattr(p, 'posicion')]
        
        # Rellenar si es necesario
        if len(self.queue) < self.get_max_size():
            self._fill_queue()
        
        return list(self.queue)
    
    def remove_dead_pieces(self):
        """
        Limpia explícitamente piezas muertas de la cola y la rellena.
        Útil para llamar después de batallas.
        """
        # CRÍTICO: Limpiar piezas muertas o inválidas
        self.queue = [p for p in self.queue if p and p.esta_viva() and hasattr(p, 'posicion')]
        
        # Rellenar
        self._fill_queue()
    
    def rebuild(self):
        """
        Reconstruye completamente la cola desde cero.
        Útil para llamar después de deshacer un movimiento.
        """
        # Vaciar la cola completamente
        self.queue = []
        
        # Llenar de nuevo desde el estado actual del turn_manager
        self._fill_queue()