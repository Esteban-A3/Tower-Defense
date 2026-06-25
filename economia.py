#  CONSTANTES — editar aquí para rebalancear el juego

#Flujo económico por ronda
DINERO_INICIAL  = 500   # ambos jugadores arrancan con esto en la ronda 1
BONO_POR_RONDA  = 150   # suma fija al inicio de cada nueva ronda (desde ronda 2)
DINERO_MAXIMO   = 800   # tope acumulable; el exceso se descarta

# Costos de defensas
COSTO_TORRE_VIGIA    =  80
COSTO_TORRE_CANON    = 200
COSTO_TORRE_SANADORA = 150
COSTO_MURO           =  30

# Costos de unidades
COSTO_TANQUE     = 180
COSTO_ARTILLERIA = 130
COSTO_PEON       =  60

# Recompensas del defensor por eliminar unidades
RECOMPENSA_ELIMINAR_PEON      =  25
RECOMPENSA_ELIMINAR_ARTILLERIA =  50
RECOMPENSA_ELIMINAR_TANQUE    =  70

# Recompensas del atacante por destruir defensas o dañar la base
RECOMPENSA_DESTRUIR_MURO   =  20
RECOMPENSA_DESTRUIR_TORRE  =  60
RECOMPENSA_DAÑO_BASE       =   1   # por cada punto de daño hecho a la base

# bono por daño hecho en la ronda anterior
# El atacante recibe el 25% del daño total que hizo en la ronda anterior
# como dinero extra al inicio de la siguiente. Premia la presión sostenida.
FACTOR_BONO_DAÑO_ANTERIOR = 0.25

# Tabla de costos por nombre de clase
# Permite que el código consulte el costo de cualquier pieza por su
# nombre de clase sin necesidad de una cadena de if/elif.
COSTOS = {
    "TorreVigia":    COSTO_TORRE_VIGIA,
    "TorreCanon":    COSTO_TORRE_CANON,
    "TorreSanadora": COSTO_TORRE_SANADORA,
    "Muro":          COSTO_MURO,
    "Tanque":        COSTO_TANQUE,
    "Artilleria":    COSTO_ARTILLERIA,
    "Peon":          COSTO_PEON,
}

# Tabla de recompensas por nombre de clase
RECOMPENSAS_DEFENSOR = {
    "Peon":      RECOMPENSA_ELIMINAR_PEON,
    "Artilleria": RECOMPENSA_ELIMINAR_ARTILLERIA,
    "Tanque":    RECOMPENSA_ELIMINAR_TANQUE,
}

RECOMPENSAS_ATACANTE = {
    "Muro":          RECOMPENSA_DESTRUIR_MURO,
    "TorreVigia":    RECOMPENSA_DESTRUIR_TORRE,
    "TorreCanon":    RECOMPENSA_DESTRUIR_TORRE,
    "TorreSanadora": RECOMPENSA_DESTRUIR_TORRE,
}


# Billetera

