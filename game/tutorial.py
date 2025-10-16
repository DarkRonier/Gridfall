import pygame
from .constants import *
from .piece import crear_soldado, crear_paladin, crear_mago, crear_dragon, crear_destructor
from .assets import crear_superficie_pieza
from .logic import calcular_casillas_posibles, calcular_ataques_posibles

import os

# Cache global para iconos
CACHE_ICONOS = {}

# Tamaño del tablero de tutorial (más pequeño)
TUTORIAL_CASILLA = 50
TUTORIAL_FILAS = 7
TUTORIAL_COLS = 7
TUTORIAL_TABLERO_ANCHO = TUTORIAL_COLS * TUTORIAL_CASILLA
TUTORIAL_TABLERO_ALTO = TUTORIAL_FILAS * TUTORIAL_CASILLA


def cargar_icono_svg(nombre_archivo, tamano=(24, 24)):
    """Carga un icono SVG desde assets/icons/ usando pygame."""
    cache_key = (nombre_archivo, tamano)
    
    if cache_key in CACHE_ICONOS:
        return CACHE_ICONOS[cache_key]
    
    try:
        ruta = os.path.join("assets", "icons", nombre_archivo)
        
        # Cargar SVG
        superficie_svg = pygame.image.load(ruta)
        
        # Escalar al tamaño deseado
        superficie_escalada = pygame.transform.smoothscale(superficie_svg, tamano)
        
        CACHE_ICONOS[cache_key] = superficie_escalada
        return superficie_escalada
        
    except Exception as e:
        print(f"Error al cargar icono {nombre_archivo}: {e}")
        # Crear un cuadrado de color como fallback
        superficie = pygame.Surface(tamano, pygame.SRCALPHA)
        superficie.fill((100, 100, 100, 200))
        CACHE_ICONOS[cache_key] = superficie
        return superficie


def mostrar_tutorial(pantalla, fuente_titulo, fuente_texto, cache_imagenes):
    """
    Punto de entrada del tutorial. Muestra la pantalla de selección de piezas.
    """
    return pantalla_seleccion_piezas(pantalla, fuente_titulo, fuente_texto, cache_imagenes)


