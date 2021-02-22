# Missionaries and cannibals

Juego 2D Puzzle de misioneros y caníbales en python 

**es con interfaz gráfica**

## Setup
tener python3 en la pc :P

1) clonar el repositorio
2) `py -m pip install pygame`, o `python3 -m pip install pygame`
3) `main.py`

## Uso
- Arrastrar el mouse con click izquierdo: mover caníbales/misioneros
- 'Q': activar modo bot -> una IA resuelve el puzzle
- 'R': poner en movimiento el bote (necesita 1 persona al menos)

## Puzzle
no voy a explicar profundamente cómo funciona el juego, pero las reglas básicas son las siguientes:
- hay 1 **río** que separa 2 **lados**
- en el lado "A" se encuentran inicialmente **6 personas**: **3 misioneros** y **3 caníbales**
- en el río hay **1 bote** que admite **2 personas**
- el **bote** puede adoptar **3 estados**: estar en el lado "A" (lado malo), estar en movimiento y estar en el lado "B" (lado bueno)
- el **bote** para ponerse en movimiento requiere tener al menos **1 persona** subida
- **objetivo**: llevar del lado "A" al lado "B" a las 6 personas usando el bote
- **NUNCA** puede haber **más** CANÍBALES que MISIONEROS (tanto en lado "A" como en lado "B"); porque los caníbales comen a los misioneros si los superan en número

hay muchos artículos/videos que explican el juego mejor que yo :D

## Más data del puzzle
https://en.wikipedia.org/wiki/Missionaries_and_cannibals_problem
