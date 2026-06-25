"""
prueba_mapa.py
-------------------------------------------------------------------
ESPACIO DE PRUEBA — Defensa y Asalto de Base
-------------------------------------------------------------------
Este archivo NO es parte del flujo principal del juego (main.py).
Es un sandbox aislado para probar visualmente que las clases de
Estructuras.py, Base_central.py y Tropas.py funcionan bien juntas
sobre una cuadrícula, antes de integrarlas al juego real (login,
menú, facciones, etc).

Requiere en la misma carpeta:
    - Estructuras.py   (Torre, TorreVigia, TorreCanon, TorreSanadora, Muro)
    - Base_central.py  (BaseCentral)
    - Tropas.py        (Unidad)

NOTA sobre Tropas.py:
    A la clase Unidad le faltan algunos métodos que sí tiene Torre
    (esta_viva, recibir_daño, curar, avanzar_turno/activar_habilidad,
    resumen, __repr__), y todavía no hay subclases concretas (Soldado,
    Tanque, Unidad Rápida). Mientras tu compañero termina eso, se
    agrega un parche TEMPORAL en la SECCIÓN 1, bien marcado. Cuando
    Tropas.py esté completo, hay que borrar la SECCIÓN 1 y simplemente
    importar las clases reales desde Tropas.py.

Cómo se usa:
    - Elegís una herramienta del panel izquierdo (torre, muro o unidad).
    - Click izquierdo en el mapa para colocarla.
    - Click derecho (o la herramienta "Borrar") para quitar algo.
    - Las torres y muros solo van en la zona verde (zona de defensa,
      alrededor de la base). Las unidades solo van fuera de esa zona
      (zona de ataque), y deben "marchar" hacia la base.
    - "Simular turno de combate" resuelve un turno completo: las
      unidades avanzan o atacan, las torres responden, y se revisan
      las condiciones de victoria.
-------------------------------------------------------------------
"""

import tkinter as tk

from Estructuras import Torre, TorreVigia, TorreCanon, TorreSanadora, Muro
from Base_central import BaseCentral
from Tropas import Unidad


# -------------------------------------------------------------------
# SECCIÓN 1 — PARCHE TEMPORAL DE TROPAS (solo para pruebas)
# Agrega los métodos que le faltan a Unidad y crea 3 subclases de
# ejemplo. BORRAR este bloque cuando Tropas.py esté completo y usar
# las clases reales directamente.
# -------------------------------------------------------------------
class _TropaPrueba(Unidad):
    """Mixin temporal: completa lo que le falta a Unidad para poder probarla."""

    def esta_viva(self):
        return self.vida_actual > 0

    def recibir_daño(self, cantidad):
        self.vida_actual = max(0, self.vida_actual - cantidad)

    def curar(self, cantidad):
        self.vida_actual = min(self.vida_maxima, self.vida_actual + cantidad)

    def avanzar_turno(self, contexto):
        self._turno_actual += 1
        if self._turno_actual >= self.turnos_para_habilidad:
            self.activar_habilidad(contexto)
            self._turno_actual = 0

    def activar_habilidad(self, contexto):
        pass  # cada subclase de prueba la sobreescribe

    def resumen(self):
        return (f"[{self.nombre}] Vida: {self.vida_actual}/{self.vida_maxima} | "
                f"Daño: {self.daño} | Vel: {self.velocidad}")

    def __repr__(self):
        estado = "vivo" if self.esta_viva() else "muerto"
        return f"{self.nombre}({estado}, {self.vida_actual}hp)"


class SoldadoPrueba(_TropaPrueba):
    """Unidad básica: estadísticas normales, costo bajo."""
    STATS = {"vida_maxima": 30, "daño": 8, "velocidad": 1,
              "alcance": 1, "costo": 0, "turnos_para_habilidad": 3}

    def __init__(self):
        super().__init__(nombre="Soldado", **self.STATS)

    def activar_habilidad(self, contexto):
        objetivo = contexto.get("objetivo")
        if objetivo and getattr(objetivo, "vida_actual", 0) > 0:
            self.atacar(objetivo)
            contexto["log"] = f"{self.nombre} usa Ataque Doble"


