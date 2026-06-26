# Defensa y Asalto de Base

Juego de estrategia por turnos para dos jugadores desarrollado en Python con Tkinter.
Cada jugador elige un rol por ronda: uno defiende su base construyendo torres y muros,
el otro ataca enviando unidades. Gana quien acumule más victorias de ronda.

---

## Requisitos

- Python **3.10 o superior** (probado en Python 3.14)
- pip (incluido con Python)

### Dependencias externas

| Librería | Uso |
|----------|-----|
| `pygame` | Reproducción de música |
| `tkinter` | Interfaz gráfica (incluido con Python en Windows) |

> `json`, `hashlib`, `os`, `random` y `abc` son parte de la librería estándar, no requieren instalación.

---

##  Instalación

### 1. Descomprimir el ZIP

Extraé el archivo en cualquier carpeta. La estructura interna debe quedar así:

```
TOWER-DEFENSE/
│
├── Defensa_y_Asalto.py       ← archivo principal del juego
├── usuarios.json              ← base de datos de jugadores (se crea automáticamente)
├── README.md
│
├── assets/                    ← imágenes de unidades y estructuras por facción
│   ├── Base Central/
│   ├── Muros/
│   ├── Soldado/
│   ├── Tanque/
│   ├── Torre Canon/
│   ├── Torre Sanadora/
│   ├── Torre Vigia/
│   └── Unidad Rapida/
│
├── Sound/                     ← música del juego
│   ├── in_game/
│   │   ├── Tower1.mp3
│   │   ├── Tower2.mp3
│   │   └── Tower3.mp3
│   └── Menu/
│       └── Tower0.mp3
│
└── Documents/                 ← documentación del proyecto
    ├── Atributos_Proyecto.pdf
    ├── Documentacion_Defensa_y_Asalto_de_Base.pdf
    ├── Manual_de_Usuario.pdf
    └── Videos.txt
```

>  No muevas ni renombres ninguna carpeta. El juego usa rutas relativas a su propia ubicación.

### 2. Instalar pygame

Abrí una terminal (CMD, PowerShell o Terminal) y ejecutá:

```bash
pip install pygame
```

Si tenés varias versiones de Python instaladas:

```bash
pip3 install pygame
```

### 3. Verificar tkinter (solo si hay error)

En Windows tkinter viene incluido con Python. Si al ejecutar el juego aparece un error de `tkinter`, reinstalá Python desde [python.org](https://www.python.org/downloads/) asegurándote de marcar la opción **"tcl/tk and IDLE"** durante la instalación.

---

##  Cómo ejecutar el juego

### Opción A — Doble clic (Windows)

Hacé doble clic sobre el archivo `Defensa_y_Asalto.py`. Si Python está correctamente instalado y asociado a archivos `.py`, el juego abre directamente.

### Opción B — Terminal (recomendado)

1. Abrí una terminal
2. Navegá hasta la carpeta del juego:

```bash
cd ruta/a/TOWER-DEFENSE
```

3. Ejecutá el juego:

```bash
python Defensa_y_Asalto.py
```

O en sistemas con Python 3 como `python3`:

```bash
python3 Defensa_y_Asalto.py
```

### Opción C — Archivo de acceso rápido (recomendado para nuevos usuarios)

1. Asegurate de tener Python y pygame instalados (ver sección de instalación)
2. En la carpeta del juego encontrarás el archivo `Jugar.bat`
3. Hacé doble clic sobre él — el juego abre directamente sin necesidad de abrir ningún código

### Opción D — VS Code

1. Abrí la carpeta `TOWER-DEFENSE` en VS Code
2. Abrí el archivo `Defensa_y_Asalto.py`
3. Presioná **F5** o el botón ▶ de la esquina superior derecha

---

##  Cómo jugar (resumen rápido)

1. **Pantalla de inicio** — Presioná cualquier tecla para comenzar
2. **Login** — Cada jugador inicia sesión o crea una cuenta
3. **Facción** — Cada jugador elige su facción (Medieval, Futurista o Naturaleza). Los dos deben ser de **facciones distintas**
4. **Menú principal** — Elegí "Jugar" para iniciar una partida
5. **Sorteo de roles** — El juego asigna aleatoriamente quién defiende y quién ataca en la primera ronda
6. **Ronda**:
   - El **defensor** coloca primero la Base Central y luego torres/muros en la zona verde
   - El **atacante** coloca sus unidades en la zona roja
   - Se inicia el combate automático por turnos
7. **Resultados** — Se muestra quién ganó la ronda y el marcador
8. Los roles se **invierten** en la siguiente ronda
9. Gana la partida el primero en ganar **3 rondas**

---

## Estructura del proyecto

```
Defensa_y_Asalto.py    Código fuente completo (pantallas, lógica, economía, combate)
usuarios.json          Registro persistente de usuarios, facciones y victorias
assets/                Sprites de cada unidad/estructura divididos por facción
Sound/                 Pistas de música para menú y partida
Documents/             Documentación técnica y manual de usuario
README.md              Este archivo
```

---

## Créditos

Proyecto desarrollado para el curso **Introducción a la Programación — ITCR 2026**.

---

## Notas adicionales

- El archivo `usuarios.json` se crea automáticamente la primera vez que se registra un usuario. No lo eliminés o perderás las cuentas guardadas.
- La música requiere que la carpeta `Sound/` esté en su lugar. Si no existe, el juego funciona igualmente pero sin audio.
- Si el juego se ve cortado en pantalla, verificá que la resolución de tu monitor sea al menos **1280×800**.