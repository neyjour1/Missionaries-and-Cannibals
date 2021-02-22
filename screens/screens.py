import os, sys, inspect
import pygame
import random

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from entidades import *
from constants import *

# programa que resuelve el problema de los misioneros y los canibales automáticamente mediante IA
import resolucion
solutions = []
resolucion.solve([3,3,1],[], solutions)

# Clase ScreenHandler. Contiene pantallas (pantalla de juego, menu, pantalla de fin). Permite utilizar cada pantalla por separado dentro del juego
class ScreenHandler:
    def __init__(self, game):
        self.game = game
        self.state = 0
        self.nextState = 0
        # self.screens = [GameScreen(self, game)]
        self.screens = [MenuScreen(self,game), GameScreen(self,game), EndScreen(self, game)]

    def draw(self, surface):
        self.screens[self.state].draw(surface)

    def update(self, dt, events):
        self.screens[self.state].update(dt, events)

    def get_screen(self, index):
        if(index >= 0 and index < len(self.screens)):
            return self.screens[index]
        return None

    def switch_screen(self, index):
        if(index >= 0 and index < len(self.screens)):
            self.state = index

# Superclase screen. Las clases children son: MenuScreen, EndScreen y GameScreen
class Screen:
    def __init__(self, sh, game):
        self.game = game
        self.screen_handler = sh
        self.pause = False

    def draw(self, surface):
        pass

    def update(self, dt, events):
        pass

    def switch_screen(self, n):
        self.screen_handler.switch_screen(n)

