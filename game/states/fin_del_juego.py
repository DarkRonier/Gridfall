"""
Estado: FIN DEL JUEGO
Maneja la pantalla de victoria
"""

import pygame
from game.constants import *
from game.audio import get_audio


def manejar_estado_fin_juego(pantalla, ganador, fuente_menu, fuente_ui):
    """
    Maneja el estado de fin del juego (pantalla de victoria).
    
    Args:
        pantalla: Superficie de pygame
        ganador: Número del jugador ganador (1 o 2)
        fuente_menu: Fuente grande para el mensaje de victoria
        fuente_ui: Fuente para instrucciones
    
    Returns:
        str: Nuevo estado ('menu_principal' o 'saliendo')
    """
    
    audio = get_audio()
    
    # Reproducir sonido de victoria una sola vez
    if not hasattr(audio, '_victoria_sonada'):
        audio.play_victory()
        audio._victoria_sonada = True
    
    reloj = pygame.time.Clock()
    
    while True:
        # Limpiar pantalla
        pantalla.fill(COLOR_FONDO)
        
        # Texto de victoria
        texto_fin = fuente_menu.render(f"¡El Jugador {ganador} ha ganado!", True, (255, 215, 0))
        texto_instr = fuente_ui.render("Pulsa cualquier tecla para volver al menú", True, (255, 255, 255))
        
        rect_fin = texto_fin.get_rect(center=(ANCHO_VENTANA/2, ALTO_VENTANA/2 - 40))
        rect_instr = texto_instr.get_rect(center=(ANCHO_VENTANA/2, ALTO_VENTANA/2 + 20))
        
        pantalla.blit(texto_fin, rect_fin)
        pantalla.blit(texto_instr, rect_instr)
        pygame.display.flip()
        
        # Manejo de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'saliendo'
            
            if evento.type == pygame.KEYDOWN:
                # Limpiar el flag de victoria para la próxima vez
                if hasattr(audio, '_victoria_sonada'):
                    delattr(audio, '_victoria_sonada')
                return 'menu_principal'
        
        reloj.tick(FPS)