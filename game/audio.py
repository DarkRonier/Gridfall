import pygame
import os

class AudioManager:
    """Gestiona todos los efectos de sonido y música del juego."""
    
    def __init__(self):
        """Inicializa el mixer de pygame y carga todos los sonidos."""
        # Inicializar el mixer de audio
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Volumen general (0.0 a 1.0) - DEBE IR ANTES de cargar sonidos
        self.master_volume = 0.7
        
        # Diccionario para almacenar todos los sonidos
        self.sounds = {}
        
        # Ruta base para los sonidos (relativa al directorio donde se ejecuta el script)
        # Obtener la ruta absoluta del directorio del proyecto
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sounds_path = os.path.join(script_dir, "assets", "sounds")
        
        print(f"Buscando sonidos en: {self.sounds_path}")
        
        # Cargar todos los sonidos
        self.load_sounds()
        
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
            'main_menu': 'main menu.mp3',
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
    
    def play_menu_music(self, loop=True):
        """Reproduce música del menú principal."""
        if 'main_menu' in self.sounds and self.sounds['main_menu'] is not None:
            if loop:
                self.sounds['main_menu'].play(loops=-1)  # -1 = loop infinito
            else:
                self.sounds['main_menu'].play()
    
    def stop_menu_music(self):
        """Detiene la música del menú."""
        if 'main_menu' in self.sounds and self.sounds['main_menu'] is not None:
            self.sounds['main_menu'].stop()


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