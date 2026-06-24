import tkinter as tk
import pygame
import json
import hashlib
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.mixer.init()

# -----------------------------------------------------------------
# Defensa y Asalto de Base — main.py
# Curso: Introducción a la Programación — ITCR
# Integrantes: Esteban, Dominick Robles
# Descripción: Archivo principal del juego. Contiene toda la lógica,
#              ventanas y clases del programa.
# -----------------------------------------------------------------

# ── Paleta de colores medieval oscura ──
COLOR_FONDO         = "#0d0a07"
COLOR_PIEDRA        = "#1a1510"
COLOR_PIEDRA_2      = "#221c14"
COLOR_ORO           = "#c9a84c"
COLOR_ORO_BRILLANTE = "#f0c060"
COLOR_SANGRE        = "#6b1a1a"
COLOR_TEXTO         = "#d4c5a9"
COLOR_TEXTO_TENUE   = "#6b5e4a"
COLOR_SEPARADOR     = "#3a2e1e"
COLOR_ENTRY_FONDO   = "#140f09"
COLOR_ENTRY_BORDE   = "#4a3820"

# ── Tipografías ──
FUENTE_TITULO    = ("Georgia", 48, "bold")
FUENTE_SUBTITULO = ("Georgia", 13, "italic")
FUENTE_BOTON     = ("Courier", 14, "bold")
FUENTE_LABEL     = ("Courier", 11)
FUENTE_PEQUENA   = ("Courier", 8)
FUENTE_ENTRY     = ("Courier", 13)


# -----------------------------------------------------------------
# SECCIÓN 1 — UTILIDADES
# Clase con funciones compartidas por todas las pantallas:
# fondo, parpadeo, hover y música.
# -----------------------------------------------------------------
class Utilidades:

    # ── Fondo ──

    def dibujar_fondo_piedra(self, canvas, ancho, alto):
        # Dibuja la cuadrícula de piedra medieval alternando dos colores
        tam = 36
        for fila in range(0, alto, tam):
            for col in range(0, ancho, tam):
                if (fila // tam + col // tam) % 2 == 0:
                    color = COLOR_PIEDRA
                else:
                    color = COLOR_PIEDRA_2
                canvas.create_rectangle(col, fila, col + tam, fila + tam,
                                        fill=color, outline="#0f0c08", width=1)

    def borde_dorado(self, canvas, ancho, alto):
        # Dibuja el borde dorado superior/inferior y esquinas rojas
        canvas.create_rectangle(0, 0, ancho, 5, fill=COLOR_ORO, outline="")
        canvas.create_rectangle(0, alto - 5, ancho, alto, fill=COLOR_ORO, outline="")
        for x in [0, ancho - 12]:
            for y in [0, alto - 12]:
                canvas.create_rectangle(x, y, x + 12, y + 12,
                                        fill=COLOR_SANGRE, outline=COLOR_ORO)

    # ── Animaciones ──

    def parpadeo(self, label, estado, color_on, color_off, ms=700):
        # Alterna el color del label entre color_on y color_off cada ms milisegundos
        label.config(fg=color_on if estado[0] else color_off)
        estado[0] = not estado[0]
        label.after(ms, self.parpadeo, label, estado, color_on, color_off, ms)

    # ── Interacción ──

    def hover(self, boton, color_normal, color_hover):
        # Aplica efecto hover: cambia color al entrar y salir el mouse
        boton.bind("<Enter>", lambda e: boton.config(fg=color_hover))
        boton.bind("<Leave>", lambda e: boton.config(fg=color_normal))

    def boton_medieval(self, padre, texto, comando, color=COLOR_TEXTO):
        # Crea un botón con el estilo medieval estándar y le aplica hover
        btn = tk.Button(
            padre, text=texto, bg=COLOR_FONDO, fg=color,
            font=FUENTE_BOTON, relief=tk.FLAT, bd=0,
            activebackground=COLOR_FONDO, activeforeground=COLOR_ORO_BRILLANTE,
            cursor="hand2", command=comando
        )
        self.hover(btn, color, COLOR_ORO_BRILLANTE)
        return btn

    # ── Música ──

    def tocar_musica_menu(self, estado_musica):
        # Carga y reproduce la música del menú en loop si no está ya sonando
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "assets", "musica", "menu.mp3")
        if estado_musica["actual"] != "menu" and os.path.exists(ruta):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play(-1)
            estado_musica["actual"]  = "menu"
            estado_musica["activa"]  = True
            estado_musica["pausada"] = False

    def alternar_musica(self, estado_musica):
        # Pausa o reanuda la música según el estado actual
        if estado_musica["activa"]:
            pygame.mixer.music.pause()
            estado_musica["activa"]  = False
            estado_musica["pausada"] = True
        elif estado_musica["pausada"]:
            pygame.mixer.music.unpause()
            estado_musica["activa"]  = True
            estado_musica["pausada"] = False

    def parar_musica(self, estado_musica):
        # Detiene completamente la música
        pygame.mixer.music.stop()
        estado_musica["activa"]  = False
        estado_musica["pausada"] = False
        estado_musica["actual"]  = ""

