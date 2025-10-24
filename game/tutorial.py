import pygame
import sys
import os
from .constants import *
from .piece import crear_soldado, crear_paladin, crear_mago, crear_dragon, crear_destructor
from .assets import crear_superficie_pieza
from .logic import calcular_casillas_posibles, calcular_ataques_posibles
from . import constants  # Importar módulo para acceder a escalado

# Cache global para iconos
CACHE_ICONOS = {}


def get_escala_tutorial():
    """Retorna escala correcta según modo actual."""
    return constants.ESCALA_GLOBAL if constants.MODO_FULLSCREEN else 1.0


def obtener_dimensiones_tutorial():
    """Calcula dimensiones que escalan SOLO en fullscreen."""
    escala = get_escala_tutorial()
    return {
        'casilla': int(50 * escala),
        'tamano_boton': int(150 * escala),
        'espacio_grid': int(30 * escala),
        'margen_titulo': int(60 * escala),
        'margen_inferior': int(80 * escala),
        'tablero_offset_x': int(50 * escala),
        'tablero_offset_y': int(120 * escala),
    }


def obtener_dimensiones_pantalla(pantalla):
    """Retorna dimensiones correctas según modo."""
    if constants.MODO_FULLSCREEN:
        # En fullscreen: usar tamaño real de la superficie
        return pantalla.get_width(), pantalla.get_height()
    else:
        # En modo ventana: usar constantes
        return constants.ANCHO_VENTANA, constants.ALTO_VENTANA


def cargar_icono_svg(nombre_archivo, tamano=(24, 24)):
    """Carga un icono SVG desde assets/icons/ usando pygame."""
    # Escalar tamaño del icono según modo
    escala = get_escala_tutorial()
    tamano_escalado = (
        int(tamano[0] * escala),
        int(tamano[1] * escala)
    )
    
    cache_key = (nombre_archivo, tamano_escalado)
    
    if cache_key in CACHE_ICONOS:
        return CACHE_ICONOS[cache_key]
    
    try:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        ruta = os.path.join(base_path, "assets", "icons", nombre_archivo)
        
        print(f"Intentando cargar icono: {ruta}")
        
        superficie_svg = pygame.image.load(ruta)
        superficie_escalada = pygame.transform.smoothscale(superficie_svg, tamano_escalado)
        
        CACHE_ICONOS[cache_key] = superficie_escalada
        print(f"Icono cargado: {nombre_archivo}")
        return superficie_escalada
        
    except Exception as e:
        print(f"Error al cargar icono {nombre_archivo}: {e}")
        superficie = pygame.Surface(tamano_escalado, pygame.SRCALPHA)
        superficie.fill((100, 100, 100, 200))
        CACHE_ICONOS[cache_key] = superficie
        return superficie


def mostrar_tutorial(pantalla, fuente_titulo, fuente_texto, cache_imagenes):
    """Punto de entrada del tutorial."""
    return pantalla_seleccion_piezas(pantalla, fuente_titulo, fuente_texto, cache_imagenes)