class TanquePrueba(_TropaPrueba):
    """Mucha vida, movimiento lento, escudo temporal."""
    STATS = {"vida_maxima": 70, "daño": 10, "velocidad": 1,
              "alcance": 1, "costo": 0, "turnos_para_habilidad": 4}

    def __init__(self):
        super().__init__(nombre="Tanque", **self.STATS)
        self.escudo_activo = False

    def activar_habilidad(self, contexto):
        self.escudo_activo = True
        contexto["log"] = f"{self.nombre} activa Escudo Temporal"

    def recibir_daño(self, cantidad):
        if self.escudo_activo:
            self.escudo_activo = False
            return
        super().recibir_daño(cantidad)


class UnidadRapidaPrueba(_TropaPrueba):
    """Poco daño, pero se mueve más rápido."""
    STATS = {"vida_maxima": 18, "daño": 5, "velocidad": 2,
              "alcance": 1, "costo": 0, "turnos_para_habilidad": 3}

    def __init__(self):
        super().__init__(nombre="Unidad Rápida", **self.STATS)

    def activar_habilidad(self, contexto):
        self.velocidad *= 2
        contexto["log"] = f"{self.nombre} usa Aumento de Velocidad"


# -------------------------------------------------------------------
# SECCIÓN 2 — MAPA (cuadrícula con zona de defensa y zona de ataque)
# -------------------------------------------------------------------
class Mapa:
    FILAS, COLUMNAS = 15, 15
    TAM_CELDA = 45
    MARGEN = 36

    # Bloque de celdas alrededor de la base donde el defensor puede construir
    ZONA_DEFENSA = {(f, c) for f in range(7, 15) for c in range(5, 15)}

    COLOR_ZONA_DEFENSA = "#16241a"
    COLOR_ZONA_ATAQUE  = "#1a1510"
    COLOR_LINEA        = "#3a2e1e"
    COLOR_BASE         = "#f0c060"

    COLORES = {
        Muro:               "#5a4a35",
        TorreVigia:         "#4a8cc9",
        TorreCanon:         "#c9794a",
        TorreSanadora:      "#5a9c4a",
        SoldadoPrueba:      "#c9a84c",
        TanquePrueba:       "#8a3a3a",
        UnidadRapidaPrueba: "#4ac9c0",
    }
    ETIQUETAS = {
        Muro:               "M",
        TorreVigia:         "TV",
        TorreCanon:         "TC",
        TorreSanadora:      "TS",
        SoldadoPrueba:      "S",
        TanquePrueba:       "T",
        UnidadRapidaPrueba: "R",
    }

    def __init__(self, canvas):
        self.canvas = canvas
        self.base = BaseCentral()
        self.ocupantes = {celda: self.base for celda in self.base.celdas}
        self.unidades = []

    # ── Consultas ──

    def es_zona_defensa(self, fila, columna):
        return (fila, columna) in self.ZONA_DEFENSA

    def esta_libre(self, fila, columna):
        return (fila, columna) not in self.ocupantes

    def puede_colocar(self, fila, columna, clase):
        if not self.esta_libre(fila, columna):
            return False, "Esa celda ya está ocupada."
        en_zona = self.es_zona_defensa(fila, columna)
        if issubclass(clase, (Torre, Muro)) and not en_zona:
            return False, "Las torres y muros solo van en la zona de defensa (verde)."
        if issubclass(clase, Unidad) and en_zona:
            return False, "Las unidades atacantes solo van en la zona de ataque (fuera del verde)."
        return True, ""

    def estructuras(self):
        return [o for o in self.ocupantes.values() if isinstance(o, (Torre, Muro))]

    def torres(self):
        return [o for o in self.ocupantes.values() if isinstance(o, Torre)]

    def contar(self):
        torres = sum(1 for o in self.ocupantes.values() if isinstance(o, Torre))
        muros = sum(1 for o in self.ocupantes.values() if isinstance(o, Muro))
        return torres, muros, len(self.unidades)

    def celda_desde_click(self, x, y):
        col = int((x - self.MARGEN) // self.TAM_CELDA)
        fila = int((y - self.MARGEN) // self.TAM_CELDA)
        if 0 <= fila < self.FILAS and 0 <= col < self.COLUMNAS:
            return fila, col
        return None

    # ── Colocación y remoción ──

    def colocar(self, fila, columna, objeto):
        puede, _ = self.puede_colocar(fila, columna, type(objeto))
        if not puede:
            return False
        objeto.fila, objeto.columna = fila, columna
        self.ocupantes[(fila, columna)] = objeto
        if isinstance(objeto, Unidad):
            self.unidades.append(objeto)
        return True

    def quitar(self, fila, columna):
        objeto = self.ocupantes.get((fila, columna))
        if objeto is None or objeto is self.base:
            return None
        del self.ocupantes[(fila, columna)]
        if objeto in self.unidades:
            self.unidades.remove(objeto)
        return objeto

    def limpiar(self):
        # Quita todo del mapa salvo la base central
        self.ocupantes = {c: self.base for c in self.base.celdas}
        self.unidades = []

    def limpiar_muertos(self):
        for pos, objeto in list(self.ocupantes.items()):
            if objeto is self.base:
                continue
            vivo = objeto.esta_viva() if hasattr(objeto, "esta_viva") else objeto.esta_vivo()
            if not vivo:
                del self.ocupantes[pos]
                if objeto in self.unidades:
                    self.unidades.remove(objeto)

    # ── Dibujo ──

    def dibujar(self):
        self.canvas.delete("all")
        m, t = self.MARGEN, self.TAM_CELDA

        for i in range(self.FILAS):
            self.canvas.create_text(m / 2, m + i * t + t / 2, text=str(i),
                                     fill="#6b5e4a", font=("Courier", 8))
            self.canvas.create_text(m + i * t + t / 2, m / 2, text=str(i),
                                     fill="#6b5e4a", font=("Courier", 8))

        for fila in range(self.FILAS):
            for col in range(self.COLUMNAS):
                x0, y0 = m + col * t, m + fila * t
                x1, y1 = x0 + t, y0 + t

                fondo = (self.COLOR_ZONA_DEFENSA if self.es_zona_defensa(fila, col)
                         else self.COLOR_ZONA_ATAQUE)

                objeto = self.ocupantes.get((fila, col))

                if objeto is self.base:
                    color, etiqueta = self.COLOR_BASE, "B"
                elif objeto is not None:
                    color = self.COLORES.get(type(objeto), "#888888")
                    etiqueta = self.ETIQUETAS.get(type(objeto), "?")
                else:
                    color, etiqueta = fondo, ""

                self.canvas.create_rectangle(x0, y0, x1, y1,
                                              fill=color, outline=self.COLOR_LINEA)

                if etiqueta:
                    self.canvas.create_text(x0 + t / 2, y0 + t / 2 - 5,
                                             text=etiqueta, fill="white",
                                             font=("Courier", 8, "bold"))
                if objeto is not None and objeto is not self.base:
                    self.canvas.create_text(x0 + t / 2, y0 + t / 2 + 9,
                                             text=str(objeto.vida_actual),
                                             fill="white", font=("Courier", 7))


# -------------------------------------------------------------------
# SECCIÓN 3 — MOTOR DE COMBATE (resuelve un turno completo)
# -------------------------------------------------------------------
class MotorCombate:

    def __init__(self, mapa, log_callback):
        self.mapa = mapa
        self.log = log_callback

    def jugar_turno(self):
        self._turno_unidades()
        self._turno_torres()
        self.mapa.limpiar_muertos()
        return self._revisar_victoria()

    # ── Fase de las unidades atacantes ──

    def _turno_unidades(self):
        for unidad in list(self.mapa.unidades):
            if unidad.esta_viva():
                self._mover_o_atacar(unidad)

    def _mover_o_atacar(self, unidad):
        celda_base = min(self.mapa.base.celdas,
                          key=lambda c: max(abs(c[0] - unidad.fila),
                                             abs(c[1] - unidad.columna)))

        if unidad.puede_atacar_a(*celda_base):
            daño = unidad.atacar(self.mapa.base)
            self.log(f"⚔ {unidad.nombre} ataca la Base Central: {daño} daño "
                      f"(vida base: {self.mapa.base.vida_actual})")
            self._intentar_habilidad(unidad, self.mapa.base)
            return

        objetivo = self._estructura_en_alcance(unidad)
        if objetivo:
            daño = unidad.atacar(objetivo)
            self.log(f"⚔ {unidad.nombre} ataca {objetivo.nombre}: "
                      f"{daño} daño (vida: {objetivo.vida_actual})")
            self._intentar_habilidad(unidad, objetivo)
            return

        self._avanzar(unidad, celda_base)

    def _estructura_en_alcance(self, unidad):
        for estructura in self.mapa.estructuras():
            if unidad.puede_atacar_a(estructura.fila, estructura.columna):
                return estructura
        return None

    def _avanzar(self, unidad, celda_base):
        fila_obj, col_obj = celda_base
        for _ in range(unidad.velocidad):
            df = (fila_obj > unidad.fila) - (fila_obj < unidad.fila)
            dc = (col_obj > unidad.columna) - (col_obj < unidad.columna)
            nueva_fila, nueva_col = unidad.fila + df, unidad.columna + dc

            if (nueva_fila, nueva_col) == (unidad.fila, unidad.columna):
                break

            if self.mapa.esta_libre(nueva_fila, nueva_col):
                del self.mapa.ocupantes[(unidad.fila, unidad.columna)]
                unidad.fila, unidad.columna = nueva_fila, nueva_col
                self.mapa.ocupantes[(nueva_fila, nueva_col)] = unidad
            else:
                break

        self.log(f"➤ {unidad.nombre} avanza a ({unidad.fila}, {unidad.columna})")

    def _intentar_habilidad(self, unidad, objetivo):
        contexto = {"objetivo": objetivo, "log": None}
        unidad.avanzar_turno(contexto)
        if contexto.get("log"):
            self.log("✦ " + contexto["log"])

    # ── Fase de las torres defensoras ──

    def _turno_torres(self):
        for torre in self.mapa.torres():
            if not torre.esta_viva():
                continue

            en_rango = [u for u in self.mapa.unidades
                        if u.esta_viva() and torre.puede_atacar_a(u.fila, u.columna)]

            if en_rango:
                objetivo = min(en_rango, key=lambda u: u.vida_actual)
                daño = torre.atacar(objetivo)
                if daño:
                    self.log(f"🛡 {torre.nombre} ataca a {objetivo.nombre}: "
                              f"{daño} daño (vida: {objetivo.vida_actual})")

            torres_cercanas = [t for t in self.mapa.torres()
                                if t is not torre and t.esta_viva()
                                and torre.puede_atacar_a(t.fila, t.columna)]

            contexto = {"unidades_en_rango": en_rango,
                        "torres_cercanas": torres_cercanas, "log": None}
            torre.avanzar_turno(contexto)
            if contexto.get("log"):
                self.log("✦ " + contexto["log"])

    # ── Condición de victoria ──

    def _revisar_victoria(self):
        if not self.mapa.base.esta_viva():
            return "atacante"
        if not self.mapa.unidades:
            return "defensor"
        return None


# -------------------------------------------------------------------
# SECCIÓN 4 — INTERFAZ (panel agrupado + barra de estado)
# -------------------------------------------------------------------
class ItemHerramienta(tk.Frame):
    """Botón del panel: cuadrado de color + nombre. Se resalta al seleccionarse."""

    def __init__(self, parent, texto, color, on_click):
        super().__init__(parent, bg="#1a1510", highlightthickness=2,
                          highlightbackground="#3a2e1e", cursor="hand2")
        swatch = tk.Frame(self, width=20, height=20, bg=color)
        swatch.pack(side="left", padx=(8, 8), pady=6)
        swatch.pack_propagate(False)

        label = tk.Label(self, text=texto, bg="#1a1510", fg="#d4c5a9",
                          font=("Courier", 9), anchor="w")
        label.pack(side="left", fill="x", expand=True, pady=6)

        for widget in (self, swatch, label):
            widget.bind("<Button-1>", lambda e: on_click())

    def marcar(self, activo):
        self.config(highlightbackground="#f0c060" if activo else "#3a2e1e",
                    highlightthickness=3 if activo else 2)


class VentanaPrueba:

    TORRES = [
        ("Torre Vigía",  TorreVigia,         "#4a8cc9"),
        ("T. Cañón",     TorreCanon,         "#c9794a"),
        ("T. Sanadora",  TorreSanadora,      "#5a9c4a"),
        ("Muro",         Muro,               "#5a4a35"),
    ]
    UNIDADES = [
        ("Soldado",        SoldadoPrueba,        "#c9a84c"),
        ("Tanque",          TanquePrueba,         "#8a3a3a"),
        ("Unidad Rápida",   UnidadRapidaPrueba,   "#4ac9c0"),
    ]

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Espacio de Prueba — Mapa, Estructuras y Tropas")
        self.ventana.config(bg="#0d0a07")

        self.herramienta_actual = None
        self.items = []
        self.nombres = {"borrar": "Borrar"}
        for texto, clase, _color in self.TORRES + self.UNIDADES:
            self.nombres[clase] = texto

        self._construir_layout()
        self._nueva_partida()

    def _construir_layout(self):
        ancho_canvas = Mapa.MARGEN * 2 + Mapa.COLUMNAS * Mapa.TAM_CELDA
        alto_canvas  = Mapa.MARGEN * 2 + Mapa.FILAS * Mapa.TAM_CELDA

        contenedor = tk.Frame(self.ventana, bg="#0d0a07")
        contenedor.pack(padx=10, pady=10)

        panel = tk.Frame(contenedor, bg="#140f09", width=220)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        self._seccion(panel, "TORRES — DEFENSAS")
        for texto, clase, color in self.TORRES:
            self._agregar_item(panel, texto, clase, color)

        self._seccion(panel, "UNIDADES — ATACANTES")
        for texto, clase, color in self.UNIDADES:
            self._agregar_item(panel, texto, clase, color)

        self._seccion(panel, "HERRAMIENTAS")
        self._agregar_item(panel, "Borrar", "borrar", "#6b1a1a")

        tk.Button(panel, text="🗑  Limpiar mapa", command=self._limpiar,
                  bg="#1a1510", fg="#d4c5a9", relief=tk.FLAT,
                  font=("Courier", 9)).pack(fill="x", padx=10, pady=(10, 4))

        self.btn_accion = tk.Button(panel, text="✔  Defensor listo", command=self._accion_fase,bg="#1a1510", fg="#c9a84c", relief=tk.FLAT,font=("Courier", 9))
        self.btn_accion.pack(fill="x", padx=10, pady=4)

        tk.Button(panel, text="↺  Reiniciar prueba", command=self._nueva_partida,
                  bg="#1a1510", fg="#d4c5a9", relief=tk.FLAT,
                  font=("Courier", 9)).pack(fill="x", padx=10, pady=(4, 12))

        self.canvas = tk.Canvas(contenedor, width=ancho_canvas, height=alto_canvas,
                                 bg="#0d0a07", highlightthickness=0)
        self.canvas.grid(row=0, column=1)
        self.canvas.bind("<Button-1>", self._click_izquierdo)
        self.canvas.bind("<Button-3>", self._click_derecho)

        self.barra_estado = tk.Label(self.ventana, text="", bg="#140f09", fg="#d4c5a9",
                                      font=("Courier", 9), anchor="w", justify="left")
        self.barra_estado.pack(fill="x", padx=10, pady=(0, 6))

        tk.Label(self.ventana, text="Registro:", bg="#0d0a07", fg="#6b5e4a",
                 font=("Courier", 8)).pack(anchor="w", padx=10)
        self.texto_log = tk.Text(self.ventana, height=6, bg="#140f09", fg="#d4c5a9",
                                  font=("Courier", 8), state="disabled")
        self.texto_log.pack(fill="x", padx=10, pady=(0, 10))

    def _seccion(self, panel, titulo):
        tk.Label(panel, text=titulo, bg="#140f09", fg="#c9a84c",
                 font=("Courier", 9, "bold")).pack(anchor="w", padx=10, pady=(12, 4))

    def _agregar_item(self, panel, texto, valor, color):
        item = ItemHerramienta(panel, texto, color, lambda v=valor: self._seleccionar(v))
        item.pack(fill="x", padx=10, pady=2)
        self.items.append((item, valor))

    def _seleccionar(self, valor):
        self.herramienta_actual = valor
        for item, v in self.items:
            item.marcar(v == valor)
        self._actualizar_barra()

    # ── Partida ──

    def _nueva_partida(self):
        self.fase = "defensor"
        self.mapa = Mapa(self.canvas)
        self.motor = MotorCombate(self.mapa, self._log)
        self._limpiar_log()
        self._log("Nueva prueba iniciada. Torres/muros: zona verde. "
                  "Unidades: fuera de la zona verde.")
        if self.items:
            self._seleccionar(self.items[0][1])
        self.mapa.dibujar()
        self._actualizar_barra()

    def _limpiar(self):
        self.mapa.limpiar()
        self.mapa.dibujar()
        self._log("🗑 Mapa limpiado (la base central se mantiene).")
        self._actualizar_barra()

    def _siguiente_turno(self):
        if not self.mapa.unidades:
            self._log("⚠ No hay unidades en el mapa para simular combate.")
            return
        resultado = self.motor.jugar_turno()
        self.mapa.dibujar()
        self._actualizar_barra()
        if resultado == "atacante":
            self._log("🏆 ¡Base destruida! Gana el ATACANTE.")
            return
        elif resultado == "defensor":
            self._log("🏆 ¡Todas las unidades eliminadas! Gana el DEFENSOR.")
            return
        self._actualizar_panel_por_fase()
    # Si no terminó, programa el siguiente turno automáticamente en 800 ms
        self.ventana.after(800, self._siguiente_turno)

    def _accion_fase(self):
        if self.fase == "defensor":
        # Pasa al atacante: oculta torres/muros, muestra solo unidades
            self.fase = "atacante"
            self.btn_accion.config(text="⚔  Iniciar combate", fg="#c9794a")
            self._log("✔ Defensor listo. Ahora el Atacante coloca sus unidades.")
            self._actualizar_panel_por_fase()

        elif self.fase == "atacante":
        # Inicia el combate automático
            if not self.mapa.unidades:
                self._log("⚠ El atacante no colocó ninguna unidad.")
                return
            self.fase = "combate"
            self.btn_accion.config(state="disabled")
            self._log("⚔ ¡Combate iniciado!")
            self._siguiente_turno()
    
    def _actualizar_panel_por_fase(self):
    # Durante fase atacante y combate: oculta torres/muros, muestra unidades
    # Durante fase defensor: muestra todo
        for item, valor in self.items:
            es_estructura = valor in (TorreVigia, TorreCanon, TorreSanadora, Muro)
            es_unidad = valor in (SoldadoPrueba, TanquePrueba, UnidadRapidaPrueba)

        if self.fase == "defensor":
            item.pack(fill="x", padx=10, pady=2)
        elif self.fase in ("atacante", "combate"):
            if es_estructura:
                item.pack_forget()  # oculta torres y muros
            else:
                item.pack(fill="x", padx=10, pady=2)  # muestra unidades y borrar

    # ── Clicks ──

    def _click_izquierdo(self, evento):
        if self.fase == "combate" and self.herramienta_actual != "borrar":
        # Durante combate solo el atacante puede colocar unidades
            if self.herramienta_actual not in (SoldadoPrueba, TanquePrueba, UnidadRapidaPrueba):
                return
        celda = self.mapa.celda_desde_click(evento.x, evento.y)
        if celda is None or self.herramienta_actual is None:
            return

        if self.herramienta_actual == "borrar":
            if self.mapa.quitar(*celda):
                self.mapa.dibujar()
                self._actualizar_barra()
            return

        puede, motivo = self.mapa.puede_colocar(*celda, self.herramienta_actual)
        if not puede:
            self._log(f"⚠ {motivo}")
            return

        self.mapa.colocar(*celda, self.herramienta_actual())
        self.mapa.dibujar()
        self._actualizar_barra()

    def _click_derecho(self, evento):
        celda = self.mapa.celda_desde_click(evento.x, evento.y)
        if celda and self.mapa.quitar(*celda):
            self.mapa.dibujar()
            self._actualizar_barra()

    # ── Utilidades ──

    def _actualizar_barra(self):
        torres, muros, unidades = self.mapa.contar()
        nombre = self.nombres.get(self.herramienta_actual, "Ninguna")
        self.barra_estado.config(
            text=f"Torres: {torres}   Muros: {muros}   Unidades: {unidades}   |   "
                 f"Selección: {nombre}   |   Vida base: "
                 f"{self.mapa.base.vida_actual}/{self.mapa.base.vida_maxima}   |   "
                 f"Zona defensa: verde   Zona ataque: gris"
        )

    def _log(self, mensaje):
        self.texto_log.config(state="normal")
        self.texto_log.insert("end", mensaje + "\n")
        self.texto_log.see("end")
        self.texto_log.config(state="disabled")

    def _limpiar_log(self):
        self.texto_log.config(state="normal")
        self.texto_log.delete("1.0", "end")
        self.texto_log.config(state="disabled")
    
    


# -------------------------------------------------------------------
# ARRANQUE DEL ESPACIO DE PRUEBA
# -------------------------------------------------------------------
if __name__ == "__main__":
    ventana = tk.Tk()
    app = VentanaPrueba(ventana)
    ventana.mainloop()