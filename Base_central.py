class BaseCentral:
    """
    Estructura central del defensor. Su destrucción significa
    la victoria inmediata del atacante en esa ronda.
    """

    # Estadísticas de la base central
    VIDA_MAXIMA = 200    # bastante más resistente que cualquier muro o torre

    # Celdas que ocupa en el mapa.
    CELDAS = [(7, 7), (7, 8), (8, 7), (8, 8)]

    def __init__(self):
        self.nombre = "Base Central"
        self.vida_maxima = self.VIDA_MAXIMA
        self.vida_actual = self.VIDA_MAXIMA

        # Las celdas que ocupa son fijas; se exponen como atributo
        # para que el Mapa pueda bloquearlas al inicializar la cuadrícula.
        self.celdas = self.CELDAS

    # Daño y estado de la base central

    def recibir_daño(self, cantidad):
        """
        Reduce la vida de la base. Nunca baja de 0.
        Devuelve el daño real aplicado.
        """
        daño_real = min(cantidad, self.vida_actual)
        self.vida_actual -= daño_real
        return daño_real

    def esta_destruida(self):
        """
        El motor de combate consulta esto al final de cada turno.
        Si devuelve True, la ronda termina con victoria del atacante.
        """
        return self.vida_actual <= 0

    def esta_viva(self):
        """Alias semántico para compatibilidad con el resto del código."""
        return self.vida_actual > 0

    def porcentaje_vida(self):
        """Vida actual como valor entre 0.0 y 1.0, para la barra visual."""
        return self.vida_actual / self.vida_maxima

    def reiniciar(self):
        """
        Restaura la base a vida completa al inicio de cada nueva ronda.
        El motor de combate llama a este método en la transición entre rondas.
        """
        self.vida_actual = self.vida_maxima

    def resumen(self):
        porcentaje = int(self.porcentaje_vida() * 100)
        return (f"[{self.nombre}] "
                f"Vida: {self.vida_actual}/{self.vida_maxima} ({porcentaje}%)")

    def __repr__(self):
        estado = "en pie" if self.esta_viva() else "DESTRUIDA"
        return f"BaseCentral({estado}, {self.vida_actual}hp)" 