def pantalla_seleccion_piezas(pantalla, fuente_titulo, fuente_texto, cache_imagenes):
    """Pantalla con cuadrícula de botones para seleccionar qué pieza ver."""
    
    # Obtener dimensiones correctas según modo
    ancho_real, alto_real = obtener_dimensiones_pantalla(pantalla)
    
    # Obtener dimensiones escaladas
    dims = obtener_dimensiones_tutorial()
    escala = get_escala_tutorial()
    
    # Lista de piezas disponibles
    piezas_disponibles = [
        {'nombre': 'Soldado', 'creador': crear_soldado},
        {'nombre': 'Paladin', 'creador': crear_paladin},
        {'nombre': 'Mago', 'creador': crear_mago},
        {'nombre': 'Dragon', 'creador': crear_dragon},
        {'nombre': 'Destructor', 'creador': crear_destructor},
    ]
    
    # Configuración de la cuadrícula de botones
    cols_grid = 3
    total_ancho_grid = cols_grid * dims['tamano_boton'] + (cols_grid - 1) * dims['espacio_grid']
    inicio_x = (ancho_real - total_ancho_grid) / 2
    inicio_y = dims['margen_titulo'] * 2.5  # Espacio para el título
    
    # Crear botones para cada pieza
    botones_piezas = []
    for i, pieza_info in enumerate(piezas_disponibles):
        fila = i // cols_grid
        col = i % cols_grid
        x = inicio_x + col * (dims['tamano_boton'] + dims['espacio_grid'])
        y = inicio_y + fila * (dims['tamano_boton'] + dims['espacio_grid'])
        rect = pygame.Rect(x, y, dims['tamano_boton'], dims['tamano_boton'])
        botones_piezas.append({'rect': rect, 'pieza_info': pieza_info})
    
    # Botón volver (centrado en la parte inferior)
    ancho_boton_volver = int(150 * escala)
    alto_boton_volver = int(50 * escala)
    boton_volver = pygame.Rect(
        ancho_real/2 - ancho_boton_volver/2,
        alto_real - dims['margen_inferior'],
        ancho_boton_volver,
        alto_boton_volver
    )
    
    # Crear fuentes escaladas
    tamano_fuente_titulo = int(40 * escala)
    tamano_fuente_texto = int(20 * escala)
    fuente_titulo_escalada = pygame.font.SysFont("Impact", tamano_fuente_titulo)
    fuente_texto_escalada = pygame.font.SysFont("Arial", tamano_fuente_texto)
    
    reloj = pygame.time.Clock()
    
    while True:
        pantalla.fill(COLOR_FONDO)
        
        # Título (centrado en pantalla real)
        texto_titulo = fuente_titulo_escalada.render("SELECCIONA UNA UNIDAD", True, (255, 255, 255))
        rect_titulo = texto_titulo.get_rect(center=(ancho_real/2, dims['margen_titulo']))
        pantalla.blit(texto_titulo, rect_titulo)
        
        # Dibujar botones de piezas
        tamano_imagen = int(100 * escala)
        for boton in botones_piezas:
            rect = boton['rect']
            pieza_info = boton['pieza_info']
            
            # Fondo del botón
            radio = int(10 * escala)
            pygame.draw.rect(pantalla, (40, 40, 60), rect, border_radius=radio)
            pygame.draw.rect(pantalla, (100, 100, 150), rect, width=3, border_radius=radio)
            
            # Imagen de la pieza
            pieza_temp = pieza_info['creador'](jugador=1)
            imagen = crear_superficie_pieza(pieza_temp.nombre, COLOR_J1_OPACO, (tamano_imagen, tamano_imagen), cache_imagenes)
            offset_imagen = int(15 * escala)
            imagen_rect = imagen.get_rect(center=(rect.centerx, rect.centery - offset_imagen))
            pantalla.blit(imagen, imagen_rect)
            
            # Nombre de la pieza
            texto_nombre = fuente_texto_escalada.render(pieza_info['nombre'], True, (255, 255, 255))
            offset_nombre = int(20 * escala)
            nombre_rect = texto_nombre.get_rect(center=(rect.centerx, rect.bottom - offset_nombre))
            pantalla.blit(texto_nombre, nombre_rect)
        
        # Botón volver
        radio_volver = int(10 * escala)
        pygame.draw.rect(pantalla, (150, 50, 50), boton_volver, border_radius=radio_volver)
        texto_volver = fuente_texto_escalada.render("Volver", True, (255, 255, 255))
        pantalla.blit(texto_volver, texto_volver.get_rect(center=boton_volver.center))
        
        pygame.display.flip()
        
        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'saliendo'
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos
                
                for idx, boton in enumerate(botones_piezas):
                    if boton['rect'].collidepoint(pos):
                        resultado = pantalla_detalle_pieza(
                            pantalla, fuente_titulo, fuente_texto, 
                            cache_imagenes, piezas_disponibles, idx
                        )
                        if resultado == 'saliendo':
                            return 'saliendo'
                
                if boton_volver.collidepoint(pos):
                    return 'menu_principal'
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return 'menu_principal'
        
        reloj.tick(60)


