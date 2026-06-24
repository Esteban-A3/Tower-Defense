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

# TORRE VIGÍA 

class TorreVigia(Torre):
    """
    Torre de vigilancia rápida.
    Vida baja y daño bajo, pero dispara dos veces cada 3 turnos.
    """

    # Estadisticas
    STATS = {
        "vida_maxima":          40,   # frágil: necesita protección de otras torres
        "daño":                 12,   # daño bajo por golpe individual
        "alcance":               2,   # cubre un radio de 2 casillas
        "costo":                 0,   # Conectar con economía 
        "turnos_para_habilidad": 3,   # disparo doble cada 3 turnos
    }

    def __init__(self):
        super().__init__(
            nombre="Torre Vigía",
            **self.STATS
        )

    def activar_habilidad(self, contexto):
        """
        Disparo doble.
        """
        unidades = contexto.get("unidades_en_rango", [])
        if not unidades:
            return

        # Apunta a la unidad más débil para maximizar eliminaciones
        objetivo = min(unidades, key=lambda u: u.vida_actual)

        primer_golpe  = self.atacar(objetivo)
        segundo_golpe = self.atacar(objetivo)   # segundo disparo en el mismo turno

        contexto["log"] = (
            f"{self.nombre} dispara doble sobre {objetivo.nombre}: "
            f"{primer_golpe} + {segundo_golpe} de daño"
        )

#CAÑÓN

class TorreCanon(Torre):
    """
    Torre de ataque pesado.
    Vida alta y daño alto, pero lenta. Su habilidad especial inflige
    daño en área a todas las unidades enemigas dentro de su alcance.
    """

    STATS = {
        "vida_maxima":          85,   # muy resistente, difícil de destruir
        "daño":                 40,   # el mayor daño individual del juego
        "alcance":               3,   # alcance amplio para compensar la lentitud
        "costo":                 0,   # Conectar con economía
        "turnos_para_habilidad": 4,   # daño en área cada 4 turnos
    }

    def __init__(self):
        super().__init__(
            nombre="Torre Cañón",
            **self.STATS
        )

    def activar_habilidad(self, contexto):
        """
        Disparo de área, inflige daño a todas las unidades enemigas
        """
        unidades = contexto.get("unidades_en_rango", [])
        if not unidades:
            return

        daño_area = int(self.daño * 0.75)   # 75% del daño base = 30 pts
        total_infligido = 0

        for unidad in unidades:
            daño_real = min(daño_area, unidad.vida_actual)
            unidad.vida_actual -= daño_real
            total_infligido += daño_real

        contexto["log"] = (
            f"{self.nombre} dispara explosión: {daño_area} dmg "
            f"a {len(unidades)} unidad(es), total {total_infligido}"
        )