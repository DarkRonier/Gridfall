# game/assets.py

import pygame
import io

# Diccionario para guardar el contenido de los archivos SVG una vez leídos del disco.
SVGS_CARGADOS = {}

def cargar_svgs():
    try:
        # Cargamos directamente la imagen. Pygame la tratará como un sprite negro sobre fondo transparente.
        SVGS_CARGADOS['Soldado'] = pygame.image.load('assets/soldier.svg')
        SVGS_CARGADOS['Paladin'] = pygame.image.load('assets/paladin.svg')
        SVGS_CARGADOS['Mago'] = pygame.image.load('assets/mago.svg')
        SVGS_CARGADOS['Dragon'] = pygame.image.load('assets/dragon.svg')
        SVGS_CARGADOS['Destructor'] = pygame.image.load('assets/destructor.svg')
        print("Archivos SVG cargados y convertidos a superficies correctamente.")
    except pygame.error as e:
        print(f"Error al cargar un archivo SVG. Asegúrate de que están en la carpeta 'assets' y son válidos.\n{e}")
        return False
    return True

def crear_superficie_pieza(nombre_pieza, color_rgb, tamano, cache_imagenes):
    """
    Crea una superficie de pieza coloreada usando la técnica de teñido.
    Usa un caché para no regenerar la misma imagen múltiples veces.
    """
    clave_cache = f"{nombre_pieza}-{color_rgb}-{tamano}"
    if clave_cache in cache_imagenes:
        return cache_imagenes[clave_cache]

    # Obtenemos la imagen "plantilla" en negro que ya cargamos.
    plantilla_img = SVGS_CARGADOS.get(nombre_pieza)
    if not plantilla_img:
        return pygame.Surface(tamano, pygame.SRCALPHA)

    # Creamos una copia de la plantilla para no modificar la original.
    imagen_copia = plantilla_img.copy()
    
    # "Teñimos" la imagen: sumamos el color del jugador a la imagen negra.
    # (0,0,0) + (R,G,B) = (R,G,B)
    imagen_copia.fill(color_rgb, special_flags=pygame.BLEND_RGB_ADD)

    # Escalamos la imagen ya coloreada.
    imagen_escalada = pygame.transform.smoothscale(imagen_copia, tamano)

    # Guardamos la imagen final en el caché para futuros usos.
    cache_imagenes[clave_cache] = imagen_escalada
    
    return imagen_escalada