# Pantalla de menu, pantalla princiapl
class MenuScreen(Screen):
    def __init__(self, sh, game, mode=0):
        super().__init__(sh, game)
        self.title = "Misioneros y Canibales"
        self.titleSurface = self.game.font64.render(self.title, True, (127,255,127))
        self.playSurface = [self.game.font.render("Jugar", True, (255,255,255)), self.game.font.render("Jugar", True, (243,75,75))]
        self.exitSurface = [self.game.font.render("Salir del juego", True, (255,255,255)), self.game.font.render("Salir del juego", True, (243,75,75))]
        self.pos = [SIZE_VENTANA[0] // 2 - self.titleSurface.get_width() // 2, self.titleSurface.get_height()/2]
        self.playPos = [SIZE_VENTANA[0] // 2 - self.playSurface[0].get_width() // 2, 60+128]
        self.exitPos = [SIZE_VENTANA[0] // 2 - self.exitSurface[0].get_width() // 2, 60+198]
        self.hovering = [False, False]
        self.changeWindow = False

    def draw(self, surface):
        surface.fill((0,0,0))
        surface.blit(self.titleSurface, self.pos)
        surface.blit(self.playSurface[self.hovering[0]], self.playPos)
        surface.blit(self.exitSurface[self.hovering[1]], self.exitPos)

    def is_colliding_with_play(self, x, y, index=0):
        if(index == 0):
            surf = self.playSurface[0]
            pos = self.playPos
        elif(index == 1):
            surf = self.exitSurface[0]
            pos = self.exitPos

        return x >= pos[0] and x <= pos[0] + surf.get_width() and y >= pos[1] and y <= pos[1] + surf.get_height()

    def update(self, dt, events):
        mouseClicks = self.game.mouseClicks
        mouseState = self.game.mouseState
        self.hovering = [False, False]

        if(self.is_colliding_with_play(mouseState[0], mouseState[1])):
            self.hovering[0] = True
        if(self.is_colliding_with_play(mouseState[0], mouseState[1], 1)):
            self.hovering[1] = True

        if(self.hovering[0] and mouseClicks[0]):
            self.changeWindow = True

        elif(self.hovering[1] and mouseClicks[0]):
            self.game.running = False

        for e in events:
            if(e.type == pygame.KEYDOWN):
                if(e.key == pygame.K_r):
                    self.changeWindow = True

        if(self.changeWindow):
            self.screen_handler.get_screen(1).init_game()
            self.screen_handler.switch_screen(1)
            self.changeWindow = False

# Pantalla de fin (muestra cartel de derrota/victoria)
class EndScreen(Screen):
    def __init__(self, sh, game, mode=0):
        super().__init__(sh, game)
        self.font = game.font
        self.winTextSurface = self.font.render('Victoria!', True, (127,127,255))
        self.loseTextSurface = self.font.render('Has perdido...', True, (255,127,127))
        self.surface = None
        self.timer = 0
        self.change_screen_timer = 2.5
        self.pos = [0,0]
        self.set_mode(mode)

    def set_mode(self, mode):
        self.mode = mode
        self.get_draw()

    def get_draw(self):
        if(self.mode == 0):
            self.surface = self.winTextSurface
            self.pos[0] = SIZE_VENTANA[0] // 2 - self.winTextSurface.get_width() // 2
            self.pos[1] = SIZE_VENTANA[1] // 2 - self.winTextSurface.get_height() // 2
            return
        self.surface = self.loseTextSurface
        self.pos[0] = SIZE_VENTANA[0] // 2 - self.loseTextSurface.get_width() // 2
        self.pos[1] = SIZE_VENTANA[1] // 2 - self.loseTextSurface.get_height() // 2


    def draw(self, surface):
        surface.blit(self.surface, self.pos)

    def update(self, dt, events):
        self.timer += dt
        if(self.timer >= self.change_screen_timer):
            self.screen_handler.switch_screen(0)
            self.timer = 0

# Pantalla de juego
class GameScreen(Screen):
    def __init__(self, sh, game):
        super().__init__(sh, game)
        # preparar entidades, posiciones, y el juego en general
        self.init_game()


    def init_game(self, modo=0):
        self.game_over = False # para derrota
        self.game_won = False # para victoria
        self.dragging_entity = False

        self.movimientos = 0
        self.tiempo = 0.00

        self.tiempoSurface = self.game.font16.render("Tiempo: " + str(self.tiempo), True, (255,255,255))
        self.movimientosSurface = self.game.font16.render("Movimientos: " + str(self.movimientos), True, (255,255,255))
        self.misioneroSurface = self.game.font16.render("Misionero", True, (0,0,255))
        self.canibalSurface = self.game.font16.render("Canibal", True, (255,0,0))

        self.textoBalsaSurface = self.game.font16.render("R: Mover la balsa", True, (255,255,255))
        self.textoSolucionSurface = self.game.font16.render("Q: Solucion de busqueda", True, (255,255,255))

        self.surfacesPosition = [[5,5], [5,24]]


        if(modo == 0):
            self.modo_bot = False # activa la resolucion

        # el estado del juego se utiliza para determinar si hay una victoria/derrota
        self.game_state = [3,3,1] # [a,b,c], a=cantidad misioneros en lado malo; b=cantidad canibales en lado malo; c= cantidad bote en lado malo
        self.last_game_state = self.game_state

        screen_width = SIZE_VENTANA[0]
        self.datos_rio = [(66,165,245), pygame.Rect(screen_width/3, 0, screen_width/3, SIZE_VENTANA[1])] # color, pygame.Rect
        rect_rio = self.datos_rio[1]

        bote_width = 128
        bote_height = 64
        # bote_x = rect_rio[0] + bote_width // 4
        bote_x = rect_rio[0]
        bote_y = rect_rio[3]//2 - bote_height // 2

        centro_mapa_y = SIZE_VENTANA[1] // 2

        # Lista de entidades
        self.entidades = [
            Persona(tipo=0), # misionero
            Persona(tipo=0), # misionero
            Persona(tipo=0), # misionero

            Persona(tipo=1), # canibal
            Persona(tipo=1), # canibal
            Persona(tipo=1), # canibal

            Bote(bote_x, bote_y, bote_width, bote_height)
        ]

        self.acomodar_entidades_en_grid()

    def acomodar_entidades_en_grid(self):

        screen_width = SIZE_VENTANA[0]
        centro_mapa_y = SIZE_VENTANA[1] // 2

        entidades = self.entidades

        entity_width = entidades[0].width
        espaciado_horizontal = entity_width // 2
        espaciado_vertical = entity_width // 2

        espacios = 2

        cuadrado_width = entidades[0].width + entidades[1].width + entidades[2].width + espacios * espaciado_horizontal
        cuadrado_height = entidades[0].height + entidades[3].height + espaciado_vertical

        cuadrado_x = ((screen_width // 3) // 2 ) - cuadrado_width // 2
        cuadrado_y = centro_mapa_y - cuadrado_height//2

        self.cuadrado_spawn = pygame.Rect(cuadrado_x, cuadrado_y, cuadrado_width, cuadrado_height)
        self.cuadrado_destino = pygame.Rect(cuadrado_x+(screen_width//3)*2, cuadrado_y, cuadrado_width, cuadrado_height)

        self.spawn_posiciones = []
        self.destino_posiciones = []

        for x in range(6):
            if(x > 2):
                self.entidades[x].y = self.cuadrado_spawn.y + entity_width + espaciado_vertical
                self.entidades[x].x = self.cuadrado_spawn.x + entity_width * (x-3) + espaciado_horizontal * (x-3)
                cuadrado = pygame.Rect(self.entidades[x].x, self.entidades[x].y, entity_width, entity_width)
                cuadrado_destino = pygame.Rect(self.entidades[x].x + SIZE_VENTANA[0]//3 * 2, self.entidades[x].y, entity_width, entity_width)
                self.spawn_posiciones.append([cuadrado, self.entidades[x]])
                self.destino_posiciones.append([cuadrado_destino, None])
                self.entidades[x].position_slot = cuadrado
            else:
                self.entidades[x].x = self.cuadrado_spawn.x + entity_width * x  + espaciado_horizontal * x
                self.entidades[x].y = self.cuadrado_spawn.y
                cuadrado = pygame.Rect(self.entidades[x].x, self.entidades[x].y, entity_width, entity_width)
                cuadrado_destino = pygame.Rect(self.entidades[x].x + SIZE_VENTANA[0]//3 * 2, self.entidades[x].y, entity_width, entity_width)
                self.spawn_posiciones.append([cuadrado, self.entidades[x]])
                self.destino_posiciones.append([cuadrado_destino, None])
                self.entidades[x].position_slot = cuadrado

            self.entidades[x].update_rect()
            self.entidades[x].set_last_position(self.entidades[x].x, self.entidades[x].y)

    def draw(self, surface):

        surface.fill((0,128,0))

        pygame.draw.rect(surface, self.datos_rio[0], self.datos_rio[1]) # rio
        pygame.draw.rect(surface, [0,255,0], self.cuadrado_spawn) # spawn zona
        pygame.draw.rect(surface, [0,255,0], self.cuadrado_destino) # destino zona

        surface.blit(self.tiempoSurface, self.surfacesPosition[0]) # tiempo
        surface.blit(self.movimientosSurface, self.surfacesPosition[1]) # movimientos

        pygame.draw.circle(surface, (255,0,0), [16+4,80], 16) # circulo rojo = canibal
        surface.blit(self.canibalSurface, [16+16+4+4, 80 - self.canibalSurface.get_height() // 2 + 4]) # texto canibal

        pygame.draw.rect(surface, [0,0,255], pygame.Rect(16+4-16, 80+32-16+4, 32, 32)) # cuadrado azul misionero
        surface.blit(self.misioneroSurface, [16+16+4+4, 80+32-16+4 + 8]) # texto canibal

        surface.blit(self.textoBalsaSurface, [self.surfacesPosition[0][0], 80+32-16+4+32+18]) # Texto R= mover balsa
        surface.blit(self.textoSolucionSurface, [self.surfacesPosition[0][0], 80+32-16+4+32+18+self.textoBalsaSurface.get_height()+4]) # Texto Q=solucion

        for x in range(len(self.spawn_posiciones)):
            posicion = self.spawn_posiciones[x]
            destino = self.destino_posiciones[x]
            pygame.draw.rect(surface, [0,0,0], posicion[0]) # spawn zona
            pygame.draw.rect(surface, [0,0,0], destino[0]) # destino zona

        for x in range(len(self.entidades)-1, -1, -1):
            self.entidades[x].draw(surface)

    def update(self, dt, events):

        self.tiempo += dt
        self.tiempo = round(self.tiempo*100)/100

        self.tiempoSurface = self.game.font16.render("Tiempo: " + str(self.tiempo), True, (255,255,255))
        self.movimientosSurface = self.game.font16.render("Movimientos: " + str(self.movimientos), True, (255,255,255))

        self.mouseClicks = self.game.mouseClicks
        self.mouseState = self.game.mouseState

        self.handle_events(events)

        bote = self.entidades[len(self.entidades)-1]

        # chequear game won (victoria)

        bote_slots = bote.get_occupied_slots()

        if(self.game_state == [0,0,0] and bote.lastState == 1 and bote.lastState != bote.state and not bote_slots):
            self.game_won = True

        # chequear game over (derrota)
        if((self.game_state[0] < self.game_state[1] and self.game_state[0] > 0) or (self.game_state[0] > self.game_state[1] and self.game_state[0] < 3)):
            self.game_over = True

        if(self.game_over):
            pass
            print("GG perdiste")
            self.screen_handler.get_screen(2).set_mode(1)
            self.screen_handler.switch_screen(2)
        elif(self.game_won):
            print("GANASTE!!")
            self.screen_handler.get_screen(2).set_mode(0)
            self.screen_handler.switch_screen(2)

        self.last_game_state = self.game_state if self.game_state != [0,0,0] else self.last_game_state
        self.game_state = [0,0,0]

        for x in range(len(self.entidades)-1, -1, -1):
            e = self.entidades[x]
            e.update(dt) # actualizar cada entidad
            # e.draw(surface) # dibujar cada entidad

            if(bote.state != 1):
                if(e.type < 2):
                    if(e.state == 0):
                        self.game_state[e.type] += 1
                if(e.type == 2):
                    if(e.state == 0):
                        self.game_state[e.type] = 1
                    else:
                        self.game_state[e.type] = 0

            if(not self.modo_bot):
                if(bote.state != 1): # el bote se esta moviendo
                    if(self.mouseClicks[0]): # si es click izquierdo
                        mouse = self.mouseState
                        if(e.is_colliding(mouse[0], mouse[1]) and not self.dragging_entity and e.es_agarrable and e.state == bote.state): # si estoy agarrando un misionero/canibal
                            e.dragging_mouse = True
                            self.dragging_entity = True
                    else:
                        if(x != len(self.entidades)-1 and e.dragging_mouse): # el bote es el ultimo indice en la lista, no queremos reposicionar al bote, si no a los canibales/misioneros
                            self.reposicionar_entidad(e)
                        e.dragging_mouse = False
                        self.dragging_entity = False


                    if(e.type != 2 and e.dragging_mouse): # si la entidad se encuentra siendo arrastrada por el mouse, actualizar su posicion
                        e.x = int(mouse[0] - e.width/2)
                        e.y = int(mouse[1] - e.height/2)

        if(self.modo_bot):
            if(bote.lastState == 1 or bote.lastState == bote.state): # el bote esta frenado

                if(bote.lastState == 1):
                    for slot in bote.slots:
                        entidad = slot[1]
                        if(entidad):
                            entidad.state = bote.state
                            entidad.boat_slot = -1
                            slot[1] = None

                    self.modo_bot_reposicionar()

                if(len(self.pasos) < 1):
                    return

                paso_actual = self.pasos.pop(0)
                for i in range(len(paso_actual) - 1):
                    cant_actual = 0
                    cantidad = paso_actual[i]
                    tipo = i

                    for e in self.entidades:
                        if(e.type == tipo and e.state == bote.state):
                            for index, slot in enumerate(bote.slots):
                                if(not slot[1] and cant_actual < cantidad):
                                    slot[1] = e
                                    e.x = slot[0].x
                                    e.y = slot[0].y
                                    e.lastY = e.y
                                    e.lastX = e.x
                                    e.boat_slot = index

                                    for k in range(len(self.spawn_posiciones)):
                                        spawn = self.spawn_posiciones[k]
                                        destino = self.destino_posiciones[k]
                                        if(e.state == 0 and e.position_slot == spawn[0]):
                                            spawn[1] = None
                                            break
                                        elif(e.state == 2 and e.position_slot == destino[0]):
                                            destino[1] = None
                                            break


                                    cant_actual += 1
                                    break


                if(bote.set_state_movimiento()): self.movimientos += 1

        for slot in bote.slots:
            persona = slot[1]
            if(persona):
                if(bote.state == 1):
                    persona.x = slot[0].x
                    persona.y = slot[0].y
                persona.set_last_position(slot[0].x, slot[0].y)
                persona.position_slot = -1
                persona.state = bote.state
                persona.update_rect()

    def modo_bot_reposicionar(self):

        for i in range(len(self.spawn_posiciones)):
            for index, e in enumerate(self.entidades):
                if(e.state != 1 and e.type != 2):
                    spawn = self.spawn_posiciones[i]
                    destino = self.destino_posiciones[i]
                    if(e.state == 0 and not spawn[1] and e.position_slot == -1):
                        self.spawn_posiciones[i][1] = e
                        e.position_slot = spawn[0]
                        e.x = spawn[0].x
                        e.y = spawn[0].y
                    elif(e.state == 2 and not destino[1] and e.position_slot == -1):
                        self.destino_posiciones[i][1] = e
                        e.position_slot = destino[0]
                        e.x = destino[0].x
                        e.y = destino[0].y


    def activar_modo_bot(self):
        if(self.modo_bot): return
        self.modo_bot = True # activar flag
        self.init_game(1) # reiniciar juego
        self.solucion = random.choice(solutions)
        self.pasos = []
        print(self.solucion)
        for x in range(0, len(self.solucion)-1):
            paso = self.solucion[x]
            paso_sig = self.solucion[x+1]
            self.pasos.append([abs(paso_i - sig_i) for paso_i, sig_i in zip(paso, paso_sig)])

        print("Pasos")
        print(self.pasos)

    def handle_events(self, events):
        for e in events:
            if(e.type == pygame.KEYDOWN):
                if(e.key == pygame.K_r):
                    bote = self.entidades[len(self.entidades)-1]
                    if(bote.set_state_movimiento()): self.movimientos += 1
                if(e.key == pygame.K_q):
                    self.activar_modo_bot()


    def is_valid_position_land_end(self, x, y):
        for i in range(len(self.destino_posiciones)):
            e = self.destino_posiciones[i][0]
            if(self.destino_posiciones[i][1]): continue
            if(x >= e.x and x <= e.x + e.width and y >= e.y and y <= e.y + e.height):
                return i
        return -1

    def is_valid_position_land_spawn(self, x, y):
        for i in range(len(self.spawn_posiciones)):
            e = self.spawn_posiciones[i][0]
            if(self.spawn_posiciones[i][1]): continue
            if(x >= e.x and x <= e.x + e.width and y >= e.y and y <= e.y + e.height):
                return i
        return -1

    def reposicionar_entidad(self, e):
        bote = self.entidades[len(self.entidades)-1]
        if(e == bote): return # no queremos reposicionar bote

        index = self.is_valid_position(self.mouseState[0], self.mouseState[1]) # colision con bote
        spawnIndex = self.is_valid_position_land_spawn(self.mouseState[0], self.mouseState[1]) # colision con spawn
        endIndex = self.is_valid_position_land_end(self.mouseState[0], self.mouseState[1]) # colision con destino

        if(spawnIndex != -1 and e.state == 0):
            e.x = self.spawn_posiciones[spawnIndex][0].x
            e.y = self.spawn_posiciones[spawnIndex][0].y
            self.spawn_posiciones[spawnIndex][1] = e

            if(e.position_slot != -1):
                # print(e.position_slot)
                for i in range(len(self.spawn_posiciones)):
                    spawn = self.spawn_posiciones[i][0]
                    destino = self.destino_posiciones[i][0]
                    if(e.position_slot == spawn): self.spawn_posiciones[i][1] = None
                    if(e.position_slot == destino): self.destino_posiciones[i][1] = None

            e.position_slot = self.spawn_posiciones[spawnIndex][0]
            e.set_last_position(e.x, e.y)
            if(e.boat_slot > -1): # si estaba en un slot del bote, desocuparlo
                bote.slots[e.boat_slot][1] = None
            e.boat_slot = -1 # desvincular al misionero/canibal del slot del bote
            return

        if(endIndex != -1 and e.state == 2):
            e.x = self.destino_posiciones[endIndex][0].x
            e.y = self.destino_posiciones[endIndex][0].y
            self.destino_posiciones[endIndex][1] = e

            if(e.position_slot != -1):
                for i in range(len(self.spawn_posiciones)):
                    spawn = self.spawn_posiciones[i][0]
                    destino = self.destino_posiciones[i][0]
                    if(e.position_slot == spawn): self.spawn_posiciones[i][1] = None
                    if(e.position_slot == destino): self.destino_posiciones[i][1] = None

            e.position_slot = self.destino_posiciones[endIndex][0]
            e.set_last_position(e.x, e.y)
            if(e.boat_slot > -1): # si estaba en un slot del bote, desocuparlo
                bote.slots[e.boat_slot][1] = None
            e.boat_slot = -1 # desvincular al misionero/canibal del slot del bote
            return

        if(bote.slots[index][1] and bote.slots[index][1] != e):
            index = -1

        if(index == -1):
            for slot in bote.slots:
                if(slot[1] == e):
                    e.x = e.lastX
                    e.y = e.lastY
                    return
            e.x = e.lastX # mandarlo al spawn
            e.y = e.lastY # mandarlo al spawn
            if(e.boat_slot > -1): # si estaba en un slot del bote, desocuparlo
                bote.slots[e.boat_slot][1] = None
            e.boat_slot = -1 # desvincular al misionero/canibal del slot del bote
            return

        if(e.position_slot != -1):
            for i in range(len(self.spawn_posiciones)):
                spawn = self.spawn_posiciones[i][0]
                destino = self.destino_posiciones[i][0]
                if(e.position_slot == spawn): self.spawn_posiciones[i][1] = None
                if(e.position_slot == destino): self.destino_posiciones[i][1] = None

        e.x = bote.slots[index][0].x
        e.y = bote.slots[index][0].y
        if(e.boat_slot > -1):
            bote.slots[e.boat_slot][1] = None
        e.boat_slot = index
        bote.slots[index][1] = e # guardar a la entidad en el slot del bote

    def is_valid_position(self, x, y):
        bote = self.entidades[len(self.entidades)-1]
        return bote.is_colliding(x,y)
