import pygame
from game import constants

class MenuExpandible:
    """Clase para manejar un menú con secciones expandibles."""
    
    def __init__(self, pantalla, fuente_grande, fuente_mediana, es_fullscreen=False):
        self.pantalla = pantalla
        self.fuente_grande = fuente_grande
        self.fuente_mediana = fuente_mediana
        
        # Estado del menú
        self.seccion_expandida = None  # 'jugar', 'opciones', o None
        
        # IMPORTANTE: Guardamos el estado de fullscreen explícitamente
        self.fullscreen_activo = es_fullscreen
        
        # Obtener dimensiones REALES de la pantalla
        self.ancho_pantalla = pantalla.get_width()
        self.alto_pantalla = pantalla.get_height()
        
        # Dimensiones base del menú
        self.ancho_boton_base = 400
        self.alto_boton_base = 70
        self.espacio_base = 20
        self.margen_superior_base = constants.ALTO_BASE / 4 + 60
        
        # Botones principales
        self.botones = {}
        self._crear_botones()
    
    def _obtener_dimensiones_escaladas(self):
        """Retorna dimensiones escaladas según el modo actual."""
        return {
            'ancho_boton': int(self.ancho_boton_base * constants.ESCALA_GLOBAL),
            'alto_boton': int(self.alto_boton_base * constants.ESCALA_GLOBAL),
            'espacio': int(self.espacio_base * constants.ESCALA_GLOBAL),
            'margen_superior': int(self.margen_superior_base * constants.ESCALA_GLOBAL)
        }
    
    def _crear_botones(self):
        """Crea los rectángulos de los botones principales."""
        dims = self._obtener_dimensiones_escaladas()
        
        # CRÍTICO: Usar el centro REAL de la pantalla
        centro_x = self.ancho_pantalla / 2
        centro_y_inicio = self.alto_pantalla / 4
        
        y_actual = centro_y_inicio
        
        # Botón JUGAR
        self.botones['jugar'] = {
            'rect': pygame.Rect(centro_x - dims['ancho_boton']/2, y_actual, 
                               dims['ancho_boton'], dims['alto_boton']),
            'color': constants.COLOR_MENU_JUGAR,
            'color_hover': constants.COLOR_MENU_JUGAR_HOVER,
            'texto': 'JUGAR',
            'expandible': True,
            'subopciones': []
        }
        
        y_actual += dims['alto_boton'] + dims['espacio']
        
        # Si JUGAR está expandido, agregar subopciones
        if self.seccion_expandida == 'jugar':
            subopciones = [
                {'texto': 'Nueva Partida Local', 'accion': 'nueva_partida', 'habilitado': True},
                {'texto': 'vs IA', 'accion': 'vs_ia', 'habilitado': False, 'tooltip': 'Disponible en v0.4.x'},
                {'texto': 'Cargar Partida', 'accion': 'cargar', 'habilitado': False, 'tooltip': 'Disponible en v0.3.x'}
            ]
            
            alto_sub = int(50 * constants.ESCALA_GLOBAL)
            for subopcion in subopciones:
                rect_sub = pygame.Rect(centro_x - dims['ancho_boton']/2 + 30 * constants.ESCALA_GLOBAL, y_actual,
                                      dims['ancho_boton'] - 30 * constants.ESCALA_GLOBAL, alto_sub)
                subopcion['rect'] = rect_sub
                self.botones['jugar']['subopciones'].append(subopcion)
                y_actual += alto_sub
            
            y_actual += dims['espacio']
        
        # Botón REGLAS
        self.botones['reglas'] = {
            'rect': pygame.Rect(centro_x - dims['ancho_boton']/2, y_actual,
                               dims['ancho_boton'], dims['alto_boton']),
            'color': constants.COLOR_MENU_REGLAS,
            'color_hover': constants.COLOR_MENU_REGLAS_HOVER,
            'texto': 'REGLAS',
            'expandible': False,
            'accion': 'tutorial'
        }
        
        y_actual += dims['alto_boton'] + dims['espacio']
        
        # Botón OPCIONES
        self.botones['opciones'] = {
            'rect': pygame.Rect(centro_x - dims['ancho_boton']/2, y_actual,
                               dims['ancho_boton'], dims['alto_boton']),
            'color': constants.COLOR_MENU_OPCIONES,
            'color_hover': constants.COLOR_MENU_OPCIONES_HOVER,
            'texto': 'OPCIONES',
            'expandible': True,
            'subopciones': []
        }
        
        y_actual += dims['alto_boton'] + dims['espacio']
        
        # Si OPCIONES está expandido, agregar subopciones
        if self.seccion_expandida == 'opciones':
            subopciones = [
                {'texto': 'Música', 'tipo': 'toggle', 'habilitado': False, 'tooltip': 'Disponible en v0.5.x'},
                {'texto': 'Volumen', 'tipo': 'slider', 'habilitado': False, 'tooltip': 'Disponible en v0.5.x'},
                {'texto': 'Pantalla Completa', 'tipo': 'toggle', 'habilitado': True, 'valor': self.fullscreen_activo}
            ]
            
            alto_sub = int(50 * constants.ESCALA_GLOBAL)
            for subopcion in subopciones:
                rect_sub = pygame.Rect(centro_x - dims['ancho_boton']/2 + 30 * constants.ESCALA_GLOBAL, y_actual,
                                      dims['ancho_boton'] - 30 * constants.ESCALA_GLOBAL, alto_sub)
                subopcion['rect'] = rect_sub
                self.botones['opciones']['subopciones'].append(subopcion)
                y_actual += alto_sub
            
            y_actual += dims['espacio']
        
        # Botón CERRAR
        self.botones['cerrar'] = {
            'rect': pygame.Rect(centro_x - dims['ancho_boton']/2, y_actual,
                               dims['ancho_boton'], dims['alto_boton']),
            'color': constants.COLOR_MENU_CERRAR,
            'color_hover': constants.COLOR_MENU_CERRAR_HOVER,
            'texto': 'CERRAR',
            'expandible': False,
            'accion': 'salir'
        }
    
    def _detectar_hover(self, pos_mouse):
        """Detecta sobre qué botón está el mouse."""
        for nombre, boton in self.botones.items():
            if boton['rect'].collidepoint(pos_mouse):
                return ('principal', nombre)
            
            # Revisar subopciones
            if 'subopciones' in boton:
                for idx, subopcion in enumerate(boton['subopciones']):
                    if 'rect' in subopcion and subopcion['rect'].collidepoint(pos_mouse):
                        return ('subopcion', nombre, idx)
        
        return (None, None)
    
    def _dibujar_triangulo(self, x, y, expandido):
        """Dibuja el triángulo indicador de expandible (▶ o ▼)."""
        color = constants.COLOR_TEXTO_NORMAL
        tamano = int(15 * constants.ESCALA_GLOBAL)
        
        if expandido:
            # Triángulo hacia abajo ▼
            puntos = [
                (x, y),
                (x + tamano, y),
                (x + tamano/2, y + tamano/2)
            ]
        else:
            # Triángulo hacia derecha ▶
            puntos = [
                (x, y),
                (x + tamano/2, y + tamano/2),
                (x, y + tamano)
            ]
        
        pygame.draw.polygon(self.pantalla, color, puntos)
    
    def _dibujar_candado(self, x, y):
        """Dibuja un icono de candado simple 🔒."""
        color = constants.COLOR_CANDADO
        tam = int(12 * constants.ESCALA_GLOBAL)
        # Cuerpo del candado
        pygame.draw.rect(self.pantalla, color, (x, y + 8 * constants.ESCALA_GLOBAL, tam, 10 * constants.ESCALA_GLOBAL))
        # Arco del candado
        pygame.draw.arc(self.pantalla, color, (x + 2 * constants.ESCALA_GLOBAL, y, 8 * constants.ESCALA_GLOBAL, 10 * constants.ESCALA_GLOBAL), 0, 3.14, int(2 * constants.ESCALA_GLOBAL))
    
    def _dibujar_toggle(self, x, y, activo):
        """Dibuja un toggle switch [✓] o [✗]."""
        # Fondo del toggle
        color_fondo = (60, 180, 60) if activo else (140, 40, 40)
        ancho_toggle = int(40 * constants.ESCALA_GLOBAL)
        alto_toggle = int(20 * constants.ESCALA_GLOBAL)
        radio = int(10 * constants.ESCALA_GLOBAL)
        
        pygame.draw.rect(self.pantalla, color_fondo, (x, y, ancho_toggle, alto_toggle), border_radius=radio)
        
        # Círculo interno
        radio_circulo = int(8 * constants.ESCALA_GLOBAL)
        pos_circulo_x = int(x + ancho_toggle - 15 * constants.ESCALA_GLOBAL if activo else x + 15 * constants.ESCALA_GLOBAL)
        pos_circulo_y = int(y + alto_toggle / 2)
        pygame.draw.circle(self.pantalla, (255, 255, 255), (pos_circulo_x, pos_circulo_y), radio_circulo)
    
    def dibujar(self):
        """Dibuja todo el menú."""
        self.pantalla.fill(constants.COLOR_FONDO)
        
        # Título - escalado según modo y centrado en pantalla real
        tamano_fuente_titulo = int(50 * constants.ESCALA_GLOBAL)
        fuente_titulo_escalada = pygame.font.SysFont("Impact", tamano_fuente_titulo)
        texto_titulo = fuente_titulo_escalada.render("GRIDFALL", True, constants.COLOR_TEXTO_NORMAL)
        
        # Posición del título usando centro REAL de pantalla
        pos_titulo_x = self.ancho_pantalla / 2
        pos_titulo_y = self.alto_pantalla / 6
        
        rect_titulo = texto_titulo.get_rect(center=(pos_titulo_x, pos_titulo_y))
        self.pantalla.blit(texto_titulo, rect_titulo)
        
        # Obtener posición del mouse para hover
        pos_mouse = pygame.mouse.get_pos()
        hover_info = self._detectar_hover(pos_mouse)
        
        # Crear fuentes escaladas
        tamano_fuente_boton = int(40 * constants.ESCALA_GLOBAL)
        tamano_fuente_sub = int(24 * constants.ESCALA_GLOBAL)
        fuente_boton = pygame.font.SysFont("Impact", tamano_fuente_boton)
        fuente_sub = pygame.font.SysFont("Arial", tamano_fuente_sub)
        
        # Dibujar botones principales
        for nombre, boton in self.botones.items():
            # Determinar color (hover o normal)
            if hover_info[0] == 'principal' and hover_info[1] == nombre:
                color = boton['color_hover']
            else:
                color = boton['color']
            
            # Dibujar rectángulo del botón
            radio_borde = int(15 * constants.ESCALA_GLOBAL)
            pygame.draw.rect(self.pantalla, color, boton['rect'], border_radius=radio_borde)
            
            # Dibujar triángulo si es expandible
            if boton['expandible']:
                expandido = (self.seccion_expandida == nombre)
                triangulo_x = boton['rect'].x + 20 * constants.ESCALA_GLOBAL
                triangulo_y = boton['rect'].centery - 7 * constants.ESCALA_GLOBAL
                self._dibujar_triangulo(triangulo_x, triangulo_y, expandido)
            
            # Dibujar texto del botón
            texto = fuente_boton.render(boton['texto'], True, constants.COLOR_TEXTO_NORMAL)
            texto_rect = texto.get_rect(center=boton['rect'].center)
            self.pantalla.blit(texto, texto_rect)
            
            # Dibujar subopciones si existen
            if 'subopciones' in boton and boton['subopciones']:
                for idx, subopcion in enumerate(boton['subopciones']):
                    # Determinar color de fondo
                    if not subopcion['habilitado']:
                        color_sub = constants.COLOR_SUBMENU_DISABLED
                    elif hover_info[0] == 'subopcion' and hover_info[1] == nombre and hover_info[2] == idx:
                        color_sub = constants.COLOR_SUBMENU_HOVER
                    else:
                        color_sub = constants.COLOR_SUBMENU
                    
                    # Dibujar fondo de subopción
                    radio_sub = int(10 * constants.ESCALA_GLOBAL)
                    pygame.draw.rect(self.pantalla, color_sub, subopcion['rect'], border_radius=radio_sub)
                    
                    # Determinar color de texto
                    color_texto = constants.COLOR_TEXTO_DISABLED if not subopcion['habilitado'] else constants.COLOR_TEXTO_NORMAL
                    
                    # Dibujar texto de subopción
                    texto_sub = fuente_sub.render(subopcion['texto'], True, color_texto)
                    texto_rect = texto_sub.get_rect(midleft=(subopcion['rect'].x + 15 * constants.ESCALA_GLOBAL, subopcion['rect'].centery))
                    self.pantalla.blit(texto_sub, texto_rect)
                    
                    # Dibujar candado si está deshabilitado
                    if not subopcion['habilitado']:
                        self._dibujar_candado(subopcion['rect'].right - 30 * constants.ESCALA_GLOBAL, 
                                            subopcion['rect'].centery - 9 * constants.ESCALA_GLOBAL)
                    
                    # Dibujar toggle si es de tipo toggle y está habilitado
                    if subopcion.get('tipo') == 'toggle' and subopcion['habilitado']:
                        valor = subopcion.get('valor', False)
                        self._dibujar_toggle(subopcion['rect'].right - 50 * constants.ESCALA_GLOBAL, 
                                           subopcion['rect'].centery - 10 * constants.ESCALA_GLOBAL, valor)
    
    def manejar_click(self, pos_click):
        """
        Maneja el click del mouse y devuelve una acción o None.
        Retorna: ('accion', valor) o None
        """
        for nombre, boton in self.botones.items():
            # Click en botón principal
            if boton['rect'].collidepoint(pos_click):
                if boton['expandible']:
                    # Toggle expandir/contraer
                    if self.seccion_expandida == nombre:
                        self.seccion_expandida = None
                    else:
                        self.seccion_expandida = nombre
                    self._crear_botones()  # Recrear botones para reflejar cambio
                    return None
                else:
                    # Botón simple, ejecutar acción
                    return ('accion', boton.get('accion'))
            
            # Click en subopciones
            if 'subopciones' in boton:
                for subopcion in boton['subopciones']:
                    if 'rect' in subopcion and subopcion['rect'].collidepoint(pos_click):
                        if not subopcion['habilitado']:
                            # Mostrar tooltip
                            print(f"[INFO] {subopcion.get('tooltip', 'No disponible aún')}")
                            return None
                        
                        # Subopción habilitada
                        if subopcion.get('tipo') == 'toggle':
                            # Toggle el valor
                            subopcion['valor'] = not subopcion.get('valor', False)
                            
                            # Si es fullscreen, aplicar cambio
                            if subopcion['texto'] == 'Pantalla Completa':
                                self.fullscreen_activo = subopcion['valor']
                                return ('toggle_fullscreen', subopcion['valor'])
                        
                        elif 'accion' in subopcion:
                            return ('accion', subopcion['accion'])
        
        return None


