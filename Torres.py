from abc import ABC, abstractmethod


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

    # Logica de ataque

    def atacar(self, unidad):
        """
        Aplica el daño base de esta torre a una unidad enemiga.
        Devuelve el daño real infligido (puede ser 0 si la unidad ya murió).
        """
        if not self.esta_viva():
            return 0

        daño_infligido = min(self.daño, unidad.vida_actual)
        unidad.vida_actual -= daño_infligido
        return daño_infligido

    def puede_atacar_a(self, fila_objetivo, columna_objetivo):
        """
        Comprueba si una casilla cae dentro del alcance de esta torre.
        """
        if self.fila is None or self.columna is None:
            return False   # la torre aún no ha sido colocada en el mapa

        distancia = max(
            abs(self.fila - fila_objetivo),
            abs(self.columna - columna_objetivo)
        )
        return distancia <= self.alcance

    # Habilidad especial y gestión de turnos

    def avanzar_turno(self, contexto):
        """
        Incrementa el contador de turnos y activa la habilidad especial
        """
        self._turno_actual += 1

        if self._turno_actual >= self.turnos_para_habilidad:
            self.activar_habilidad(contexto)
            self._turno_actual = 0   # reinicia el contador después de activarse

    @abstractmethod
    def activar_habilidad(self, contexto):
        """
        Habilidad especial de esta torre. Cada subclase implementa la suya.
        """

    # Estado de la torre y gestión de vida

    def esta_viva(self):
        """Devuelve True mientras la torre no haya sido destruida."""
        return self.vida_actual > 0

    def recibir_daño(self, cantidad):
        """Reduce la vida de la torre. Nunca baja de 0."""
        self.vida_actual = max(0, self.vida_actual - cantidad)

    def curar(self, cantidad):
        """Restaura vida sin superar la vida máxima."""
        self.vida_actual = min(self.vida_maxima, self.vida_actual + cantidad)

    def resumen(self):
        """Devuelve un texto corto con el estado actual de la torre, útil para debug."""
        return (f"[{self.nombre}] "
                f"Vida: {self.vida_actual}/{self.vida_maxima} | "
                f"Daño: {self.daño} | "
                f"Alcance: {self.alcance} | "
                f"Turno habilidad: {self._turno_actual}/{self.turnos_para_habilidad}")

    def __repr__(self):
        estado = "viva" if self.esta_viva() else "destruida"
        return f"{self.nombre}({estado}, {self.vida_actual}hp)"

