import tkinter as tk
import pygame
import json
import hashlib
import os
import random
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.mixer.init()


# CONSTANTES Y CONFIGURACIONES


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

# UTILIDADES
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


# GESTOR DE USUARIOS
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
            "victorias_atacante": 0,
            "faccion"           : None
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
    
    def asignar_faccion(self, nombre, faccion):
        # Vincula permanentemente una facción al perfil del usuario
        datos = self._cargar()
        if nombre not in datos:
            return False, "Usuario no encontrado."
        datos[nombre]["faccion"] = faccion
        self._guardar(datos)
        return True, f"¡Facción '{faccion}' vinculada a tu cuenta!"

    def obtener_faccion(self, nombre):
        # Retorna la facción guardada del usuario, o None si no eligió ninguna
        datos = self._cargar()
        if nombre in datos:
            return datos[nombre].get("faccion", None)
        return None

#PANTALLA INTRO
# Pantalla de inicio del juego: "presiona cualquier tecla".
class PantallaIntro:

    def __init__(self, ventana, utils, estado_musica, ir_a_login): # recibe callback para navegar al login
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

        # Canvas de fondo con cuadrícula de piedra y marco dorado
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

        # Frame central para los widgets de texto
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


# PANTALLA LOGIN
# Formulario de inicio de sesión y registro de usuarios.
class PantallaLogin:

    def __init__(self, ventana, utils, gestor, numero_jugador, ir_a_continuar, nombre_excluido=None):
        self.ventana   = ventana
        self.utils     = utils    # instancia de Utilidades
        self.gestor    = gestor   # instancia de GestorUsuarios
        self.numero_jugador  = numero_jugador     # 1 o 2
        self.ir_a_continuar  = ir_a_continuar     # callback que recibe el usuario logueado
        self.nombre_excluido = nombre_excluido    # nombre del jugador que ya inició sesión
        self._modo     = "login"  # puede ser "login" o "registro"

    def mostrar(self):
        # Limpia la ventana y construye la pantalla
        for widget in self.ventana.winfo_children():
            widget.destroy()

        ancho = 900
        alto  = 620

        # Canvas de fondo
        canvas = tk.Canvas(self.ventana, width=ancho, height=alto, bg=COLOR_FONDO, highlightthickness=0)
        canvas.place(x=0, y=0)
        self.utils.dibujar_fondo_piedra(canvas, ancho, alto)
        canvas.create_rectangle(0, 0, ancho, alto,fill=COLOR_FONDO, stipple="gray50", outline="")

        # Panel del formulario (simulado con rectángulos en el canvas)
        canvas.create_rectangle(250, 100, 650, 520,fill=COLOR_PIEDRA, outline=COLOR_SEPARADOR, width=2)
        canvas.create_rectangle(252, 102, 648, 518,fill="", outline=COLOR_ORO, width=1)

        self.utils.borde_dorado(canvas, ancho, alto)

        # Frame del formulario 
        self._frame = tk.Frame(self.ventana, bg=COLOR_PIEDRA)
        self._frame.place(relx=0.5, rely=0.5, anchor="center")

        self._construir_formulario()

        # Pie de página
        tk.Label(self.ventana,text="ITCR  ·  Introducción a la Programación  ·  2026",bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

    def _construir_formulario(self):
        # Limpia el frame y reconstruye el formulario según el modo actual
        for w in self._frame.winfo_children():
            w.destroy()

        frame = self._frame

       # Etiqueta de turno: JUGADOR 1 / JUGADOR 2
        color_jugador = COLOR_ORO_BRILLANTE if self.numero_jugador == 1 else COLOR_SANGRE
        tk.Label(frame, text=f"⚜  JUGADOR {self.numero_jugador}  ⚜",bg=COLOR_PIEDRA, fg=color_jugador,font=("Georgia", 13, "bold")).pack(pady=(16, 2))

        titulo = "INICIO DE SESIÓN" if self._modo == "login" else "CREAR CUENTA"
        tk.Label(frame, text=titulo,bg=COLOR_PIEDRA, fg=COLOR_ORO,font=("Georgia", 16, "bold")).pack(pady=(0, 4))

        # Separador
        tk.Label(frame, text="━━━━━━━  ✦  ━━━━━━━", bg=COLOR_PIEDRA, fg=COLOR_SEPARADOR,font=("Courier", 10)).pack(pady=(0, 20))

        # Campo: nombre de usuario
        tk.Label(frame, text="Nombre de Usuario", bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE,font=FUENTE_LABEL).pack(anchor="w", padx=30)

        self._entry_nombre = tk.Entry(frame, bg=COLOR_ENTRY_FONDO, fg=COLOR_TEXTO,font=FUENTE_ENTRY, relief=tk.FLAT, width=24,insertbackground=COLOR_ORO,highlightthickness=1, highlightcolor=COLOR_ORO,
            highlightbackground=COLOR_ENTRY_BORDE)
        self._entry_nombre.pack(padx=30, pady=(2, 14), ipady=6)
        self._entry_nombre.focus()

        # Campo: contraseña
        tk.Label(frame, text="Contraseña",bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE,font=FUENTE_LABEL).pack(anchor="w", padx=30)

        self._entry_contrasena = tk.Entry(frame, bg=COLOR_ENTRY_FONDO, fg=COLOR_TEXTO,font=FUENTE_ENTRY, relief=tk.FLAT, width=24,insertbackground=COLOR_ORO, show="•",highlightthickness=1, highlightcolor=COLOR_ORO,highlightbackground=COLOR_ENTRY_BORDE)
        self._entry_contrasena.pack(padx=30, pady=(2, 6), ipady=6)

        # Enter dispara la acción principal
        self.ventana.bind("<Return>", lambda e: self._accion_principal())

        # Label de mensajes de error o éxito
        self._label_msg = tk.Label(frame, text="", bg=COLOR_PIEDRA, fg=COLOR_SANGRE, font=("Courier", 9), wraplength=240)
        self._label_msg.pack(pady=(0, 14))

        # Botón principal: ingresar o registrarse
        texto_btn = "⚔  INGRESAR" if self._modo == "login" else "⚜  REGISTRARSE"
        btn_principal = self.utils.boton_medieval(frame, texto_btn, self._accion_principal, COLOR_ORO)
        btn_principal.pack(pady=(0, 10))

        # Separador
        tk.Label(frame, text="─" * 28,bg=COLOR_PIEDRA, fg=COLOR_SEPARADOR, font=("Courier", 8)).pack(pady=(0, 8))

        # Botón para cambiar de modo
        if self._modo == "login":
            txt_cambio = "¿No tenés cuenta?  Registrate aquí"
        else:
            txt_cambio = "¿Ya tenés cuenta?  Iniciá sesión"

        btn_cambio = tk.Button(frame, text=txt_cambio,bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE,font=("Courier", 9), relief=tk.FLAT, bd=0,activebackground=COLOR_PIEDRA, activeforeground=COLOR_ORO,cursor="hand2", command=self._cambiar_modo)
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
            # Evita que el mismo jugador inicie sesión dos veces en la misma partida
            if self.nombre_excluido and nombre == self.nombre_excluido:
                self._mostrar_msg(f"Ese usuario ya está en partida. El Jugador "
                                  f"{self.numero_jugador} debe usar otra cuenta.", error=True)
                return

            exito, resultado = self.gestor.iniciar_sesion(nombre, contrasena)

            if exito:
                self.ventana.unbind("<Return>")
                # Pasa el usuario completo al callback de navegación
                usuario = {"nombre": nombre, **resultado}
                self.ir_a_continuar(usuario)
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

# PANTALLA MENÚ PRINCIPAL
# Pantalla que se muestra después del login. Permite navegar a:
# Jugar, Mejores Puntuaciones, Cómo Jugar y Cuenta. Incluye un
# botón en la esquina inferior derecha para pausar/reanudar música.
class PantallaMenu:

    def __init__(self, ventana, utils, gestor, jugadores, estado_musica,ir_a_jugar, ir_a_top, ir_a_como_jugar, ir_a_cuenta):
        self.ventana       = ventana
        self.utils         = utils           # instancia de Utilidades
        self.gestor        = gestor          # instancia de GestorUsuarios
        self.jugadores     = jugadores       # dict {1: usuario1, 2: usuario2}
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
        
        nombre1 = self.jugadores[1]["nombre"]
        nombre2 = self.jugadores[2]["nombre"]

        # Encabezado con el nombre de los usuarios
        tk.Label(self.ventana, text="⚔  ⚜  ⚔",bg=COLOR_FONDO, fg=COLOR_SANGRE,font=("Georgia", 16)).place(relx=0.5, y=70, anchor="center")
        tk.Label(self.ventana,text=f"Jugador 1: {nombre1}    ⚔    Jugador 2: {nombre2}",bg=COLOR_FONDO, fg=COLOR_ORO,font=("Georgia", 18, "bold")).place(relx=0.5, y=108, anchor="center")

        tk.Label(self.ventana, text="━━━━━━━  ✦  ━━━━━━━",bg=COLOR_FONDO, fg=COLOR_SEPARADOR,font=("Courier", 12)).place(relx=0.5, y=148, anchor="center")

        # Frame central con las opciones del menú
        frame = tk.Frame(self.ventana, bg=COLOR_FONDO)
        frame.place(relx=0.5, rely=0.55, anchor="center")

        opciones = [("⚔  JUGAR",self.ir_a_jugar),("🏆  MEJORES PUNTUACIONES",self.ir_a_top),("📜  CÓMO JUGAR",self.ir_a_como_jugar),("⚜  CUENTAS",self.ir_a_cuenta),]

        for texto, comando in opciones:
            btn = self.utils.boton_medieval(frame, texto, comando, COLOR_TEXTO)
            btn.pack(pady=14)
        
        # Pie de página
        tk.Label(self.ventana,text="ITCR  ·  Introducción a la Programación  ·  2026",bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

        # botón de música en la esquina inferior derecha
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

# mejor puntuación
# Muestra los dos rankings (top 5 defensores y top 5 atacantes)
# usando GestorUsuarios.obtener_ranking().
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

        #Canvas de fondo
        canvas = tk.Canvas(self.ventana, width=ancho, height=alto,bg=COLOR_FONDO, highlightthickness=0)
        canvas.place(x=0, y=0)
        self.utils.dibujar_fondo_piedra(canvas, ancho, alto)
        canvas.create_rectangle(0, 0, ancho, alto, fill=COLOR_FONDO, stipple="gray50", outline="")
        self.utils.borde_dorado(canvas, ancho, alto)

        # Paneles de los dos rankings (simulados con rectángulos en el canvas)
        canvas.create_rectangle(70, 140, 430, 500,fill=COLOR_PIEDRA, outline=COLOR_SEPARADOR, width=2)
        canvas.create_rectangle(72, 142, 428, 498,fill="", outline=COLOR_ORO, width=1)

        canvas.create_rectangle(470, 140, 830, 500, fill=COLOR_PIEDRA, outline=COLOR_SEPARADOR, width=2)
        canvas.create_rectangle(472, 142, 828, 498,fill="", outline=COLOR_ORO, width=1)

        # Título
        tk.Label(self.ventana, text="🏆  MEJORES PUNTUACIONES  🏆",bg=COLOR_FONDO, fg=COLOR_ORO,font=("Georgia", 24, "bold")).place(relx=0.5, y=70, anchor="center")

        tk.Label(self.ventana, text="━━━━━━━  ✦  ━━━━━━━",bg=COLOR_FONDO, fg=COLOR_SEPARADOR, font=("Courier", 12)).place(relx=0.5, y=108, anchor="center")

        # Construye cada panel de ranking 
        self._construir_panel(x_centro=250, rol="defensor",titulo="⚔  TOP DEFENSORES", icono="🛡")
        self._construir_panel(x_centro=650, rol="atacante", titulo="⚔  TOP ATACANTES", icono="⚔")

        # Botón volver
        btn_volver = self.utils.boton_medieval(self.ventana, "←  VOLVER AL MENÚ",self.ir_a_menu, COLOR_TEXTO)
        btn_volver.place(relx=0.5, y=555, anchor="center")

        #Pie de página
        tk.Label(self.ventana,text="ITCR  ·  Introducción a la Programación  ·  2026",bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

    def _construir_panel(self, x_centro, rol, titulo, icono):
        # Construye un panel de ranking (lista de 5 jugadores) centrado en x_centro
        ranking = self.gestor.obtener_ranking(rol, cantidad=5)

        # Título del panel
        tk.Label(self.ventana, text=titulo,bg=COLOR_PIEDRA, fg=COLOR_ORO_BRILLANTE,font=("Georgia", 14, "bold")).place(x=x_centro, y=165, anchor="center")

        tk.Label(self.ventana, text="─" * 24,bg=COLOR_PIEDRA, fg=COLOR_SEPARADOR,font=("Courier", 9)).place(x=x_centro, y=192, anchor="center")

        if not ranking:
            # Mensaje si todavía no hay datos registrados
            tk.Label(self.ventana, text="Aún no hay jugadores registrados.",bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE,font=("Courier", 10, "italic")).place(x=x_centro, y=300, anchor="center")
            return

        # Medallas para los primeros 3 lugares, número simple para el resto
        medallas = ["🥇", "🥈", "🥉"]

        y = 225
        for posicion, (nombre, victorias) in enumerate(ranking):
            simbolo = medallas[posicion] if posicion < 3 else f"{posicion + 1}."

            fila = tk.Frame(self.ventana, bg=COLOR_PIEDRA)
            fila.place(x=x_centro, y=y, anchor="center")

            tk.Label(fila, text=simbolo, bg=COLOR_PIEDRA, fg=COLOR_ORO, font=("Courier", 12, "bold"), width=3).pack(side="left")
            tk.Label(fila, text=nombre, bg=COLOR_PIEDRA, fg=COLOR_TEXTO, font=("Courier", 12), width=14, anchor="w").pack(side="left")
            tk.Label(fila, text=f"{victorias} {icono}", bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE, font=("Courier", 11), width=8, anchor="e").pack(side="left")
            y += 50

# USUARIO LOGUEADO
# Muestra los datos del usuario logueado: nombre y victorias como
# defensor y como atacante. Permite volver al menú o cerrar sesión.
class PantallaCuenta:

    def __init__(self, ventana, utils, gestor, jugadores, estado_musica,ir_a_menu, ir_a_login, ir_a_faccion,pagina_inicial=1):
        self.ventana       = ventana
        self.utils         = utils
        self.gestor        = gestor          # instancia de GestorUsuarios
        self.jugadores     = jugadores       # dict {1: usuario1, 2: usuario2}
        self.estado_musica = estado_musica
        self.ir_a_menu      = ir_a_menu      # callback para volver al menú
        self.ir_a_login     = ir_a_login     # callback para cerrar sesión
        self.ir_a_faccion   = ir_a_faccion   # callback a la pantalla de facciones
        self._pagina        = pagina_inicial  # 1 o 2

    def mostrar(self):
        # Limpia la ventana y construye la pantalla
        for widget in self.ventana.winfo_children(): 
            widget.destroy()

        ancho = 900
        alto  = 620

        #Canvas de fondo
        canvas = tk.Canvas(self.ventana, width=ancho, height=alto,bg=COLOR_FONDO, highlightthickness=0)
        canvas.place(x=0, y=0)
        self.utils.dibujar_fondo_piedra(canvas, ancho, alto)
        canvas.create_rectangle(0, 0, ancho, alto,fill=COLOR_FONDO, stipple="gray50", outline="")
        self.utils.borde_dorado(canvas, ancho, alto)

        # Panel central de la cuenta
        canvas.create_rectangle(250, 120, 650, 500,fill=COLOR_PIEDRA, outline=COLOR_SEPARADOR, width=2)
        canvas.create_rectangle(252, 122, 648, 498,fill="", outline=COLOR_ORO, width=1)

        #Frame central con los datos
        frame = tk.Frame(self.ventana, bg=COLOR_PIEDRA)
        frame.place(relx=0.5, y=310, anchor="center")

        # Símbolo y título
        tk.Label(frame, text="⚜",bg=COLOR_PIEDRA, fg=COLOR_ORO,font=("Georgia", 22)).pack(pady=(20, 4))

        tk.Label(frame, text="CUENTAS",bg=COLOR_PIEDRA, fg=COLOR_ORO,font=("Georgia", 18, "bold")).pack(pady=(0, 4))

        tk.Label(frame, text="━━━━━━━  ✦  ━━━━━━━",bg=COLOR_PIEDRA, fg=COLOR_SEPARADOR,font=("Courier", 10)).pack(pady=(0, 24))

        # Datos del usuario (vuelve a leer del archivo para mostrar
        #  el dato más actualizado, por si cambió tras una partida) ──
        self._frame = tk.Frame(self.ventana, bg=COLOR_PIEDRA)
        self._frame.place(relx=0.5, y=275, anchor="center")

        self._btn_anterior = self.utils.boton_medieval(self.ventana, "◄  ANTERIOR",self._pagina_anterior, COLOR_TEXTO)
        self._btn_anterior.place(x=160, y=480, anchor="center")

        self._btn_siguiente = self.utils.boton_medieval(self.ventana, "SIGUIENTE  ►",self._pagina_siguiente, COLOR_TEXTO)
        self._btn_siguiente.place(x=740, y=480, anchor="center")

        self._label_pagina = tk.Label(self.ventana, text="",bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=("Courier", 9))
        self._label_pagina.place(relx=0.5, y=513, anchor="center")

        # Botón volver al menú
        btn_volver = self.utils.boton_medieval(self.ventana, "←  VOLVER AL MENÚ", self.ir_a_menu, COLOR_TEXTO)
        btn_volver.place(relx=0.5, y=555, anchor="center")
        
        # Botón cerrar sesión
        btn_cerrar = self.utils.boton_medieval(self.ventana, "⏻  CERRAR SESIÓN (AMBOS)",self._cerrar_sesion, COLOR_SANGRE)
        btn_cerrar.place(relx=0.5, y=578, anchor="center")
        # Pie de página
        tk.Label(self.ventana, text="ITCR  ·  Introducción a la Programación  ·  2026",bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

        self._construir_pagina()
        
    def _construir_pagina(self): # Construye la página actual (1 o 2) con los datos del usuario correspondiente
        for w in self._frame.winfo_children():
            w.destroy()
        
        usuario = self.jugadores[self._pagina]
        datos_actuales = self.gestor._cargar().get(usuario["nombre"], usuario)
        faccion_actual = datos_actuales.get("faccion") or "Sin asignar"
        
        color_jugador = COLOR_ORO_BRILLANTE if self._pagina == 1 else COLOR_SANGRE
        
        tk.Label(self._frame, text=f"JUGADOR {self._pagina}",bg=COLOR_PIEDRA, fg=color_jugador,font=("Georgia", 14, "bold")).pack(pady=(18, 2))
        
        tk.Label(self._frame, text="━━━━━━━  ✦  ━━━━━━━",bg=COLOR_PIEDRA, fg=COLOR_SEPARADOR,font=("Courier", 10)).pack(pady=(0, 16))
        
        self._fila_dato(self._frame, "Nombre de usuario", usuario["nombre"])
        self._fila_dato(self._frame, "Victorias como defensor 🛡",datos_actuales.get("victorias_defensor", 0))
        self._fila_dato(self._frame, "Victorias como atacante ⚔", datos_actuales.get("victorias_atacante", 0))
        self._fila_dato(self._frame, "Facción", faccion_actual)
        
        tk.Label(self._frame, text="", bg=COLOR_PIEDRA).pack(pady=(4, 0))
        
        texto_btn_faccion = "⚜  CAMBIAR FACCIÓN" if datos_actuales.get("faccion") else "⚜  ELEGIR FACCIÓN"
        btn_faccion = self.utils.boton_medieval(self._frame, texto_btn_faccion,lambda: self.ir_a_faccion(self._pagina), COLOR_ORO)
        btn_faccion.pack(pady=(0, 14))
        
        self._label_pagina.config(text=f"Cuenta {self._pagina} de 2")
        self._btn_anterior.config(state="disabled" if self._pagina == 1 else "normal")
        self._btn_siguiente.config(state="disabled" if self._pagina == 2 else "normal")
        

    def _fila_dato(self, frame, etiqueta, valor):
        # Crea una fila con una etiqueta a la izquierda y el valor a la derecha
        fila = tk.Frame(frame, bg=COLOR_PIEDRA)
        fila.pack(fill="x", padx=30, pady=6)

        tk.Label(fila, text=etiqueta,bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE,font=FUENTE_LABEL, anchor="w").pack(side="left")
        tk.Label(fila, text=str(valor),bg=COLOR_PIEDRA, fg=COLOR_TEXTO,font=("Courier", 11, "bold"), anchor="e").pack(side="right")

    def _pagina_anterior(self): # Muestra la página anterior (jugador 1) si es posible
        if self._pagina > 1:
            self._pagina -= 1
            self._construir_pagina()

    def _pagina_siguiente(self): # Muestra la página siguiente (jugador 2) si es posible
        if self._pagina < 2:
            self._pagina += 1
            self._construir_pagina()

    def _cerrar_sesion(self): 
        # Detiene la música y vuelve a la pantalla de login
        self.utils.parar_musica(self.estado_musica)
        self.ir_a_login()


# PANTALLA SELECCIÓN DE FACCIÓN
# Permite vincular permanentemente una facción al perfil del
# usuario. La elección se guarda en usuarios.json mediante
# GestorUsuarios.asignar_faccion().
class PantallaFaccion: # Pantalla de selección de facción para un jugador

    FACCIONES = [
        {
            "nombre"     : "Medieval",
            "icono"      : "🏰",
            "descripcion": "Torres de piedra, muros sólidos\ny unidades con espada y escudo.",
            "color"      : COLOR_ORO,
        },
        {
            "nombre"     : "Futurista",
            "icono"      : "🚀",
            "descripcion": "Torres láser, muros de energía\ny unidades blindadas de alta tecnología.",
            "color"      : "#4ab8c9",
        },
        {
            "nombre"     : "Naturaleza",
            "icono"      : "🌿",
            "descripcion": "Torres vivientes, muros de raíces\ny unidades salvajes del bosque.",
            "color"      : "#5a9c4a",
        },
    ]

    def __init__(self, ventana, utils, gestor, jugadores, numero_jugador, ir_volver, forzado=False):
        # Inicializa la pantalla de selección de facción para un jugador
        self.ventana        = ventana
        self.utils          = utils
        self.gestor         = gestor
        self.jugadores      = jugadores
        self.numero_jugador = numero_jugador
        self.usuario        = jugadores[numero_jugador]
        self.ir_volver       = ir_volver
        self.forzado         = forzado
        self._seleccion      = self.gestor.obtener_faccion(self.usuario["nombre"])
        self._botones_carta  = []

    def mostrar(self): # Limpia la ventana y construye la pantalla de selección de facción
        for widget in self.ventana.winfo_children():
            widget.destroy()

        ancho = 900
        alto  = 620

        canvas = tk.Canvas(self.ventana, width=ancho, height=alto,bg=COLOR_FONDO, highlightthickness=0)
        canvas.place(x=0, y=0)
        self.utils.dibujar_fondo_piedra(canvas, ancho, alto)
        canvas.create_rectangle(0, 0, ancho, alto,fill=COLOR_FONDO, stipple="gray50", outline="")
        self.utils.borde_dorado(canvas, ancho, alto)

        color_jugador = COLOR_ORO_BRILLANTE if self.numero_jugador == 1 else COLOR_SANGRE

        tk.Label(self.ventana,text=f"⚜  JUGADOR {self.numero_jugador}: {self.usuario['nombre']}  ⚜",bg=COLOR_FONDO, fg=color_jugador, font=("Georgia", 16, "bold")).place(relx=0.5, y=50, anchor="center")

        tk.Label(self.ventana, text="ELEGÍ TU FACCIÓN",bg=COLOR_FONDO, fg=COLOR_ORO, font=("Georgia", 20, "bold")).place(relx=0.5, y=85, anchor="center")

        if self.forzado:
            subtitulo = "Tu rival ya está listo. ¡Elegí una facción para empezar la partida!"
        else:
            subtitulo = "Esta elección quedará vinculada a tu cuenta de forma permanente."

        tk.Label(self.ventana, text=subtitulo,bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=FUENTE_SUBTITULO).place(relx=0.5, y=115, anchor="center")

        self._frame_cartas = tk.Frame(self.ventana, bg=COLOR_FONDO)
        self._frame_cartas.place(relx=0.5, y=290, anchor="center")

        self._botones_carta = []
        for faccion in self.FACCIONES: 
            self._crear_carta(faccion)

        self._label_msg = tk.Label(self.ventana, text="",bg=COLOR_FONDO, fg="#4a8c4a",font=("Courier", 10))

        if self.forzado:
            btn_confirmar = self.utils.boton_medieval(self.ventana, "✔  CONFIRMAR Y CONTINUAR",self._confirmar, COLOR_ORO)
            btn_confirmar.place(relx=0.5, y=515, anchor="center")
        else:
            btn_confirmar = self.utils.boton_medieval(self.ventana, "✔  CONFIRMAR ELECCIÓN",self._confirmar, COLOR_ORO)
            btn_confirmar.place(relx=0.5, y=505, anchor="center")

            btn_volver = self.utils.boton_medieval(self.ventana, "←  VOLVER A MI CUENTA",self.ir_volver, COLOR_TEXTO)
            btn_volver.place(relx=0.5, y=550, anchor="center")
        
        tk.Label(self.ventana,text="ITCR  ·  Introducción a la Programación  ·  2026",bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

        self._actualizar_cartas()

    def _crear_carta(self, faccion):
        # Crea una "tarjeta" clickeable para una facción
        carta = tk.Frame(self._frame_cartas, bg=COLOR_PIEDRA, width=220, height=250,highlightthickness=2, highlightbackground=COLOR_SEPARADOR)
        carta.pack(side="left", padx=14)
        carta.pack_propagate(False)

        tk.Label(carta, text=faccion["icono"], bg=COLOR_PIEDRA, font=("Georgia", 30)).pack(pady=(18, 6))
        tk.Label(carta, text=faccion["nombre"],bg=COLOR_PIEDRA, fg=faccion["color"],font=("Georgia", 14, "bold")).pack(pady=(0, 10))
        tk.Label(carta, text=faccion["descripcion"], bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE, font=("Courier", 9), justify="center").pack(padx=8)

        def seleccionar(e=None, nombre=faccion["nombre"]):
            # Marca la facción seleccionada y actualiza el borde de las tarjetas
            self._seleccion = nombre
            self._actualizar_cartas()

        for widget in (carta, *carta.winfo_children()):
            widget.bind("<Button-1>", seleccionar)
            widget.config(cursor="hand2")

        self._botones_carta.append((carta, faccion))

    def _actualizar_cartas(self):
        # Resalta con borde dorado la tarjeta seleccionada actualmente
        for carta, faccion in self._botones_carta:
            if faccion["nombre"] == self._seleccion:
                carta.config(highlightbackground=COLOR_ORO_BRILLANTE, highlightthickness=3)
            else:
                carta.config(highlightbackground=COLOR_SEPARADOR, highlightthickness=2)

    def _confirmar(self): 
        # Confirma la selección de facción y la guarda en usuarios.json mediante GestorUsuarios.asignar_faccion()
        if not self._seleccion:
            self._label_msg.config(text="Elegí una facción antes de continuar.", fg=COLOR_SANGRE)
            return

        exito, mensaje = self.gestor.asignar_faccion(self.usuario["nombre"], self._seleccion)
        self._label_msg.config(text=mensaje, fg="#4a8c4a" if exito else COLOR_SANGRE)

        if exito and self.forzado:
            self.ventana.after(1000, self.ir_volver)

# Pantalla de guia de juego, que explica las mecánicas principales.
# Muestra las reglas del juego en formato de "libro" paginado,
# basadas en las reglas oficiales del proyecto.
class PantallaComoJugar:
    REGLAS = [
        {
            "titulo": "⚔  Objetivo del Juego",
            "texto": ("Dos jugadores se enfrentan: uno asume el rol de Defensor y el "
                      "otro el de Atacante.\n\n"
                      "El Defensor debe proteger su base central construyendo muros y "
                      "torres defensivas. El Atacante debe destruir esa base usando "
                      "diferentes unidades.\n\n"
                      "La partida se juega por rondas. El primer jugador que gane 3 "
                      "rondas se convierte en el ganador de la partida."),
        },
        {
            "titulo": "🗺  El Mapa y las Facciones",
            "texto": ("El campo de batalla es una cuadrícula de al menos 10x10 casillas, "
                      "donde se ubican la base central, los muros, las torres, las "
                      "unidades y los caminos libres. La base central siempre está en "
                      "una posición fija.\n\n"
                      "Antes de iniciar, cada jugador elige una facción distinta a la "
                      "de su rival. La facción cambia el aspecto visual de tus torres, "
                      "muros, unidades y base central."),
        },
        {
            "titulo": "🛡  Rol del Defensor",
            "texto": ("Al inicio de cada ronda el Defensor recibe dinero y construye "
                      "sus defensas antes de que llegue el ataque.\n\n"
                      "• Puede construir muros y al menos 3 tipos de torres "
                      "(básica, pesada y mágica).\n"
                      "• Cada torre tiene costo, vida, daño, alcance y una habilidad "
                      "especial.\n"
                      "• Gana dinero extra por cada unidad enemiga eliminada."),
        },
        {
            "titulo": "⚔  Rol del Atacante",
            "texto": ("El Atacante juega después de que el Defensor termina de "
                      "construir, comprando y colocando sus unidades.\n\n"
                      "• Puede comprar al menos 3 tipos de unidades "
                      "(soldado básico, tanque y unidad rápida).\n"
                      "• Cada unidad tiene costo, vida, daño, velocidad y una "
                      "habilidad especial.\n"
                      "• Gana dinero al dañar una torre, destruirla o dañar la base."),
        },
        {
            "titulo": "🔄  Desarrollo de una Ronda",
            "texto": ("Cada ronda sigue siempre el mismo orden:\n\n"
                      "1. El Defensor recibe su dinero inicial.\n"
                      "2. El Defensor coloca muros y torres.\n"
                      "3. El Atacante recibe su dinero inicial.\n"
                      "4. El Atacante compra y coloca sus unidades.\n"
                      "5. Se ejecuta la fase de combate.\n"
                      "6. Se determina el ganador de la ronda.\n"
                      "7. Se actualiza el marcador.\n"
                      "8. Si nadie ha ganado 3 rondas, empieza una nueva."),
        },
        {
            "titulo": "🏆  Condiciones de Victoria",
            "texto": ("El Defensor gana la ronda si:\n"
                      "• El Atacante se queda sin dinero.\n"
                      "• Todas las unidades atacantes son eliminadas.\n"
                      "• La base central no fue destruida.\n\n"
                      "El Atacante gana la ronda si logra destruir la base central.\n\n"
                      "El primer jugador en ganar 3 rondas gana la partida, y esa "
                      "victoria queda registrada en su cuenta."),
        },
    ]

    def __init__(self, ventana, utils, estado_musica, ir_a_menu): 
        # Inicializa la pantalla de "Cómo Jugar" con la ventana, utilidades, estado de música y callback para volver al menú
        self.ventana       = ventana
        self.utils         = utils
        self.estado_musica = estado_musica
        self.ir_a_menu      = ir_a_menu
        self._pagina        = 0

    def mostrar(self): # Limpia la ventana y construye la pantalla de "Cómo Jugar"
        for widget in self.ventana.winfo_children():
            widget.destroy()

        ancho = 900
        alto  = 620

        canvas = tk.Canvas(self.ventana, width=ancho, height=alto,bg=COLOR_FONDO, highlightthickness=0)
        canvas.place(x=0, y=0)
        self.utils.dibujar_fondo_piedra(canvas, ancho, alto)
        canvas.create_rectangle(0, 0, ancho, alto,fill=COLOR_FONDO, stipple="gray50", outline="")
        self.utils.borde_dorado(canvas, ancho, alto)

        canvas.create_rectangle(110, 95, 790, 500,fill=COLOR_PIEDRA, outline=COLOR_SEPARADOR, width=2)
        canvas.create_rectangle(112, 97, 788, 498, fill="", outline=COLOR_ORO, width=1)

        tk.Label(self.ventana, text="📜  CÓMO JUGAR  📜",bg=COLOR_FONDO, fg=COLOR_ORO,font=("Georgia", 22, "bold")).place(relx=0.5, y=65, anchor="center")

        self._frame = tk.Frame(self.ventana, bg=COLOR_PIEDRA)
        self._frame.place(relx=0.5, y=290, anchor="center")

        self._btn_anterior = self.utils.boton_medieval(self.ventana, "◄  ANTERIOR",self._pagina_anterior, COLOR_TEXTO)
        self._btn_anterior.place(x=160, y=460, anchor="center")

        self._btn_siguiente = self.utils.boton_medieval(self.ventana, "SIGUIENTE  ►", self._pagina_siguiente, COLOR_TEXTO)
        self._btn_siguiente.place(x=740, y=460, anchor="center")

        self._label_pagina = tk.Label(self.ventana, text="", bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE, font=("Courier", 9))
        self._label_pagina.place(relx=0.5, y=495, anchor="center")

        btn_volver = self.utils.boton_medieval(self.ventana, "←  VOLVER AL MENÚ", self.ir_a_menu, COLOR_TEXTO)
        btn_volver.place(relx=0.5, y=545, anchor="center")

        tk.Label(self.ventana,text="ITCR  ·  Introducción a la Programación  ·  2026", bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

        self._construir_pagina()

    def _construir_pagina(self): # Construye la página actual de reglas según self._pagina
        for w in self._frame.winfo_children():
            w.destroy()

        regla = self.REGLAS[self._pagina]

        tk.Label(self._frame, text=regla["titulo"], bg=COLOR_PIEDRA, fg=COLOR_ORO_BRILLANTE,font=("Georgia", 15, "bold")).pack(pady=(20, 10))

        tk.Label(self._frame, text="━━━━━━━  ✦  ━━━━━━━",bg=COLOR_PIEDRA, fg=COLOR_SEPARADOR,font=("Courier", 10)).pack(pady=(0, 16))

        tk.Label(self._frame, text=regla["texto"],bg=COLOR_PIEDRA, fg=COLOR_TEXTO,font=("Courier", 10), justify="left",wraplength=620).pack(padx=40, pady=(0, 20))

        self._label_pagina.config(text=f"Página {self._pagina + 1} de {len(self.REGLAS)}")

        self._btn_anterior.config(state="disabled" if self._pagina == 0 else "normal")
        self._btn_siguiente.config(state="disabled" if self._pagina == len(self.REGLAS) - 1 else "normal")

    def _pagina_anterior(self): # Muestra la página anterior de reglas si es posible
        if self._pagina > 0:
            self._pagina -= 1
            self._construir_pagina()

    def _pagina_siguiente(self): # Muestra la página siguiente de reglas si es posible
        if self._pagina < len(self.REGLAS) - 1:
            self._pagina += 1
            self._construir_pagina()


# PANTALLA SORTEO DE ROLES
# Antes de iniciar la Ronda 1, se sortea al azar quién será el
# Defensor y quién el Atacante.

class PantallaRoles: # Pantalla de sorteo de roles para la Ronda 1

    def __init__(self, ventana, utils, jugadores, ir_a_menu, ir_continuar):
        self.ventana      = ventana
        self.utils        = utils
        self.jugadores    = jugadores
        self.ir_a_menu     = ir_a_menu
        self.ir_continuar  = ir_continuar
        # Sorteo al azar de roles para la Ronda 1
        self.numero_defensor = random.choice([1, 2])
        self.numero_atacante = 2 if self.numero_defensor == 1 else 1

    def mostrar(self): # Limpia la ventana y construye la pantalla de sorteo de roles
        for widget in self.ventana.winfo_children():
            widget.destroy()

        ancho = 900
        alto  = 620

        canvas = tk.Canvas(self.ventana, width=ancho, height=alto,bg=COLOR_FONDO, highlightthickness=0)
        canvas.place(x=0, y=0)
        self.utils.dibujar_fondo_piedra(canvas, ancho, alto)
        canvas.create_rectangle(0, 0, ancho, alto,fill=COLOR_FONDO, stipple="gray50", outline="")
        self.utils.borde_dorado(canvas, ancho, alto)

        tk.Label(self.ventana, text="🎲  SORTEO DE ROLES — RONDA 1  🎲",bg=COLOR_FONDO, fg=COLOR_ORO,font=("Georgia", 22, "bold")).place(relx=0.5, y=80, anchor="center")

        tk.Label(self.ventana, text="━━━━━━━  ✦  ━━━━━━━",bg=COLOR_FONDO, fg=COLOR_SEPARADOR,font=("Courier", 12)).place(relx=0.5, y=118, anchor="center")

        nombre_defensor = self.jugadores[self.numero_defensor]["nombre"]
        nombre_atacante = self.jugadores[self.numero_atacante]["nombre"]

        # Tarjeta del Defensor
        canvas.create_rectangle(110, 200, 430, 420,fill=COLOR_PIEDRA, outline=COLOR_ORO, width=2)
        tk.Label(self.ventana, text="🛡", bg=COLOR_PIEDRA,font=("Georgia", 36)).place(x=270, y=250, anchor="center")
        tk.Label(self.ventana, text="DEFENSOR", bg=COLOR_PIEDRA, fg=COLOR_ORO_BRILLANTE,font=("Georgia", 16, "bold")).place(x=270, y=300, anchor="center")
        tk.Label(self.ventana, text=f"Jugador {self.numero_defensor}", bg=COLOR_PIEDRA,fg=COLOR_TEXTO_TENUE, font=("Courier", 10)).place(x=270, y=335, anchor="center")
        tk.Label(self.ventana, text=nombre_defensor, bg=COLOR_PIEDRA, fg=COLOR_TEXTO,font=("Courier", 13, "bold")).place(x=270, y=362, anchor="center")

        # Tarjeta del Atacante
        canvas.create_rectangle(470, 200, 790, 420,fill=COLOR_PIEDRA, outline=COLOR_SANGRE, width=2)
        tk.Label(self.ventana, text="⚔", bg=COLOR_PIEDRA,font=("Georgia", 36)).place(x=630, y=250, anchor="center")
        tk.Label(self.ventana, text="ATACANTE", bg=COLOR_PIEDRA, fg=COLOR_SANGRE,font=("Georgia", 16, "bold")).place(x=630, y=300, anchor="center")
        tk.Label(self.ventana, text=f"Jugador {self.numero_atacante}", bg=COLOR_PIEDRA, fg=COLOR_TEXTO_TENUE, font=("Courier", 10)).place(x=630, y=335, anchor="center")
        tk.Label(self.ventana, text=nombre_atacante, bg=COLOR_PIEDRA, fg=COLOR_TEXTO,font=("Courier", 13, "bold")).place(x=630, y=362, anchor="center")

        btn_continuar = self.utils.boton_medieval(self.ventana, "⚔  COMENZAR RONDA 1  ⚔",self._continuar, COLOR_ORO)
        btn_continuar.place(relx=0.5, y=480, anchor="center")

        btn_volver = self.utils.boton_medieval(self.ventana, "←  VOLVER AL MENÚ",self.ir_a_menu, COLOR_TEXTO)
        btn_volver.place(relx=0.5, y=530, anchor="center")

        tk.Label(self.ventana,text="ITCR  ·  Introducción a la Programación  ·  2026",bg=COLOR_FONDO, fg=COLOR_TEXTO_TENUE,font=FUENTE_PEQUENA).place(relx=0.5, rely=0.97, anchor="center")

    def _continuar(self): # Llama al callback ir_continuar con los roles sorteados para iniciar la partida
        roles = {"defensor": self.numero_defensor, "atacante": self.numero_atacante}
        self.ir_continuar(roles)



# INICIO DEL PROGRAMA
# Aquí se crea la ventana, los servicios compartidos, y se navega
# entre pantallas mediante callbacks.

ventana = tk.Tk()
ventana.title("Defensa y Asalto de Base")
ventana.geometry("900x620")
ventana.resizable(False, False)
ventana.config(bg=COLOR_FONDO)

# Servicios compartidos (se crean una sola vez)
utils  = Utilidades()
gestor = GestorUsuarios()

# Datos de los dos jugadores de la partida actual
jugadores = {1: {}, 2: {}}

# Estado de la música (diccionario compartido entre pantallas)
estado_musica = {"actual": "", "activa": False, "pausada": False}

# Funciones de navegación (callbacks entre pantallas)
def ir_a_intro():
    pantalla = PantallaIntro(ventana, utils, estado_musica, ir_a_login_jugador1)
    pantalla.mostrar()

def ir_a_login_jugador1():
    # Reinicia ambos jugadores e inicia el flujo de login desde cero
    global jugadores
    jugadores = {1: {}, 2: {}}
    pantalla = PantallaLogin(ventana, utils, gestor, 1, ir_a_login_jugador2)
    pantalla.mostrar()

def ir_a_login_jugador2(usuario1):
    global jugadores
    jugadores[1] = usuario1
    pantalla = PantallaLogin(ventana, utils, gestor, 2, ir_a_menu,nombre_excluido=usuario1["nombre"])
    pantalla.mostrar()

def ir_a_menu(usuario2): #  Se llama después de que el segundo jugador inicia sesión correctamente
    global jugadores
    jugadores[2] = usuario2
    ir_a_menu_actual()

def ir_a_menu_actual(): # Muestra el menú principal con los dos jugadores ya logueados
    pantalla = PantallaMenu(ventana, utils, gestor, jugadores, estado_musica,ir_a_jugar, ir_a_top, ir_a_como_jugar, ir_a_cuenta)
    pantalla.mostrar()

def ir_a_jugar():
    # Verifica que ambos jugadores tengan facción antes de avanzar
    falta = _jugador_sin_faccion()
    if falta:
        pantalla = PantallaFaccion(ventana, utils, gestor, jugadores, falta,ir_a_jugar, forzado=True)
        pantalla.mostrar()
        return
    pantalla = PantallaRoles(ventana, utils, jugadores, ir_a_menu_actual, ir_a_partida)
    pantalla.mostrar()

def _jugador_sin_faccion():
    # Retorna el número del primer jugador sin facción asignada, o None si ambos tienen
    for numero in (1, 2):
        if not gestor.obtener_faccion(jugadores[numero]["nombre"]):
            return numero
    return None

def ir_a_partida(roles): # Se llama después de que se sortean los roles y se inicia la partida
    print(f"[DEBUG] Defensor: Jugador {roles['defensor']} "
          f"({jugadores[roles['defensor']]['nombre']}) | "
          f"Atacante: Jugador {roles['atacante']} "
          f"({jugadores[roles['atacante']]['nombre']})")
    # TODO: pantalla del tablero de juego (Ronda 1)

def ir_a_top(): # Muestra la pantalla de ranking de jugadores según victorias
    pantalla = PantallaTop(ventana, utils, gestor, estado_musica, ir_a_menu_actual)
    pantalla.mostrar()

def ir_a_como_jugar(): # Muestra la pantalla de guía de juego con las reglas y mecánicas
    pantalla = PantallaComoJugar(ventana, utils, estado_musica, ir_a_menu_actual)
    pantalla.mostrar()

def ir_a_cuenta(pagina_inicial=1): # Muestra la pantalla de cuenta del usuario logueado, con la página inicial (1 o 2)
    pantalla = PantallaCuenta(ventana, utils, gestor, jugadores, estado_musica,ir_a_menu_actual, ir_a_login_jugador1, ir_a_faccion, pagina_inicial)
    pantalla.mostrar()

def ir_a_faccion(numero_jugador): # Muestra la pantalla de selección de facción para el jugador indicado (1 o 2)
    pantalla = PantallaFaccion(ventana, utils, gestor, jugadores, numero_jugador,lambda: ir_a_cuenta(numero_jugador), forzado=False)
    pantalla.mostrar()

# Inicia el programa mostrando la pantalla de introducción
ir_a_intro()
ventana.mainloop()