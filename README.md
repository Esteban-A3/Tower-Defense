# ⚔️ Sistema-de-tropas — Clases de Unidades Atacantes

> Rama: `Sistema-de-tropas` · Proyecto — Defensa y Asalto de Base | ITCR | Introducción a la Programación | 2026

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-orange?style=flat)
![Branch](https://img.shields.io/badge/Rama-Sistema--de--tropas-red?style=flat)
![Estado](https://img.shields.io/badge/Estado-Archivo%20Histórico-gray?style=flat)
![Proyecto](https://img.shields.io/badge/Proyecto-ITCR-red?style=flat)

---

## 📖 ¿Qué es esta rama?

Esta rama contiene el **sistema completo de unidades atacantes** de *Defensa y Asalto de Base*. Aquí se diseñaron las tres tropas que el jugador **Atacante** puede desplegar para destruir la base enemiga: el Tanque, la Artillería y el Peón.

Cada unidad hereda de una clase base abstracta (`Unidad`) y define su propia **habilidad especial**, estadísticas y prioridad de movimiento.

> Sirve como referencia histórica del diseño orientado a objetos del sistema de combate.

---

## 🗂️ Archivos

| Archivo | Descripción |
|---------|-------------|
| `Tropas.py` | Contiene la clase abstracta `Unidad` y las tres clases concretas: `Tanque`, `Artilleria` y `Peon`. Define toda la lógica de vida, ataque, movimiento, turnos y habilidades especiales. |

---

## 🏗️ Arquitectura de Clases

```
Unidad (ABC)
├── atacar(objetivo)
├── puede_atacar_a(fila, columna)
├── puede_moverse()
├── avanzar_turno(contexto)
├── activar_habilidad(contexto)  ← abstracto
├── recibir_daño(cantidad)
├── curar(cantidad)
└── porcentaje_vida()
    │
    ├── Tanque          → habilidad: pulso de recuperación + modo emergencia
    ├── Artilleria      → habilidad: disparo perforante (2 objetivos)
    └── Peon            → habilidad: ataque doble (redirige si mata al primero)
```

---

## 👾 Unidades

### 🛡️ Tanque
> *"Avanza lento pero imparable. Cuando cae al 25% de vida, se detiene y se cura."*

| Estadística | Valor |
|-------------|-------|
| Vida | 90 hp |
| Daño | 30 |
| Velocidad | 1 casilla/turno |
| Alcance | 1 (cuerpo a cuerpo) |
| Habilidad | Cada 5 turnos: +20 hp |
| Emergencia | Bajo el 25% de vida: +6 hp/turno hasta recuperarse |
| Prioridad | Siempre avanza hacia la base central |

---

### 💣 Artillería
> *"Ataca desde lejos. Su disparo perforante atraviesa el primer objetivo y golpea al siguiente."*

| Estadística | Valor |
|-------------|-------|
| Vida | 55 hp |
| Daño | 22 |
| Velocidad | 2 casillas/turno |
| Alcance | 4 casillas |
| Habilidad | Cada 4 turnos: disparo perforante (2º objetivo recibe 60% del daño) |
| Prioridad de ataque | Torre → Muro → Base |

---

### ⚡ Peón
> *"El más rápido y el más frágil. En grupos es devastador gracias a su ataque doble."*

| Estadística | Valor |
|-------------|-------|
| Vida | 30 hp |
| Daño | 10 |
| Velocidad | 3 casillas/turno |
| Alcance | 1 (cuerpo a cuerpo) |
| Habilidad | Cada 2 turnos: ataque doble (se redirige si elimina al primero) |
| Prioridad de ataque | Torre → Muro → Base |

---

## ⚙️ Sistema de Turnos

El motor de combate llama a `avanzar_turno(contexto)` en cada unidad al inicio de su turno. El `contexto` es un diccionario que le pasa información del entorno al momento de ejecutar:

```python
contexto = {
    "objetivos_en_rango": [torre1, muro2],  # estructuras al alcance
    "log": ""                                # se rellena con el resultado
}
```

Cuando el contador interno alcanza `turnos_para_habilidad`, se dispara `activar_habilidad(contexto)` y el contador vuelve a 0.

---

## 🔗 Ramas del Repositorio

| Rama | Contenido |
|------|-----------|
| `main` | Código completo e integrado del juego |
| `Documentacion-y-seguimiento` | Documentación del proyecto y bitácora de avance |
| `Mapa-y-sistema-de-tienda` | Lógica del mapa de juego y sistema de compra de estructuras |
| `Sistema-de-tropas` ← *estás aquí* | Clases de las unidades atacantes |
| `Torres` | Clases iniciales de la base central y estructuras defensivas |

---

## ⚙️ Requisitos

```bash
Python 3.10+
```

> Esta rama usa solo la librería estándar de Python (`abc`). No requiere dependencias externas.

---

## 🚀 Cómo explorar

```bash
# Clonar solo esta rama
git clone --branch Sistema-de-tropas --single-branch https://github.com/tu-usuario/tu-repo.git

cd tu-repo

python Tropas.py
```

---

## 👥 Autores

**Esteban Sanchez · Dominick Robles** — ITCR, Introducción a la Programación, 2026
