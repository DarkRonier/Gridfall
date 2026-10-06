# game/effects.py
import math
import random
import pygame
from game import constants
from .piece import Pieza


# ----------------------------------------------------------------------------
# Utilidades de easing / escala
# ----------------------------------------------------------------------------
def _clamp01(t):
    return max(0.0, min(1.0, t))

def ease_out_cubic(t):
    t = _clamp01(t)
    return 1 - (1 - t) ** 3

def ease_in_cubic(t):
    t = _clamp01(t)
    return t ** 3

def ease_in_out(t):
    t = _clamp01(t)
    return t * t * (3 - 2 * t)

def ease_out_back(t, s=1.9):
    t = _clamp01(t) - 1
    return t * t * ((s + 1) * t + s) + 1

def _escala():
    """Factor para que los efectos se adapten al tamaño actual de casilla."""
    return constants.TAMANO_CASILLA / 90.0


# Colores de efectos según el tipo de pieza que ataca.
COLORES_PROYECTIL = {
    "Mago": ((190, 120, 255), (120, 200, 255)),
    "Dragon": ((255, 210, 60), (255, 90, 20)),
}
COLOR_PROYECTIL_DEFECTO = ((255, 220, 120), (255, 120, 0))


class Visual:
    """Estado visual de una pieza durante una animación (posición en suelo, altura y deformación)."""
    __slots__ = ("pos", "elevacion", "sx", "sy", "brillo")

    def __init__(self, pos, elevacion=0.0, sx=1.0, sy=1.0, brillo=0.0):
        self.pos = pygame.Vector2(pos)   # punto en el suelo (centro de casilla)
        self.elevacion = elevacion       # píxeles que el sprite está despegado del suelo
        self.sx = sx                     # deformación horizontal
        self.sy = sy                     # deformación vertical
        self.brillo = brillo             # 0..1 destello blanco


