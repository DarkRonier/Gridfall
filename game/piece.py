class Pieza:
    """
    Versión actualizada para manejar múltiples reglas de movimiento y ataque.
    """
    def __init__(self, nombre, jugador, hp, atk, agi, movimientos, rango_ataque, tipo_turno, tipo_ataque, puede_saltar=False):
        self.nombre = nombre
        self.jugador = jugador
        self.hp_max = hp
        self.hp = hp
        self.atk = atk
        self.agi = agi
        self.movimientos = movimientos
        self.rango_ataque = rango_ataque
        self.tipo_turno = tipo_turno #0: move or attack, 1: move then attack, 2: move & attack
        self.tipo_ataque = tipo_ataque #melee, ranged, magic
        self.puede_saltar = puede_saltar
        self.posicion = None

        self.ha_movido = False
        self.ha_atacado = False
        self.proximo_turno = 0
    
    def reiniciar_estado_turno(self):
        """Resetea el estado de la pieza al iniciar su turno."""
        self.ha_movido = False
        self.ha_atacado = False
    
    def calcular_siguiente_turno(self, reloj_actual):
        """Calcula el siguiente tic en el que la pieza tendrá un turno."""
        incremento = 1000 // self.agi 
        self.proximo_turno = reloj_actual + incremento

    def recibir_dano(self, cantidad):
        """Reduce el HP de la pieza y comprueba si sigue viva."""
        self.hp -= cantidad
        print(f"¡{self.nombre} (J{self.jugador}) recibe {cantidad} de daño! HP restante: {self.hp}")
        if not self.esta_viva():
            print(f"¡{self.nombre} (J{self.jugador}) ha sido derrotado!")

    def esta_viva(self):
        """Devuelve True si la pieza tiene HP por encima de 0."""
        return self.hp > 0

    def __repr__(self):
        """Representación en texto de la pieza, útil para depurar."""
        return f"{self.nombre[0:3]}(J{self.jugador}, H:{self.hp})"

# --- FÁBRICAS DE PIEZAS ---
def crear_soldado(jugador):
    return Pieza(
        nombre="Soldado", jugador=jugador, hp=15, atk=4, agi=6,
        movimientos=[('steps', 2)],
        rango_ataque=[('allsides', 1)],
        tipo_turno=1,
        tipo_ataque='melee',
        puede_saltar=False
    )

def crear_paladin(jugador):
    return Pieza(
        nombre="Paladin", jugador=jugador, hp=30, atk=5, agi=5.4,
        movimientos=[('rect', 4), ('diag', 3)],
        rango_ataque=[('rect', 1)],
        tipo_turno=1,
        tipo_ataque='melee',
        puede_saltar=False
    )

def crear_mago(jugador):
    return Pieza(
        nombre="Mago", jugador=jugador, hp=12, atk=6, agi=5.1,
        movimientos=[('steps', 2)],
        rango_ataque=[('steps', (0, 3))],
        tipo_turno=1,
        tipo_ataque='ranged',
        puede_saltar=False
    )

def crear_dragon(jugador):
    return Pieza(
        nombre="Dragon", jugador=jugador, hp=40, atk=7, agi=4.5,
        movimientos=[('allsides', 2)],
        rango_ataque=[('steps', (0, 3))],
        tipo_turno=1,
        tipo_ataque='ranged',
        puede_saltar=True
    )

def crear_destructor(jugador):
    return Pieza(
        nombre="Destructor", jugador=jugador, hp=50, atk=10, agi=4.8,
        movimientos=[('allsides', 1)],
        rango_ataque=[('allsides', 1)],
        tipo_turno=1,
        tipo_ataque='melee',
        puede_saltar=False
    )