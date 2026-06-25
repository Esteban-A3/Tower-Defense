# 🏰 Torres — Clases Base del Sistema Defensivo

> Rama: `Torres` · Proyecto — Defensa y Asalto de Base | ITCR | Introducción a la Programación | 2026

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-orange?style=flat)
![Branch](https://img.shields.io/badge/Rama-Torres-gold?style=flat)
![Estado](https://img.shields.io/badge/Estado-Archivo%20Histórico-gray?style=flat)
![Proyecto](https://img.shields.io/badge/Proyecto-ITCR-red?style=flat)

---

## 📖 ¿Qué es esta rama?

Esta rama conserva los **archivos iniciales** donde se diseñaron y construyeron las clases del sistema defensivo del juego. Es el punto de origen de toda la lógica de estructuras de *Defensa y Asalto de Base*: aquí se definió la estructura, atributos y comportamiento de la base central y las torres antes de integrarse al proyecto completo.

> Sirve como referencia histórica del proceso de diseño orientado a objetos del proyecto.

---

## 🗂️ Archivos

| Archivo | Descripción |
|---------|-------------|
| `Base_central.py` | Define la clase `BaseCentral`: la estructura principal del defensor. Contiene la lógica de vida, daño, destrucción y reinicio entre rondas. Su caída significa victoria inmediata del atacante. |
| `Estructuras.py` | Implementa las clases de torres y estructuras defensivas que el jugador Defensor puede colocar en el mapa para proteger la base. |

---

## 🏗️ Clase Principal — `BaseCentral`

```python
class BaseCentral:
    VIDA_MAXIMA = 200
    CELDAS = [(7, 7), (7, 8), (8, 7), (8, 8)]  # posición fija en el mapa
```

### Métodos clave

| Método | Descripción |
|--------|-------------|
| `recibir_daño(cantidad)` | Reduce la vida sin bajar de 0. Retorna el daño real aplicado. |
| `esta_destruida()` | Retorna `True` si la vida llegó a 0 → fin de ronda. |
| `esta_viva()` | Alias semántico para compatibilidad con el resto del código. |
| `porcentaje_vida()` | Devuelve un valor entre `0.0` y `1.0` para la barra de vida visual. |
| `reiniciar()` | Restaura la vida completa al iniciar una nueva ronda. |
| `resumen()` | Imprime el estado actual: `[Base Central] Vida: 180/200 (90%)` |

### Rol en el juego

La `BaseCentral` ocupa **4 celdas fijas** en el centro del mapa (`(7,7)` a `(8,8)`). El motor de combate la consulta al final de cada turno — si `esta_destruida()` devuelve `True`, la ronda termina con **victoria del Atacante**.

---

## 🔗 Ramas del Repositorio

| Rama | Contenido |
|------|-----------|
| `main` | Código completo e integrado del juego |
| `Documentacion-y-seguimiento` | Documentación del proyecto y bitácora de avance |
| `Mapa-y-sistema-de-tienda` | Lógica del mapa de juego y sistema de compra de estructuras |
| `Sistema-de-tropas` | Clases y lógica de las tropas atacantes |
| `Torres` ← *estás aquí* | Clases iniciales de la base central y estructuras defensivas |

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

cd tu-repo

python Base_central.py
python Estructuras.py
```

---

## 👥 Autores

**Esteban Sanchez · Dominick Robles** — ITCR, Introducción a la Programación, 2026
