#  autor: @wandinggc

import pygame

from constants import *
from entidades import *
from screens import *

# -------------------------------------------------------------------------------------
# Misioneros y Canibales, juego
# Reglas
# Existen:
#  a) 1 grupo de 3 Canibales
#  b) 1 grupo de 3 Misioneros
#  c) Dos lados separados por un río.
#  d) Un bote que puede transportar a dos personas.
#
#  Ambos grupos se encuentran inicialmente de un lado del río.
#
#  Objetivo:
#  Encontrar una forma de llevar a TODOS (a las 6 personas) al otro lado del río, evitando en todo momento que el grupo de
#  misioneros tenga un número menor de personas respecto del número de caníbales.
#
#  Si el número de misioneros en un lado de la tierra es menor al número de caníbales en el mismo lado, los caníbales devoran a los misioneros
# -------------------------------------------------------------------------------------

# Clase principal del juego, contiene screens, un screenhandler y pone en funcionamiento el módulo pygame (interfaz gráfica)
class Game:
    def __init__(self):
        import os
        os.environ['SDL_VIDEO_CENTERED'] = '1' # Permite que la ventana de la aplicación se cree inicialmente "centrada" en la pantalla
        self.running = False # Flag / bool que permite controlar el inicio y el fin del programa
        self.clock = pygame.time.Clock() # Reloj del módulo pygame. Se utiliza para múltiples cosas dentro del game loop (bucle de juego)
        self.size = SIZE_VENTANA # Almacenar el tamaño de la ventana como una list con el formato [ancho_ventana, altura_ventana]
        self.window = pygame.display.set_mode(self.size) # Establecer un tamaño [ancho, altura] para la ventana
        self.framerate = 60 # FPS del juego
        pygame.display.set_caption("Misioneros y Canibales") # Cambiar el título de la ventana

    # Método que se encarga de iniciar la aplicación/programa del juego, como tal (inicializar cosas + llamar al bucle princiapl)
    def run(self):
        # Inicializar el módulo pygame
        pygame.init()

        # Eventos
        self.mouseClicks = pygame.mouse.get_pressed() # booleano para registrar clicks del mouse (izquierdo, derecho)
        self.mouseState = pygame.mouse.get_pos() # posicion del mouse
        self.dragging_entity = False # booleano que indica si se está arrastrando algún misionero/canibal
        self.events = None

        # Instanciar objetos
        self.font = pygame.font.Font(FONT_PATH, 48) # almacenar el objeto de la fuente (.ttf), que se usa para mostrar texto (48 pixeles)
        self.font16 = pygame.font.Font(FONT_PATH, 16) # objeto de fuente mas chica (16 pixeles)
        self.font64 = pygame.font.Font(FONT_PATH, 64) # almacenar el objeto de la fuente (.ttf), que se usa para mostrar texto (64 pixeles)
        self.screen_handler = ScreenHandler(self) # se instancia el objeto ScreenHandler

        # Correr el bucle principal del juego
        self.running = True # establecer el flag en True, indicando que el juego se encuentra corriendo (running)
        self.main_loop() # despues de todas las inicializaciones, se invoca al bucle principal

    # bucle de juego princiapl
    def main_loop(self):
        while self.running:
            # dt (delta_time). Es, en milisegundos, la cantidad de tiempo que pasó entre la iteración actual del while self.running, y la iteración anterior. Si el juego corre a 60 FPS, esto indica que el código ejecutado acá adentro debería llamarse 60 veces en un segundo. Para que eso ocurra, cada iteración debe ocurrir cada 0.016 segundos aproximadamente (16,667... milisegundos)
            dt = self.clock.tick(self.framerate) / 1000.0

            # Actualizar el estado de los eventos, obtenidos por pygame
            self.events = pygame.event.get()

            self.handle_input()

            # Limpiar la pantalla a color negro
            self.window.fill((0,0,0))

            # Invocar el update() en screen_handler. screen_handler llamará el update() de la pantalla que se encuentre activa.
            self.screen_handler.update(dt, self.events)
            # Invocar el draw() en screen_handler. screen_handler llamará el draw() de la pantalla que se encuentre activa.
            self.screen_handler.draw(self.window)

            # Manejar eventos (cerrar ventana)
            self.handle_events()

            # este metodo se utiliza para llevar todo lo que se ha dibujado en self.window (la ventana) en esta iteración a nuestra pantalla / monitor
            pygame.display.flip()

        # Al salir del bucle self.running, desinicializar el módulo pygame y terminar el programa
        pygame.quit()

    # Actualizar posicion y estado del mouse
    def handle_input(self):
        self.mouseClicks = pygame.mouse.get_pressed()
        self.mouseState = pygame.mouse.get_pos()

    # Manejar eventos en la ventana (presión de alguna tecla, click y estado del mouse, cerrar ventana...)
    def handle_events(self):
        for e in self.events:
            if(e.type == pygame.QUIT): # Al cerrar la ventana con la "X", cambiar el flag running a False, para salir del bucle del main_loop
                self.running = False

game = Game() # se instancia un objeto de la clase Game
game.run() # se llama al método que inicia el juego como tal (se pone a correr el bucle de juego)
