import pygame
from game import constants  # ← CAMBIO: Importar el módulo completo
from .assets import crear_superficie_pieza
from game.effects import MeleeAttackAnimation, ProjectileAnimation, MoveAnimation

def dibujar_tablero(pantalla):
    """Dibuja las casillas del tablero."""
    # Ahora usamos constants.VARIABLE para leer los valores actuales
    for fila in range(constants.FILAS):
        for col in range(constants.COLUMNAS):
            color = (230, 230, 230) if (fila + col) % 2 == 0 else (150, 150, 150)  # GRIS_CLARO y GRIS_OSCURO
            x = constants.OFFSET_X + col * constants.TAMANO_CASILLA
            y = constants.OFFSET_Y + fila * constants.TAMANO_CASILLA + constants.UI_ALTO
            pygame.draw.rect(pantalla, color, (x, y, constants.TAMANO_CASILLA, constants.TAMANO_CASILLA))

def dibujar_piezas(pantalla, tablero, pieza_activa, cache_imagenes, fuente_hp, animacion_activa=None):
    """Dibuja las piezas sobre el tablero."""
    tamano_pieza = (int(constants.TAMANO_CASILLA * 0.7), int(constants.TAMANO_CASILLA * 0.7))

    for fila in range(constants.FILAS):
        for col in range(constants.COLUMNAS):
            pieza = tablero[fila][col]
            if pieza is not None:
                if animacion_activa and isinstance(animacion_activa, (MoveAnimation, MeleeAttackAnimation)):
                    if pieza is animacion_activa.entidad:
                        continue

                if pieza is pieza_activa:
                    color = (80, 120, 255) if pieza.jugador == 1 else (255, 80, 80)  # COLOR_J1_VIBRANTE / COLOR_J2_VIBRANTE
                else:
                    color = (60, 60, 180) if pieza.jugador == 1 else (180, 60, 60)  # COLOR_J1_OPACO / COLOR_J2_OPACO

                # Obtenemos la imagen de la pieza (desde el caché o la creamos)
                imagen_pieza = crear_superficie_pieza(pieza.nombre, color, tamano_pieza, cache_imagenes)
                
                # Calcular la posición para centrar la imagen en la casilla (CON OFFSETS)
                centro_x = int(constants.OFFSET_X + col * constants.TAMANO_CASILLA + constants.TAMANO_CASILLA / 2)
                centro_y = int(constants.OFFSET_Y + fila * constants.TAMANO_CASILLA + constants.UI_ALTO + constants.TAMANO_CASILLA / 2)
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
                    color_vida = (40, 170, 90)  # COLOR_HP_ALTA
                elif porcentaje_vida > 0.3:
                    color_vida = (255, 215, 0)  # COLOR_HP_MEDIA
                else:
                    color_vida = (255, 60, 30)  # COLOR_HP_BAJA

                pygame.draw.rect(pantalla, (70, 80, 70), (pos_x_barra, pos_y_barra, ancho_barra_total, alto_barra))  # COLOR_HP_FONDO
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
        activo_surface = pygame.Surface((constants.TAMANO_CASILLA, constants.TAMANO_CASILLA), pygame.SRCALPHA)
        activo_surface.fill((240, 240, 160, 250))  # COLOR_RESALTADO_ACTIVO
        fila, col = pieza_activa.posicion
        x = constants.OFFSET_X + col * constants.TAMANO_CASILLA
        y = constants.OFFSET_Y + fila * constants.TAMANO_CASILLA + constants.UI_ALTO
        pantalla.blit(activo_surface, (x, y))
        
    mov_surface = pygame.Surface((constants.TAMANO_CASILLA, constants.TAMANO_CASILLA), pygame.SRCALPHA)
    mov_surface.fill((100, 255, 100, 100))
    for fila, col in casillas_movimiento:
        x = constants.OFFSET_X + col * constants.TAMANO_CASILLA
        y = constants.OFFSET_Y + fila * constants.TAMANO_CASILLA + constants.UI_ALTO
        pantalla.blit(mov_surface, (x, y))

    # Superficie para ataque
    atk_surface = pygame.Surface((constants.TAMANO_CASILLA, constants.TAMANO_CASILLA), pygame.SRCALPHA)
    atk_surface.fill((255, 50, 50, 120)) # Rojo semitransparente
    for fila, col in casillas_ataque:
        x = constants.OFFSET_X + col * constants.TAMANO_CASILLA
        y = constants.OFFSET_Y + fila * constants.TAMANO_CASILLA + constants.UI_ALTO
        pantalla.blit(atk_surface, (x, y))


