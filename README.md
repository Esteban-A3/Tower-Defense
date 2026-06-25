# 🏰 Torres — Clases Base del Sistema Defensivo

> Rama: `Torres` · Proyecto — Defensa y Asalto de Base | ITCR | Introducción a la Programación | 2026

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Branch](https://img.shields.io/badge/Rama-Torres-gold?style=flat)
![Estado](https://img.shields.io/badge/Estado-Archivo%20Histórico-gray?style=flat)
![Proyecto](https://img.shields.io/badge/Proyecto-ITCR-red?style=flat)

---

## 📖 ¿Qué es esta rama?

Esta rama conserva los **archivos iniciales** donde se diseñaron y construyeron las clases de las torres del juego. Es el punto de origen del sistema defensivo de *Defensa y Asalto de Base*: aquí se definió la estructura, atributos y comportamiento de cada tipo de torre antes de integrarse al proyecto completo.

> Sirve como referencia histórica del proceso de diseño orientado a objetos del proyecto.

---

## 🗂️ Archivos

| Archivo | Descripción |
|---------|-------------|
| `Base_central.py` | Define la clase base de la que heredan todas las torres. Contiene los atributos y métodos comunes: costo, nivel, rango de ataque y lógica de mejora. |
| `Estructuras.py` | Implementa las clases concretas de cada tipo de torre, extendiendo `Base_central.py` con comportamientos específicos de ataque, daño y cadencia. |

---

## 🏗️ Arquitectura de Clases

```
Base_central.py
└── TorreBase
    ├── atributos: costo, nivel, rango, daño
    └── métodos: mejorar(), atacar(), describir()

Estructuras.py
├── TorreFlechas(TorreBase)
├── TorreCañon(TorreBase)
└── ... (demás tipos definidos aquí)
```

---

## 🔗 Relación con el Proyecto Principal

Esta rama forma parte del repositorio **Defensa y Asalto de Base**, un juego de estrategia para dos jugadores desarrollado completamente en Python con Tkinter.

| Rama | Contenido |
|------|-----------|
| `main` | Código completo e integrado del juego |
| `Torres` ← *estás aquí* | Clases iniciales del sistema de torres |

Las clases definidas aquí fueron la base para el sistema defensivo que el jugador **Defensor** utiliza durante la partida para proteger su base del jugador **Atacante**.

---

## ⚙️ Requisitos

```bash
Python 3.10+
```

> Esta rama no depende de librerías externas. Los archivos son clases puras sin interfaz gráfica.

---

## 🚀 Cómo explorar

```bash
# Clonar solo esta rama
git clone --branch Torres --single-branch https://github.com/tu-usuario/tu-repo.git

# Entrar al directorio
cd tu-repo

# Explorar los archivos
python Base_central.py
python Estructuras.py
```

---

## 👥 Autores

**Esteban Sanchez · Dominick Robles** — ITCR, Introducción a la Programación, 2026
