import pygame
import os
import sys

class AudioManager:
    """Gestiona todos los efectos de sonido y música del juego."""
    
    def __init__(self):
        """Inicializa el mixer de pygame y carga todos los sonidos."""
        # Inicializar el mixer de audio
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Volumen general (0.0 a 1.0) - DEBE IR ANTES de cargar sonidos
        self.master_volume = 0.7
        self.music_volume = 0.6  # Volumen independiente para música de fondo
        
        # Diccionario para almacenar todos los sonidos
        self.sounds = {}
        
        # Ruta base para los sonidos compatible con ejecutable PyInstaller
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sounds_path = os.path.join(base_path, "assets", "sounds")
        
        print(f"Buscando sonidos en: {self.sounds_path}")
        
        # Cargar todos los sonidos
        self.load_sounds()

        # Configuración de música de fondo (usando pygame.mixer.music)
        self.music_files = {
            'menu': os.path.join(self.sounds_path, 'Menu-song.ogg'),
            'battle': os.path.join(self.sounds_path, 'Battle-song.ogg'),
        }
        self.current_music_mode = None  # 'menu' | 'battle' | None
        
    def load_sounds(self):
        """Carga todos los archivos de sonido desde la carpeta assets/sounds/"""
        # Lista de sonidos a cargar (nombre_en_codigo: nombre_de_archivo)
        sound_files = {
            'move': 'move-piece.mp3',
            'melee_attack': 'sword-slice.mp3',  # Con el número completo
            'ranged_cast': 'lanzar-fb.mp3',
            'ranged_impact': 'impact-fb.mp3',
            'death': 'death-sound.mp3',
            'victory': 'victory.mp3',
            'game_start': 'game-start.mp3',
            # Nota: la música de fondo ahora se gestiona con pygame.mixer.music
        }
        
        # Intentar cargar cada sonido
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(self.sounds_path, filename)
            print(f"Intentando cargar: {filepath}")
            
            try:
                if not os.path.exists(filepath):
                    print(f"Archivo NO existe: {filepath}")
                    self.sounds[sound_name] = None
                    continue
                    
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self.master_volume)
                self.sounds[sound_name] = sound
                print(f"Sonido cargado: {sound_name}")
            except Exception as e:
                print(f"Error al cargar {filename}: {e}")
                # Crear un sonido vacío para evitar errores
                self.sounds[sound_name] = None
    
    def play(self, sound_name, volume=None):
        """
        Reproduce un sonido.
        
        Args:
            sound_name: Nombre del sonido a reproducir
            volume: Volumen específico (0.0 a 1.0), opcional
        """
        if sound_name in self.sounds and self.sounds[sound_name] is not None:
            sound = self.sounds[sound_name]
            
            # Si se especifica un volumen, usarlo temporalmente
            if volume is not None:
                original_volume = sound.get_volume()
                sound.set_volume(volume * self.master_volume)
                sound.play()
                sound.set_volume(original_volume)
            else:
                sound.play()
        else:
            print(f"Sonido '{sound_name}' no encontrado")
    
    def set_master_volume(self, volume):
        """
        Ajusta el volumen general de todos los sonidos.
        
        Args:
            volume: Valor entre 0.0 (silencio) y 1.0 (máximo)
        """
        self.master_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound is not None:
                sound.set_volume(self.master_volume)
    
    def stop_all(self):
        """Detiene todos los sonidos que se estén reproduciendo."""
        pygame.mixer.stop()
    
    def play_move(self):
        """Sonido al mover una pieza."""
        self.play('move', volume=0.6)
    
    def play_melee_attack(self):
        """Sonido de ataque cuerpo a cuerpo."""
        self.play('melee_attack', volume=0.8)
    
    def play_ranged_cast(self):
        """Sonido de lanzar proyectil a distancia."""
        self.play('ranged_cast', volume=0.7)
    
    def play_ranged_impact(self):
        """Sonido de impacto del proyectil."""
        self.play('ranged_impact', volume=0.8)
    
    def play_death(self):
        """Sonido de muerte de una pieza."""
        self.play('death', volume=0.8)
    
    def play_victory(self):
        """Sonido de victoria."""
        self.play('victory', volume=0.9)
    
    def play_game_start(self):
        """Sonido al iniciar partida."""
        self.play('game_start', volume=0.7)
    
    # ====== MÚSICA DE FONDO (NO INTERFIERE CON SFX) ======
    def _load_and_play_music(self, filepath, loop=True, fade_ms=300):
        """Carga y reproduce una pista de música en bucle usando mixer.music."""
        try:
            if not os.path.exists(filepath):
                print(f"[Audio] Archivo de música no encontrado: {filepath}")
                return
            # Cortar la música previa si hay
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_ms)
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            print(f"[Audio] Error al reproducir música {filepath}: {e}")

    def set_music_mode(self, mode):
        """
        Asegura que esté sonando la música del modo indicado.
        mode: 'menu' o 'battle'. No hace nada si ya está puesta.
        """
        if mode not in self.music_files:
            print(f"[Audio] Modo de música desconocido: {mode}")
            return
        if self.current_music_mode == mode and pygame.mixer.music.get_busy():
            return  # Ya está sonando la pista correcta
        filepath = self.music_files[mode]
        self._load_and_play_music(filepath, loop=True)
        self.current_music_mode = mode

    def stop_music(self, fade_ms=300):
        """Detiene la música de fondo actual (con fadeout)."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)
        self.current_music_mode = None

    def set_music_volume(self, volume):
        """Ajusta solo el volumen de la música de fondo (0.0 - 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)


# Instancia global del gestor de audio (se inicializará en main.py)
audio_manager = None

def init_audio():
    """Inicializa el gestor de audio global."""
    global audio_manager
    audio_manager = AudioManager()
    return audio_manager

def get_audio():
    """Obtiene la instancia del gestor de audio."""
    return audio_manager