from abc import ABC


class Torre(ABC):
    """
    Clase abstracta que representa una torre en el juego.
    Contiene atributos y métodos comunes a todas las torres.
    """

    def __init__(self, nombre, vida_maxima, daño, alcance,
                 costo, turnos_para_habilidad):
        self.nombre = nombre

        # vida
        self.vida_maxima = vida_maxima
        self.vida_actual = vida_maxima   # al colocarse empieza con vida completa

        # daño y alcance
        self.daño = daño
        self.alcance = alcance           # en cantidad de casillas (radio)

        # Economía
        # El costo está declarado pero no se usa todavía; se conectará
        # cuando implementemos el sistema económico.
        self.costo = costo               

        # Habilidad especial
        self.turnos_para_habilidad = turnos_para_habilidad
        self._turno_actual = 0           # privado: solo la clase lo administra

        # Posición en el mapa
        # Se asigna cuando el defensor coloca la torre en la cuadrícula.
        self.fila = None
        self.columna = None