def dibujar_ui(pantalla, fuente, pieza_activa):
    """Dibuja elementos de la interfaz, como el botón de pasar turno."""
    # Fondo del UI (CON OFFSETS)
    fondo_ui = pygame.Rect(constants.OFFSET_X, constants.OFFSET_Y, constants.ANCHO_TABLERO, constants.UI_ALTO)
    pygame.draw.rect(pantalla, (30, 30, 30), fondo_ui)

    # Actualizar las posiciones de los botones con offsets
    boton_volver = pygame.Rect(constants.OFFSET_X + 10, constants.OFFSET_Y + 10, 100, 40)
    boton_deshacer = pygame.Rect(constants.OFFSET_X + constants.ANCHO_TABLERO - 120, constants.OFFSET_Y + 10, 50, 40)
    boton_pasar = pygame.Rect(constants.OFFSET_X + constants.ANCHO_TABLERO - 60, constants.OFFSET_Y + 10, 50, 40)

    # Boton Volver
    pygame.draw.rect(pantalla, (180, 50, 50), boton_volver, border_radius=5)
    texto_volver = fuente.render("Salir", True, (255, 255, 255))
    pantalla.blit(texto_volver, texto_volver.get_rect(center=boton_volver.center))

    # Botón Deshacer
    pygame.draw.rect(pantalla, (90, 90, 90), boton_deshacer, border_radius=5)
    texto_deshacer = fuente.render("<-", True, (255, 255, 255))
    pantalla.blit(texto_deshacer, texto_deshacer.get_rect(center=boton_deshacer.center))
    
    # Botón de Pasar Turno
    pygame.draw.rect(pantalla, (90, 90, 90), boton_pasar, border_radius=5)
    texto_pasar = fuente.render(">|", True, (255, 255, 255))
    pantalla.blit(texto_pasar, texto_pasar.get_rect(center=boton_pasar.center))
    
    # Indicador de turno
    if pieza_activa:
        pos_x_texto = boton_volver.right + 20
        
        texto_turno = f"Turno de J{pieza_activa.jugador}: {pieza_activa.nombre} en [{pieza_activa.posicion[0]},{pieza_activa.posicion[1]}]"
        indicador = fuente.render(texto_turno, True, (255, 255, 255))
        pos_y_texto = constants.OFFSET_Y + constants.UI_ALTO / 2 - indicador.get_height() / 2
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
        color = (80, 120, 255) if entidad.jugador == 1 else (255, 80, 80)  # COLOR_J1_VIBRANTE / COLOR_J2_VIBRANTE
        tamano_pieza = (int(constants.TAMANO_CASILLA * 0.7), int(constants.TAMANO_CASILLA * 0.7))
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

    # Obtener panel centrado
    panel_rect = obtener_panel_confirmacion()

    # 2. Dibuja el panel semitransparente para el texto.
    pygame.draw.rect(pantalla, (40, 40, 40, 200), panel_rect)
    pygame.draw.rect(pantalla, (200, 200, 200), panel_rect, 2) # Borde

    # 3. Dibuja el texto de advertencia.
    texto1 = "Seguro que quieres volver al Menu Principal?"
    texto2 = "Se perderá el progreso del juego."
    
    superficie_texto1 = fuente_ui.render(texto1, True, (255, 255, 255))
    superficie_texto2 = fuente_ui.render(texto2, True, (255, 200, 200))
    
    pantalla.blit(superficie_texto1, superficie_texto1.get_rect(center=(panel_rect.centerx, panel_rect.centery - 30)))
    pantalla.blit(superficie_texto2, superficie_texto2.get_rect(center=(panel_rect.centerx, panel_rect.centery)))

    # 4. Dibuja los botones de Sí y No.
    boton_si_rect, boton_no_rect = obtener_botones_confirmacion()
    
    pygame.draw.rect(pantalla, (80, 180, 80), boton_si_rect, border_radius=10) # Verde para Sí
    pygame.draw.rect(pantalla, (180, 80, 80), boton_no_rect, border_radius=10) # Rojo para No

    texto_si = fuente_menu.render("Sí", True, (255, 255, 255))
    texto_no = fuente_menu.render("No", True, (255, 255, 255))

    pantalla.blit(texto_si, texto_si.get_rect(center=boton_si_rect.center))
    pantalla.blit(texto_no, texto_no.get_rect(center=boton_no_rect.center))