def pantalla_seleccion_piezas(pantalla, fuente_titulo, fuente_texto, cache_imagenes):
    """
    Pantalla con cuadrícula de botones para seleccionar qué pieza ver.
    """
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
    tamano_boton = 150
    espacio = 30
    inicio_x = (ANCHO_VENTANA - (cols_grid * tamano_boton + (cols_grid-1) * espacio)) / 2
    inicio_y = 150
    
    # Crear botones para cada pieza
    botones_piezas = []
    for i, pieza_info in enumerate(piezas_disponibles):
        fila = i // cols_grid
        col = i % cols_grid
        x = inicio_x + col * (tamano_boton + espacio)
        y = inicio_y + fila * (tamano_boton + espacio)
        rect = pygame.Rect(x, y, tamano_boton, tamano_boton)
        botones_piezas.append({'rect': rect, 'pieza_info': pieza_info})
    
    # Botón volver
    boton_volver = pygame.Rect(ANCHO_VENTANA/2 - 75, ALTO_VENTANA - 80, 150, 50)
    
    reloj = pygame.time.Clock()
    
    while True:
        pantalla.fill(COLOR_FONDO)
        
        # Título
        texto_titulo = fuente_titulo.render("CÓMO JUGAR - SELECCIONA UNA UNIDAD", True, (255, 255, 255))
        rect_titulo = texto_titulo.get_rect(center=(ANCHO_VENTANA/2, 60))
        pantalla.blit(texto_titulo, rect_titulo)
        
        # Dibujar botones de piezas
        for boton in botones_piezas:
            rect = boton['rect']
            pieza_info = boton['pieza_info']
            
            # Fondo del botón
            pygame.draw.rect(pantalla, (40, 40, 60), rect, border_radius=10)
            pygame.draw.rect(pantalla, (100, 100, 150), rect, width=3, border_radius=10)
            
            # Imagen de la pieza
            pieza_temp = pieza_info['creador'](jugador=1)
            imagen = crear_superficie_pieza(pieza_temp.nombre, COLOR_J1_OPACO, (100, 100), cache_imagenes)
            imagen_rect = imagen.get_rect(center=(rect.centerx, rect.centery - 15))
            pantalla.blit(imagen, imagen_rect)
            
            # Nombre de la pieza
            texto_nombre = fuente_texto.render(pieza_info['nombre'], True, (255, 255, 255))
            nombre_rect = texto_nombre.get_rect(center=(rect.centerx, rect.bottom - 20))
            pantalla.blit(texto_nombre, nombre_rect)
        
        # Botón volver
        pygame.draw.rect(pantalla, (150, 50, 50), boton_volver, border_radius=10)
        texto_volver = fuente_texto.render("Volver", True, (255, 255, 255))
        pantalla.blit(texto_volver, texto_volver.get_rect(center=boton_volver.center))
        
        pygame.display.flip()
        
        # Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'saliendo'
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos
                
                # Verificar clic en botones de piezas
                for boton in botones_piezas:
                    if boton['rect'].collidepoint(pos):
                        # Ir a la pantalla de detalle de esta pieza
                        resultado = pantalla_detalle_pieza(
                            pantalla, fuente_titulo, fuente_texto, 
                            cache_imagenes, boton['pieza_info']
                        )
                        if resultado == 'saliendo':
                            return 'saliendo'
                        # Si volvió de la pantalla de detalle, continuar en selección
                
                # Botón volver
                if boton_volver.collidepoint(pos):
                    return 'menu_principal'
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return 'menu_principal'
        
        reloj.tick(60)


