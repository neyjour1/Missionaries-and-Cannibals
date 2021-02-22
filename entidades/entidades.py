import pygame
from constants import *

# Superclase de entidad. Las clases Bote y Persona heredan de Entidad
class Entidad:
    def __init__(self, x=0, y=0, width=32, height=32):
        self.x = x
        self.y = y
        self.lastX = x
        self.lastY = y
        self.width = width
        self.height = height
        self.type = -1
        self.color = [127,127,127]
        self.es_agarrable = True

    def draw(self, screen):
        pass

    def is_colliding(self, x, y):
        return x >= self.x and x <= self.x + self.width and y >= self.y and y <= self.y + self.height

# Representa al bote que transporta 2 personas
class Bote(Entidad):
    def __init__(self, x=0, y=0, width=64, height=32):
        super().__init__(x,y,width,height)
        self.update_rect()
        self.color = [162,61,20]
        self.es_agarrable = False
        self.type = 2

        self.direction = 1

        self.occupied_slots = 0

        x = self.x
        y = self.y

        self.slots = [
            [pygame.Rect(x+16, y+self.height//2-16, 32, 32), None],
            [pygame.Rect(x+16*5, y+self.height//2-16, 32, 32), None]
        ]

        self.state = 0 # 0 wrong side, 1 rio, 2 destino
        self.lastState = self.state


    def set_state_movimiento(self):
        if(self.state == 1): return False
        flag = False
        for slot in self.slots:
            if(slot[1]):
                flag = True
                break
        if(not flag):
            return
        self.lastState = self.state
        self.state = 1
        print("SE cambio el state a 1")
        return True

    def update_slots(self):
        x = self.x
        y = self.y

        self.slots[0][0] = pygame.Rect(x+16, y+self.height//2-16, 32, 32)
        self.slots[1][0] = pygame.Rect(x+16*5, y+self.height//2-16, 32, 32)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        for e in self.slots:
            pygame.draw.rect(screen, [4,4,4], e[0])

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def is_colliding(self, x, y):
        for i in range(0, len(self.slots)):
            e = self.slots[i][0]
            # if(self.slots[i][1]): continue
            if(x >= e.x and x <= e.x + e.width and y >= e.y and y <= e.y + e.height):
                return i
        return -1


    def get_occupied_slots(self):
        busy = 0
        for slot in self.slots:
            if(slot[1]): busy += 1
        return busy


    def update(self, dt):
        self.occupied_slots = self.get_occupied_slots()


        if(self.lastState == 1):
            # acabo de llegar a uno de los lados
            pass


        if(self.state == 1): # movimiento
            newX = self.x
            newX += self.direction * 130 * dt

            if(newX + self.width >= SIZE_VENTANA[0] // 3 * 2):
                self.lastState = self.state
                self.state = 2
                self.direction = -1
            elif(newX <= SIZE_VENTANA[0] // 3 ):
                self.lastState = self.state
                self.state = 0
                self.direction = 1
            else:
                self.x = newX

        self.update_rect()
        self.update_slots()

# Representa a un canibal o a un misionero
class Persona(Entidad):
    def __init__(self, x=0, y=0, tipo=0):
        super().__init__(x=x,y=y)
        self.type = tipo # type == 0 -> misionero ; type == 1 -> canibal ; type == 2 -> bote
        self.update_rect()
        self.color = [0,0,255] if self.type == 0 else [255,0,0]
        self.dragging_mouse = False
        self.state = 0 # 0 wrong side, 1 en bote, 2 destino
        self.boat_slot = -1
        self.position_slot = -1

    def set_last_position(self, x, y):
        self.lastX = x
        self.lastY = y

    def draw(self, screen):
        if(self.type == 0):
            pygame.draw.rect(screen, self.color, self.rect) # dibujar misionero
        elif(self.type == 1):
            pygame.draw.circle(screen, self.color, (self.x+self.width//2, self.y+self.width//2), self.width//2) # dibujar canibal


    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height) if self.type == 0 else None

    def update(self, dt):
        self.update_rect()