def pantalla_detalle_pieza(pantalla, fuente_titulo, fuente_texto, cache_imagenes, piezas_disponibles, indice_actual):
    """Pantalla que muestra el tablero con la pieza, sus movimientos/ataques y stats."""
    
    # Obtener dimensiones correctas según modo
    ancho_real, alto_real = obtener_dimensiones_pantalla(pantalla)
    
    # Obtener dimensiones escaladas
    dims = obtener_dimensiones_tutorial()
    escala = get_escala_tutorial()
    
    # Estado inicial
    modo = 'movimiento'
    
    # Dimensiones del tablero tutorial escaladas
    TUTORIAL_FILAS = 7
    TUTORIAL_COLS = 7
    tablero_ancho = TUTORIAL_COLS * dims['casilla']
    tablero_alto = TUTORIAL_FILAS * dims['casilla']
    
    # Layout: centrar tablero en la mitad izquierda de la pantalla
    mitad_izquierda = ancho_real / 2
    tablero_x = (mitad_izquierda - tablero_ancho) / 2
    tablero_y = (alto_real - tablero_alto) / 2
    
    # Crear fuentes escaladas
    tamano_fuente_titulo = int(40 * escala)
    tamano_fuente_texto = int(20 * escala)
    fuente_titulo_escalada = pygame.font.SysFont("Impact", tamano_fuente_titulo)
    fuente_texto_escalada = pygame.font.SysFont("Arial", tamano_fuente_texto)
    
    reloj = pygame.time.Clock()
    
    while True:
        # Obtener pieza actual según índice
        pieza_info = piezas_disponibles[indice_actual]
        
        # Crear la pieza
        pieza = pieza_info['creador'](jugador=1)
        pieza.posicion = (TUTORIAL_FILAS // 2, TUTORIAL_COLS // 2)
        
        # Crear tablero pequeño
        tablero_tutorial = [[None for _ in range(TUTORIAL_COLS)] for _ in range(TUTORIAL_FILAS)]
        tablero_tutorial[pieza.posicion[0]][pieza.posicion[1]] = pieza
        
        # Botones de navegación (<<  NOMBRE  >>)
        tamano_boton_nav = int(50 * escala)
        espacio_nav = int(20 * escala)
        
        # Calcular posición del título
        texto_titulo = fuente_titulo_escalada.render(pieza_info['nombre'].upper(), True, (255, 215, 0))
        rect_titulo = texto_titulo.get_rect(center=(ancho_real/2, int(40 * escala)))
        
        # Botones de navegación a los lados del título
        boton_anterior = pygame.Rect(
            rect_titulo.left - tamano_boton_nav - espacio_nav,
            rect_titulo.centery - tamano_boton_nav/2,
            tamano_boton_nav,
            tamano_boton_nav
        )
        
        boton_siguiente = pygame.Rect(
            rect_titulo.right + espacio_nav,
            rect_titulo.centery - tamano_boton_nav/2,
            tamano_boton_nav,
            tamano_boton_nav
        )
        
        # Botones de modo (debajo del tablero)
        ancho_boton_modo = int(150 * escala)
        alto_boton_modo = int(40 * escala)
        espacio_botones = int(20 * escala)
        
        y_botones = tablero_y + tablero_alto + espacio_botones
        boton_movimiento = pygame.Rect(
            tablero_x,
            y_botones,
            ancho_boton_modo,
            alto_boton_modo
        )
        boton_ataque = pygame.Rect(
            tablero_x + ancho_boton_modo + espacio_botones,
            y_botones,
            ancho_boton_modo,
            alto_boton_modo
        )
        
        # Tabla de stats (mitad derecha de la pantalla)
        stats_x = mitad_izquierda + int(50 * escala)
        stats_y = tablero_y
        
        # Botón volver
        ancho_boton_volver = int(150 * escala)
        alto_boton_volver = int(50 * escala)
        boton_volver = pygame.Rect(
            ancho_real/2 - ancho_boton_volver/2,
            alto_real - int(80 * escala),
            ancho_boton_volver,
            alto_boton_volver
        )
        
        pantalla.fill(COLOR_FONDO)
        
        # Título con botones de navegación
        pantalla.blit(texto_titulo, rect_titulo)
        
        # Botón anterior (<<)
        radio_nav = int(8 * escala)
        color_anterior = (80, 80, 120) if indice_actual > 0 else (40, 40, 40)
        pygame.draw.rect(pantalla, color_anterior, boton_anterior, border_radius=radio_nav)
        texto_anterior = fuente_texto_escalada.render("<<", True, (255, 255, 255) if indice_actual > 0 else (100, 100, 100))
        pantalla.blit(texto_anterior, texto_anterior.get_rect(center=boton_anterior.center))
        
        # Botón siguiente (>>)
        color_siguiente = (80, 80, 120) if indice_actual < len(piezas_disponibles) - 1 else (40, 40, 40)
        pygame.draw.rect(pantalla, color_siguiente, boton_siguiente, border_radius=radio_nav)
        texto_siguiente = fuente_texto_escalada.render(">>", True, (255, 255, 255) if indice_actual < len(piezas_disponibles) - 1 else (100, 100, 100))
        pantalla.blit(texto_siguiente, texto_siguiente.get_rect(center=boton_siguiente.center))
        
        # Dibujar tablero con resaltados
        dibujar_tablero_con_resaltados_tutorial(
            pantalla, tablero_x, tablero_y, pieza, 
            tablero_tutorial, modo, dims['casilla'], TUTORIAL_FILAS, TUTORIAL_COLS
        )
        
        # Dibujar pieza
        dibujar_pieza_tutorial(pantalla, pieza, tablero_x, tablero_y, cache_imagenes, dims['casilla'])
        
        # Botones de modo
        radio = int(8 * escala)
        color_mov = (0, 150, 0) if modo == 'movimiento' else (50, 50, 50)
        pygame.draw.rect(pantalla, color_mov, boton_movimiento, border_radius=radio)
        pygame.draw.rect(pantalla, (200, 200, 200), boton_movimiento, width=2, border_radius=radio)
        texto_mov = fuente_texto_escalada.render("Movimiento", True, (255, 255, 255))
        pantalla.blit(texto_mov, texto_mov.get_rect(center=boton_movimiento.center))
        
        color_atk = (150, 0, 0) if modo == 'ataque' else (50, 50, 50)
        pygame.draw.rect(pantalla, color_atk, boton_ataque, border_radius=radio)
        pygame.draw.rect(pantalla, (200, 200, 200), boton_ataque, width=2, border_radius=radio)
        texto_atk = fuente_texto_escalada.render("Ataque", True, (255, 255, 255))
        pantalla.blit(texto_atk, texto_atk.get_rect(center=boton_ataque.center))
        
        # Tabla de stats (SIN el nombre de la pieza)
        dibujar_tabla_stats(pantalla, pieza, stats_x, stats_y, fuente_titulo_escalada, fuente_texto_escalada)
        
        # Descripción
        desc_y = stats_y + int(150 * escala)  # Ajustado para compensar la eliminación del nombre
        dibujar_descripcion(pantalla, pieza, stats_x, desc_y, fuente_texto_escalada, ancho_real)
        
        # Botón volver
        radio_volver = int(10 * escala)
        pygame.draw.rect(pantalla, (150, 50, 50), boton_volver, border_radius=radio_volver)
        texto_volver = fuente_texto_escalada.render("Volver", True, (255, 255, 255))
        pantalla.blit(texto_volver, texto_volver.get_rect(center=boton_volver.center))
        
        pygame.display.flip()
        
        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'saliendo'
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos
                
                if boton_movimiento.collidepoint(pos):
                    modo = 'movimiento'
                elif boton_ataque.collidepoint(pos):
                    modo = 'ataque'
                elif boton_volver.collidepoint(pos):
                    return 'seleccion'
                
                # Navegación entre piezas
                elif boton_anterior.collidepoint(pos) and indice_actual > 0:
                    indice_actual -= 1
                    modo = 'movimiento'  # Resetear modo al cambiar de pieza
                elif boton_siguiente.collidepoint(pos) and indice_actual < len(piezas_disponibles) - 1:
                    indice_actual += 1
                    modo = 'movimiento'  # Resetear modo al cambiar de pieza
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return 'seleccion'
                # Navegación con flechas
                elif evento.key == pygame.K_LEFT and indice_actual > 0:
                    indice_actual -= 1
                    modo = 'movimiento'
                elif evento.key == pygame.K_RIGHT and indice_actual < len(piezas_disponibles) - 1:
                    indice_actual += 1
                    modo = 'movimiento'
        
        reloj.tick(60)


def dibujar_tablero_con_resaltados_tutorial(pantalla, x_offset, y_offset, pieza, tablero, modo, tamano_casilla, filas, cols):
    """Dibuja el tablero y resalta casillas según el modo."""
    for fila in range(filas):
        for col in range(cols):
            x = x_offset + col * tamano_casilla
            y = y_offset + fila * tamano_casilla
            
            # Color base
            if (fila + col) % 2 == 0:
                color = COLOR_CASILLA_CLARA
            else:
                color = COLOR_CASILLA_OSCURA
            
            pygame.draw.rect(pantalla, color, (x, y, tamano_casilla, tamano_casilla))
            
            # Resaltar si corresponde
            if modo == 'movimiento':
                if casilla_en_rango_movimiento(pieza, (fila, col), tablero, filas, cols):
                    superficie_resaltado = pygame.Surface((tamano_casilla, tamano_casilla), pygame.SRCALPHA)
                    superficie_resaltado.fill((100, 255, 100, 120))
                    pantalla.blit(superficie_resaltado, (x, y))
            else:
                if casilla_en_rango_ataque(pieza, (fila, col), tablero, filas, cols):
                    superficie_resaltado = pygame.Surface((tamano_casilla, tamano_casilla), pygame.SRCALPHA)
                    superficie_resaltado.fill((255, 50, 50, 180))
                    pantalla.blit(superficie_resaltado, (x, y))
    
    # Borde
    pygame.draw.rect(pantalla, (100, 100, 100), 
                     (x_offset, y_offset, cols * tamano_casilla, filas * tamano_casilla), 
                     width=3)


def dibujar_pieza_tutorial(pantalla, pieza, x_offset, y_offset, cache_imagenes, tamano_casilla):
    """Dibuja la pieza en el tablero tutorial."""
    fila, col = pieza.posicion
    centro_x = x_offset + col * tamano_casilla + tamano_casilla // 2
    centro_y = y_offset + fila * tamano_casilla + tamano_casilla // 2
    
    color_pieza = COLOR_J1_OPACO
    tamano_imagen = int(tamano_casilla * 0.7)
    imagen = crear_superficie_pieza(pieza.nombre, color_pieza, (tamano_imagen, tamano_imagen), cache_imagenes)
    
    rect_imagen = imagen.get_rect(center=(centro_x, centro_y))
    pantalla.blit(imagen, rect_imagen)


def dibujar_tabla_stats(pantalla, pieza, x, y, fuente_titulo, fuente_texto):
    """Dibuja la tabla de estadísticas SIN el nombre de la pieza."""
    
    escala = get_escala_tutorial()
    
    # Cargar iconos escalados
    icono_hp = cargar_icono_svg("HP.svg", (24, 24))
    icono_atk = cargar_icono_svg("damage.svg", (24, 24))
    icono_agi = cargar_icono_svg("turn-over.svg", (24, 24))
    
    # Stats directamente (sin título ni línea)
    stats = [
        (icono_hp, str(pieza.hp_max)),
        (icono_atk, str(pieza.atk)),
        (icono_agi, str(pieza.agi)),
    ]
    
    y_actual = y
    espacio_stat = int(35 * escala)
    offset_texto = int(35 * escala)
    
    for icono, valor_stat in stats:
        pantalla.blit(icono, (x, y_actual - 2))
        texto_valor = fuente_texto.render(valor_stat, True, (255, 255, 100))
        pantalla.blit(texto_valor, (x + offset_texto, y_actual))
        y_actual += espacio_stat


def dibujar_descripcion(pantalla, pieza, x, y, fuente_texto, ancho_pantalla):
    """Dibuja descripción de la pieza."""
    
    escala = get_escala_tutorial()
    
    # Título
    texto_titulo = fuente_texto.render("DESCRIPCIÓN:", True, (255, 255, 255))
    pantalla.blit(texto_titulo, (x, y))
    
    y_actual = y + int(30 * escala)
    
    descripciones = {
        "Soldado": "Unidad básica de infantería. Puede moverse y luego atacar en el mismo turno, ideal para avanzar y presionar.",
        "Paladin": "Un Guerrero con alta movilidad. Muy versátil para penetrar en el terreno enemigo, sin embargo su rango de ataque es reducido",
        "Mago": "Pieza con un gran rango de ataque y gran daño, sin embargo no puede moverse y atacar en el mismo turno.",
        "Dragon": "Bestia voladora que puede saltar sobre otras piezas. Su ataque a distancia y movilidad lo hacen mortalmente peligroso.",
        "Destructor": "La unidad más poderosa del juego. Alta vida y daño devastador, pero su movimiento lento lo hace vulnerable a ataques coordinados."
    }
    
    descripcion = descripciones.get(pieza.nombre, "Sin descripción disponible.")
    
    # Dividir en líneas con margen derecho
    palabras = descripcion.split()
    lineas = []
    linea_actual = ""
    max_ancho = ancho_pantalla - x - int(15 * escala)
    
    for palabra in palabras:
        test_linea = linea_actual + palabra + " "
        if fuente_texto.size(test_linea)[0] < max_ancho:
            linea_actual = test_linea
        else:
            if linea_actual:
                lineas.append(linea_actual.strip())
            linea_actual = palabra + " "
    
    if linea_actual:
        lineas.append(linea_actual.strip())
    
    # Dibujar líneas
    espacio_linea = int(25 * escala)
    for linea in lineas:
        texto_linea = fuente_texto.render(linea, True, (200, 200, 200))
        pantalla.blit(texto_linea, (x, y_actual))
        y_actual += espacio_linea


# ============================================================================
# FUNCIONES DE LÓGICA (detección de alcance)
# ============================================================================

def casilla_en_rango_movimiento(pieza, casilla_objetivo, tablero, filas, cols):
    """Verifica si una casilla está en rango de movimiento."""
    fila_obj, col_obj = casilla_objetivo
    fila_pieza, col_pieza = pieza.posicion
    
    if fila_obj == fila_pieza and col_obj == col_pieza:
        return False
    
    if tablero[fila_obj][col_obj] is not None:
        return False
    
    for tipo_mov, valor_mov in pieza.movimientos:
        if tipo_mov == 'steps':
            if casilla_alcanzable_por_pasos(pieza, casilla_objetivo, valor_mov, tablero, filas, cols):
                return True
        elif tipo_mov == 'rect':
            if casilla_alcanzable_recto(pieza, casilla_objetivo, valor_mov, tablero, filas, cols):
                return True
        elif tipo_mov == 'diag':
            if casilla_alcanzable_diagonal(pieza, casilla_objetivo, valor_mov, tablero, filas, cols):
                return True
        elif tipo_mov == 'allsides':
            if casilla_alcanzable_recto(pieza, casilla_objetivo, valor_mov, tablero, filas, cols):
                return True
            if casilla_alcanzable_diagonal(pieza, casilla_objetivo, valor_mov, tablero, filas, cols):
                return True
    
    return False


def casilla_en_rango_ataque(pieza, casilla_objetivo, tablero, filas, cols):
    """Verifica si una casilla está en rango de ataque."""
    fila_obj, col_obj = casilla_objetivo
    fila_pieza, col_pieza = pieza.posicion
    
    if fila_obj == fila_pieza and col_obj == col_pieza:
        return False
    
    for tipo_ran, valor_ran in pieza.rango_ataque:
        if tipo_ran == 'steps':
            if isinstance(valor_ran, tuple):
                min_ran, max_ran = valor_ran
            else:
                min_ran, max_ran = 0, valor_ran
            
            if casilla_en_rango_pasos(pieza, casilla_objetivo, min_ran, max_ran, tablero, filas, cols):
                return True
        elif tipo_ran == 'rect':
            if casilla_alcanzable_recto(pieza, casilla_objetivo, valor_ran, tablero, filas, cols, is_attack=True):
                return True
        elif tipo_ran == 'diag':
            if casilla_alcanzable_diagonal(pieza, casilla_objetivo, valor_ran, tablero, filas, cols, is_attack=True):
                return True
        elif tipo_ran == 'allsides':
            if casilla_alcanzable_recto(pieza, casilla_objetivo, valor_ran, tablero, filas, cols, is_attack=True):
                return True
            if casilla_alcanzable_diagonal(pieza, casilla_objetivo, valor_ran, tablero, filas, cols, is_attack=True):
                return True
    
    return False


def casilla_alcanzable_por_pasos(pieza, casilla_objetivo, max_pasos, tablero, filas, cols):
    """BFS para movimiento tipo steps."""
    if max_pasos == 0:
        return False
    
    fila_origen, col_origen = pieza.posicion
    fila_obj, col_obj = casilla_objetivo
    
    visitados = {(fila_origen, col_origen)}
    cola = [((fila_origen, col_origen), 0)]
    
    while cola:
        (f, c), pasos = cola.pop(0)
        
        if pasos >= max_pasos:
            continue
        
        for df, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nf, nc = f + df, c + dc
            
            if not (0 <= nf < filas and 0 <= nc < cols):
                continue
            
            if (nf, nc) in visitados:
                continue
            
            visitados.add((nf, nc))
            
            if nf == fila_obj and nc == col_obj:
                return True
            
            if tablero[nf][nc] is None:
                cola.append(((nf, nc), pasos + 1))
    
    return False


def casilla_alcanzable_recto(pieza, casilla_objetivo, distancia, tablero, filas, cols, is_attack=False):
    """Verifica alcance en línea recta."""
    fila_pieza, col_pieza = pieza.posicion
    fila_obj, col_obj = casilla_objetivo
    
    if fila_pieza != fila_obj and col_pieza != col_obj:
        return False
    
    if fila_pieza == fila_obj:
        df, dc = 0, 1 if col_obj > col_pieza else -1
    else:
        df, dc = 1 if fila_obj > fila_pieza else -1, 0
    
    dist = abs(fila_obj - fila_pieza) + abs(col_obj - col_pieza)
    if dist > distancia:
        return False
    
    if pieza.puede_saltar:
        return True
    
    f, c = fila_pieza + df, col_pieza + dc
    while (f, c) != (fila_obj, col_obj):
        if tablero[f][c] is not None:
            return False
        f += df
        c += dc
    
    return True


def casilla_alcanzable_diagonal(pieza, casilla_objetivo, distancia, tablero, filas, cols, is_attack=False):
    """Verifica alcance diagonal."""
    fila_pieza, col_pieza = pieza.posicion
    fila_obj, col_obj = casilla_objetivo
    
    dist_fila = abs(fila_obj - fila_pieza)
    dist_col = abs(col_obj - col_pieza)
    
    if dist_fila != dist_col:
        return False
    
    if dist_fila > distancia:
        return False
    
    if pieza.puede_saltar:
        return True
    
    df = 1 if fila_obj > fila_pieza else -1
    dc = 1 if col_obj > col_pieza else -1
    
    f, c = fila_pieza + df, col_pieza + dc
    while (f, c) != (fila_obj, col_obj):
        if tablero[f][c] is not None:
            return False
        f += df
        c += dc
    
    return True


def casilla_en_rango_pasos(pieza, casilla_objetivo, min_pasos, max_pasos, tablero, filas, cols):
    """Verifica rango por pasos (para ataques)."""
    if max_pasos == 0:
        return False
    
    fila_origen, col_origen = pieza.posicion
    fila_obj, col_obj = casilla_objetivo
    
    visitados = {(fila_origen, col_origen): 0}
    cola = [((fila_origen, col_origen), 0)]
    
    while cola:
        (f, c), pasos = cola.pop(0)
        
        if pasos >= max_pasos:
            continue
        
        for df, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nf, nc = f + df, c + dc
            
            if not (0 <= nf < filas and 0 <= nc < cols):
                continue
            
            if (nf, nc) in visitados:
                continue
            
            nueva_dist = pasos + 1
            visitados[(nf, nc)] = nueva_dist
            
            if nf == fila_obj and nc == col_obj:
                if min_pasos <= nueva_dist <= max_pasos:
                    return True
            
            cola.append(((nf, nc), nueva_dist))
    
    return False