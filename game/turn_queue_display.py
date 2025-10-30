"""
Módulo para dibujar el panel de cola de turnos
"""

import pygame
from game import constants
from game.assets import crear_superficie_pieza


def dibujar_panel_turnos(pantalla, turn_queue, cache_imagenes, fuente_ui):
    """
    Dibuja el panel de cola de turnos al lado derecho del tablero.
    
    Args:
        pantalla: Superficie de pygame donde dibujar
        turn_queue: Instancia de TurnQueue con las piezas en cola
        cache_imagenes: Caché de imágenes de piezas
        fuente_ui: Fuente para el texto
    """
    # Obtener la cola de piezas
    cola = turn_queue.get_queue()
    
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
    altura_slot = espacio_disponible // 5
    
    # Dibujar cada slot de la cola
    for i in range(5):
        slot_y = panel_y + margen_superior + (i * altura_slot)
        
        # Determinar si este slot tiene una pieza
        pieza = cola[i] if i < len(cola) else None
        
        # Dibujar el slot
        _dibujar_slot_turno(
            pantalla, 
            panel_x, 
            slot_y, 
            panel_ancho, 
            altura_slot,
            pieza, 
            (i == 0),  # El primero es el activo
            cache_imagenes,
            fuente_ui
        )


def _dibujar_slot_turno(pantalla, x, y, ancho, alto, pieza, es_activo, cache_imagenes, fuente):
    """
    Dibuja un slot individual de la cola de turnos.
    
    Args:
        pantalla: Superficie donde dibujar
        x, y: Coordenadas del slot
        ancho, alto: Dimensiones del slot
        pieza: Pieza a mostrar (o None si el slot está vacío)
        es_activo: True si es la pieza del turno actual
        cache_imagenes: Caché de imágenes
        fuente: Fuente para el texto
    """
    # Márgenes internos
    margen = 5
    slot_rect = pygame.Rect(x + margen, y + margen, ancho - 2*margen, alto - 2*margen)
    
    # Color de fondo del slot
    if es_activo and pieza:
        # Slot activo - fondo con resaltado
        fondo_surface = pygame.Surface((slot_rect.width, slot_rect.height), pygame.SRCALPHA)
        fondo_surface.fill(constants.COLOR_SLOT_ACTIVO)
        pantalla.blit(fondo_surface, (slot_rect.x, slot_rect.y))
        color_borde = (255, 215, 0)  # Dorado
        grosor_borde = 3
    else:
        # Slot normal
        pygame.draw.rect(pantalla, constants.COLOR_SLOT_NORMAL, slot_rect)
        color_borde = constants.COLOR_PANEL_BORDE
        grosor_borde = 2
    
    # Dibujar borde del slot
    pygame.draw.rect(pantalla, color_borde, slot_rect, grosor_borde)
    
    # Si hay una pieza, dibujarla
    if pieza:
        # Determinar color de la pieza
        if es_activo:
            color = constants.COLOR_J1_VIBRANTE if pieza.jugador == 1 else constants.COLOR_J2_VIBRANTE
        else:
            color = constants.COLOR_J1_OPACO if pieza.jugador == 1 else constants.COLOR_J2_OPACO
        
        # Calcular tamaño de la imagen de la pieza (más pequeña que en el tablero)
        tamano_pieza = (int(alto * 0.5), int(alto * 0.5))
        
        # Obtener imagen de la pieza
        imagen_pieza = crear_superficie_pieza(pieza.nombre, color, tamano_pieza, cache_imagenes)
        
        # Posicionar la imagen a la izquierda del slot
        imagen_x = slot_rect.x + 10
        imagen_y = slot_rect.centery - tamano_pieza[1] // 2
        pantalla.blit(imagen_pieza, (imagen_x, imagen_y))
        
        # Dibujar información de la pieza a la derecha
        texto_x = imagen_x + tamano_pieza[0] + 10
        
        # Nombre de la pieza
        texto_nombre = fuente.render(pieza.nombre, True, constants.COLOR_TEXTO_NORMAL)
        texto_y = slot_rect.y + 5
        pantalla.blit(texto_nombre, (texto_x, texto_y))
        
        # HP de la pieza
        texto_hp = fuente.render(f"HP: {pieza.hp}/{pieza.hp_max}", True, constants.COLOR_TEXTO_NORMAL)
        texto_y += texto_nombre.get_height() + 3
        pantalla.blit(texto_hp, (texto_x, texto_y))
        
        # Jugador
        color_jugador = constants.COLOR_J1_VIBRANTE if pieza.jugador == 1 else constants.COLOR_J2_VIBRANTE
        texto_jugador = fuente.render(f"J{pieza.jugador}", True, color_jugador)
        texto_y += texto_hp.get_height() + 3
        pantalla.blit(texto_jugador, (texto_x, texto_y))
        
        # Posición de la pieza (para diferenciar piezas del mismo tipo)
        if hasattr(pieza, 'posicion') and pieza.posicion:
            pos_texto = fuente.render(f"[{pieza.posicion[0]},{pieza.posicion[1]}]", True, (180, 180, 180))
            texto_y += texto_jugador.get_height() + 3
            pantalla.blit(pos_texto, (texto_x, texto_y))
        
        # Si es el turno activo, agregar indicador
        if es_activo:
            indicador = fuente.render("▶ ACTIVO", True, (255, 215, 0))
            pantalla.blit(indicador, (slot_rect.x + 10, slot_rect.bottom - indicador.get_height() - 5))
    else:
        # Slot vacío - mostrar mensaje
        texto_vacio = fuente.render("---", True, (100, 100, 100))
        texto_rect = texto_vacio.get_rect(center=slot_rect.center)
        pantalla.blit(texto_vacio, texto_rect)