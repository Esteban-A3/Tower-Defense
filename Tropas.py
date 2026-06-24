from abc import ABC, abstractmethod

class Unidad(ABC):
    """
    Clase base abstracta para todas las unidades atacantes.
    """

    def __init__(self, nombre, vida_maxima, daño, velocidad,
                 alcance, costo, turnos_para_habilidad):
        self.nombre = nombre

        # Salud
        self.vida_maxima = vida_maxima
        self.vida_actual = vida_maxima

        # Estadisitcas
        self.daño = daño
        self.velocidad = velocidad          # casillas por turno
        self.alcance = alcance              # radio de ataque en casillas

        #economía
        self.costo = costo                  # Conectar con economía

        # Habilidad especial
        self.turnos_para_habilidad = turnos_para_habilidad
        self._turno_actual = 0

        # Ubicacion en el mapa
        self.fila = None
        self.columna = None

        # Regeneracion 
        self.en_recuperacion = False

    # Logica de ataque

    def atacar(self, objetivo):
        """
        Inflige el daño base de esta unidad a un objetivo (torre, muro
        o la base central).
        """
        if not self.esta_viva():
            return 0

        daño_infligido = min(self.daño, objetivo.vida_actual)
        objetivo.recibir_daño(daño_infligido)
        return daño_infligido

    def puede_atacar_a(self, fila_objetivo, columna_objetivo):
        """
        Verifica si un objetivo cae dentro del alcance de ataque.
        """
        if self.fila is None or self.columna is None:
            return False

        distancia = max(
            abs(self.fila - fila_objetivo),
            abs(self.columna - columna_objetivo)
        )
        return distancia <= self.alcance
    # Logica de movimiento

    def puede_moverse(self):
        """
        Devuelve True si la unidad puede avanzar este turno.
        """
        return self.esta_viva() and not self.en_recuperacion

    # Logica de turnos y habilidades especiales

    def avanzar_turno(self, contexto):
        """
        Llamado por el motor de combate al inicio de cada turno.
        Incrementa el contador y dispara la habilidad cuando toca.
        """
        self._turno_actual += 1

        if self._turno_actual >= self.turnos_para_habilidad:
            self.activar_habilidad(contexto)
            self._turno_actual = 0

    @abstractmethod
    def activar_habilidad(self, contexto):
        """
        Habilidad especial de esta unidad.
        """