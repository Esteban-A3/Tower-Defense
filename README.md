# Defensa y Asalto de Base

> Proyecto Final — Introducción a la Programación | ITCR | Primer Semestre 2026

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-orange?style=flat)
![Pygame](https://img.shields.io/badge/Audio-Pygame-green?style=flat)
![Branch](https://img.shields.io/badge/Rama-main-brightgreen?style=flat)
![Commits](https://img.shields.io/badge/Commits-67-lightgray?style=flat)
![Proyecto](https://img.shields.io/badge/Proyecto-ITCR-red?style=flat)

---

## Descripción

*Defensa y Asalto de Base* es un juego de estrategia por turnos para **dos jugadores** desarrollado completamente en Python con Tkinter. Cada jugador elige un rol por ronda: uno **defiende** su base construyendo torres y muros, el otro **ataca** enviando unidades. Gana quien acumule más victorias de ronda.

Incluye sistema de cuentas de usuario, tres facciones jugables, economía por ronda, motor de combate automático por turnos y música de fondo.

---

## Estructura del Repositorio

```
TOWER-DEFENSE/
│
├── Defensa_y_Asalto.py       ← archivo principal — todo el código del juego
├── usuarios.json              ← base de datos de jugadores (se crea automáticamente)
├── Jugar.bat                  ← ejecutador directo (recomendado para nuevos usuarios)
├── README.md
│
├── assets/                    ← sprites de cada unidad y estructura por facción
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
│   ├── Menu/
│   │   └── Tower0.mp3
│   └── in_game/
│       ├── Tower1.mp3
│       ├── Tower2.mp3
│       └── Tower3.mp3
│
└── Documents/                 ← documentación del proyecto
    ├── Atributos_Proyecto.pdf
    ├── Documentacion_Defensa_y_Asalto_de_Base.pdf
    ├── Manual_de_Usuario.pdf
    └── Videos.txt
```

> No muevas ni renombres ninguna carpeta. El juego usa rutas relativas a su propia ubicación.

---

## Branches

| Rama | Contenido |
|------|-----------|
| `main` ← *estás aquí* | Código completo y funcional del juego |
| `Documentacion-y-seguimiento` | Documentación técnica, manual de usuario y videos de seguimiento |
| `Mapa-y-sistema-de-tienda` | Alfa del juego + primera versión del sistema económico |
| `Sistema-de-tropas` | Clases iniciales de las unidades atacantes |
| `Torres` | Clases iniciales de la base central y estructuras defensivas |

---

## Características

-  **Dos jugadores** — cada uno con su propia cuenta registrada
-  **3 facciones** — Medieval, Futurista y Naturaleza (deben ser distintas entre jugadores)
-  **Mapa 15×15** — zona verde para defensas, zona roja para unidades
-  **3 tipos de unidades** — Soldado, Tanque y Unidad Rápida, cada uno con habilidad especial
-  **4 estructuras defensivas** — Torre Vigía, Torre Cañón, Torre Sanadora y Muro
-  **Sistema económico** — dinero inicial, bonos por ronda, recompensas en combate y bono de presión
-  **Motor de combate automático** — resuelve cada turno sin intervención del jugador
-  **Mejor de 5 rondas** — gana quien llegue primero a 3 victorias
-  **Música** — pista diferente para menú y partida
-  **Cuentas persistentes** — usuarios guardados en `usuarios.json` entre sesiones

---

## Requisitos

```bash
Python 3.10+
pip install pygame
```

> `tkinter`, `json`, `hashlib`, `os`, `random` y `abc` son parte de la librería estándar — no requieren instalación.

---

## Cómo ejecutar

### Opción A — Archivo de acceso rápido (recomendado)
Hacé doble clic sobre `Jugar.bat`. El juego abre directamente sin necesidad de abrir ningún código.

### Opción B — Terminal
```bash
cd ruta/a/TOWER-DEFENSE
python Defensa_y_Asalto.py
```

### Opción C — VS Code
Abrí la carpeta en VS Code, abrí `Defensa_y_Asalto.py` y presioná **F5**.

---

## Cómo jugar

```
1. Pantalla de inicio     → presioná cualquier tecla
2. Login                  → cada jugador inicia sesión o crea una cuenta
3. Facción                → cada jugador elige su facción (deben ser distintas)
4. Menú principal         → elegí "Jugar"
5. Sorteo de roles        → el juego asigna aleatoriamente quién defiende y quién ataca
         ↓
   ┌─────────────────────────────────────┐
   │            RONDA                    │
   │  Defensor → coloca torres y muros   │
   │  Atacante → coloca sus unidades     │
   │  Combate automático por turnos      │
   └─────────────────────────────────────┘
         ↓
6. Resultados             → se muestra quién ganó la ronda y el marcador
7. Los roles se invierten → nueva ronda con roles cambiados
8. Victoria               → primer jugador en ganar 3 rondas gana la partida
```

---

## Unidades y Estructuras

### Unidades atacantes

| Unidad | Vida | Daño | Velocidad | Alcance | Habilidad especial |
|--------|------|------|-----------|---------|-------------------|
| Soldado | 30 hp | 8 | 1 casilla/turno | 1 | Ataque doble cada 3 turnos |
| Tanque | 90 hp | 30 | 1 casilla/turno | 1 | Pulso de curación cada 5 turnos + recuperación de emergencia bajo 25% de vida |
| Unidad Rápida | 18 hp | 5 | 2 casillas/turno | 1 | Aumento de velocidad cada 3 turnos |

### Estructuras defensivas

| Estructura | Rol |
|------------|-----|
| Torre Vigía | Cobertura de largo alcance |
| Torre Cañón | Alto daño en área reducida |
| Torre Sanadora | Cura torres cercanas durante el combate |
| Muro | Barrera sin ataque — absorbe daño para proteger las torres |

---

## Sistema Económico

| Concepto | Valor |
|----------|-------|
| Dinero inicial | $500 por jugador |
| Bono por ronda | +$150 al inicio de cada ronda (desde ronda 2) |
| Tope acumulable | $800 — el exceso se descarta |
| Bono de presión | El atacante recibe el 25% del daño hecho a la base como dinero extra en la siguiente ronda (máx. $200) |

---

## Notas

- `usuarios.json` se crea automáticamente al registrar el primer usuario. No lo eliminés o perderás las cuentas guardadas.
- Sin la carpeta `Sound/` el juego funciona igual pero sin audio.
- Resolución mínima recomendada: **1280×800**.

---

## Documentación

La documentación completa del proyecto se encuentra en la carpeta `Documents/` y en la rama [`Documentacion-y-seguimiento`](../../tree/Documentacion-y-seguimiento).

---

## Autores

**Esteban Sanchez · Dominick Robles** — ITCR, Introducción a la Programación, 2026
