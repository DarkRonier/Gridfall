import copy
import pygame
import sys
from game.constants import *
from game.drawing import (dibujar_tablero, dibujar_piezas, dibujar_resaltados, dibujar_ui,
                          dibujar_numeros_flotantes, dibujar_animacion_activa, dibujar_proyectiles,
                          dibujar_pantalla_confirmacion, dibujar_borde_turno)
from game.menu import mostrar_menu
from game.tutorial import mostrar_tutorial
from game.game_setup import crear_nuevo_juego
from game.turn_manager import TurnManager
from game.assets import cargar_svgs, crear_superficie_pieza
from game.logic import calcular_casillas_posibles, calcular_ataques_posibles, verificar_ganador
from game.effects import (DamageText, MoveAnimation, MeleeAttackAnimation,
                          FadeOutAnimation, ProjectileAnimation)
from game.piece import Pieza
from game.audio import init_audio, get_audio

import atexit

def pausar_al_salir():
    print("\n" + "="*50)
    print("PRESIONA ENTER PARA CERRAR...")
    print("="*50)
    input()

atexit.register(pausar_al_salir)

# --- INICIALIZACIÓN DE PYGAME Y FUENTES ---
pygame.init()
if not cargar_svgs():
    pygame.quit()
    sys.exit()

audio = init_audio() # Inicializar sistema de audio
audio.play_game_start()

pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption(NOMBRE_VENTANA)
reloj = pygame.time.Clock()
fuente_piezas = pygame.font.SysFont("Arial", 24)
fuente_ui = pygame.font.SysFont("Arial", 20)
fuente_menu = pygame.font.SysFont("Impact", 40)
fuente_hp = pygame.font.SysFont("Arial", 14, bold=True)
fuente_damage = pygame.font.SysFont("Impact", 28)

# --- GESTOR DE ESTADOS DEL JUEGO ---
estado_juego = 'menu_principal'
tablero = None
turn_manager = None
pieza_activa = None
movimientos_resaltados = []
ataques_resaltados = []
ganador = None
numeros_flotantes = []
animacion_en_curso = None
superficie_blur = None
animaciones_muerte = []
CACHE_IMAGENES = {}
historial_turnos = []

