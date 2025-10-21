"""
Estado: EN JUEGO
Maneja toda la lógica del juego principal
"""

import copy
import pygame
from game.constants import *
from game.drawing import (dibujar_tablero, dibujar_piezas, dibujar_resaltados, dibujar_ui,
                          dibujar_numeros_flotantes, dibujar_animacion_activa, dibujar_proyectiles,
                          dibujar_borde_turno)
from game.logic import calcular_casillas_posibles, calcular_ataques_posibles, verificar_ganador
from game.effects import (DamageText, MoveAnimation, MeleeAttackAnimation,
                          FadeOutAnimation, ProjectileAnimation)
from game.audio import get_audio


def manejar_estado_en_juego(pantalla, tablero, turn_manager, historial_turnos, 
                             numeros_flotantes, animaciones_muerte, CACHE_IMAGENES,
                             fuente_hp, fuente_damage):
    """
    Maneja el estado del juego principal.
    
    Returns:
        tuple: (nuevo_estado, datos_actualizados)
        donde datos_actualizados es un dict con:
        - pieza_activa
        - movimientos_resaltados
        - ataques_resaltados
        - ganador
        - animacion_en_curso
        - superficie_blur (para confirmación)
    """
    
    # Estado local del juego
    pieza_activa = None
    movimientos_resaltados = []
    ataques_resaltados = []
    ganador = None
    animacion_en_curso = None
    superficie_blur = None
    
    audio = get_audio()
    
    def finalizar_turno():
        """Finaliza el turno actual y prepara el siguiente."""
        nonlocal pieza_activa, movimientos_resaltados, ataques_resaltados, ganador
        
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
                ganador = resultado
                return 'fin_del_juego'
        
        pieza_activa = None
        movimientos_resaltados = []
        ataques_resaltados = []
        return 'en_juego'
    
    # Loop principal del estado
    reloj = pygame.time.Clock()
    
    while True:
        # --- Actualización de estado ---
        if animacion_en_curso:
            terminada = animacion_en_curso.update()
            if terminada:
                entidad_ended = animacion_en_curso.entidad
                
                if isinstance(animacion_en_curso, MoveAnimation):
                    if entidad_ended.tipo_turno > 0 and not entidad_ended.ha_atacado:
                        ataques_resaltados = calcular_ataques_posibles(entidad_ended, tablero)
                        if not ataques_resaltados:
                            nuevo_estado = finalizar_turno()
                            if nuevo_estado == 'fin_del_juego':
                                return (nuevo_estado, {
                                    'pieza_activa': pieza_activa,
                                    'movimientos_resaltados': movimientos_resaltados,
                                    'ataques_resaltados': ataques_resaltados,
                                    'ganador': ganador,
                                    'animacion_en_curso': animacion_en_curso,
                                    'superficie_blur': superficie_blur
                                })
                    else:
                        finalizar_turno()
                
                elif isinstance(animacion_en_curso, (MeleeAttackAnimation, ProjectileAnimation)):
                    if entidad_ended.tipo_turno == 2 and not entidad_ended.ha_movido:
                        movimientos_resaltados = calcular_casillas_posibles(entidad_ended, tablero)
                        if not movimientos_resaltados:
                            nuevo_estado = finalizar_turno()
                            if nuevo_estado == 'fin_del_juego':
                                return (nuevo_estado, {
                                    'pieza_activa': pieza_activa,
                                    'movimientos_resaltados': movimientos_resaltados,
                                    'ataques_resaltados': ataques_resaltados,
                                    'ganador': ganador,
                                    'animacion_en_curso': animacion_en_curso,
                                    'superficie_blur': superficie_blur
                                })
                    else:
                        finalizar_turno()
                
                animacion_en_curso = None
        
        for animacion in list(animaciones_muerte):
            if animacion.update():
                animaciones_muerte.remove(animacion)
        
        for numero in numeros_flotantes:
            numero.update()
        numeros_flotantes[:] = [n for n in numeros_flotantes if n.lifetime > 0]
        
        if pieza_activa is None and not animacion_en_curso:
            while pieza_activa is None:
                pieza_encontrada = turn_manager.avanzar_reloj_y_obtener_pieza()
                if pieza_encontrada:
                    pieza_activa = pieza_encontrada
                    pieza_activa.reiniciar_estado_turno()
                    movimientos_resaltados = calcular_casillas_posibles(pieza_activa, tablero)
                    ataques_resaltados = calcular_ataques_posibles(pieza_activa, tablero)
                    break
        
        # --- Manejo de Eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return ('saliendo', {
                    'pieza_activa': pieza_activa,
                    'movimientos_resaltados': movimientos_resaltados,
                    'ataques_resaltados': ataques_resaltados,
                    'ganador': ganador,
                    'animacion_en_curso': animacion_en_curso,
                    'superficie_blur': superficie_blur
                })
            
            if evento.type == pygame.MOUSEBUTTONDOWN and pieza_activa and not animacion_en_curso:
                pos_clic = evento.pos
                
                if BOTON_VOLVER_RECT.collidepoint(pos_clic):
                    print("Volviendo al menú principal...")
                    copia_pantalla = pantalla.copy()
                    pequena = pygame.transform.smoothscale(copia_pantalla, (ANCHO_VENTANA // 10, ALTO_VENTANA // 10))
                    superficie_blur = pygame.transform.scale(pequena, (ANCHO_VENTANA, ALTO_VENTANA))
                    velo_oscuro = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
                    velo_oscuro.fill((0, 0, 0, 150))
                    superficie_blur.blit(velo_oscuro, (0, 0))
                    return ('confirmacion_salir', {
                        'pieza_activa': pieza_activa,
                        'movimientos_resaltados': movimientos_resaltados,
                        'ataques_resaltados': ataques_resaltados,
                        'ganador': ganador,
                        'animacion_en_curso': animacion_en_curso,
                        'superficie_blur': superficie_blur
                    })
                
                elif BOTON_DESHACER_RECT.collidepoint(pos_clic):
                    if historial_turnos:
                        print("Deshaciendo el último movimiento...")
                        estado_anterior = historial_turnos.pop()
                        
                        # Restaurar datos básicos
                        tablero[:] = estado_anterior['tablero']
                        turn_manager.piezas_en_juego = estado_anterior['piezas_en_juego'][:]
                        turn_manager.reloj = estado_anterior['reloj']
                        
                        # Reconstruir el tablero desde piezas_en_juego
                        for fila in range(FILAS):
                            for col in range(COLUMNAS):
                                tablero[fila][col] = None
                        
                        for pieza in turn_manager.piezas_en_juego:
                            fila, col = pieza.posicion
                            tablero[fila][col] = pieza
                        
                        # Limpiar piezas muertas
                        for fila in range(FILAS):
                            for col in range(COLUMNAS):
                                pieza = tablero[fila][col]
                                if pieza is not None and pieza.hp <= 0:
                                    tablero[fila][col] = None
                        
                        # Resetear estado visual
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
                            
                            def aplicar_dano_callback():
                                print(f"{pieza_activa.nombre} impacta a {pieza_atacada.nombre}.")
                                if pieza_activa.tipo_ataque == 'ranged':
                                    audio.play_ranged_impact()
                                
                                pieza_atacada.recibir_dano(pieza_activa.atk)
                                
                                centro_x = col_clic * TAMANO_CASILLA + TAMANO_CASILLA / 2
                                centro_y = fila_clic * TAMANO_CASILLA + UI_ALTO + TAMANO_CASILLA / 2
                                pos_damage = (centro_x, centro_y + (0.05 * TAMANO_CASILLA))
                                nuevo_numero = DamageText(pieza_activa.atk, pos_damage, fuente_damage)
                                numeros_flotantes.append(nuevo_numero)
                                
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
                            
                            tablero[vieja_fila][vieja_col] = None
                            tablero[fila_clic][col_clic] = pieza_activa
                            pieza_activa.posicion = (fila_clic, col_clic)
                            pieza_activa.ha_movido = True
                            
                            movimientos_resaltados = []
                            ataques_resaltados = []
        
        # --- Dibujado ---
        dibujar_tablero(pantalla)
        dibujar_borde_turno(pantalla, pieza_activa)
        
        if pieza_activa or animacion_en_curso:
            dibujar_resaltados(pantalla, movimientos_resaltados, ataques_resaltados, pieza_activa)
        
        dibujar_piezas(pantalla, tablero, pieza_activa, CACHE_IMAGENES, fuente_hp, animacion_en_curso)
        
        if animacion_en_curso:
            dibujar_animacion_activa(pantalla, animacion_en_curso, CACHE_IMAGENES)
        
        for animacion in animaciones_muerte:
            pieza = animacion.entidad
            alpha = animacion.get_alpha()
            
            from game.assets import crear_superficie_pieza
            color = COLOR_J1_OPACO if pieza.jugador == 1 else COLOR_J2_OPACO
            imagen_original = crear_superficie_pieza(pieza.nombre, color, (int(TAMANO_CASILLA*0.7), int(TAMANO_CASILLA*0.7)), CACHE_IMAGENES)
            
            imagen_draw = imagen_original.copy()
            imagen_draw.set_alpha(alpha)
            centro_x = int(pieza.posicion[1] * TAMANO_CASILLA + TAMANO_CASILLA / 2)
            centro_y = int(pieza.posicion[0] * TAMANO_CASILLA + UI_ALTO + TAMANO_CASILLA / 2)
            rect_imagen = imagen_draw.get_rect(center=(centro_x, centro_y))
            pantalla.blit(imagen_draw, rect_imagen)
        
        dibujar_numeros_flotantes(pantalla, numeros_flotantes)
        dibujar_ui(pantalla, pygame.font.SysFont("Arial", 20), pieza_activa)
        
        pygame.display.flip()
        reloj.tick(FPS)