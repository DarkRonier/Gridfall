# game/assets.py

import sys
import os
import pygame
import io

SVGS_CARGADOS = {}

def cargar_svgs():
    """Carga todos los SVG de las piezas."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_assets = os.path.join(base_path, "assets", "pieces")

    mapeo_piezas = {
        "Soldado": "soldier",
        "Paladin": "paladin", 
        "Mago": "mago",
        "Dragon": "dragon",
        "Destructor": "destructor"
    }
    
    for nombre_codigo, nombre_archivo in mapeo_piezas.items():
        ruta_svg = os.path.join(ruta_assets, f"{nombre_archivo}.svg")
        
        try:
            SVGS_CARGADOS[nombre_codigo] = pygame.image.load(ruta_svg)
            print(f"✓ Cargado: {nombre_archivo}.svg")
        except Exception as e:
            print(f"✗ Error cargando {nombre_archivo}.svg: {e}")
            print(f"  Buscando en: {ruta_svg}")
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