# ----------------------------------------------------------------------------
# Partículas y efectos globales (golpes, temblor, destellos)
# ----------------------------------------------------------------------------
class Particula:
    def __init__(self, pos, vel, vida, color, tam, gravedad=0.0, friccion=0.96, brillo=False):
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.vida = vida
        self.vida_max = vida
        self.color = color
        self.tam = tam
        self.gravedad = gravedad
        self.friccion = friccion
        self.brillo = brillo

    def update(self):
        self.vida -= 1
        self.vel *= self.friccion
        self.vel.y += self.gravedad
        self.pos += self.vel
        return self.vida > 0

    def draw(self, pantalla):
        t = self.vida / self.vida_max
        radio = max(1, int(self.tam * (0.35 + 0.65 * t)))
        if self.brillo:
            # halo suave + núcleo
            lado = radio * 4
            sup = pygame.Surface((lado, lado), pygame.SRCALPHA)
            pygame.draw.circle(sup, (*self.color, int(70 * t)), (lado // 2, lado // 2), radio * 2)
            pygame.draw.circle(sup, (*self.color, int(255 * t)), (lado // 2, lado // 2), radio)
            pantalla.blit(sup, sup.get_rect(center=(int(self.pos.x), int(self.pos.y))))
        else:
            sup = pygame.Surface((radio * 2, radio * 2), pygame.SRCALPHA)
            pygame.draw.circle(sup, (*self.color, int(255 * min(1.0, t * 1.6))), (radio, radio), radio)
            pantalla.blit(sup, sup.get_rect(center=(int(self.pos.x), int(self.pos.y))))


class Anillo:
    """Onda expansiva circular (impactos, aterrizajes)."""
    def __init__(self, pos, color, radio_final, vida=14, grosor=3):
        self.pos = pygame.Vector2(pos)
        self.color = color
        self.radio_final = radio_final
        self.vida = vida
        self.vida_max = vida
        self.grosor = grosor

    def update(self):
        self.vida -= 1
        return self.vida > 0

    def draw(self, pantalla):
        t = 1 - self.vida / self.vida_max
        radio = max(2, int(self.radio_final * ease_out_cubic(t)))
        alpha = int(220 * (1 - t))
        grosor = max(1, int(self.grosor * (1 - t) + 1))
        lado = radio * 2 + grosor * 2
        sup = pygame.Surface((lado, lado), pygame.SRCALPHA)
        pygame.draw.circle(sup, (*self.color, alpha), (lado // 2, lado // 2), radio, grosor)
        pantalla.blit(sup, sup.get_rect(center=(int(self.pos.x), int(self.pos.y))))


class GestorEfectos:
    """Singleton con las partículas y sacudidas activas. Se actualiza una vez por frame."""
    MAX_PARTICULAS = 260

    def __init__(self):
        self.particulas = []
        self.anillos = []
        self._golpes = {}   # pieza -> [frames_restantes, frames_totales, direccion, amplitud]

    def clear(self):
        self.particulas.clear()
        self.anillos.clear()
        self._golpes.clear()

    # --- generadores ---
    def _añadir(self, p):
        if len(self.particulas) < self.MAX_PARTICULAS:
            self.particulas.append(p)

    def chispas(self, pos, color, cantidad=10, velocidad=4.5, vida=22, tam=4, brillo=True, gravedad=0.0):
        s = _escala()
        for _ in range(cantidad):
            ang = random.uniform(0, math.tau)
            v = random.uniform(0.35, 1.0) * velocidad * s
            self._añadir(Particula(pos, (math.cos(ang) * v, math.sin(ang) * v),
                                   random.randint(vida - 6, vida + 6), color,
                                   tam * s * random.uniform(0.7, 1.2), gravedad * s, 0.92, brillo))

    def polvo(self, pos, cantidad=6, color=(220, 210, 190)):
        s = _escala()
        for _ in range(cantidad):
            ang = random.uniform(math.pi * 0.05, math.pi * 0.95) + math.pi  # hacia arriba/lados
            v = random.uniform(0.4, 1.6) * s
            self._añadir(Particula((pos[0] + random.uniform(-8, 8) * s, pos[1] + random.uniform(0, 6) * s),
                                   (math.cos(ang) * v * 1.4, math.sin(ang) * v * 0.5),
                                   random.randint(14, 22), color, random.uniform(3, 5.5) * s, -0.01, 0.93))

    def onda(self, pos, color, radio=None, vida=14):
        self.anillos.append(Anillo(pos, color, (radio or 38 * _escala()), vida))

    def golpe(self, pieza, desde, hacia, frames=16, amplitud=9):
        """Hace retroceder y parpadear a la pieza golpeada."""
        d = pygame.Vector2(hacia) - pygame.Vector2(desde)
        d = d.normalize() if d.length_squared() > 0 else pygame.Vector2(0, 0)
        self._golpes[pieza] = [frames, frames, d, amplitud]

    def impacto(self, pos, color_a, color_b, intensidad=1.0):
        self.onda(pos, color_a, 36 * _escala() * intensidad)
        self.chispas(pos, color_a, int(10 * intensidad), 5.0 * intensidad)
        self.chispas(pos, color_b, int(6 * intensidad), 3.0 * intensidad, tam=3)

    # --- consultas de dibujo ---
    def desplazamiento_golpe(self, pieza):
        g = self._golpes.get(pieza)
        if not g:
            return (0.0, 0.0)
        restante, total, d, amp = g
        t = restante / total
        # empujón inicial + vibración que se amortigua
        empuje = d * amp * _escala() * ease_out_cubic(t) * 0.6
        vib = math.sin((1 - t) * math.pi * 6) * amp * 0.35 * _escala() * t
        perp = pygame.Vector2(-d.y, d.x) * vib
        res = empuje + perp
        return (res.x, res.y)

    def destello(self, pieza):
        g = self._golpes.get(pieza)
        if not g:
            return 0.0
        return _clamp01(g[0] / g[1] * 1.6) * 0.75

    # --- ciclo de vida ---
    def update(self):
        self.particulas[:] = [p for p in self.particulas if p.update()]
        self.anillos[:] = [a for a in self.anillos if a.update()]
        for pieza in list(self._golpes):
            self._golpes[pieza][0] -= 1
            if self._golpes[pieza][0] <= 0:
                del self._golpes[pieza]

    def draw(self, pantalla):
        for a in self.anillos:
            a.draw(pantalla)
        for p in self.particulas:
            p.draw(pantalla)


_gestor = GestorEfectos()

def get_fx():
    return _gestor


# ----------------------------------------------------------------------------
# Animaciones
# ----------------------------------------------------------------------------
class MoveAnimation:
    """Movimiento con aceleración suave, pequeño salto y deformación al despegar/aterrizar."""
    def __init__(self, entidad, start_pos_px, end_pos_px, duration_frames=20):
        self.entidad = entidad
        self.start_pos = pygame.Vector2(start_pos_px)
        self.end_pos = pygame.Vector2(end_pos_px)
        # Las distancias largas duran un poco más (sin pasarse).
        distancia_casillas = self.start_pos.distance_to(self.end_pos) / max(1, constants.TAMANO_CASILLA)
        self.duration = int(duration_frames + min(10, max(0, distancia_casillas - 1) * 3))
        self.frames_pasados = 0
        self.current_pos = self.start_pos.copy()
        self.vuela = bool(getattr(entidad, "puede_saltar", False))
        self._visual = Visual(self.start_pos)
        self._polvo_inicial = False

    def update(self):
        """Devuelve True si la animación ha terminado."""
        fx = get_fx()
        if not self._polvo_inicial:
            self._polvo_inicial = True
            if not self.vuela:
                fx.polvo((self.start_pos.x, self.start_pos.y + 20 * _escala()), 4)

        self.frames_pasados += 1
        t = self.frames_pasados / self.duration
        terminada = self.frames_pasados >= self.duration
        if terminada:
            t = 1.0

        self.current_pos = self.start_pos.lerp(self.end_pos, ease_in_out(t))
        s = _escala()

        # Salto parabólico (más alto si la pieza vuela) y deformación
        altura = (14 if self.vuela else 9) * s
        elevacion = math.sin(math.pi * t) * altura
        sx, sy = 1.0, 1.0
        if t < 0.2:                       # anticipación: se agacha
            k = math.sin(t / 0.2 * math.pi / 2)
            sx, sy = 1 + 0.10 * k, 1 - 0.12 * k
        elif t < 0.8:                     # en el aire: se estira
            k = math.sin((t - 0.2) / 0.6 * math.pi)
            sx, sy = 1 - 0.06 * k, 1 + 0.10 * k
        else:                             # aterrizaje: rebote amortiguado
            k = (t - 0.8) / 0.2
            sx = 1 + 0.14 * math.sin(k * math.pi)
            sy = 1 - 0.16 * math.sin(k * math.pi)
        self._visual = Visual(self.current_pos, elevacion, sx, sy)

        if terminada:
            self.current_pos = self.end_pos.copy()
            self._visual = Visual(self.end_pos)
            if self.vuela:
                fx.onda((self.end_pos.x, self.end_pos.y + 18 * s), (255, 255, 255), 26 * s, 10)
            else:
                fx.polvo((self.end_pos.x, self.end_pos.y + 20 * s), 7)
            return True
        return False

    def get_pos(self):
        return self.current_pos

    def get_visual(self):
        return self._visual


class MeleeAttackAnimation:
    """Ataque cuerpo a cuerpo: carga hacia atrás, embestida, impacto con parada y regreso."""
    FASE_CARGA = 0.30
    FASE_EMBESTIDA = 0.46    # el impacto ocurre aquí
    PARADA = 0.54

    def __init__(self, atacante, start_pos_px, target_pos_px, duration_frames, callback_dano, objetivo=None):
        self.entidad = atacante
        self.objetivo = objetivo
        self.duration = max(24, int(duration_frames * 1.25))
        self.callback_dano = callback_dano

        self.start_pos = pygame.Vector2(start_pos_px)
        self.target_pos = pygame.Vector2(target_pos_px)
        direccion = self.target_pos - self.start_pos
        self.direccion = direccion.normalize() if direccion.length_squared() > 0 else pygame.Vector2(0, -1)
        self.peak_pos = self.start_pos.lerp(self.target_pos, 0.55)

        self.frames_pasados = 0
        self.damage_applied = False
        self.current_pos = self.start_pos.copy()
        self._visual = Visual(self.start_pos)

    def update(self):
        """Devuelve True al terminar."""
        self.frames_pasados += 1
        t = self.frames_pasados / self.duration
        s = _escala()

        pos = self.start_pos.copy()
        sx, sy, elev = 1.0, 1.0, 0.0
        if t < self.FASE_CARGA:                       # 1) toma impulso hacia atrás
            k = ease_out_cubic(t / self.FASE_CARGA)
            pos = self.start_pos - self.direccion * 12 * s * k
            sx, sy = 1 + 0.08 * k, 1 - 0.10 * k
            elev = 2 * s * k
        elif t < self.FASE_EMBESTIDA:                 # 2) embestida rápida
            k = ease_in_cubic((t - self.FASE_CARGA) / (self.FASE_EMBESTIDA - self.FASE_CARGA))
            atras = self.start_pos - self.direccion * 12 * s
            pos = atras.lerp(self.peak_pos, k)
            sx, sy = 1 - 0.08 * k, 1 + 0.10 * k
        elif t < self.PARADA:                         # 3) instante de impacto
            pos = self.peak_pos.copy()
            sx, sy = 1.12, 0.9
        else:                                         # 4) regreso suave
            k = ease_out_cubic((t - self.PARADA) / (1 - self.PARADA))
            pos = self.peak_pos.lerp(self.start_pos, k)
            sx, sy = 1 + 0.12 * (1 - k), 1 - 0.1 * (1 - k)

        # Impacto: daño, destello y sacudida del objetivo
        if t >= self.FASE_EMBESTIDA and not self.damage_applied:
            self.damage_applied = True
            fx = get_fx()
            punto = self.target_pos
            fx.impacto(punto, (255, 245, 200), (255, 140, 40))
            if self.objetivo is not None:
                fx.golpe(self.objetivo, self.start_pos, self.target_pos)
            self.callback_dano()

        self.current_pos = pos
        self._visual = Visual(pos, elev, sx, sy)
        if self.frames_pasados >= self.duration:
            self.current_pos = self.start_pos.copy()
            self._visual = Visual(self.start_pos)
            return True
        return False

    def get_pos(self):
        return self.current_pos

    def get_visual(self):
        return self._visual


class ProjectileAnimation:
    """Ataque a distancia: carga de energía, proyectil con estela y explosión al impactar."""
    FASE_CARGA = 0.25

    def __init__(self, atacante, start_pos_px, end_pos_px, duration_frames, callback_dano, objetivo=None):
        self.entidad = atacante
        self.objetivo = objetivo
        self.start_pos = pygame.Vector2(start_pos_px)
        self.end_pos = pygame.Vector2(end_pos_px)
        self.duration = max(30, int(duration_frames * 1.1))
        self.callback_dano = callback_dano

        self.frames_pasados = 0
        self.current_pos = self.start_pos.copy()
        self.color_a, self.color_b = COLORES_PROYECTIL.get(atacante.nombre, COLOR_PROYECTIL_DEFECTO)
        self.estela = []          # posiciones recientes del proyectil
        self.visible = False
        self._visual = Visual(self.start_pos)
        self._cargando = 0.0

    def update(self):
        self.frames_pasados += 1
        t = self.frames_pasados / self.duration
        s = _escala()
        fx = get_fx()
        direccion = self.end_pos - self.start_pos
        direccion = direccion.normalize() if direccion.length_squared() > 0 else pygame.Vector2(0, -1)

        if t < self.FASE_CARGA:
            k = t / self.FASE_CARGA
            self._cargando = k
            self.visible = k > 0.55
            self.current_pos = self.start_pos + direccion * 14 * s * ease_out_cubic(k)
            sx, sy = 1 - 0.06 * k, 1 + 0.10 * k
            retroceso = -direccion * 4 * s * k
            self._visual = Visual(self.start_pos + retroceso, 3 * s * k, sx, sy, brillo=0.25 * k)
            # partículas que convergen hacia el lanzador
            if self.frames_pasados % 2 == 0:
                ang = random.uniform(0, math.tau)
                origen = self.start_pos + pygame.Vector2(math.cos(ang), math.sin(ang)) * 30 * s
                fx._añadir(Particula(origen, (self.start_pos - origen) * 0.12, 8, self.color_a, 3.2 * s, 0, 0.98, True))
        else:
            k = ease_in_cubic((t - self.FASE_CARGA) / (1 - self.FASE_CARGA)) * 0.6 + \
                ((t - self.FASE_CARGA) / (1 - self.FASE_CARGA)) * 0.4
            k = _clamp01(k)
            self._cargando = 1.0
            self.visible = True
            origen = self.start_pos + direccion * 14 * s
            self.current_pos = origen.lerp(self.end_pos, k)
            # pequeña ondulación perpendicular
            perp = pygame.Vector2(-direccion.y, direccion.x)
            self.current_pos += perp * math.sin(k * math.pi * 3) * 3 * s * (1 - k)
            # retroceso al disparar (rebote del lanzador)
            rebote = max(0.0, 1 - (t - self.FASE_CARGA) / 0.15)
            self._visual = Visual(self.start_pos - direccion * 5 * s * rebote, 0, 1 + 0.08 * rebote, 1 - 0.08 * rebote)

            self.estela.append(self.current_pos.copy())
            if len(self.estela) > 9:
                self.estela.pop(0)
            if self.frames_pasados % 1 == 0:
                fx._añadir(Particula(self.current_pos + pygame.Vector2(random.uniform(-3, 3), random.uniform(-3, 3)) * s,
                                     (random.uniform(-0.4, 0.4) * s, random.uniform(-0.4, 0.4) * s),
                                     12, random.choice((self.color_a, self.color_b)), 3.2 * s, 0, 0.95, True))

        if self.frames_pasados >= self.duration:
            self._visual = Visual(self.start_pos)
            self.visible = False
            fx.impacto(self.end_pos, self.color_a, self.color_b, 1.3)
            if self.objetivo is not None:
                fx.golpe(self.objetivo, self.start_pos, self.end_pos, 18, 11)
            self.callback_dano()
            return True
        return False

    def get_pos(self):
        return self.start_pos

    def get_visual(self):
        return self._visual

    def draw(self, screen):
        s = _escala()
        # halo de carga alrededor del lanzador
        if self._cargando < 1.0 or self.frames_pasados < self.duration * (self.FASE_CARGA + 0.1):
            radio = int((6 + 14 * min(1.0, self._cargando)) * s)
            lado = radio * 4
            sup = pygame.Surface((lado, lado), pygame.SRCALPHA)
            pygame.draw.circle(sup, (*self.color_a, int(60 + 80 * self._cargando)), (lado // 2, lado // 2), radio * 2)
            pygame.draw.circle(sup, (*self.color_b, int(120 + 100 * self._cargando)), (lado // 2, lado // 2), radio)
            if self._cargando < 1.0:
                screen.blit(sup, sup.get_rect(center=(int(self.start_pos.x), int(self.start_pos.y))))
        if not self.visible:
            return
        # estela
        n = len(self.estela)
        for i, p in enumerate(self.estela):
            f = (i + 1) / (n + 1)
            r = max(1, int(7 * s * f))
            sup = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(sup, (*self.color_b, int(150 * f)), (r * 2, r * 2), r * 2)
            screen.blit(sup, sup.get_rect(center=(int(p.x), int(p.y))))
        # proyectil: halo + cuerpo + núcleo
        r = max(3, int(8 * s))
        sup = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
        c = r * 3
        pygame.draw.circle(sup, (*self.color_a, 70), (c, c), int(r * 2.4))
        pygame.draw.circle(sup, (*self.color_b, 255), (c, c), r)
        pygame.draw.circle(sup, (*self.color_a, 255), (c, c), max(2, int(r * 0.7)))
        pygame.draw.circle(sup, (255, 255, 255, 255), (c, c), max(1, int(r * 0.35)))
        screen.blit(sup, sup.get_rect(center=(int(self.current_pos.x), int(self.current_pos.y))))


class DamageText:
    """Número de daño: aparece con rebote, sube y se desvanece. Con contorno para leerse sobre cualquier fondo."""
    DURACION = 60

    def __init__(self, damage, position, font):
        self.text = str(damage)
        self.font = font
        self.color = (255, 70, 60)

        base = font.render(self.text, True, self.color)
        contorno = font.render(self.text, True, (20, 0, 0))
        w, h = base.get_size()
        self.surface = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            self.surface.blit(contorno, (2 + dx, 2 + dy))
        self.surface.blit(base, (2, 2))

        self.position = pygame.Vector2(position)
        self.lifetime = self.DURACION
        self.alpha = 255
        self.escala = 1.0

    def update(self):
        self.lifetime -= 1
        edad = self.DURACION - self.lifetime
        self.position.y -= 0.9 * _escala() * (1.0 if edad > 10 else 1.8)
        self.alpha = max(0, min(255, 255 * (self.lifetime / (self.DURACION * 0.5))))
        # rebote de entrada: crece por encima de su tamaño y se asienta
        self.escala = 0.4 + 0.6 * ease_out_back(edad / 12) if edad < 12 else 1.0

    def draw(self, screen):
        surf = self.surface
        if abs(self.escala - 1.0) > 0.02:
            surf = pygame.transform.smoothscale(
                self.surface, (max(1, int(self.surface.get_width() * self.escala)),
                               max(1, int(self.surface.get_height() * self.escala))))
        surf = surf.copy()
        surf.set_alpha(int(self.alpha))
        screen.blit(surf, surf.get_rect(center=(int(self.position.x), int(self.position.y))))


class FadeOutAnimation:
    """Muerte de una pieza: destello blanco, se encoge/eleva y se desintegra en partículas."""
    def __init__(self, entidad, duration_frames=32):
        self.entidad = entidad
        self.duration = duration_frames
        self.frames_pasados = 0
        self.alpha = 255
        self.escala = 1.0
        self.elevacion = 0.0
        self.brillo = 0.0

        # Explosión de partículas con los colores del equipo
        if entidad.posicion is not None:
            fila, col = entidad.posicion
            cx = constants.OFFSET_X + col * constants.TAMANO_CASILLA + constants.TAMANO_CASILLA / 2
            cy = constants.OFFSET_Y + fila * constants.TAMANO_CASILLA + constants.UI_ALTO + constants.TAMANO_CASILLA / 2
            color = (110, 150, 255) if entidad.jugador == 1 else (255, 110, 110)
            fx = get_fx()
            fx.chispas((cx, cy), color, 16, 5.5, 30, 4.5, True, gravedad=0.06)
            fx.chispas((cx, cy), (255, 255, 255), 8, 3.5, 22, 3, True)
            fx.onda((cx, cy), color, 46 * _escala(), 18)

    def update(self):
        """Devuelve True si la animación ha terminado."""
        self.frames_pasados += 1
        if self.frames_pasados >= self.duration:
            self.alpha = 0
            return True
        t = self.frames_pasados / self.duration
        self.brillo = _clamp01(1 - t * 3.5) * 0.9          # destello inicial
        self.escala = 1 - 0.35 * ease_in_out(t)
        self.elevacion = 14 * _escala() * ease_out_cubic(t)
        self.alpha = int(255 * (1 - ease_in_cubic(t)))
        return False

    def get_alpha(self):
        return self.alpha
