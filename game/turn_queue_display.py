"""
Módulo para dibujar el panel de cola de turnos con animaciones
"""

import pygame
from game import constants
from game.assets import crear_superficie_pieza


class TurnQueueAnimator:
    """
    Maneja las animaciones de la cola de turnos.
    """
    def __init__(self):
        self.slots = []  # Lista de slots animados
        self.animating_slide = False
        self.slide_animation_progress = 0
        self.slide_animation_duration = 20  # frames para completar la animación de deslizamiento
        self.death_animation_duration = 40  # frames para completar fade a gris
        self.fade_first_slot = False

    def inicializar_slots(self, cola_piezas):
        """Inicializa los slots con las piezas actuales."""
        self.slots = []
        for i in range(5):
            pieza = cola_piezas[i] if i < len(cola_piezas) else None
            self.slots.append({
                'pieza': pieza,
                'graying': False,
                'gray_progress': 0,
                'death_timer': 0,
            })
    
    def resetear(self, cola_piezas):
        """Resetea completamente el animador con una nueva cola (usado al deshacer)."""
        self.slots = []
        self.animating_slide = False
        self.slide_animation_progress = 0
        self.fade_first_slot = False
        self.inicializar_slots(cola_piezas)
    
    def iniciar_animacion_avanzar(self, nueva_cola):
        """Inicia la animación de deslizar hacia arriba al avanzar turno."""
        if not self.animating_slide:
            self.animating_slide = True
            self.slide_animation_progress = 0
            self.fade_first_slot = True
    
    def iniciar_animacion_muerte(self, pieza):
        """Inicia la animación de muerte de una pieza."""
        # Buscar el slot con esta pieza
        for slot in self.slots:
            if slot['pieza'] == pieza and not slot['graying']:
                slot['graying'] = True
                slot['gray_progress'] = 0
                slot['death_timer'] = 0
                break
    
    def sincronizar_con_cola(self, cola_real):
        """Sincroniza los slots con la cola real sin animaciones."""
        # Actualizar cada slot para que coincida con la cola real
        for i in range(5):
            pieza_real = cola_real[i] if i < len(cola_real) else None
            
            if i < len(self.slots):
                # Si la pieza cambió y no está en animación de muerte, actualizarla
                if self.slots[i]['pieza'] != pieza_real and not self.slots[i]['graying']:
                    self.slots[i]['pieza'] = pieza_real
                    self.slots[i]['graying'] = False
                    self.slots[i]['gray_progress'] = 0
                    self.slots[i]['death_timer'] = 0
    
    def update(self, cola_real):
        """Actualiza el estado de las animaciones."""
        # Actualizar animación de muerte (fade a gris)
        for slot in self.slots:
            if slot['graying']:
                slot['death_timer'] += 1
                
                # Actualizar progreso del fade
                if slot['gray_progress'] < 1.0:
                    slot['gray_progress'] += 1.0 / self.death_animation_duration
                    if slot['gray_progress'] >= 1.0:
                        slot['gray_progress'] = 1.0
                
                # Si completó la animación de muerte, limpiar el slot
                if slot['death_timer'] >= self.death_animation_duration:
                    # Marcar como no gris para que se pueda actualizar
                    slot['graying'] = False
                    slot['gray_progress'] = 0
                    slot['death_timer'] = 0
        
        # Actualizar animación de deslizamiento
        if self.animating_slide:
            self.slide_animation_progress += 1
            
            if self.slide_animation_progress >= self.slide_animation_duration:
                # Animación completada
                self.animating_slide = False
                self.slide_animation_progress = 0
                self.fade_first_slot = False
        
        # Sincronizar con la cola real si no hay animaciones activas
        if not self.animating_slide:
            self.sincronizar_con_cola(cola_real)
    
    def get_slot_offset(self, slot_index, altura_slot):
        """Calcula el offset Y para un slot durante la animación."""
        if not self.animating_slide:
            return 0
        
        # Interpolación suave (ease-out)
        t = self.slide_animation_progress / self.slide_animation_duration
        t = 1 - (1 - t) ** 3  # Cubic ease-out
        
        return -altura_slot * t
    
    def get_slot_alpha(self, slot_index):
        """
        Calcula el alpha (opacidad) para un slot durante la animación.
        El primer slot hace fade out mientras se desliza hacia arriba.
        """
        if not self.animating_slide or not self.fade_first_slot or slot_index != 0:
            return 255  # Opacidad completa
        
        # Fade out del primer slot mientras se desliza
        t = self.slide_animation_progress / self.slide_animation_duration
        alpha = int(255 * (1 - t))  # De 255 a 0
        return max(0, alpha)

# Instancia global del animador
_animator = TurnQueueAnimator()


