import pygame

# --- DIMENSIONES BASE (DISEÑO ORIGINAL) ---
UI_ALTO_BASE = 60
ANCHO_BASE = 720
ALTO_BASE = 870
FILAS, COLUMNAS = 9, 8

# --- DIMENSIONES ACTUALES (se actualizan dinámicamente) ---
UI_ALTO = UI_ALTO_BASE
ANCHO_TABLERO = ANCHO_BASE
ALTO_TABLERO = ANCHO_BASE + 90
TAMANO_CASILLA = ANCHO_BASE // COLUMNAS

ANCHO_VENTANA = ANCHO_BASE
ALTO_VENTANA = ALTO_BASE

NOMBRE_VENTANA = "Gridfall"
FPS = 60

# --- SISTEMA DE ESCALADO ---
ESCALA_GLOBAL = 1.0  # Factor de escala actual
OFFSET_X = 0  # Offset para centrar horizontalmente
OFFSET_Y = 0  # Offset para centrar verticalmente
MODO_FULLSCREEN = False

# --- COLORES ---
GRIS_CLARO = (230, 230, 230)
GRIS_OSCURO = (150, 150, 150)
COLOR_FONDO = (30, 30, 30)

COLOR_J1_OPACO = (60, 60, 180)
COLOR_J1_VIBRANTE = (80, 120, 255)
COLOR_J2_OPACO = (180, 60, 60)
COLOR_J2_VIBRANTE = (255, 80, 80)

COLOR_CASILLA_CLARA = (240, 217, 181)
COLOR_CASILLA_OSCURA = (181, 136, 99)

COLOR_HP_FONDO = (70, 80, 70) # Gris verdoso oscuro
COLOR_HP_ALTA = (40, 170, 90)  # Verde
COLOR_HP_MEDIA = (255, 215, 0) # Amarillo
COLOR_HP_BAJA = (255, 60, 30)   # Rojo

# --- ESTADOS DE CASILLA (PARA LA VISUALIZACIÓN) ---
# Estos ya no representan la lógica principal, sino cómo se dibuja
# una casilla al ser marcada como accesible, por ejemplo.
VACIA = 0
ACCESIBLE = 1
BAJO_ATAQUE = 2


# --- UI ---
BOTON_VOLVER_RECT = pygame.Rect(10, 10, 100, 40)
BOTON_PASAR_RECT = pygame.Rect(ANCHO_VENTANA - 60, 10, 50, 40)
BOTON_DESHACER_RECT = pygame.Rect(ANCHO_VENTANA - 120, 10, 50, 40)
# Rectángulo para el panel de confirmación
PANEL_CONFIRMACION_RECT = pygame.Rect(ANCHO_VENTANA / 2 - 250, ALTO_VENTANA / 2 - 100, 500, 200)
# Botones dentro del panel de confirmación
BOTON_CONFIRMAR_SI_RECT = pygame.Rect(ANCHO_VENTANA / 2 - 150, ALTO_VENTANA / 2 + 20, 120, 50)
BOTON_CONFIRMAR_NO_RECT = pygame.Rect(ANCHO_VENTANA / 2 + 30, ALTO_VENTANA / 2 + 20, 120, 50)

COLOR_RESALTADO_ACTIVO = (240, 240, 160, 250)

# Rectángulo para el borde del turno. Es 10px más grande que el tablero en cada lado.
GROSOR_BORDE = 7
TABLERO_RECT = pygame.Rect(0, UI_ALTO, ANCHO_TABLERO, ALTO_TABLERO)
BORDE_RECT = TABLERO_RECT.inflate(GROSOR_BORDE, GROSOR_BORDE)
COLOR_BORDE_NEUTRO = (40, 40, 40) 

# --- COLORES DEL MENÚ ---
# Botones principales
COLOR_MENU_JUGAR = (40, 120, 40)      # Verde oscuro
COLOR_MENU_REGLAS = (40, 80, 140)     # Azul oscuro
COLOR_MENU_OPCIONES = (100, 60, 140)  # Morado oscuro
COLOR_MENU_CERRAR = (140, 40, 40)     # Rojo oscuro

# Hover (más brillantes)
COLOR_MENU_JUGAR_HOVER = (60, 180, 60)
COLOR_MENU_REGLAS_HOVER = (60, 120, 200)
COLOR_MENU_OPCIONES_HOVER = (140, 90, 200)
COLOR_MENU_CERRAR_HOVER = (200, 60, 60)

# Submenú
COLOR_SUBMENU = (50, 50, 50)           # Gris oscuro
COLOR_SUBMENU_HOVER = (70, 70, 70)     # Gris más claro
COLOR_SUBMENU_DISABLED = (30, 30, 30)  # Casi negro

# Texto
COLOR_TEXTO_NORMAL = (255, 255, 255)
COLOR_TEXTO_DISABLED = (100, 100, 100)
COLOR_CANDADO = (80, 80, 80) 


# --- FUNCIONES DE UTILIDAD ---

def actualizar_dimensiones_ventana(ancho, alto, escala=1.0, offset_x=0, offset_y=0, es_fullscreen=False):
    """
    Actualiza las dimensiones globales de la ventana.
    Usado cuando se cambia de modo ventana a fullscreen y viceversa.
    """
    global ANCHO_VENTANA, ALTO_VENTANA, ESCALA_GLOBAL, OFFSET_X, OFFSET_Y, MODO_FULLSCREEN
    global UI_ALTO, ANCHO_TABLERO, ALTO_TABLERO, TAMANO_CASILLA
    
    ANCHO_VENTANA = ancho
    ALTO_VENTANA = alto
    ESCALA_GLOBAL = escala
    OFFSET_X = offset_x
    OFFSET_Y = offset_y
    MODO_FULLSCREEN = es_fullscreen
    
    # Actualizar dimensiones escaladas
    UI_ALTO = int(UI_ALTO_BASE * escala)
    ANCHO_TABLERO = int(ANCHO_BASE * escala)
    ALTO_TABLERO = int((ANCHO_BASE + 90) * escala)
    TAMANO_CASILLA = int((ANCHO_BASE // COLUMNAS) * escala)

def calcular_fullscreen():
    """
    Calcula las dimensiones y escalado para modo fullscreen.
    Retorna: (ancho, alto, escala, offset_x, offset_y)
    """
    info = pygame.display.Info()
    ancho_monitor = info.current_w
    alto_monitor = info.current_h
    
    # Calcular escala manteniendo aspecto
    escala_x = ancho_monitor / ANCHO_BASE
    escala_y = alto_monitor / ALTO_BASE
    escala = min(escala_x, escala_y)  # Usar la menor para que quepa todo
    
    # Calcular tamaño escalado
    ancho_escalado = int(ANCHO_BASE * escala)
    alto_escalado = int(ALTO_BASE * escala)
    
    # Calcular offsets para centrar
    offset_x = (ancho_monitor - ancho_escalado) // 2
    offset_y = (alto_monitor - alto_escalado) // 2
    
    return ancho_monitor, alto_monitor, escala, offset_x, offset_y
