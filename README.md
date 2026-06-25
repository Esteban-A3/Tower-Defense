# 🗺️ Mapa-y-sistema-de-tienda — Alfa del Juego + Sistema Económico

> Rama: `Mapa-y-sistema-de-tienda` · Proyecto — Defensa y Asalto de Base | ITCR | Introducción a la Programación | 2026

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-orange?style=flat)
![Branch](https://img.shields.io/badge/Rama-Mapa--y--sistema--de--tienda-purple?style=flat)
![Estado](https://img.shields.io/badge/Estado-Archivo%20Histórico-gray?style=flat)
![Proyecto](https://img.shields.io/badge/Proyecto-ITCR-red?style=flat)

---

## 📖 ¿Qué es esta rama?

Esta rama marca el primer gran hito de integración del proyecto. Aquí se juntaron por primera vez las clases de torres (`Estructuras.py`), tropas (`Tropas.py`) y base central (`Base_central.py`) sobre un mapa jugable con interfaz gráfica real.

Además se subió la **primera versión del sistema económico** (`economia.py`), que define las reglas de dinero, compras, recompensas y bonos entre rondas.

> Es la alfa funcional del juego — todo corre junto por primera vez.

---

## 🗂️ Archivos

| Archivo | Descripción |
|---------|-------------|
| `Base_central.py` | Clase de la base central del defensor. Importada directamente desde la rama `Torres`. |
| `Estructuras.py` | Clases de torres y muros. Importada directamente desde la rama `Torres`. |
| `Tropas.py` | Clases de unidades atacantes. Importada directamente desde la rama `Sistema-de-tropas`. |
| `economia.py` | **Primera versión del sistema económico.** Constantes de balance, clase `Billetera` y `EconomiaController`. |
| `sistema de tienda.py` | Primer archivo del sistema de tienda: interfaz de compra para ambos jugadores. |
| `Juego en beta.py` | Alfa del juego completo — integra el mapa, las clases y el motor de combate en una interfaz jugable. |
| `image.png` | Concepto visual del mapa usado como referencia de diseño. |

---

## 💰 Sistema Económico — `economia.py`

El archivo define todas las **constantes de balance** del juego y dos clases principales:

### Flujo de dinero

| Constante | Valor | Descripción |
|-----------|-------|-------------|
| `DINERO_INICIAL` | $500 | Saldo inicial de ambos jugadores en ronda 1 |
| `BONO_POR_RONDA` | $150 | Suma fija al inicio de cada ronda (desde ronda 2) |
| `DINERO_MAXIMO` | $800 | Tope acumulable — el exceso se descarta |

### Costos de compra

| Pieza | Costo |
|-------|-------|
| Torre Vigía | $80 |
| Muro | $30 |
| Peón | $60 |
| Artillería | $130 |
| Torre Sanadora | $150 |
| Tanque | $180 |
| Torre Cañón | $200 |

### Recompensas en combate

| Evento | Quién cobra | Monto |
|--------|-------------|-------|
| Eliminar Peón | Defensor | $25 |
| Eliminar Artillería | Defensor | $50 |
| Eliminar Tanque | Defensor | $70 |
| Destruir Muro | Atacante | $20 |
| Destruir Torre | Atacante | $60 |
| Daño a la base | Atacante | $1 por punto de daño |

### Bono de presión sostenida
El atacante recibe al inicio de cada ronda el **25% del daño total** que infligió a la base en la ronda anterior, hasta un máximo de $200. Premia mantener presión constante.

---

### Clase `Billetera`
Administra el saldo de un jugador. Encapsula todas las reglas para que ninguna otra parte del código tenga que aplicarlas manualmente.

| Método | Descripción |
|--------|-------------|
| `puede_comprar(costo)` | Verifica si hay saldo suficiente |
| `comprar(nombre_pieza)` | Descuenta el costo usando la tabla `COSTOS` |
| `ganar(cantidad)` | Suma respetando el tope de $800 |
| `aplicar_bono_ronda()` | Suma el bono fijo de inicio de ronda |
| `calcular_bono_daño()` | Calcula el 25% del daño hecho la ronda anterior |
| `reiniciar_daño_ronda()` | Resetea el contador al terminar cada ronda |

---

### Clase `EconomiaController`
Conecta la economía con el motor de combate. Se instancia con las billeteras de ambos jugadores y se llama en cada evento relevante.

```python
economia = EconomiaController(billetera_defensor, billetera_atacante)

economia.unidad_eliminada(unidad)     # torre mata a una tropa
economia.defensa_destruida(torre)     # tropa destruye una torre o muro
economia.daño_a_base(cantidad)        # tropa golpea la base central
economia.iniciar_nueva_ronda()        # transición entre rondas
```

---

## 🎮 Juego Beta — `Juego en beta.py`

Primera integración funcional del juego completo sobre un mapa **15×15** con interfaz Tkinter.

### Zonas del mapa
- **Zona verde** — zona de defensa: solo torres y muros
- **Zona gris** — zona de ataque: solo unidades atacantes

### Flujo de una partida de prueba

```
1. Defensor coloca torres y muros en la zona verde
        ↓
2. Defensor presiona "Defensor listo"
        ↓
3. Atacante coloca sus unidades en la zona gris
        ↓
4. Atacante presiona "Iniciar combate"
        ↓
5. El motor resuelve turnos automáticamente cada 800 ms
        ↓
6. Gana quien cumpla su condición primero
```

### Motor de combate (por turno)

```
Fase 1 — Unidades atacantes:
  → Si la base está al alcance: atacar base
  → Si hay estructura al alcance: atacar estructura
  → Si no: avanzar hacia la base (velocidad casillas/turno)

Fase 2 — Torres defensoras:
  → Atacan a la unidad con menos vida dentro de su rango
  → Activan habilidad especial si corresponde
  
Limpieza: se retiran del mapa las unidades y estructuras destruidas

Revisión: ¿base destruida? → gana atacante | ¿sin unidades? → gana defensor
```

---

## 🔗 Ramas del Repositorio

| Rama | Contenido |
|------|-----------|
| `main` | Código completo e integrado del juego |
| `Documentacion-y-seguimiento` | Documentación del proyecto y bitácora de avance |
| `Mapa-y-sistema-de-tienda` ← *estás aquí* | Alfa del juego + primera versión de la economía |
| `Sistema-de-tropas` | Clases de las unidades atacantes |
| `Torres` | Clases iniciales de la base central y estructuras defensivas |

---

## ⚙️ Requisitos

```bash
Python 3.10+
# No requiere librerías externas — solo tkinter (incluido en Python)
```

---

## 🚀 Cómo ejecutar la alfa

```bash
# Clonar solo esta rama
git clone --branch Mapa-y-sistema-de-tienda --single-branch https://github.com/tu-usuario/tu-repo.git

cd tu-repo

# Ejecutar el juego beta
python "Juego en beta.py"
```

> Asegurate de que `Base_central.py`, `Estructuras.py` y `Tropas.py` estén en la misma carpeta.

---

## 👥 Autores

**Esteban Sanchez · Dominick Robles** — ITCR, Introducción a la Programación, 2026