while True:
    if estado_juego == 'menu_principal':
        estado_juego = mostrar_menu(pantalla, fuente_menu)
        if estado_juego == 'en_juego':
            tablero = crear_nuevo_juego()
            turn_manager = TurnManager(tablero)
            pieza_activa = None
            movimientos_resaltados = []
            ataques_resaltados = []
            historial_turnos = []

    elif estado_juego == 'en_juego':
        def finalizar_turno():
            global pieza_activa, movimientos_resaltados, ataques_resaltados, estado_juego, ganador

            estado_actual = {
                'tablero': copy.deepcopy(tablero),
                'piezas_en_juego': copy.deepcopy(turn_manager.piezas_en_juego),
                'reloj': turn_manager.reloj,
            }
            historial_turnos.append(estado_actual)
            if len(historial_turnos) > 5:
                historial_turnos.pop(0)
            
            if pieza_activa:
                pieza_activa.calcular_siguiente_turno(turn_manager.reloj)
                resultado = verificar_ganador(turn_manager.piezas_en_juego)
                if resultado is not None:
                    estado_juego = 'fin_del_juego'
                    ganador = resultado
            pieza_activa = None
            movimientos_resaltados = []
            ataques_resaltados = []

        # --- Actualización de estado  ---
        if animacion_en_curso:
            terminada = animacion_en_curso.update()
            if terminada:
                entidad_ended = animacion_en_curso.entidad
                
                if isinstance(animacion_en_curso, MoveAnimation):
                    if entidad_ended.tipo_turno > 0 and not entidad_ended.ha_atacado:
                        ataques_resaltados = calcular_ataques_posibles(entidad_ended, tablero)
                        if not ataques_resaltados:
                            finalizar_turno()
                    else:
                        finalizar_turno()

                elif isinstance(animacion_en_curso, (MeleeAttackAnimation, ProjectileAnimation)):
                    if entidad_ended.tipo_turno == 2 and not entidad_ended.ha_movido:
                        movimientos_resaltados = calcular_casillas_posibles(entidad_ended, tablero)
                        if not movimientos_resaltados:
                            finalizar_turno()
                    else:
                        finalizar_turno()
                
                animacion_en_curso = None
        
        for animacion in list(animaciones_muerte):
            if animacion.update():
                animaciones_muerte.remove(animacion)
        for numero in numeros_flotantes:
            numero.update()
        numeros_flotantes = [n for n in numeros_flotantes if n.lifetime > 0]

        if pieza_activa is None and not animacion_en_curso:
            while pieza_activa is None:
                pieza_encontrada = turn_manager.avanzar_reloj_y_obtener_pieza()
                if pieza_encontrada:                    
                    pieza_activa = pieza_encontrada
                    pieza_activa.reiniciar_estado_turno()
                    movimientos_resaltados = calcular_casillas_posibles(pieza_activa, tablero)
                    ataques_resaltados = calcular_ataques_posibles(pieza_activa, tablero)
                    break

        # --- Manejo de Eventos del Jugador ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                estado_juego = 'saliendo'
            
            if evento.type == pygame.MOUSEBUTTONDOWN and pieza_activa and not animacion_en_curso:
                pos_clic = evento.pos

                if BOTON_VOLVER_RECT.collidepoint(pos_clic):
                    print("Volviendo al menú principal...")
                    copia_pantalla = pantalla.copy()
                    pequena = pygame.transform.smoothscale(copia_pantalla, (ANCHO_VENTANA // 10, ALTO_VENTANA // 10))
                    superficie_blur = pygame.transform.scale(pequena, (ANCHO_VENTANA, ALTO_VENTANA))
                    velo_oscuro = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
                    velo_oscuro.fill((0, 0, 0, 150))
                    superficie_blur.blit(velo_oscuro, (0,0))
                    estado_juego = 'confirmacion_salir'

                elif BOTON_DESHACER_RECT.collidepoint(pos_clic):
                    if historial_turnos:
                        print("Deshaciendo el último movimiento...")
                        estado_anterior = historial_turnos.pop()

                        # 1. Restaurar datos básicos
                        tablero[:] = estado_anterior['tablero']
                        turn_manager.piezas_en_juego = estado_anterior['piezas_en_juego'][:]
                        turn_manager.reloj = estado_anterior['reloj']

                        # 2. CRÍTICO: Reconstruir el tablero desde piezas_en_juego
                        # Esto asegura que las referencias sean consistentes
                        for fila in range(FILAS):
                            for col in range(COLUMNAS):
                                tablero[fila][col] = None
                        
                        for pieza in turn_manager.piezas_en_juego:
                            fila, col = pieza.posicion
                            tablero[fila][col] = pieza

                        # 3. CRÍTICO: Limpiar piezas muertas (por si acaso)
                        piezas_vivas = [p for p in turn_manager.piezas_en_juego if p.hp > 0]
                        turn_manager.piezas_en_juego = piezas_vivas

                        # 4. Limpiar tablero de piezas muertas
                        for fila in range(FILAS):
                            for col in range(COLUMNAS):
                                pieza = tablero[fila][col]
                                if pieza is not None and pieza.hp <= 0:
                                    tablero[fila][col] = None

                        # 5. Resetear todo el estado visual
                        pieza_activa = None
                        animacion_en_curso = None
                        numeros_flotantes.clear()
                        animaciones_muerte.clear()
                        movimientos_resaltados.clear()
                        ataques_resaltados.clear()
                    else:
                        print("No hay movimientos para deshacer.")
                        
                elif BOTON_PASAR_RECT.collidepoint(pos_clic):
                    print("Pasando turno...")
                    finalizar_turno()

                elif pos_clic[1] >= UI_ALTO:
                    fila_clic = (pos_clic[1] - UI_ALTO) // TAMANO_CASILLA
                    col_clic = pos_clic[0] // TAMANO_CASILLA
                
                    if (fila_clic, col_clic) in ataques_resaltados:
                        if not pieza_activa.ha_atacado:
                            pieza_atacada = tablero[fila_clic][col_clic]

                            # --- LÓGICA DE CALLBACK ---
                            # 1. Empaquetamos toda la lógica de daño en una función anónima (lambda)
                            def aplicar_dano_callback():
                                # Esta función se ejecutará a mitad de la animación
                                print(f"{pieza_activa.nombre} impacta a {pieza_atacada.nombre}.")
                                if pieza_activa.tipo_ataque == 'ranged':
                                    audio.play_ranged_impact()

                                pieza_atacada.recibir_dano(pieza_activa.atk)

                                centro_x = col_clic * TAMANO_CASILLA + TAMANO_CASILLA / 2
                                centro_y = fila_clic * TAMANO_CASILLA + UI_ALTO + TAMANO_CASILLA / 2
                                pos_damage = (centro_x, centro_y + (0.05 * TAMANO_CASILLA))
                                nuevo_numero = DamageText(pieza_activa.atk, pos_damage, fuente_damage)
                                numeros_flotantes.append(nuevo_numero)

                                # Comprobamos si la pieza murió
                                if not pieza_atacada.esta_viva():
                                    audio.play_death()
                                    if pieza_atacada in turn_manager.piezas_en_juego:
                                        turn_manager.piezas_en_juego.remove(pieza_atacada)
                                        nueva_anim_muerte = FadeOutAnimation(pieza_atacada)
                                        animaciones_muerte.append(nueva_anim_muerte)
                                        tablero[fila_clic][col_clic] = None

                            pieza_activa.ha_atacado = True
                            ataques_resaltados = []
                            movimientos_resaltados = []

                            # 2. Calculamos las posiciones en píxeles
                            start_px = (pieza_activa.posicion[1] * TAMANO_CASILLA + TAMANO_CASILLA / 2,
                                        pieza_activa.posicion[0] * TAMANO_CASILLA + UI_ALTO + TAMANO_CASILLA / 2)
                            target_px = (col_clic * TAMANO_CASILLA + TAMANO_CASILLA / 2,
                                        fila_clic * TAMANO_CASILLA + UI_ALTO + TAMANO_CASILLA / 2)
                            
                            if pieza_activa.tipo_ataque == 'melee':
                                animacion_en_curso = MeleeAttackAnimation(pieza_activa, start_px, target_px, 30, aplicar_dano_callback)
                                audio.play_melee_attack()

                            elif pieza_activa.tipo_ataque == 'ranged':
                                animacion_en_curso = ProjectileAnimation(pieza_activa, start_px, target_px, 40, aplicar_dano_callback)
                                audio.play_ranged_cast()
                    
                    elif (fila_clic, col_clic) in movimientos_resaltados:
                        if not pieza_activa.ha_movido:
                            vieja_fila, vieja_col = pieza_activa.posicion

                            start_px = (vieja_col * TAMANO_CASILLA + TAMANO_CASILLA / 2,
                                        vieja_fila * TAMANO_CASILLA + UI_ALTO + TAMANO_CASILLA / 2)
                            end_px = (col_clic * TAMANO_CASILLA + TAMANO_CASILLA / 2,
                                    fila_clic * TAMANO_CASILLA + UI_ALTO + TAMANO_CASILLA / 2)
                            
                            animacion_en_curso = MoveAnimation(pieza_activa, start_px, end_px, 10)

                            audio.play_move()

                            # Actualizamos el tablero y la posición de la pieza
                            tablero[vieja_fila][vieja_col] = None
                            tablero[fila_clic][col_clic] = pieza_activa
                            pieza_activa.posicion = (fila_clic, col_clic)
                            pieza_activa.ha_movido = True

                            movimientos_resaltados = []
                            ataques_resaltados = []

        # --- DIBUJADO DEL JUEGO ---
        dibujar_tablero(pantalla)
        dibujar_borde_turno(pantalla, pieza_activa)
        # La función de dibujado ahora necesita ambas listas de resaltados
        if pieza_activa or animacion_en_curso:
            dibujar_resaltados(pantalla, movimientos_resaltados, ataques_resaltados, pieza_activa)
        dibujar_piezas(pantalla, tablero, pieza_activa, CACHE_IMAGENES, fuente_hp, animacion_en_curso)
        
        if animacion_en_curso:
            dibujar_animacion_activa(pantalla, animacion_en_curso, CACHE_IMAGENES)

        for animacion in animaciones_muerte:
            pieza = animacion.entidad
            alpha = animacion.get_alpha()

            color = COLOR_J1_OPACO if pieza.jugador == 1 else COLOR_J2_OPACO
            imagen_original = crear_superficie_pieza(pieza.nombre, color, (int(TAMANO_CASILLA*0.7), int(TAMANO_CASILLA*0.7)), CACHE_IMAGENES)
            
            imagen_draw = imagen_original.copy()
            imagen_draw.set_alpha(alpha)
            centro_x = int(pieza.posicion[1] * TAMANO_CASILLA + TAMANO_CASILLA / 2)
            centro_y = int(pieza.posicion[0] * TAMANO_CASILLA + UI_ALTO + TAMANO_CASILLA / 2)
            rect_imagen = imagen_draw.get_rect(center=(centro_x, centro_y))
            pantalla.blit(imagen_draw, rect_imagen)

        dibujar_numeros_flotantes(pantalla, numeros_flotantes)
        dibujar_ui(pantalla, fuente_ui, pieza_activa)
        pygame.display.flip()
        reloj.tick(FPS)

    elif estado_juego == 'confirmacion_salir':
        dibujar_pantalla_confirmacion(pantalla, superficie_blur, fuente_menu, fuente_ui)
        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                estado_juego = 'saliendo'
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if BOTON_CONFIRMAR_SI_RECT.collidepoint(evento.pos):
                    estado_juego = 'menu_principal'
                elif BOTON_CONFIRMAR_NO_RECT.collidepoint(evento.pos):
                    estado_juego = 'en_juego'
    
    elif estado_juego == 'tutorial':
        estado_juego = mostrar_tutorial(pantalla, fuente_menu, fuente_ui, CACHE_IMAGENES)

    elif estado_juego == 'fin_del_juego':
        if not hasattr(audio, '_victoria_sonada'):
            audio.play_victory()
            audio._victoria_sonada = True

        # Pantalla de fin de juego
        texto_fin = fuente_menu.render(f"¡El Jugador {ganador} ha ganado!", True, (255, 215, 0))
        texto_instr = fuente_ui.render("Pulsa cualquier tecla para volver al menú", True, (255, 255, 255))
        
        rect_fin = texto_fin.get_rect(center=(ANCHO_VENTANA/2, ALTO_VENTANA/2 - 40))
        rect_instr = texto_instr.get_rect(center=(ANCHO_VENTANA/2, ALTO_VENTANA/2 + 20))

        pantalla.blit(texto_fin, rect_fin)
        pantalla.blit(texto_instr, rect_instr)
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                estado_juego = 'saliendo'
            if evento.type == pygame.KEYDOWN:
                if hasattr(audio, '_victoria_sonada'):
                    delattr(audio, '_victoria_sonada')
                estado_juego = 'menu_principal'

    elif estado_juego == 'saliendo':
        break

# --- SALIDA DEL JUEGO ---
pygame.quit()
sys.exit()