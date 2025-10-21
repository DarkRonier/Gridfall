"""
Estado: CONFIRMACIÓN SALIR
Maneja la pantalla de confirmación para volver al menú
"""

import pygame
from game.constants import *
from game.drawing import dibujar_pantalla_confirmacion


def manejar_estado_confirmar_salir(pantalla, superficie_blur, fuente_menu, fuente_ui):
    """
    Maneja el estado de confirmación para salir del juego.
    
    Args:
        pantalla: Superficie de pygame
        superficie_blur: Superficie con el blur/velo del juego pausado
        fuente_menu: Fuente grande para títulos
        fuente_ui: Fuente para texto normal
    
    Returns:
        str: Nuevo estado ('menu_principal', 'en_juego', o 'saliendo')
    """
    
    reloj = pygame.time.Clock()
    
    while True:
        # Dibujar la pantalla de confirmación
        dibujar_pantalla_confirmacion(pantalla, superficie_blur, fuente_menu, fuente_ui)
        pygame.display.flip()
        
        # Manejo de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'saliendo'
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if BOTON_CONFIRMAR_SI_RECT.collidepoint(evento.pos):
                    return 'menu_principal'
                elif BOTON_CONFIRMAR_NO_RECT.collidepoint(evento.pos):
                    return 'en_juego'
        
        reloj.tick(FPS)