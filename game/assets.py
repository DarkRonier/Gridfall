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

def _gradiente_vertical(tamano, arriba, abajo):
    """Superficie opaca con un degradado vertical (arriba -> abajo)."""
    ancho, alto = tamano
    grad = pygame.Surface((1, alto))
    for y in range(alto):
        t = y / max(1, alto - 1)
        grad.set_at((0, y), tuple(int(arriba[i] + (abajo[i] - arriba[i]) * t) for i in range(3)))
    return pygame.transform.scale(grad, (ancho, alto))


def _aclarar(color, f):
    return tuple(min(255, int(c + (255 - c) * f)) for c in color)


def _oscurecer(color, f):
    return tuple(int(c * (1 - f)) for c in color)


def crear_superficie_pieza(nombre_pieza, color_rgb, tamano, cache_imagenes):
    """
    Crea el sprite de una pieza a partir de su silueta SVG: relleno con degradado
    (luz arriba, sombra abajo), brillo en el borde superior-izquierdo y contorno oscuro.
    Usa un caché para no regenerar la misma imagen múltiples veces.
    """
    clave_cache = f"{nombre_pieza}-{color_rgb}-{tamano}"
    if clave_cache in cache_imagenes:
        return cache_imagenes[clave_cache]

    plantilla_img = SVGS_CARGADOS.get(nombre_pieza)
    if not plantilla_img:
        return pygame.Surface(tamano, pygame.SRCALPHA)

    ancho, alto = tamano
    grosor = max(1, round(min(ancho, alto) / 40))      # grosor del contorno
    interior = (max(1, ancho - 2 * grosor), max(1, alto - 2 * grosor))

    # Silueta (alfa) escalada al área interior; el contorno ocupa el margen.
    silueta = pygame.transform.smoothscale(plantilla_img, interior).convert_alpha()
    mascara = pygame.mask.from_surface(silueta, 110)

    # Relleno con degradado: más claro arriba y más oscuro abajo.
    cuerpo = _gradiente_vertical(interior, _aclarar(color_rgb, 0.38), _oscurecer(color_rgb, 0.42))
    cuerpo = cuerpo.convert_alpha()
    cuerpo.blit(mascara.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0)), (0, 0),
                special_flags=pygame.BLEND_RGBA_MULT)

    # Luz de borde (arriba-izquierda) y sombra interior (abajo-derecha).
    d = max(1, grosor)
    luz = mascara.copy()
    luz.erase(mascara, (d, d))
    sombra = mascara.copy()
    sombra.erase(mascara, (-d, -d))
    cuerpo.blit(luz.to_surface(setcolor=(*_aclarar(color_rgb, 0.8), 210), unsetcolor=(0, 0, 0, 0)), (0, 0))
    cuerpo.blit(sombra.to_surface(setcolor=(*_oscurecer(color_rgb, 0.65), 170), unsetcolor=(0, 0, 0, 0)), (0, 0))

    # Contorno oscuro: la silueta teñida de casi negro, desplazada en 8 direcciones.
    color_contorno = _oscurecer(color_rgb, 0.85)
    sil_contorno = mascara.to_surface(setcolor=(*color_contorno, 255), unsetcolor=(0, 0, 0, 0))
    final = pygame.Surface(tamano, pygame.SRCALPHA)
    for dx in (-grosor, 0, grosor):
        for dy in (-grosor, 0, grosor):
            if dx or dy:
                final.blit(sil_contorno, (grosor + dx, grosor + dy))
    final.blit(cuerpo, (grosor, grosor))

    cache_imagenes[clave_cache] = final
    return final


def crear_sombra_suelo(ancho, alto, cache_imagenes, intensidad=90):
    """Elipse suave y oscura para apoyar las piezas en el suelo."""
    clave = f"sombra-{ancho}-{alto}-{intensidad}"
    if clave in cache_imagenes:
        return cache_imagenes[clave]
    sup = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pasos = 5
    for i in range(pasos):
        t = i / (pasos - 1)
        w = int(ancho * (1 - 0.55 * t))
        h = int(alto * (1 - 0.55 * t))
        pygame.draw.ellipse(sup, (0, 0, 0, int(intensidad / pasos * 1.6)),
                            ((ancho - w) // 2, (alto - h) // 2, w, h))
    cache_imagenes[clave] = sup
    return sup


def crear_base_ficha(ancho, alto, color_rgb, activa, cache_imagenes):
    """Peana elíptica con el color del equipo sobre la que se apoya cada pieza."""
    clave = f"base-{ancho}-{alto}-{color_rgb}-{activa}"
    if clave in cache_imagenes:
        return cache_imagenes[clave]
    sup = pygame.Surface((ancho, alto + 4), pygame.SRCALPHA)
    grosor = max(2, alto // 4)
    # canto (lado inferior) más oscuro para dar volumen
    pygame.draw.ellipse(sup, _oscurecer(color_rgb, 0.6), (0, 3, ancho, alto))
    pygame.draw.ellipse(sup, _oscurecer(color_rgb, 0.25), (0, 0, ancho, alto))
    pygame.draw.ellipse(sup, _aclarar(color_rgb, 0.25 if activa else 0.05),
                        (grosor, grosor // 2, ancho - 2 * grosor, max(2, alto - grosor)))
    pygame.draw.ellipse(sup, _aclarar(color_rgb, 0.55 if activa else 0.3), (0, 0, ancho, alto), 1)
    cache_imagenes[clave] = sup
    return sup