def get_animator():
    """Retorna la instancia del animador."""
    return _animator


def dibujar_panel_turnos(pantalla, turn_queue, cache_imagenes, fuente_ui):
    """
    Dibuja el panel de cola de turnos al lado derecho del tablero.
    
    Args:
        pantalla: Superficie de pygame donde dibujar
        turn_queue: Instancia de TurnQueue con las piezas en cola
        cache_imagenes: Caché de imágenes de piezas
        fuente_ui: Fuente para el texto
    """
    global _animator
    
    # Obtener la cola de piezas
    cola = turn_queue.get_queue()
    
    # Inicializar animator si está vacío
    if not _animator.slots:
        _animator.inicializar_slots(cola)
    
    # Actualizar animaciones
    _animator.update(cola)
    
    # Calcular dimensiones y posición del panel
    panel_x = constants.OFFSET_X + constants.ANCHO_TABLERO
    panel_y = constants.OFFSET_Y + constants.UI_ALTO
    panel_ancho = constants.ANCHO_PANEL_TURNOS
    panel_alto = constants.ALTO_TABLERO
    
    # Dibujar fondo del panel
    panel_rect = pygame.Rect(panel_x, panel_y, panel_ancho, panel_alto)
    pygame.draw.rect(pantalla, constants.COLOR_PANEL_FONDO, panel_rect)
    
    # Dibujar borde del panel
    pygame.draw.rect(pantalla, constants.COLOR_PANEL_BORDE, panel_rect, 3)
    
    # Título del panel
    titulo = fuente_ui.render("Próximos Turnos", True, constants.COLOR_TEXTO_NORMAL)
    titulo_rect = titulo.get_rect(centerx=panel_x + panel_ancho // 2, y=panel_y + 10)
    pantalla.blit(titulo, titulo_rect)
    
    # Calcular espacio para cada slot
    margen_superior = 50  # Espacio para el título
    espacio_disponible = panel_alto - margen_superior - 20  # 20 de margen inferior
    altura_slot = int(espacio_disponible / 5.75)
    espacio_superior = altura_slot * 0.75

    # Dibujar cada slot de la cola
    for i in range(5):
        if i >= len(_animator.slots):
            break
            
        slot_data = _animator.slots[i]
        offset_y = _animator.get_slot_offset(i, altura_slot)
        alpha = _animator.get_slot_alpha(i)
        slot_y = panel_y + margen_superior + espacio_superior + (i * altura_slot) + offset_y
        
        # Dibujar el slot con los datos animados
        _dibujar_slot_turno(
            pantalla, 
            panel_x, 
            slot_y, 
            panel_ancho, 
            altura_slot,
            slot_data,
            (i == 0),  # El primero es el activo
            cache_imagenes,
            fuente_ui,
            alpha
        )


def _dibujar_slot_turno(pantalla, x, y, ancho, alto, slot_data, es_activo, cache_imagenes, fuente, alpha=255):
    """
    Dibuja un slot individual de la cola de turnos.
    
    Args:
        pantalla: Superficie donde dibujar
        x, y: Coordenadas del slot
        ancho, alto: Dimensiones del slot
        slot_data: Diccionario con datos del slot (pieza, y_offset, etc.)
        es_activo: True si es la pieza del turno actual
        cache_imagenes: Caché de imágenes
        fuente: Fuente para el texto
    """
    pieza = slot_data['pieza']
    graying = slot_data['graying']
    gray_progress = slot_data['gray_progress']
    
    # Márgenes internos
    margen = 5
    slot_rect = pygame.Rect(x + margen, y + margen, ancho - 2*margen, alto - 2*margen)
    
    if alpha < 255:
        temp_surface = pygame.Surface((slot_rect.width, slot_rect.height), pygame.SRCALPHA)
        temp_surface.fill((0, 0, 0, 0))
    else:
        temp_surface = pantalla
    
    offset_x = 0 if alpha >= 255 else -slot_rect.x
    offset_y = 0 if alpha >= 255 else -slot_rect.y

    # Color de fondo del slot
    if es_activo and pieza and not graying:
        # Slot activo - fondo con resaltado
        fondo_surface = pygame.Surface((slot_rect.width, slot_rect.height), pygame.SRCALPHA)
        fondo_surface.fill(constants.COLOR_SLOT_ACTIVO)
        temp_surface.blit(fondo_surface, (slot_rect.x + offset_x, slot_rect.y + offset_y))
        color_borde = (255, 215, 0)  # Dorado
        grosor_borde = 3
    else:
        # Slot normal
        pygame.draw.rect(temp_surface, constants.COLOR_SLOT_NORMAL,
                         pygame.Rect(slot_rect.x + offset_x, slot_rect.y + offset_y, slot_rect.width, slot_rect.height))
        color_borde = constants.COLOR_PANEL_BORDE
        grosor_borde = 2
    

    pygame.draw.rect(temp_surface, color_borde, 
                    pygame.Rect(slot_rect.x + offset_x, slot_rect.y + offset_y, slot_rect.width, slot_rect.height), 
                    grosor_borde)

    if pieza:
        # Determinar color de la pieza
        if graying:
            # Interpolar entre el color original y gris
            if es_activo:
                color_original = constants.COLOR_J1_VIBRANTE if pieza.jugador == 1 else constants.COLOR_J2_VIBRANTE
            else:
                color_original = constants.COLOR_J1_OPACO if pieza.jugador == 1 else constants.COLOR_J2_OPACO
            
            color_gris = (100, 100, 100)
            
            # Interpolar RGB
            color = tuple(
                int(color_original[i] * (1 - gray_progress) + color_gris[i] * gray_progress)
                for i in range(3)
            )
        else:
            if es_activo:
                color = constants.COLOR_J1_VIBRANTE if pieza.jugador == 1 else constants.COLOR_J2_VIBRANTE
            else:
                color = constants.COLOR_J1_OPACO if pieza.jugador == 1 else constants.COLOR_J2_OPACO
        
        # Calcular tamaño de la imagen de la pieza
        tamano_pieza = (int(alto * 0.5), int(alto * 0.5))
        
        # Obtener imagen de la pieza
        imagen_pieza = crear_superficie_pieza(pieza.nombre, color, tamano_pieza, cache_imagenes)
        
        # Aplicar alpha si está en fade
        if graying:
            alpha = int(255 * (1 - gray_progress * 0.5))  # Fade a 50% de alpha
            imagen_pieza.set_alpha(alpha)
        
        # Posicionar la imagen a la izquierda del slot
        imagen_x = slot_rect.x + 10
        imagen_y = slot_rect.centery - tamano_pieza[1] // 2
        pantalla.blit(imagen_pieza, (imagen_x, imagen_y))
        
        # Dibujar información de la pieza a la derecha
        texto_x = imagen_x + tamano_pieza[0] + 10
        
        # Color del texto
        color_texto = constants.COLOR_TEXTO_NORMAL
        if graying:
            # Fade del texto también
            color_texto = tuple(
                int(constants.COLOR_TEXTO_NORMAL[i] * (1 - gray_progress * 0.5))
                for i in range(3)
            )
        
        # Nombre de la pieza
        texto_nombre = fuente.render(pieza.nombre, True, color_texto)
        texto_y = slot_rect.y + 5
        pantalla.blit(texto_nombre, (texto_x, texto_y))
        
        # HP de la pieza
        texto_hp = fuente.render(f"HP: {pieza.hp}/{pieza.hp_max}", True, color_texto)
        texto_y += texto_nombre.get_height() + 3
        pantalla.blit(texto_hp, (texto_x, texto_y))
        
        # Jugador
        color_jugador = constants.COLOR_J1_VIBRANTE if pieza.jugador == 1 else constants.COLOR_J2_VIBRANTE
        if graying:
            color_jugador = tuple(
                int(color_jugador[i] * (1 - gray_progress * 0.5))
                for i in range(3)
            )
        texto_jugador = fuente.render(f"J{pieza.jugador}", True, color_jugador)
        texto_y += texto_hp.get_height() + 3
        pantalla.blit(texto_jugador, (texto_x, texto_y))
        
        # Posición de la pieza
        if hasattr(pieza, 'posicion') and pieza.posicion:
            color_pos = (180, 180, 180)
            if graying:
                color_pos = tuple(
                    int(color_pos[i] * (1 - gray_progress * 0.5))
                    for i in range(3)
                )
            pos_texto = fuente.render(f"[{pieza.posicion[0]},{pieza.posicion[1]}]", True, color_pos)
            texto_y += texto_jugador.get_height() + 3
            pantalla.blit(pos_texto, (texto_x, texto_y))
        
        # Si es el turno activo, agregar indicador
        if es_activo and not graying:
            indicador = fuente.render("▶ ACTIVO", True, (255, 215, 0))
            pantalla.blit(indicador, (slot_rect.x + 10, slot_rect.bottom - indicador.get_height() - 5))
    
    if alpha < 255:
        # Aplicar alpha a la superficie temporal y blitear a la pantalla principal
        temp_surface.set_alpha(alpha)
        pantalla.blit(temp_surface, (slot_rect.x, slot_rect.y))

    else:
        # Slot vacío - mostrar mensaje
        texto_vacio = fuente.render("---", True, (100, 100, 100))
        texto_rect = texto_vacio.get_rect(center=slot_rect.center)
        pantalla.blit(texto_vacio, texto_rect)