def mostrar_menu(pantalla_actual, fuente_grande, es_fullscreen=False):
    """
    Muestra el menú principal y maneja sus eventos.
    
    Args:
        pantalla_actual: La pantalla de pygame actual
        fuente_grande: Fuente para el menú
        es_fullscreen: Si estamos en modo fullscreen
    
    Devuelve: (nuevo_estado, nueva_pantalla, nuevo_es_fullscreen)
    """
    # Crear fuente mediana para subopciones
    fuente_mediana = pygame.font.SysFont("Arial", 24)
    
    # Usar la pantalla actual
    pantalla = pantalla_actual
    menu = MenuExpandible(pantalla, fuente_grande, fuente_mediana, es_fullscreen)
    
    while True:
        menu.dibujar()
        pygame.display.flip()
        
        # Manejo de eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return ('saliendo', pantalla, es_fullscreen)
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                resultado = menu.manejar_click(evento.pos)
                
                if resultado:
                    tipo, valor = resultado
                    
                    if tipo == 'accion':
                        if valor == 'salir':
                            return ('saliendo', pantalla, es_fullscreen)
                        elif valor == 'tutorial':
                            return ('tutorial', pantalla, es_fullscreen)
                        elif valor == 'nueva_partida':
                            return ('en_juego', pantalla, es_fullscreen)
                        elif valor == 'vs_ia':
                            return ('en_juego_ia', pantalla, es_fullscreen)
                        elif valor == 'cargar':
                            return ('cargar_partida', pantalla, es_fullscreen)
                    
                    elif tipo == 'toggle_fullscreen':
                        # Cambiar modo fullscreen
                        if valor:
                            # Activar fullscreen
                            ancho, alto, escala, offset_x, offset_y = constants.calcular_fullscreen()
                            constants.actualizar_dimensiones_ventana(ancho, alto, escala, offset_x, offset_y, True)
                            print(f"DEBUG: Activando fullscreen con offset_x={offset_x}, offset_y={offset_y}")
                            pantalla = pygame.display.set_mode((ancho, alto), pygame.FULLSCREEN)
                            es_fullscreen = True
                        else:
                            # Desactivar fullscreen
                            constants.actualizar_dimensiones_ventana(constants.ANCHO_BASE, constants.ALTO_BASE, 1.0, 0, 0, False)
                            pantalla = pygame.display.set_mode((constants.ANCHO_BASE, constants.ALTO_BASE))
                            es_fullscreen = False
                        
                        # Recrear menú con nuevas dimensiones y estado
                        menu = MenuExpandible(pantalla, fuente_grande, fuente_mediana, es_fullscreen)