def dibujar_borde_turno(pantalla, pieza_activa):
    """
    Dibuja un borde alrededor del tablero que se ilumina con el color del jugador activo.
    """
    color_borde = (40, 40, 40)  # COLOR_BORDE_NEUTRO

    if pieza_activa:
        # Si hay una pieza activa, usamos su color vibrante
        color_borde = (80, 120, 255) if pieza_activa.jugador == 1 else (255, 80, 80)  # COLOR_J1_VIBRANTE / COLOR_J2_VIBRANTE
    
    # Crear el rectángulo del borde con offsets
    tablero_rect = pygame.Rect(constants.OFFSET_X, constants.OFFSET_Y + constants.UI_ALTO, constants.ANCHO_TABLERO, constants.ALTO_TABLERO)
    borde_rect = tablero_rect.inflate(constants.GROSOR_BORDE, constants.GROSOR_BORDE)
    
    # Dibujamos el rectángulo con el grosor definido.
    # El parámetro de grosor hace que se dibuje solo el contorno.
    pygame.draw.rect(pantalla, color_borde, borde_rect, constants.GROSOR_BORDE)


def obtener_boton_volver():
    """Retorna el rectángulo del botón Volver con offsets aplicados."""
    return pygame.Rect(constants.OFFSET_X + 10, constants.OFFSET_Y + 10, 100, 40)

def obtener_boton_deshacer():
    """Retorna el rectángulo del botón Deshacer con offsets aplicados."""
    return pygame.Rect(constants.OFFSET_X + constants.ANCHO_TABLERO - 120, constants.OFFSET_Y + 10, 50, 40)

def obtener_boton_pasar():
    """Retorna el rectángulo del botón Pasar con offsets aplicados."""
    return pygame.Rect(constants.OFFSET_X + constants.ANCHO_TABLERO - 60, constants.OFFSET_Y + 10, 50, 40)

def obtener_panel_confirmacion():
    """Retorna el rectángulo del panel de confirmación centrado en la pantalla real."""
    # Obtener el tamaño REAL de la pantalla actual
    pantalla = pygame.display.get_surface()
    if pantalla is None:
        # Fallback si no hay pantalla
        ancho_real = constants.ANCHO_VENTANA
        alto_real = constants.ALTO_VENTANA
    else:
        ancho_real = pantalla.get_width()
        alto_real = pantalla.get_height()
    
    panel_ancho = int(500 * constants.ESCALA_GLOBAL)
    panel_alto = int(200 * constants.ESCALA_GLOBAL)
    
    # Centrar en la pantalla REAL, no en las coordenadas del juego
    panel_x = (ancho_real - panel_ancho) // 2
    panel_y = (alto_real - panel_alto) // 2
    
    return pygame.Rect(panel_x, panel_y, panel_ancho, panel_alto)

def obtener_botones_confirmacion():
    """Retorna los rectángulos de los botones Sí y No centrados en la pantalla real."""
    panel = obtener_panel_confirmacion()
    boton_ancho = int(120 * constants.ESCALA_GLOBAL)
    boton_alto = int(50 * constants.ESCALA_GLOBAL)
    espacio_entre = int(30 * constants.ESCALA_GLOBAL)
    
    # Los botones están dentro del panel, que ya está centrado en la pantalla real
    boton_si = pygame.Rect(panel.centerx - boton_ancho - espacio_entre // 2, 
                           panel.centery + int(20 * constants.ESCALA_GLOBAL), 
                           boton_ancho, boton_alto)
    boton_no = pygame.Rect(panel.centerx + espacio_entre // 2, 
                           panel.centery + int(20 * constants.ESCALA_GLOBAL), 
                           boton_ancho, boton_alto)
    
    return boton_si, boton_no