import pygame
from .constants import *

def mostrar_menu(pantalla, fuente_grande):
    """Muestra el menú principal y maneja sus eventos. Devuelve el siguiente estado."""
    # Definimos los rectángulos para los botones
    boton_nuevo_juego = pygame.Rect(ANCHO_VENTANA/2 - 150, ALTO_VENTANA/2 - 90, 300, 60)
    boton_tutorial = pygame.Rect(ANCHO_VENTANA/2 - 150, ALTO_VENTANA/2 - 10, 300, 60)
    boton_salir = pygame.Rect(ANCHO_VENTANA/2 - 150, ALTO_VENTANA/2 + 70, 300, 60)
    
    while True:
        # Dibujado del menú
        pantalla.fill(COLOR_FONDO)
        
        # Título
        texto_titulo = fuente_grande.render("GridFall", True, (255, 255, 255))
        rect_titulo = texto_titulo.get_rect(center=(ANCHO_VENTANA/2, ALTO_VENTANA/4))
        pantalla.blit(texto_titulo, rect_titulo)

        # Botones
        pygame.draw.rect(pantalla, (0, 100, 0), boton_nuevo_juego, border_radius=15)
        pygame.draw.rect(pantalla, (0, 0, 150), boton_tutorial, border_radius=15)
        pygame.draw.rect(pantalla, (100, 0, 0), boton_salir, border_radius=15)

        # Texto de los botones
        texto_nuevo = fuente_grande.render("Nuevo Juego", True, (255, 255, 255))
        pantalla.blit(texto_nuevo, texto_nuevo.get_rect(center=boton_nuevo_juego.center))
        
        texto_tutorial = fuente_grande.render("Cómo Jugar", True, (255, 255, 255))
        pantalla.blit(texto_tutorial, texto_tutorial.get_rect(center=boton_tutorial.center))

        texto_salir = fuente_grande.render("Salir", True, (255, 255, 255))
        pantalla.blit(texto_salir, texto_salir.get_rect(center=boton_salir.center))

        pygame.display.flip()

        # Manejo de eventos del menú
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'saliendo' # Devuelve el estado para salir
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_nuevo_juego.collidepoint(evento.pos):
                    return 'en_juego' # Devuelve el estado para empezar a jugar
                if boton_tutorial.collidepoint(evento.pos):
                    return 'tutorial'
                if boton_salir.collidepoint(evento.pos):
                    return 'saliendo' # Devuelve el estado para salir