# ChessLike/game/drawing.py

import pygame
from .constants import *
from .assets import crear_superficie_pieza
from game.effects import MeleeAttackAnimation, ProjectileAnimation, MoveAnimation

def dibujar_tablero(pantalla):
    """Dibuja las casillas del tablero."""
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            color = GRIS_CLARO if (fila + col) % 2 == 0 else GRIS_OSCURO
            pygame.draw.rect(pantalla, color, (col * TAMANO_CASILLA, fila * TAMANO_CASILLA + UI_ALTO, TAMANO_CASILLA, TAMANO_CASILLA))

def dibujar_piezas(pantalla, tablero, pieza_activa, cache_imagenes, fuente_hp, animacion_activa=None):
    """Dibuja las piezas sobre el tablero."""
    tamano_pieza = (int(TAMANO_CASILLA * 0.7), int(TAMANO_CASILLA * 0.7))

    for fila in range(FILAS):
        for col in range(COLUMNAS):
            pieza = tablero[fila][col]
            if pieza is not None:
                if animacion_activa and isinstance(animacion_activa, (MoveAnimation, MeleeAttackAnimation)):
                    if pieza is animacion_activa.entidad:
                        continue

                if pieza is pieza_activa:
                    color = COLOR_J1_VIBRANTE if pieza.jugador == 1 else COLOR_J2_VIBRANTE
                else:
                    color = COLOR_J1_OPACO if pieza.jugador == 1 else COLOR_J2_OPACO

                # Obtenemos la imagen de la pieza (desde el caché o la creamos)
                imagen_pieza = crear_superficie_pieza(pieza.nombre, color, tamano_pieza, cache_imagenes)
                
                # Calcular la posición para centrar la imagen en la casilla.
                centro_x = int(col * TAMANO_CASILLA + TAMANO_CASILLA / 2)
                centro_y = int(fila * TAMANO_CASILLA + UI_ALTO + TAMANO_CASILLA / 2)
                rect_imagen = imagen_pieza.get_rect(center=(centro_x, centro_y))

                # Dibujar la imagen de la pieza.
                pantalla.blit(imagen_pieza, rect_imagen)

                # 6. Dibujar la barra de vida debajo de la pieza.
                # Posición y tamaño de la barra de vida
                ancho_barra_total = tamano_pieza[0]
                alto_barra = 8
                pos_x_barra = rect_imagen.left
                pos_y_barra = rect_imagen.bottom + 2

                # Calcular el porcentaje de vida
                porcentaje_vida = pieza.hp / pieza.hp_max
                ancho_vida_actual = ancho_barra_total * porcentaje_vida

                # Seleccionar el color de la barra según el porcentaje
                if porcentaje_vida > 0.6:
                    color_vida = COLOR_HP_ALTA
                elif porcentaje_vida > 0.3:
                    color_vida = COLOR_HP_MEDIA
                else:
                    color_vida = COLOR_HP_BAJA

                pygame.draw.rect(pantalla, COLOR_HP_FONDO, (pos_x_barra, pos_y_barra, ancho_barra_total, alto_barra))
                if ancho_vida_actual > 0:
                    pygame.draw.rect(pantalla, color_vida, (pos_x_barra, pos_y_barra, ancho_vida_actual, alto_barra))
                
                # 7. Dibujar el número de vida actual sobre la barra.
                texto_hp = fuente_hp.render(str(pieza.hp), True, (255, 255, 255))
                texto_hp_sombra = fuente_hp.render(str(pieza.hp), True, (0, 0, 0))
                rect_texto_hp = texto_hp.get_rect(center=(pos_x_barra + ancho_barra_total / 2, pos_y_barra + alto_barra / 2))

                pantalla.blit(texto_hp_sombra, (rect_texto_hp.left - 1, rect_texto_hp.top - 1))
                pantalla.blit(texto_hp_sombra, (rect_texto_hp.left + 1, rect_texto_hp.top - 1))
                pantalla.blit(texto_hp_sombra, (rect_texto_hp.left - 1, rect_texto_hp.top + 1))
                pantalla.blit(texto_hp_sombra, (rect_texto_hp.left + 1, rect_texto_hp.top + 1))

                pantalla.blit(texto_hp, rect_texto_hp)

def dibujar_resaltados(pantalla, casillas_movimiento, casillas_ataque, pieza_activa):
    if pieza_activa:
        activo_surface = pygame.Surface((TAMANO_CASILLA, TAMANO_CASILLA), pygame.SRCALPHA)
        activo_surface.fill(COLOR_RESALTADO_ACTIVO)
        fila, col = pieza_activa.posicion
        pantalla.blit(activo_surface, (col * TAMANO_CASILLA, fila * TAMANO_CASILLA + UI_ALTO))
        
    mov_surface = pygame.Surface((TAMANO_CASILLA, TAMANO_CASILLA), pygame.SRCALPHA)
    mov_surface.fill((100, 255, 100, 100))
    for fila, col in casillas_movimiento:
        pantalla.blit(mov_surface, (col * TAMANO_CASILLA, fila * TAMANO_CASILLA + UI_ALTO))

    # Superficie para ataque
    atk_surface = pygame.Surface((TAMANO_CASILLA, TAMANO_CASILLA), pygame.SRCALPHA)
    atk_surface.fill((255, 50, 50, 120)) # Rojo semitransparente
    for fila, col in casillas_ataque:
        pantalla.blit(atk_surface, (col * TAMANO_CASILLA, fila * TAMANO_CASILLA + UI_ALTO))


