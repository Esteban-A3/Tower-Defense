import tkinter as tk
import pygame
import json
import hashlib
import os
import random
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.mixer.init()

# -----------------------------------------------------------------
# Defensa y Asalto de Base — main.py
# Curso: Introducción a la Programación — ITCR
# Integrantes: Esteban, Dominick Robles
# Descripción: Archivo principal del juego. Contiene toda la lógica,
#              ventanas y clases del programa.
# -----------------------------------------------------------------

#Paleta de colores
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

#Tipografías
FUENTE_TITULO    = ("Georgia", 48, "bold")
FUENTE_SUBTITULO = ("Georgia", 13, "italic")
FUENTE_BOTON     = ("Courier", 14, "bold")
FUENTE_LABEL     = ("Courier", 11)
FUENTE_PEQUENA   = ("Courier", 8)
FUENTE_ENTRY     = ("Courier", 13)


# 
# SECCIÓN 1 — UTILIDADES
# Clase con funciones compartidas por todas las pantallas:
# fondo, parpadeo, hover y música.
class Utilidades:

    # Fondo 
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

    # Animaciones
    def parpadeo(self, label, estado, color_on, color_off, ms=700):
        # Alterna el color del label entre color_on y color_off cada ms milisegundos
        label.config(fg=color_on if estado[0] else color_off)
        estado[0] = not estado[0]
        label.after(ms, self.parpadeo, label, estado, color_on, color_off, ms)

    # Interacción
    def hover(self, boton, color_normal, color_hover):
        # Aplica efecto hover: cambia color al entrar y salir el mouse
        boton.bind("<Enter>", lambda e: boton.config(fg=color_hover))
        boton.bind("<Leave>", lambda e: boton.config(fg=color_normal))

    def boton_medieval(self, padre, texto, comando, color=COLOR_TEXTO):
        # Crea un botón con el estilo medieval estándar y le aplica hover
        btn = tk.Button(padre, text=texto, bg=COLOR_FONDO, fg=color,font=FUENTE_BOTON, relief=tk.FLAT, bd=0, activebackground=COLOR_FONDO, activeforeground=COLOR_ORO_BRILLANTE,
            cursor="hand2", command=comando)
        self.hover(btn, color, COLOR_ORO_BRILLANTE)
        return btn

    # Música
    def tocar_musica_menu(self, estado_musica):
        # Carga y reproduce la música del menú en loop si no está ya sonando
        ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Sound", "Menu", "Tower0.mp3")
        if estado_musica["actual"] != "menu" and os.path.exists(ruta):
            pygame.mixer.music.stop()
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play(-1)
            estado_musica["actual"]  = "menu"
            estado_musica["activa"]  = True
            estado_musica["pausada"] = False

    def tocar_musica_juego(self, estado_musica):
        # Carga y reproduce en loop una pista aleatoria de las 3 disponibles
        # para la fase de partida (construcción + combate)
        carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)),"Sound", "in_game")
        pistas  = ["Tower1.mp3", "Tower2.mp3", "Tower3.mp3"]

        if estado_musica["actual"] != "juego":
            ruta = os.path.join(carpeta, random.choice(pistas))
            if os.path.exists(ruta):
                pygame.mixer.music.stop()
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.play(-1)
                estado_musica["actual"]  = "juego"
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