def pantalla_detalle_pieza(pantalla, fuente_titulo, fuente_texto, cache_imagenes, pieza_info):
    """
    Pantalla que muestra el tablero con la pieza, sus movimientos/ataques y stats.
    """
    # Crear la pieza
    pieza = pieza_info['creador'](jugador=1)
    
    # Posición de la pieza en el centro del tablero tutorial
    pieza.posicion = (TUTORIAL_FILAS // 2, TUTORIAL_COLS // 2)
    
    # Crear tablero pequeño para el tutorial
    tablero_tutorial = [[None for _ in range(TUTORIAL_COLS)] for _ in range(TUTORIAL_FILAS)]
    tablero_tutorial[pieza.posicion[0]][pieza.posicion[1]] = pieza
    
    # Estado inicial: mostrar movimientos
    modo = 'movimiento'  # 'movimiento' o 'ataque'
    
    # Posiciones de elementos en pantalla
    tablero_x = 50
    tablero_y = 120
    
    # Botones de modo
    boton_movimiento = pygame.Rect(tablero_x, tablero_y + TUTORIAL_TABLERO_ALTO + 20, 150, 40)
    boton_ataque = pygame.Rect(tablero_x + 170, tablero_y + TUTORIAL_TABLERO_ALTO + 20, 150, 40)
    
    # Tabla de stats (a la derecha del tablero)
    stats_x = tablero_x + TUTORIAL_TABLERO_ANCHO + 50
    stats_y = tablero_y
    
    # Botón volver
    boton_volver = pygame.Rect(ANCHO_VENTANA/2 - 75, ALTO_VENTANA - 80, 150, 50)
    
    reloj = pygame.time.Clock()
    
    while True:
        pantalla.fill(COLOR_FONDO)
        
        # --- TÍTULO ---
        texto_titulo = fuente_titulo.render(f"UNIDAD: {pieza_info['nombre'].upper()}", True, (255, 215, 0))
        rect_titulo = texto_titulo.get_rect(center=(ANCHO_VENTANA/2, 40))
        pantalla.blit(texto_titulo, rect_titulo)
        
        # --- DIBUJAR TABLERO CON RESALTADOS INTEGRADOS ---
        dibujar_tablero_con_resaltados_tutorial(pantalla, tablero_x, tablero_y, pieza, tablero_tutorial, modo)
        
        # --- DIBUJAR PIEZA ---
        dibujar_pieza_tutorial(pantalla, pieza, tablero_x, tablero_y, cache_imagenes)
        
        # --- BOTONES DE MODO ---
        # Botón Movimiento
        color_mov = (0, 150, 0) if modo == 'movimiento' else (50, 50, 50)
        pygame.draw.rect(pantalla, color_mov, boton_movimiento, border_radius=8)
        pygame.draw.rect(pantalla, (200, 200, 200), boton_movimiento, width=2, border_radius=8)
        texto_mov = fuente_texto.render("Movimiento", True, (255, 255, 255))
        pantalla.blit(texto_mov, texto_mov.get_rect(center=boton_movimiento.center))
        
        # Botón Ataque
        color_atk = (150, 0, 0) if modo == 'ataque' else (50, 50, 50)
        pygame.draw.rect(pantalla, color_atk, boton_ataque, border_radius=8)
        pygame.draw.rect(pantalla, (200, 200, 200), boton_ataque, width=2, border_radius=8)
        texto_atk = fuente_texto.render("Ataque", True, (255, 255, 255))
        pantalla.blit(texto_atk, texto_atk.get_rect(center=boton_ataque.center))
        
        # --- TABLA DE STATS ---
        dibujar_tabla_stats(pantalla, pieza, stats_x, stats_y, fuente_titulo, fuente_texto)
        
        # --- DESCRIPCIÓN ADICIONAL ---
        desc_y = stats_y + 200
        dibujar_descripcion(pantalla, pieza, stats_x, desc_y, fuente_texto)
        
        # --- BOTÓN VOLVER ---
        pygame.draw.rect(pantalla, (150, 50, 50), boton_volver, border_radius=10)
        texto_volver = fuente_texto.render("Volver", True, (255, 255, 255))
        pantalla.blit(texto_volver, texto_volver.get_rect(center=boton_volver.center))
        
        pygame.display.flip()
        
        # --- EVENTOS ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return 'saliendo'
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                pos = evento.pos
                
                # Cambiar modo
                if boton_movimiento.collidepoint(pos):
                    modo = 'movimiento'
                elif boton_ataque.collidepoint(pos):
                    modo = 'ataque'
                elif boton_volver.collidepoint(pos):
                    return 'seleccion'  # Volver a la pantalla de selección
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    return 'seleccion'
        
        reloj.tick(60)


def dibujar_tablero_con_resaltados_tutorial(pantalla, x_offset, y_offset, pieza, tablero, modo):
    """
    Dibuja el tablero y cada casilla pregunta a la pieza si debe resaltarse.
    Lógica invertida: evita crasheos por casillas fuera de rango.
    """
    for fila in range(TUTORIAL_FILAS):
        for col in range(TUTORIAL_COLS):
            x = x_offset + col * TUTORIAL_CASILLA
            y = y_offset + fila * TUTORIAL_CASILLA
            
            # Color base de la casilla (patrón de ajedrez)
            if (fila + col) % 2 == 0:
                color = COLOR_CASILLA_CLARA
            else:
                color = COLOR_CASILLA_OSCURA
            
            pygame.draw.rect(pantalla, color, (x, y, TUTORIAL_CASILLA, TUTORIAL_CASILLA))
            
            # Verificar si esta casilla debe resaltarse
            if modo == 'movimiento':
                if casilla_en_rango_movimiento(pieza, (fila, col), tablero):
                    superficie_resaltado = pygame.Surface((TUTORIAL_CASILLA, TUTORIAL_CASILLA), pygame.SRCALPHA)
                    superficie_resaltado.fill((100, 255, 100, 120))  # Verde
                    pantalla.blit(superficie_resaltado, (x, y))
            else:  # modo ataque
                if casilla_en_rango_ataque(pieza, (fila, col), tablero):
                    superficie_resaltado = pygame.Surface((TUTORIAL_CASILLA, TUTORIAL_CASILLA), pygame.SRCALPHA)
                    superficie_resaltado.fill((255, 50, 50, 180))  # Rojo más fuerte y opaco
                    pantalla.blit(superficie_resaltado, (x, y))
    
    # Borde del tablero
    pygame.draw.rect(pantalla, (100, 100, 100), 
                     (x_offset, y_offset, TUTORIAL_TABLERO_ANCHO, TUTORIAL_TABLERO_ALTO), 
                     width=3)


def casilla_en_rango_movimiento(pieza, casilla_objetivo, tablero):
    """
    Verifica si una casilla específica está en el rango de movimiento de la pieza.
    Safe: no crashea si la casilla está fuera de rango.
    """
    fila_obj, col_obj = casilla_objetivo
    fila_pieza, col_pieza = pieza.posicion
    
    # No puede moverse a su propia casilla
    if fila_obj == fila_pieza and col_obj == col_pieza:
        return False
    
    # La casilla debe estar vacía
    if tablero[fila_obj][col_obj] is not None:
        return False
    
    # Verificar cada regla de movimiento
    for tipo_mov, valor_mov in pieza.movimientos:
        if tipo_mov == 'steps':
            # Movimiento tipo ajedrez (pasos)
            if casilla_alcanzable_por_pasos(pieza, casilla_objetivo, valor_mov, tablero):
                return True
        
        elif tipo_mov == 'rect':
            # Movimiento recto
            if casilla_alcanzable_recto(pieza, casilla_objetivo, valor_mov, tablero):
                return True
        
        elif tipo_mov == 'diag':
            # Movimiento diagonal
            if casilla_alcanzable_diagonal(pieza, casilla_objetivo, valor_mov, tablero):
                return True
        
        elif tipo_mov == 'allsides':
            # Movimiento en todas direcciones
            if casilla_alcanzable_recto(pieza, casilla_objetivo, valor_mov, tablero):
                return True
            if casilla_alcanzable_diagonal(pieza, casilla_objetivo, valor_mov, tablero):
                return True
    
    return False


def casilla_en_rango_ataque(pieza, casilla_objetivo, tablero):
    """
    Verifica si una casilla específica está en el rango de ataque de la pieza.
    Safe: no crashea si la casilla está fuera de rango.
    """
    fila_obj, col_obj = casilla_objetivo
    fila_pieza, col_pieza = pieza.posicion
    
    # No puede atacar su propia casilla
    if fila_obj == fila_pieza and col_obj == col_pieza:
        return False
    
    # Verificar cada regla de ataque
    for tipo_ran, valor_ran in pieza.rango_ataque:
        if tipo_ran == 'steps':
            # Rango por pasos
            if isinstance(valor_ran, tuple):
                min_ran, max_ran = valor_ran
            else:
                min_ran, max_ran = 0, valor_ran
            
            if casilla_en_rango_pasos(pieza, casilla_objetivo, min_ran, max_ran, tablero):
                return True
        
        elif tipo_ran == 'rect':
            # Rango recto
            if casilla_alcanzable_recto(pieza, casilla_objetivo, valor_ran, tablero, is_attack=True):
                return True
        
        elif tipo_ran == 'diag':
            # Rango diagonal
            if casilla_alcanzable_diagonal(pieza, casilla_objetivo, valor_ran, tablero, is_attack=True):
                return True
        
        elif tipo_ran == 'allsides':
            # Rango en todas direcciones
            if casilla_alcanzable_recto(pieza, casilla_objetivo, valor_ran, tablero, is_attack=True):
                return True
            if casilla_alcanzable_diagonal(pieza, casilla_objetivo, valor_ran, tablero, is_attack=True):
                return True
    
    return False


def casilla_alcanzable_por_pasos(pieza, casilla_objetivo, max_pasos, tablero):
    """Verifica si una casilla es alcanzable con movimiento tipo 'steps' (BFS)."""
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
            
            # Verificar límites del tablero tutorial
            if not (0 <= nf < TUTORIAL_FILAS and 0 <= nc < TUTORIAL_COLS):
                continue
            
            if (nf, nc) in visitados:
                continue
            
            visitados.add((nf, nc))
            
            # Si llegamos al objetivo
            if nf == fila_obj and nc == col_obj:
                return True
            
            # Si la casilla está vacía, seguimos explorando
            if tablero[nf][nc] is None:
                cola.append(((nf, nc), pasos + 1))
    
    return False


def casilla_alcanzable_recto(pieza, casilla_objetivo, distancia, tablero, is_attack=False):
    """Verifica si una casilla es alcanzable en línea recta."""
    fila_pieza, col_pieza = pieza.posicion
    fila_obj, col_obj = casilla_objetivo
    
    # Verificar si está en la misma fila o columna
    if fila_pieza != fila_obj and col_pieza != col_obj:
        return False
    
    # Calcular dirección
    if fila_pieza == fila_obj:
        df, dc = 0, 1 if col_obj > col_pieza else -1
    else:
        df, dc = 1 if fila_obj > fila_pieza else -1, 0
    
    # Verificar distancia
    dist = abs(fila_obj - fila_pieza) + abs(col_obj - col_pieza)
    if dist > distancia:
        return False
    
    # Si puede saltar, no verificar obstáculos
    if pieza.puede_saltar:
        return True
    
    # Verificar camino sin obstáculos
    f, c = fila_pieza + df, col_pieza + dc
    while (f, c) != (fila_obj, col_obj):
        if tablero[f][c] is not None:
            return False
        f += df
        c += dc
    
    return True


def casilla_alcanzable_diagonal(pieza, casilla_objetivo, distancia, tablero, is_attack=False):
    """Verifica si una casilla es alcanzable en diagonal."""
    fila_pieza, col_pieza = pieza.posicion
    fila_obj, col_obj = casilla_objetivo
    
    # Verificar si está en diagonal (misma distancia en filas y columnas)
    dist_fila = abs(fila_obj - fila_pieza)
    dist_col = abs(col_obj - col_pieza)
    
    if dist_fila != dist_col:
        return False
    
    # Verificar distancia
    if dist_fila > distancia:
        return False
    
    # Si puede saltar, no verificar obstáculos
    if pieza.puede_saltar:
        return True
    
    # Calcular dirección
    df = 1 if fila_obj > fila_pieza else -1
    dc = 1 if col_obj > col_pieza else -1
    
    # Verificar camino sin obstáculos
    f, c = fila_pieza + df, col_pieza + dc
    while (f, c) != (fila_obj, col_obj):
        if tablero[f][c] is not None:
            return False
        f += df
        c += dc
    
    return True


def casilla_en_rango_pasos(pieza, casilla_objetivo, min_pasos, max_pasos, tablero):
    """Verifica si una casilla está dentro del rango de pasos (para ataques)."""
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
            
            # Verificar límites del tablero tutorial
            if not (0 <= nf < TUTORIAL_FILAS and 0 <= nc < TUTORIAL_COLS):
                continue
            
            if (nf, nc) in visitados:
                continue
            
            nueva_dist = pasos + 1
            visitados[(nf, nc)] = nueva_dist
            
            # Si llegamos al objetivo y está en el rango correcto
            if nf == fila_obj and nc == col_obj:
                if min_pasos <= nueva_dist <= max_pasos:
                    return True
            
            # Seguir explorando (para ataques pasamos por aliados)
            cola.append(((nf, nc), nueva_dist))
    
    return False


def dibujar_pieza_tutorial(pantalla, pieza, x_offset, y_offset, cache_imagenes):
    """Dibuja la pieza en el tablero tutorial."""
    fila, col = pieza.posicion
    centro_x = x_offset + col * TUTORIAL_CASILLA + TUTORIAL_CASILLA // 2
    centro_y = y_offset + fila * TUTORIAL_CASILLA + TUTORIAL_CASILLA // 2
    
    color_pieza = COLOR_J1_OPACO
    tamano_imagen = int(TUTORIAL_CASILLA * 0.7)
    imagen = crear_superficie_pieza(pieza.nombre, color_pieza, (tamano_imagen, tamano_imagen), cache_imagenes)
    
    rect_imagen = imagen.get_rect(center=(centro_x, centro_y))
    pantalla.blit(imagen, rect_imagen)


def dibujar_tabla_stats(pantalla, pieza, x, y, fuente_titulo, fuente_texto):
    """Dibuja la tabla de estadísticas de la pieza con iconos."""
    
    # Cargar iconos (sin modificar colores, ya están editados en los SVG)
    icono_hp = cargar_icono_svg("HP.svg", (24, 24))
    icono_atk = cargar_icono_svg("damage.svg", (24, 24))
    icono_agi = cargar_icono_svg("turn-over.svg", (24, 24))
    
    # Título: NOMBRE DE LA PIEZA
    texto_titulo = fuente_titulo.render(pieza.nombre.upper(), True, (255, 215, 0))
    pantalla.blit(texto_titulo, (x, y))
    
    # Línea divisoria
    pygame.draw.line(pantalla, (150, 150, 150), (x, y + 35), (x + 200, y + 35), 2)
    
    # Stats con iconos
    stats = [
        (icono_hp, str(pieza.hp_max)),
        (icono_atk, str(pieza.atk)),
        (icono_agi, str(pieza.agi)),
    ]
    
    y_actual = y + 50
    for icono, valor_stat in stats:
        # Dibujar icono a la izquierda
        pantalla.blit(icono, (x, y_actual - 2))
        
        # Valor del stat (a la derecha del icono)
        texto_valor = fuente_texto.render(valor_stat, True, (255, 255, 100))
        pantalla.blit(texto_valor, (x + 35, y_actual))
        
        y_actual += 35


def dibujar_descripcion(pantalla, pieza, x, y, fuente_texto):
    """Dibuja una nota descriptiva personalizada para cada pieza."""
    # Título
    texto_titulo = fuente_texto.render("DESCRIPCIÓN:", True, (255, 255, 255))
    pantalla.blit(texto_titulo, (x, y))
    
    y_actual = y + 30
    
    # Descripciones personalizadas para cada pieza
    descripciones = {
        "Soldado": "Unidad básica de infantería. Puede moverse y luego atacar en el mismo turno, ideal para avanzar y presionar.",
        
        "Paladin": "Un Guerrero con alta movilidad. Muy versátil para penetrar en el terreno enemigo, sin embargo su rango de ataque es reducido",
        
        "Mago": "Pieza con un gran rango de ataque y gran daño, sin embargo no puede moverse y atacar en el mismo turno.",
        
        "Dragon": "Bestia voladora que puede saltar sobre otras piezas. Su ataque a distancia y movilidad lo hacen mortalmente peligroso.",
        
        "Destructor": "La unidad más poderosa del juego. Alta vida y daño devastador, pero su movimiento lento lo hace vulnerable a ataques coordinados."
    }
    
    # Obtener descripción de la pieza actual
    descripcion = descripciones.get(pieza.nombre, "Sin descripción disponible.")
    
    # Dividir en líneas para que quepa en pantalla (con margen derecho de 15px)
    palabras = descripcion.split()
    lineas = []
    linea_actual = ""
    max_ancho = ANCHO_VENTANA - x - 15  # Margen derecho de 15px
    
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
    
    # Dibujar cada línea
    for linea in lineas:
        texto_linea = fuente_texto.render(linea, True, (200, 200, 200))
        pantalla.blit(texto_linea, (x, y_actual))
        y_actual += 25