def dibujar_ui(pantalla, fuente, pieza_activa):
    """Dibuja elementos de la interfaz, como el botón de pasar turno."""
    # Fondo del UI
    fondo_ui = pygame.Rect(0, 0, ANCHO_VENTANA, UI_ALTO)
    pygame.draw.rect(pantalla, (30, 30, 30), fondo_ui)

    # Boton Volver
    pygame.draw.rect(pantalla, (180, 50, 50), BOTON_VOLVER_RECT, border_radius=5)
    texto_volver = fuente.render("Volver", True, (255, 255, 255))
    pantalla.blit(texto_volver, texto_volver.get_rect(center=BOTON_VOLVER_RECT.center))

    # Botón de Pasar Turno
    pygame.draw.rect(pantalla, (90, 90, 90), BOTON_PASAR_RECT, border_radius=5)
    texto_pasar = fuente.render(">|", True, (255, 255, 255))
    pantalla.blit(texto_pasar, texto_pasar.get_rect(center=BOTON_PASAR_RECT.center))
    
    # Indicador de turno
    if pieza_activa:
        pos_x_texto = BOTON_VOLVER_RECT.right + 20
        
        texto_turno = f"Turno de J{pieza_activa.jugador}: {pieza_activa.nombre} en [{pieza_activa.posicion[0]},{pieza_activa.posicion[1]}]"
        indicador = fuente.render(texto_turno, True, (255, 255, 255))
        pos_y_texto = UI_ALTO / 2 - indicador.get_height() / 2
        pantalla.blit(indicador, (pos_x_texto, pos_y_texto))

def dibujar_proyectiles(pantalla, proyectiles):
    for proyectil in proyectiles:
        proyectil.draw(pantalla)

def dibujar_numeros_flotantes(pantalla, numeros):
    """Recorre la lista de números de daño y los dibuja."""
    for numero in numeros:
        numero.draw(pantalla)

def dibujar_animacion_activa(pantalla, animacion, cache_imagenes):
    """Dibuja la pieza que está en medio de una animación de movimiento."""
    if isinstance(animacion, (MoveAnimation, MeleeAttackAnimation)):
        entidad = animacion.entidad
        color = COLOR_J1_VIBRANTE if entidad.jugador == 1 else COLOR_J2_VIBRANTE
        tamano_pieza = (int(TAMANO_CASILLA * 0.7), int(TAMANO_CASILLA * 0.7))
        imagen_pieza = crear_superficie_pieza(entidad.nombre, color, tamano_pieza, cache_imagenes)
        pos_actual = animacion.get_pos()
        rect_imagen = imagen_pieza.get_rect(center=pos_actual)
        pantalla.blit(imagen_pieza, rect_imagen)
    elif isinstance(animacion, ProjectileAnimation):
        animacion.draw(pantalla)

def dibujar_pantalla_confirmacion(pantalla, fondo_blur, fuente_menu, fuente_ui):
    """Dibuja la pantalla de confirmación sobre un fondo desenfocado."""
    
    # 1. Dibuja el fondo desenfocado que ya hemos creado.
    pantalla.blit(fondo_blur, (0, 0))

    # 2. Dibuja el panel semitransparente para el texto.
    pygame.draw.rect(pantalla, (40, 40, 40, 200), PANEL_CONFIRMACION_RECT)
    pygame.draw.rect(pantalla, (200, 200, 200), PANEL_CONFIRMACION_RECT, 2) # Borde

    # 3. Dibuja el texto de advertencia.
    texto1 = "Seguro que quieres volver al Menu Principal?"
    texto2 = "Se perderá el progreso del juego."
    
    superficie_texto1 = fuente_ui.render(texto1, True, (255, 255, 255))
    superficie_texto2 = fuente_ui.render(texto2, True, (255, 200, 200))
    
    pantalla.blit(superficie_texto1, superficie_texto1.get_rect(center=(PANEL_CONFIRMACION_RECT.centerx, PANEL_CONFIRMACION_RECT.centery - 30)))
    pantalla.blit(superficie_texto2, superficie_texto2.get_rect(center=(PANEL_CONFIRMACION_RECT.centerx, PANEL_CONFIRMACION_RECT.centery)))

    # 4. Dibuja los botones de Sí y No.
    pygame.draw.rect(pantalla, (80, 180, 80), BOTON_CONFIRMAR_SI_RECT, border_radius=10) # Verde para Sí
    pygame.draw.rect(pantalla, (180, 80, 80), BOTON_CONFIRMAR_NO_RECT, border_radius=10) # Rojo para No

    texto_si = fuente_menu.render("Sí", True, (255, 255, 255))
    texto_no = fuente_menu.render("No", True, (255, 255, 255))

    pantalla.blit(texto_si, texto_si.get_rect(center=BOTON_CONFIRMAR_SI_RECT.center))
    pantalla.blit(texto_no, texto_no.get_rect(center=BOTON_CONFIRMAR_NO_RECT.center))

def dibujar_borde_turno(pantalla, pieza_activa):
    """
    Dibuja un borde alrededor del tablero que se ilumina con el color del jugador activo.
    """
    color_borde = COLOR_BORDE_NEUTRO

    if pieza_activa:
        # Si hay una pieza activa, usamos su color vibrante
        color_borde = COLOR_J1_VIBRANTE if pieza_activa.jugador == 1 else COLOR_J2_VIBRANTE
    
    # Dibujamos el rectángulo con el grosor definido.
    # El parámetro de grosor hace que se dibuje solo el contorno.
    pygame.draw.rect(pantalla, color_borde, BORDE_RECT, GROSOR_BORDE)