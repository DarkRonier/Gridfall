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
    
    # Inicializar audio
    audio = init_audio()
    audio.play_game_start()
    
    # Crear ventana
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption(NOMBRE_VENTANA)
    
    # Crear fuentes
    # Crear fuentes escaladas
    tamanos = constants.obtener_tamanos_fuente()
    fuente_menu = pygame.font.SysFont("Impact", tamanos['menu'])
    fuente_ui = pygame.font.SysFont("Arial", tamanos['ui'])
    fuente_hp = pygame.font.SysFont("Arial", tamanos['hp'], bold=True)
    fuente_damage = pygame.font.SysFont("Impact", tamanos['damage'])
    
    # Variable para rastrear modo fullscreen
    es_fullscreen = False
    
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