class Billetera:
    """
    Administra el dinero de un jugador durante la partida.
    Encapsula las reglas de tope y validación de compras para que
    ninguna vista ni controlador tenga que aplicarlas manualmente.
    """

    def __init__(self, saldo_inicial=DINERO_INICIAL):
        self.saldo = saldo_inicial
        self.daño_hecho_esta_ronda = 0   # acumulado para calcular bono siguiente

    def puede_comprar(self, costo):
        """Devuelve True si el jugador tiene suficiente saldo."""
        return self.saldo >= costo

    def comprar(self, nombre_pieza):
        """
        Descuenta el costo de una pieza del saldo.
        Devuelve (exito: bool, mensaje: str).
        """
        costo = COSTOS.get(nombre_pieza)
        if costo is None:
            return False, f"Pieza desconocida: {nombre_pieza}"
        if not self.puede_comprar(costo):
            return False, f"Saldo insuficiente (tienes ${self.saldo}, necesitas ${costo})"
        self.saldo -= costo
        return True, f"Comprado {nombre_pieza} por ${costo}. Saldo: ${self.saldo}"

    def ganar(self, cantidad):
        """
        Suma dinero al saldo respetando el tope máximo.
        Devuelve el monto real acreditado (puede ser menor que cantidad
        si se alcanzó el tope).
        """
        espacio = DINERO_MAXIMO - self.saldo
        acreditado = min(cantidad, espacio)
        self.saldo += acreditado
        return acreditado

    def aplicar_bono_ronda(self):
        """
        Suma el bono fijo de inicio de ronda.
        Llamar al inicio de cada ronda desde la segunda en adelante.
        """
        return self.ganar(BONO_POR_RONDA)

    def registrar_daño(self, cantidad):
        """
        Acumula el daño hecho esta ronda para calcular el bono
        de la ronda siguiente. Solo relevante para el atacante.
        """
        self.daño_hecho_esta_ronda += cantidad

    def calcular_bono_daño(self):
        """
        Calcula el bono por daño de la ronda anterior.
        Se llama al iniciar una nueva ronda ANTES de reiniciar el contador.
        """
        bono_crudo = int(self.daño_hecho_esta_ronda * FACTOR_BONO_DAÑO_ANTERIOR)
        return min(bono_crudo, 200)  # tope de bono por daño

    def reiniciar_daño_ronda(self):
        """Resetea el contador de daño al terminar cada ronda."""
        self.daño_hecho_esta_ronda = 0

    def resumen(self):
        return f"Saldo: ${self.saldo} | Daño acumulado: {self.daño_hecho_esta_ronda}"

    def __repr__(self):
        return f"Billetera(${self.saldo})"


# Controlador económico 

class EconomiaController:
    """
    Aplica las recompensas económicas durante el combate.
    El motor de combate llama a estos métodos cada vez que ocurre
    un evento relevante (unidad eliminada, torre destruida, daño a la base).
    Mantiene separada la lógica económica de la lógica de combate.
    """

    def __init__(self, billetera_defensor, billetera_atacante):
        self.defensor = billetera_defensor
        self.atacante = billetera_atacante

    # Recompesas para el defensor

    def unidad_eliminada(self, unidad):
        """
        El defensor gana dinero cuando una torre elimina una unidad.
        Devuelve el monto ganado.
        """
        monto = RECOMPENSAS_DEFENSOR.get(type(unidad).__name__, 0)
        acreditado = self.defensor.ganar(monto)
        return acreditado

    # Recompensas para el atacante

    def defensa_destruida(self, defensa):
        """
        El atacante gana dinero al destruir un muro o una torre.
        Devuelve el monto ganado.
        """
        monto = RECOMPENSAS_ATACANTE.get(type(defensa).__name__, 0)
        acreditado = self.atacante.ganar(monto)
        return acreditado

    def daño_a_base(self, cantidad_daño):
        """
        El atacante gana dinero proporcional al daño hecho a la base
        central. También lo acumula para el bono de la siguiente ronda.
        Devuelve el monto ganado.
        """
        monto = cantidad_daño * RECOMPENSA_DAÑO_BASE
        acreditado = self.atacante.ganar(monto)
        self.atacante.registrar_daño(cantidad_daño)
        return acreditado

    # Transición de rondas

    def iniciar_nueva_ronda(self):
        """
        Aplica todos los bonos al inicio de una nueva ronda.
        Orden importante: primero calcular el bono de daño anterior
        (antes de reiniciarlo) y luego aplicar el bono fijo.
        """
        # Bono de daño anterior solo para el atacante
        bono_daño = self.atacante.calcular_bono_daño()
        self.atacante.reiniciar_daño_ronda()

        # Bono fijo para ambos
        bono_def = self.defensor.aplicar_bono_ronda()
        bono_atk = self.atacante.aplicar_bono_ronda()

        # Bono de daño se aplica después del bono fijo
        bono_atk_daño = self.atacante.ganar(bono_daño)

        return {
            "defensor": {"bono_ronda": bono_def},
            "atacante": {"bono_ronda": bono_atk, "bono_daño": bono_atk_daño},
        }