# SECCIÓN 2 — GESTOR DE USUARIOS
# Clase que maneja toda la lógica de registro, login y ranking.
# Lee y escribe en un archivo JSON. No depende de Tkinter.
class GestorUsuarios:
    ARCHIVO = "usuarios.json"

    def __init__(self):
        # Si no existe el archivo lo crea vacío
        if not os.path.exists(self.ARCHIVO):
            self._guardar({})

    # Métodos privados de bajo nivel

    def _cargar(self):
        # Lee el archivo JSON y retorna el diccionario de usuarios
        try:
            with open(self.ARCHIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _guardar(self, datos):
        # Escribe el diccionario en el archivo JSON con sangría legible
        with open(self.ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def _hashear(self, contrasena):
        # Retorna el hash SHA-256 de la contraseña (nunca guardamos texto plano)
        return hashlib.sha256(contrasena.encode()).hexdigest()

    # Métodos públicos

    def registrar(self, nombre, contrasena):
        # Registra un usuario nuevo. Retorna (True, msg) o (False, msg).
        if len(nombre.strip()) < 3:
            return False, "El nombre debe tener al menos 3 caracteres."
        if len(contrasena) < 4:
            return False, "La contraseña debe tener al menos 4 caracteres."

        datos = self._cargar()

        if nombre in datos:
            return False, "Ese nombre de usuario ya existe."

        datos[nombre] = {
            "contrasena"        : self._hashear(contrasena),
            "victorias_defensor": 0,
            "victorias_atacante": 0
        }
        self._guardar(datos)
        return True, "¡Cuenta creada exitosamente!"

    def iniciar_sesion(self, nombre, contrasena):
        # Valida credenciales. Retorna (True, datos) o (False, msg).
        datos = self._cargar()

        if nombre not in datos:
            return False, "Usuario no encontrado."

        if datos[nombre]["contrasena"] != self._hashear(contrasena):
            return False, "Contraseña incorrecta."

        return True, datos[nombre]

    def actualizar_victorias(self, nombre, rol):
        # Suma 1 victoria al rol indicado: 'defensor' o 'atacante'
        datos = self._cargar()
        if nombre in datos and rol in ("defensor", "atacante"):
            datos[nombre][f"victorias_{rol}"] += 1
            self._guardar(datos)

    def obtener_ranking(self, rol, cantidad=5):
        # Retorna lista de (nombre, victorias) ordenada de mayor a menor
        datos = self._cargar()
        clave   = f"victorias_{rol}"
        ranking = [(nombre, info[clave]) for nombre, info in datos.items()]
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking[:cantidad]

# SECCIÓN 3 — PANTALLA INTRO
# Pantalla de inicio del juego: "presiona cualquier tecla".
class PantallaIntro:

    def __init__(self, ventana, utils, estado_musica, ir_a_login):
        self.ventana       = ventana
        self.utils         = utils          # instancia de Utilidades
        self.estado_musica = estado_musica  # dict compartido con toda la app
        self.ir_a_login    = ir_a_login     # callback para navegar al login

    def mostrar(self):
        # Limpia la ventana y construye la pantalla
        for widget in self.ventana.winfo_children():
            widget.destroy()

        self.utils.tocar_musica_menu(self.estado_musica)

        ancho = 900
        alto  = 620

        # ── Canvas de fondo ──
        canvas = tk.Canvas(self.ventana, width=ancho, height=alto,
                           bg=COLOR_FONDO, highlightthickness=0)
        canvas.place(x=0, y=0)
        self.utils.dibujar_fondo_piedra(canvas, ancho, alto)

        # Velo oscuro sobre la cuadrícula para más dramatismo
        canvas.create_rectangle(0, 0, ancho, alto,
                                 fill=COLOR_FONDO, stipple="gray50", outline="")

        # Marco de pergamino decorativo
        canvas.create_rectangle(60, 60, ancho - 60, alto - 60,
                                 fill="", outline=COLOR_SEPARADOR, width=2)
        canvas.create_rectangle(70, 70, ancho - 70, alto - 70,
                                 fill="", outline=COLOR_ORO, width=1)

        self.utils.borde_dorado(canvas, ancho, alto)

        # ── Frame central ──
        frame = tk.Frame(self.ventana, bg=COLOR_FONDO)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Símbolo decorativo superior
        tk.Label(frame, text="⚔  ⚜  ⚔",
                 bg=COLOR_FONDO, fg=COLOR_SANGRE,
                 font=("Georgia", 18)).pack(pady=(0, 14))

        # Título principal con parpadeo
        label_titulo = tk.Label(frame, text="DEFENSA Y ASALTO",
                                 bg=COLOR_FONDO, fg=COLOR_ORO,
                                 font=FUENTE_TITULO)
        label_titulo.pack(pady=(0, 4))
        self.utils.parpadeo(label_titulo, [True], COLOR_ORO, "#7a5e28")

        # Subtítulo
        tk.Label(frame, text="DE BASE",
                 bg=COLOR_FONDO, fg=COLOR_ORO_BRILLANTE,
                 font=("Georgia", 22, "italic")).pack(pady=(0, 20))

        # Separador ornamental
        tk.Label(frame, text="━━━━━━━  ✦  ━━━━━━━",
                 bg=COLOR_FONDO, fg=COLOR_SEPARADOR,
                 font=("Courier", 12)).pack(pady=(0, 12))

        # Descripción
        tk.Label(frame,
                 text="Dos jugadores. Una fortaleza. Solo uno sobrevivirá.",
                 bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,
                 font=FUENTE_SUBTITULO).pack(pady=(0, 40))

        # Texto "presiona cualquier tecla" con parpadeo suave
        label_tecla = tk.Label(frame,
                                text="— Presiona cualquier tecla para comenzar —",
                                bg=COLOR_FONDO, fg=COLOR_TEXTO,
                                font=("Courier", 11))
        label_tecla.pack(pady=(0, 8))
        self.utils.parpadeo(label_tecla, [True], COLOR_TEXTO, COLOR_TEXTO_TENUE, ms=900)

        # Pie de página
        tk.Label(self.ventana,
                 text="ITCR  ·  Introducción a la Programación  ·  2026",
                 bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,
                 font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

        # Bind: cualquier tecla o click avanza al login
        self.ventana.bind("<Key>",      self._avanzar)
        self.ventana.bind("<Button-1>", self._avanzar)

    def _avanzar(self, evento=None):
        # Quita los binds y navega al login
        self.ventana.unbind("<Key>")
        self.ventana.unbind("<Button-1>")
        self.ir_a_login()


# SECCIÓN 4 — PANTALLA LOGIN
# Formulario de inicio de sesión y registro de usuarios.
class PantallaLogin:

    def __init__(self, ventana, utils, gestor, ir_a_menu):
        self.ventana   = ventana
        self.utils     = utils    # instancia de Utilidades
        self.gestor    = gestor   # instancia de GestorUsuarios
        self.ir_a_menu = ir_a_menu  # callback que recibe el usuario logueado
        self._modo     = "login"  # puede ser "login" o "registro"

    def mostrar(self):
        # Limpia la ventana y construye la pantalla
        for widget in self.ventana.winfo_children():
            widget.destroy()

        ancho = 900
        alto  = 620

        # Canvas de fondo
        canvas = tk.Canvas(self.ventana, width=ancho, height=alto,
                           bg=COLOR_FONDO, highlightthickness=0)
        canvas.place(x=0, y=0)
        self.utils.dibujar_fondo_piedra(canvas, ancho, alto)
        canvas.create_rectangle(0, 0, ancho, alto,
                                 fill=COLOR_FONDO, stipple="gray50", outline="")

        # Panel del formulario (simulado con rectángulos en el canvas)
        canvas.create_rectangle(250, 100, 650, 520,
                                 fill=COLOR_PIEDRA, outline=COLOR_SEPARADOR, width=2)
        canvas.create_rectangle(252, 102, 648, 518,
                                 fill="", outline=COLOR_ORO, width=1)

        self.utils.borde_dorado(canvas, ancho, alto)

        # Frame del formulario 
        self._frame = tk.Frame(self.ventana, bg=COLOR_PIEDRA)
        self._frame.place(relx=0.5, rely=0.5, anchor="center")

        self._construir_formulario()

        # Pie de página
        tk.Label(self.ventana,
                 text="ITCR  ·  Introducción a la Programación  ·  2026",
                 bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,
                 font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

    def _construir_formulario(self):
        # Limpia el frame y reconstruye el formulario según el modo actual
        for w in self._frame.winfo_children():
            w.destroy()

        frame = self._frame

        # Símbolo y título del panel
        tk.Label(frame, text="⚜",
                 bg=COLOR_PIEDRA, fg=COLOR_ORO,
                 font=("Georgia", 20)).pack(pady=(16, 4))

        titulo = "INICIO DE SESIÓN" if self._modo == "login" else "CREAR CUENTA"
        tk.Label(frame, text=titulo,
                 bg=COLOR_PIEDRA, fg=COLOR_ORO,
                 font=("Georgia", 16, "bold")).pack(pady=(0, 4))

        # Separador
        tk.Label(frame, text="━━━━━━━  ✦  ━━━━━━━",
                 bg=COLOR_PIEDRA, fg=COLOR_SEPARADOR,
                 font=("Courier", 10)).pack(pady=(0, 20))

        # Campo: nombre de usuario
        tk.Label(frame, text="Nombre de Usuario",
                 bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE,
                 font=FUENTE_LABEL).pack(anchor="w", padx=30)

        self._entry_nombre = tk.Entry(
            frame, bg=COLOR_ENTRY_FONDO, fg=COLOR_TEXTO,
            font=FUENTE_ENTRY, relief=tk.FLAT, width=24,
            insertbackground=COLOR_ORO,
            highlightthickness=1, highlightcolor=COLOR_ORO,
            highlightbackground=COLOR_ENTRY_BORDE
        )
        self._entry_nombre.pack(padx=30, pady=(2, 14), ipady=6)
        self._entry_nombre.focus()

        # Campo: contraseña
        tk.Label(frame, text="Contraseña",
                 bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE,
                 font=FUENTE_LABEL).pack(anchor="w", padx=30)

        self._entry_contrasena = tk.Entry(
            frame, bg=COLOR_ENTRY_FONDO, fg=COLOR_TEXTO,
            font=FUENTE_ENTRY, relief=tk.FLAT, width=24,
            insertbackground=COLOR_ORO, show="•",
            highlightthickness=1, highlightcolor=COLOR_ORO,
            highlightbackground=COLOR_ENTRY_BORDE
        )
        self._entry_contrasena.pack(padx=30, pady=(2, 6), ipady=6)

        # Enter dispara la acción principal
        self.ventana.bind("<Return>", lambda e: self._accion_principal())

        # Label de mensajes de error o éxito
        self._label_msg = tk.Label(frame, text="",
                                    bg=COLOR_PIEDRA, fg=COLOR_SANGRE,
                                    font=("Courier", 9), wraplength=240)
        self._label_msg.pack(pady=(0, 14))

        # Botón principal: ingresar o registrarse
        texto_btn = "⚔  INGRESAR" if self._modo == "login" else "⚜  REGISTRARSE"
        btn_principal = self.utils.boton_medieval(frame, texto_btn,
                                                   self._accion_principal, COLOR_ORO)
        btn_principal.pack(pady=(0, 10))

        # Separador
        tk.Label(frame, text="─" * 28,
                 bg=COLOR_PIEDRA, fg=COLOR_SEPARADOR,
                 font=("Courier", 8)).pack(pady=(0, 8))

        # Botón para cambiar de modo
        if self._modo == "login":
            txt_cambio = "¿No tenés cuenta?  Registrate aquí"
        else:
            txt_cambio = "¿Ya tenés cuenta?  Iniciá sesión"

        btn_cambio = tk.Button(
            frame, text=txt_cambio,
            bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE,
            font=("Courier", 9), relief=tk.FLAT, bd=0,
            activebackground=COLOR_PIEDRA, activeforeground=COLOR_ORO,
            cursor="hand2", command=self._cambiar_modo
        )
        btn_cambio.pack(pady=(0, 6))
        self.utils.hover(btn_cambio, COLOR_TEXTO_TENUE, COLOR_ORO)

    def _cambiar_modo(self):
        # Alterna entre login y registro y reconstruye el formulario
        self._modo = "registro" if self._modo == "login" else "login"
        self._construir_formulario()

    def _accion_principal(self):
        # Ejecuta login o registro dependiendo del modo actual
        nombre    = self._entry_nombre.get().strip()
        contrasena = self._entry_contrasena.get()

        if not nombre or not contrasena:
            self._mostrar_msg("Completá todos los campos.", error=True)
            return

        if self._modo == "login":
            exito, resultado = self.gestor.iniciar_sesion(nombre, contrasena)
            if exito:
                self.ventana.unbind("<Return>")
                # Pasa el usuario completo al callback de navegación
                usuario = {"nombre": nombre, **resultado}
                self.ir_a_menu(usuario)
            else:
                self._mostrar_msg(resultado, error=True)

        else:  # modo registro
            exito, mensaje = self.gestor.registrar(nombre, contrasena)
            if exito:
                self._mostrar_msg(mensaje + " Ahora iniciá sesión.", error=False)
                self._modo = "login"
                self.ventana.after(1200, self._construir_formulario)
            else:
                self._mostrar_msg(mensaje, error=True)

    def _mostrar_msg(self, texto, error=True):
        # Muestra un mensaje en rojo (error) o verde (éxito)
        color = COLOR_SANGRE if error else "#4a8c4a"
        self._label_msg.config(text=texto, fg=color)

# SECCIÓN 5 — PANTALLA MENÚ PRINCIPAL
# Pantalla que se muestra después del login. Permite navegar a:
# Jugar, Mejores Puntuaciones, Cómo Jugar y Cuenta. Incluye un
# botón en la esquina inferior derecha para pausar/reanudar música.
class PantallaMenu:

    def __init__(self, ventana, utils, gestor, usuario, estado_musica,ir_a_jugar, ir_a_top, ir_a_como_jugar, ir_a_cuenta):
        self.ventana       = ventana
        self.utils         = utils           # instancia de Utilidades
        self.gestor        = gestor          # instancia de GestorUsuarios
        self.usuario       = usuario         # dict del usuario logueado
        self.estado_musica = estado_musica  # callbacks de navegación a cada sub-pantalla
        self.ir_a_jugar      = ir_a_jugar
        self.ir_a_top        = ir_a_top
        self.ir_a_como_jugar = ir_a_como_jugar
        self.ir_a_cuenta     = ir_a_cuenta
    
    def mostrar(self):
        # Limpia la ventana y construye el menú
        for widget in self.ventana.winfo_children():
            widget.destroy()

        self.utils.tocar_musica_menu(self.estado_musica)

        ancho = 900
        alto  = 620

        # Canvas de fondo 
        canvas = tk.Canvas(self.ventana, width=ancho, height=alto,bg=COLOR_FONDO, highlightthickness=0)
        canvas.place(x=0, y=0)
        self.utils.dibujar_fondo_piedra(canvas, ancho, alto)
        canvas.create_rectangle(0, 0, ancho, alto, fill=COLOR_FONDO, stipple="gray50", outline="")
        self.utils.borde_dorado(canvas, ancho, alto)
        
        # Encabezado con el nombre del usuario
        tk.Label(self.ventana, text="⚔  ⚜  ⚔",bg=COLOR_FONDO, fg=COLOR_SANGRE,font=("Georgia", 16)).place(relx=0.5, y=70, anchor="center")
        tk.Label(self.ventana, text=f"Bienvenido, {self.usuario['nombre']}",bg=COLOR_FONDO, fg=COLOR_ORO,font=("Georgia", 22, "bold")).place(relx=0.5, y=112, anchor="center")
        tk.Label(self.ventana, text="━━━━━━━  ✦  ━━━━━━━",bg=COLOR_FONDO, fg=COLOR_SEPARADOR,font=("Courier", 12)).place(relx=0.5, y=148, anchor="center")

        # Frame central con las opciones del menú
        frame = tk.Frame(self.ventana, bg=COLOR_FONDO)
        frame.place(relx=0.5, rely=0.55, anchor="center")

        opciones = [("⚔  JUGAR",self.ir_a_jugar),("🏆  MEJORES PUNTUACIONES",self.ir_a_top),("📜  CÓMO JUGAR",self.ir_a_como_jugar),("⚜  CUENTA",self.ir_a_cuenta),]

        for texto, comando in opciones:
            btn = self.utils.boton_medieval(frame, texto, comando, COLOR_TEXTO)
            btn.pack(pady=14)
        # ── Pie de página ──
        tk.Label(self.ventana,text="ITCR  ·  Introducción a la Programación  ·  2026",bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

        # ── Botón de música, esquina inferior derecha ──
        self._construir_boton_musica()

    def _construir_boton_musica(self):
        # Texto cambia según si la música está sonando o pausada
        texto = "♪  MÚSICA" if self.estado_musica["activa"] else "✕  MÚSICA"
        self._btn_musica = tk.Button(self.ventana, text=texto,bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=("Courier", 10, "bold"), relief=tk.FLAT, bd=0,activebackground=COLOR_FONDO, activeforeground=COLOR_ORO_BRILLANTE,
            cursor="hand2", command=self._alternar_musica)
        self._btn_musica.place(relx=0.97, rely=0.94, anchor="se")
        self.utils.hover(self._btn_musica, COLOR_TEXTO_TENUE, COLOR_ORO_BRILLANTE)

    def _alternar_musica(self):
        # Pausa o reanuda la música y actualiza el texto del botón
        self.utils.alternar_musica(self.estado_musica)
        nuevo_texto = "♪  MÚSICA" if self.estado_musica["activa"] else "✕  MÚSICA"
        self._btn_musica.config(text=nuevo_texto)

# -----------------------------------------------------------------
# SECCIÓN 6 — PANTALLA MEJORES PUNTUACIONES
# Muestra los dos rankings (top 5 defensores y top 5 atacantes)
# usando GestorUsuarios.obtener_ranking().
# -----------------------------------------------------------------
class PantallaTop:

    def __init__(self, ventana, utils, gestor, estado_musica, ir_a_menu):
        self.ventana       = ventana
        self.utils         = utils
        self.gestor        = gestor          # instancia de GestorUsuarios
        self.estado_musica = estado_musica
        self.ir_a_menu      = ir_a_menu      # callback para volver al menú

    def mostrar(self):
        # Limpia la ventana y construye la pantalla
        for widget in self.ventana.winfo_children():
            widget.destroy()

        ancho = 900
        alto  = 620

        # ── Canvas de fondo ──
        canvas = tk.Canvas(self.ventana, width=ancho, height=alto,
                           bg=COLOR_FONDO, highlightthickness=0)
        canvas.place(x=0, y=0)
        self.utils.dibujar_fondo_piedra(canvas, ancho, alto)
        canvas.create_rectangle(0, 0, ancho, alto,
                                 fill=COLOR_FONDO, stipple="gray50", outline="")
        self.utils.borde_dorado(canvas, ancho, alto)

        # Paneles de los dos rankings (simulados con rectángulos en el canvas)
        canvas.create_rectangle(70, 140, 430, 500,
                                 fill=COLOR_PIEDRA, outline=COLOR_SEPARADOR, width=2)
        canvas.create_rectangle(72, 142, 428, 498,
                                 fill="", outline=COLOR_ORO, width=1)

        canvas.create_rectangle(470, 140, 830, 500,
                                 fill=COLOR_PIEDRA, outline=COLOR_SEPARADOR, width=2)
        canvas.create_rectangle(472, 142, 828, 498,
                                 fill="", outline=COLOR_ORO, width=1)

        # ── Título ──
        tk.Label(self.ventana, text="🏆  MEJORES PUNTUACIONES  🏆",
                 bg=COLOR_FONDO, fg=COLOR_ORO,
                 font=("Georgia", 24, "bold")).place(relx=0.5, y=70, anchor="center")

        tk.Label(self.ventana, text="━━━━━━━  ✦  ━━━━━━━",
                 bg=COLOR_FONDO, fg=COLOR_SEPARADOR,
                 font=("Courier", 12)).place(relx=0.5, y=108, anchor="center")

        # ── Construye cada panel de ranking ──
        self._construir_panel(x_centro=250, rol="defensor",
                              titulo="⚔  TOP DEFENSORES", icono="🛡")
        self._construir_panel(x_centro=650, rol="atacante",
                              titulo="⚔  TOP ATACANTES", icono="⚔")

        # ── Botón volver ──
        btn_volver = self.utils.boton_medieval(self.ventana, "←  VOLVER AL MENÚ",
                                               self.ir_a_menu, COLOR_TEXTO)
        btn_volver.place(relx=0.5, y=555, anchor="center")

        # ── Pie de página ──
        tk.Label(self.ventana,
                 text="ITCR  ·  Introducción a la Programación  ·  2026",
                 bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,
                 font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

    def _construir_panel(self, x_centro, rol, titulo, icono):
        # Construye un panel de ranking (lista de 5 jugadores) centrado en x_centro
        ranking = self.gestor.obtener_ranking(rol, cantidad=5)

        # Título del panel
        tk.Label(self.ventana, text=titulo,
                 bg=COLOR_PIEDRA, fg=COLOR_ORO_BRILLANTE,
                 font=("Georgia", 14, "bold")).place(x=x_centro, y=165, anchor="center")

        tk.Label(self.ventana, text="─" * 24,
                 bg=COLOR_PIEDRA, fg=COLOR_SEPARADOR,
                 font=("Courier", 9)).place(x=x_centro, y=192, anchor="center")

        if not ranking:
            # Mensaje si todavía no hay datos registrados
            tk.Label(self.ventana, text="Aún no hay jugadores registrados.",
                     bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE,
                     font=("Courier", 10, "italic")).place(x=x_centro, y=300, anchor="center")
            return

        # Medallas para los primeros 3 lugares, número simple para el resto
        medallas = ["🥇", "🥈", "🥉"]

        y = 225
        for posicion, (nombre, victorias) in enumerate(ranking):
            simbolo = medallas[posicion] if posicion < 3 else f"{posicion + 1}."

            fila = tk.Frame(self.ventana, bg=COLOR_PIEDRA)
            fila.place(x=x_centro, y=y, anchor="center")

            tk.Label(fila, text=simbolo, bg=COLOR_PIEDRA, fg=COLOR_ORO,
                     font=("Courier", 12, "bold"), width=3).pack(side="left")
            tk.Label(fila, text=nombre, bg=COLOR_PIEDRA, fg=COLOR_TEXTO,
                     font=("Courier", 12), width=14, anchor="w").pack(side="left")
            tk.Label(fila, text=f"{victorias} {icono}", bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE,
                     font=("Courier", 11), width=8, anchor="e").pack(side="left")

            y += 50

# INICIO DEL PROGRAMA
# Aquí se crea la ventana, los servicios compartidos, y se navega
# entre pantallas mediante callbacks.

# Ventana principal
ventana = tk.Tk()
ventana.title("Defensa y Asalto de Base")
ventana.geometry("900x620")
ventana.resizable(False, False)
ventana.config(bg=COLOR_FONDO)

# Servicios compartidos (se crean una sola vez) 
utils   = Utilidades()
gestor  = GestorUsuarios()
usuario_actual = {}  #se llena después del login exitoso

# Estado de la música (diccionario compartido entre pantallas)
estado_musica = {"actual" : "","activa" : False,"pausada": False}

# Funciones de navegación (callbacks entre pantallas)

def ir_a_intro():
    pantalla = PantallaIntro(ventana, utils, estado_musica, ir_a_login)
    pantalla.mostrar()

def ir_a_login():
    pantalla = PantallaLogin(ventana, utils, gestor, ir_a_menu)
    pantalla.mostrar()

def ir_a_menu(usuario):
    # Guarda el usuario logueado y navega al menú principal
    global usuario_actual
    usuario_actual = usuario
    pantalla = PantallaMenu(ventana, utils, gestor, usuario_actual, estado_musica, ir_a_jugar, ir_a_top, ir_a_como_jugar, ir_a_cuenta)
    pantalla.mostrar()

def ir_a_jugar():
    print("[DEBUG] Entrando a Jugar")
    # TODO: pantalla de selección de facción / partida

def ir_a_top():
    pantalla = PantallaTop(ventana, utils, gestor, estado_musica, ir_a_menu_actual)
    pantalla.mostrar()

def ir_a_como_jugar():
    print("[DEBUG] Entrando a Cómo Jugar")
    # TODO: pantalla de reglas

def ir_a_cuenta():
    print("[DEBUG] Entrando a Cuenta")
    # TODO: pantalla de perfil / cerrar sesión

def ir_a_menu_actual():
    # Vuelve al menú principal usando el usuario ya logueado
    ir_a_menu(usuario_actual)

# ── Arrancar en la intro ──
ir_a_intro()

ventana.mainloop()

