# game/effects.py
import pygame
from .piece import Pieza

class MoveAnimation:
    def __init__(self, entidad, start_pos_px, end_pos_px, duration_frames):
        self.entidad = entidad
        self.start_pos = pygame.Vector2(start_pos_px)
        self.end_pos = pygame.Vector2(end_pos_px)
        self.duration = duration_frames
        self.frames_pasados = 0
        self.current_pos = self.start_pos.copy()

    def update(self):
        """
        Actualiza la posición de la pieza. Devuelve True si la animación ha terminado.
        """
        self.frames_pasados += 1
        if self.frames_pasados >= self.duration:
            self.current_pos = self.end_pos.copy()
            return True

        progreso = self.frames_pasados / self.duration
        self.current_pos = self.start_pos.lerp(self.end_pos, progreso)
        return False

    def get_pos(self):
        """Devuelve la posición actual de la pieza animada."""
        return self.current_pos

class MeleeAttackAnimation:
    def __init__(self, atacante, start_pos_px, target_pos_px, duration_frames, callback_dano):
        self.entidad = atacante
        self.duration = duration_frames
        self.callback_dano = callback_dano # Función que se llamará en el momento del impacto
        
        self.start_pos = pygame.Vector2(start_pos_px)
        self.target_pos = pygame.Vector2(target_pos_px)
        self.peak_pos = self.start_pos.lerp(self.target_pos, 0.4)
        
        self.frames_pasados = 0
        self.damage_applied = False
        self.current_pos = self.start_pos.copy()

    def update(self):
        """Mueve la pieza hacia el objetivo y luego de vuelta. Devuelve True al terminar."""
        self.frames_pasados += 1
        
        # Sincronización: Aplicar el daño en el punto medio de la animación
        if self.frames_pasados >= self.duration / 2 and not self.damage_applied:
            self.callback_dano()
            self.damage_applied = True
            
        if self.frames_pasados >= self.duration:
            return True

        # Fase 1: Moverse hacia el punto de impacto
        if self.frames_pasados <= self.duration / 2:
            progreso = self.frames_pasados / (self.duration / 2)
            self.current_pos = self.start_pos.lerp(self.peak_pos, progreso)
        # Fase 2: Regresar a la posición original
        else:
            progreso = (self.frames_pasados - self.duration / 2) / (self.duration / 2)
            self.current_pos = self.peak_pos.lerp(self.start_pos, progreso)
            
        return False

    def get_pos(self):
        return self.current_pos

class ProjectileAnimation:
    def __init__(self, atacante, start_pos_px, end_pos_px, duration_frames, callback_dano):
        self.entidad = atacante
        self.start_pos = pygame.Vector2(start_pos_px)
        self.end_pos = pygame.Vector2(end_pos_px)
        self.duration = duration_frames
        self.callback_dano = callback_dano

        self.frames_pasados = 0
        self.current_pos = self.start_pos.copy()

    def update(self):
        self.frames_pasados += 1
        if self.frames_pasados >= self.duration:
            self.callback_dano()
            return True
        
        progreso = self.frames_pasados / self.duration
        self.current_pos = self.start_pos.lerp(self.end_pos, progreso)
        return False
    
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 200, 0), self.current_pos, 8)
        pygame.draw.circle(screen, (255, 120, 0), self.current_pos, 5)  

class DamageText:
    def __init__(self, damage, position, font):
        self.text = str(damage)
        self.font = font
        self.color = (255, 40, 40) # Rojo para el daño
        
        self.surface = self.font.render(self.text, True, self.color)
        self.position = pygame.Vector2(position)

        self.lifetime = 60
        self.alpha = 255

    def update(self):
        """Mueve el texto hacia arriba y lo desvanece."""
        self.lifetime -= 1
        self.position.y -= 0.8 # Velocidad de subida
        self.alpha = max(0, 255 * (self.lifetime / 60))

    def draw(self, screen):
        """Dibuja el texto en la pantalla con la opacidad actual."""
        self.surface.set_alpha(self.alpha)
        screen.blit(self.surface, self.position)

class FadeOutAnimation:
    def __init__(self, entidad, duration_frames=20):
        self.entidad = entidad
        self.duration = duration_frames
        self.frames_pasados = 0
        self.alpha = 255 # Opacidad inicial (completamente visible)

    def update(self):
        """Actualiza la opacidad. Devuelve True si la animación ha terminado."""
        self.frames_pasados += 1
        if self.frames_pasados >= self.duration:
            self.alpha = 0
            return True # Animación completada

        # Calculamos el progreso de la animación (de 0.0 a 1.0) y actualizamos el alpha
        progreso = self.frames_pasados / self.duration
        self.alpha = int(255 * (1 - progreso))
        return False # La animación sigue en curso

    def get_alpha(self):
        """Devuelve la opacidad actual de la pieza."""
        return self.alpha