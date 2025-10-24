"""
GRIDFALL v0.1.0
Juego de estrategia por turnos

Main refactorizado con estados modulares
"""

import pygame
import sys
import atexit

# Importar módulos del juego
from game.constants import *
from game import constants
from game.menu import mostrar_menu
from game.tutorial import mostrar_tutorial
from game.game_setup import crear_nuevo_juego
from game.turn_manager import TurnManager
from game.assets import cargar_svgs
from game.audio import init_audio

# Importar estados del juego
from game.states import (
    manejar_estado_en_juego,
    manejar_estado_confirmar_salir,
    manejar_estado_fin_juego
)


def pausar_al_salir():
    """Pausa la consola al salir del programa"""
    print("\n" + "="*50)
    print("PRESIONA ENTER PARA CERRAR...")
    print("="*50)
    input()


# Registrar función para pausar al salir
atexit.register(pausar_al_salir)


def main():
    """Función principal del juego"""
    
    # --- INICIALIZACIÓN DE PYGAME ---
    pygame.init()
    
    if not cargar_svgs():
        pygame.quit()
        sys.exit()
    
    # ===== PANTALLA DE CONFIGURACIÓN INICIAL =====
    temp_screen = pygame.display.set_mode((500, 250))
    pygame.display.set_caption("Gridfall - Configuración Inicial")
    
    fuente_titulo = pygame.font.SysFont("Impact", 28)
    fuente_texto = pygame.font.SysFont("Arial", 18)
    fuente_boton = pygame.font.SysFont("Arial", 20)
    
    preguntando = True
    es_fullscreen = False
    
    while preguntando:
        temp_screen.fill((30, 30, 30))
        
        # Título
        texto_titulo = fuente_titulo.render("GRIDFALL", True, (255, 215, 0))
        temp_screen.blit(texto_titulo, (180, 30))
        
        # Pregunta
        texto_pregunta = fuente_texto.render("¿Iniciar en pantalla completa?", True, (255, 255, 255))
        temp_screen.blit(texto_pregunta, (110, 90))
        
        # Botones
        boton_si = pygame.Rect(100, 150, 120, 50)
        boton_no = pygame.Rect(280, 150, 120, 50)
        
        # Detectar hover
        pos_mouse = pygame.mouse.get_pos()
        color_si = (80, 200, 80) if boton_si.collidepoint(pos_mouse) else (60, 180, 60)
        color_no = (200, 80, 80) if boton_no.collidepoint(pos_mouse) else (180, 60, 60)
        
        pygame.draw.rect(temp_screen, color_si, boton_si, border_radius=8)
        pygame.draw.rect(temp_screen, color_no, boton_no, border_radius=8)
        
        # Texto de botones
        texto_si = fuente_boton.render("Sí (F)", True, (255, 255, 255))
        texto_no = fuente_boton.render("No (W)", True, (255, 255, 255))
        
        temp_screen.blit(texto_si, texto_si.get_rect(center=boton_si.center))
        temp_screen.blit(texto_no, texto_no.get_rect(center=boton_no.center))
        
        # Hint de atajos
        texto_hint = fuente_texto.render("Puedes usar F (Fullscreen) o W (Ventana)", True, (150, 150, 150))
        temp_screen.blit(texto_hint, (60, 220))
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if boton_si.collidepoint(evento.pos):
                    es_fullscreen = True
                    preguntando = False
                elif boton_no.collidepoint(evento.pos):
                    es_fullscreen = False
                    preguntando = False
            
            if evento.type == pygame.KEYDOWN:
                # F = Fullscreen, W = Windowed (Ventana)
                if evento.key == pygame.K_f:
                    es_fullscreen = True
                    preguntando = False
                elif evento.key == pygame.K_w:
                    es_fullscreen = False
                    preguntando = False
                # También permitir Enter=Sí, Escape=No
                elif evento.key == pygame.K_RETURN:
                    es_fullscreen = True
                    preguntando = False
                elif evento.key == pygame.K_ESCAPE:
                    es_fullscreen = False
                    preguntando = False
    
    # Cerrar ventana temporal y reiniciar Pygame limpiamente
    pygame.display.quit()
    pygame.quit()
    pygame.init()
    
    # ===== CREAR VENTANA FINAL (UNA SOLA VEZ, SIN CAMBIOS POSTERIORES) =====
    if es_fullscreen:
        ancho, alto, escala, offset_x, offset_y = constants.calcular_fullscreen()
        constants.actualizar_dimensiones_ventana(ancho, alto, escala, offset_x, offset_y, True)
        pantalla = pygame.display.set_mode((ancho, alto), pygame.FULLSCREEN)
        print(f"[INICIO] Modo fullscreen: {ancho}x{alto}, escala={escala:.2f}")
    else:
        constants.actualizar_dimensiones_ventana(constants.ANCHO_BASE, constants.ALTO_BASE, 1.0, 0, 0, False)
        pantalla = pygame.display.set_mode((constants.ANCHO_BASE, constants.ALTO_BASE))
        print(f"[INICIO] Modo ventana: {constants.ANCHO_BASE}x{constants.ALTO_BASE}")
    
    pygame.display.set_caption(NOMBRE_VENTANA)
    
    # Inicializar audio
    audio = init_audio()
    audio.play_game_start()
    
    # Crear fuentes escaladas
    tamanos = constants.obtener_tamanos_fuente()
    fuente_menu = pygame.font.SysFont("Impact", tamanos['menu'])
    fuente_ui = pygame.font.SysFont("Arial", tamanos['ui'])
    fuente_hp = pygame.font.SysFont("Arial", tamanos['hp'], bold=True)
    fuente_damage = pygame.font.SysFont("Impact", tamanos['damage'])
    
    # --- ESTADO DEL JUEGO ---
    estado_juego = 'menu_principal'
    
    # Variables de juego (se inicializan cuando empieza una partida)
    tablero = None
    turn_manager = None
    historial_turnos = []
    numeros_flotantes = []
    animaciones_muerte = []
    CACHE_IMAGENES = {}
    
    # Variables del estado en_juego (se mantienen entre transiciones)
    datos_en_juego = {
        'pieza_activa': None,
        'movimientos_resaltados': [],
        'ataques_resaltados': [],
        'ganador': None,
        'animacion_en_curso': None,
        'superficie_blur': None
    }
    
    # --- LOOP PRINCIPAL ---
    while True:
        
        # ===== MENÚ PRINCIPAL =====
        if estado_juego == 'menu_principal':
            estado_juego, pantalla, es_fullscreen = mostrar_menu(pantalla, fuente_menu, es_fullscreen)
            
            # Si el usuario inicia un juego nuevo, inicializar todo
            if estado_juego == 'en_juego':
                tablero = crear_nuevo_juego()
                turn_manager = TurnManager(tablero)
                historial_turnos = []
                numeros_flotantes = []
                animaciones_muerte = []
                
                # Resetear datos del estado en_juego
                datos_en_juego = {
                    'pieza_activa': None,
                    'movimientos_resaltados': [],
                    'ataques_resaltados': [],
                    'ganador': None,
                    'animacion_en_curso': None,
                    'superficie_blur': None
                }
        
        # ===== EN JUEGO =====
        elif estado_juego == 'en_juego':
            estado_juego, datos_en_juego = manejar_estado_en_juego(
                pantalla, 
                tablero, 
                turn_manager,
                historial_turnos,
                numeros_flotantes,
                animaciones_muerte,
                CACHE_IMAGENES,
                fuente_hp,
                fuente_damage
            )
        
        # ===== CONFIRMACIÓN DE SALIR =====
        elif estado_juego == 'confirmacion_salir':
            estado_juego = manejar_estado_confirmar_salir(
                pantalla,
                datos_en_juego['superficie_blur'],
                fuente_menu,
                fuente_ui
            )
        
        # ===== TUTORIAL =====
        elif estado_juego == 'tutorial':
            estado_juego = mostrar_tutorial(pantalla, fuente_menu, fuente_ui, CACHE_IMAGENES)
        
        # ===== FIN DEL JUEGO =====
        elif estado_juego == 'fin_del_juego':
            estado_juego = manejar_estado_fin_juego(
                pantalla,
                datos_en_juego['ganador'],
                fuente_menu,
                fuente_ui
            )
        
        # ===== SALIR =====
        elif estado_juego == 'saliendo':
            break
    
    # --- SALIDA LIMPIA ---
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()