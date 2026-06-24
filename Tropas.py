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

    # Logica de vida y estado

    def esta_viva(self):
        """Devuelve True mientras la unidad no haya sido eliminada."""
        return self.vida_actual > 0

    def recibir_daño(self, cantidad):
        """Reduce la vida de la unidad. Nunca baja de 0."""
        self.vida_actual = max(0, self.vida_actual - cantidad)

    def curar(self, cantidad):
        """Restaura vida sin superar la vida máxima."""
        self.vida_actual = min(self.vida_maxima, self.vida_actual + cantidad)

    def porcentaje_vida(self):
        """Devuelve la vida actual como porcentaje (0.0 a 1.0)."""
        return self.vida_actual / self.vida_maxima

    def resumen(self):
        estado = "recuperando" if self.en_recuperacion else "activa"
        return (f"[{self.nombre}] "
                f"Vida: {self.vida_actual}/{self.vida_maxima} | "
                f"Daño: {self.daño} | "
                f"Vel: {self.velocidad} | "
                f"Estado: {estado}")

    def __repr__(self):
        estado = "viva" if self.esta_viva() else "eliminada"
        return f"{self.nombre}({estado}, {self.vida_actual}hp)"


# Umbral de vida para activar recuperación del Tanque
UMBRAL_RECUPERACION = 0.25   # 25% de la vida máxima


#Tanque

class Tanque(Unidad):
    """
    Unidad pesada que avanza directamente hacia la base central
    destruyendo todo lo que encuentre en su camino.
    """

    STATS = {
        "vida_maxima":          90,   # el más resistente de las tres unidades
        "daño":                 30,   # daño medio-alto al atacar cuerpo a cuerpo
        "velocidad":             1,   # solo 1 casilla por turno
        "alcance":               1,   # cuerpo a cuerpo, necesita estar adyacente
        "costo":                 0,   # TODO: conectar con economía
        "turnos_para_habilidad": 5,   # curación extra cada 5 turnos
    }

    CURACION_POR_TURNO = 6    # vida que recupera cada turno mientras está detenido
    CURACION_HABILIDAD = 20   # curación puntual cuando activa la habilidad

    # Qué objetivo prioriza el motor de combate al moverlo
    PRIORIDAD_MOVIMIENTO = "base"   # siempre avanza hacia la base central

    def __init__(self):
        super().__init__(nombre="Tanque", **self.STATS)

    def avanzar_turno(self, contexto):
        """
        Antes de avanzar el contador de habilidad, revisamos si la unidad
        debe entrar o salir del estado de recuperación de emergencia.
        """
        # Recuperacion de emergencia: si la vida baja del umbral, se detiene y se cura
        if self.vida_actual < self.vida_maxima * UMBRAL_RECUPERACION:
            # Entramos (o seguimos) en modo recuperación
            self.en_recuperacion = True
            self.curar(self.CURACION_POR_TURNO)
            contexto["log"] = (
                f"{self.nombre} en recuperación: "
                f"+{self.CURACION_POR_TURNO} vida → {self.vida_actual}hp"
            )
        else:
            # Vida por encima del umbral: retomamos el avance
            self.en_recuperacion = False

        #Habilidad especial
        super().avanzar_turno(contexto)

    def activar_habilidad(self, contexto):
        """
        Pulso de recuperación: curación puntual independiente del ciclo
        de emergencia. Se activa cada 5 turnos esté o no en recuperación.
        """
        vida_antes = self.vida_actual
        self.curar(self.CURACION_HABILIDAD)
        curado = self.vida_actual - vida_antes

        contexto["log"] = (
            f"{self.nombre} activa pulso de recuperación: "
            f"+{curado} vida → {self.vida_actual}hp"
        )

#Artilleria

class Artilleria(Unidad):
    """
    Unidad de rango medio que puede atacar torres y muros desde lejos
    sin necesidad de estar cerca de ellos.
    """

    STATS = {
        "vida_maxima":          55,   # vida media, ni frágil ni resistente
        "daño":                 22,   # daño medio, equilibrado con su alcance
        "velocidad":             2,   # 2 casillas por turno
        "alcance":               4,   # puede atacar desde 4 casillas de distancia
        "costo":                 0,   # TODO: conectar con economía
        "turnos_para_habilidad": 4,   # disparo perforante cada 4 turnos
    }

    FACTOR_DAÑO_SECUNDARIO = 0.60   # el segundo objetivo recibe el 60% del daño

    PRIORIDAD_MOVIMIENTO = "libre"  # avanza hacia lo que esté en rango
    PRIORIDAD_ATAQUE = ["torre", "muro", "base"]

    def __init__(self):
        super().__init__(nombre="Artillería", **self.STATS)

    def activar_habilidad(self, contexto):
        """
        Disparo perforante: impacta al primer objetivo en rango y,
        si hay un segundo objetivo detrás (mismo eje), también lo daña
        con el 60% del daño base.
        """
        objetivos = contexto.get("objetivos_en_rango", [])

        if not objetivos:
            contexto["log"] = f"{self.nombre} dispara pero no hay objetivos en rango"
            return

        # Primer impacto: daño completo
        primero = objetivos[0]
        daño_principal = self.atacar(primero)
        log = f"{self.nombre} disparo perforante: {primero.nombre} -{daño_principal}"

        # Segundo impacto: 60% del daño si hay otro objetivo detrás
        if len(objetivos) >= 2:
            segundo = objetivos[1]
            daño_secundario = int(self.daño * self.FACTOR_DAÑO_SECUNDARIO)
            daño_real = min(daño_secundario, segundo.vida_actual)
            segundo.recibir_daño(daño_real)
            log += f" | {segundo.nombre} -{daño_real} (perforación)"

        contexto["log"] = log