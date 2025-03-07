import random


class MonkeyState:
    def __init__(self, monkey):
        self.monkey = monkey  # Reference to the monkey

    def update(self):
        raise NotImplementedError("Subclasses should implement this method")

    def draw(self):
        raise NotImplementedError("Subclasses should implement this method")

class IdleState(MonkeyState):
    def __init__(self):
        super().__init__()
        self.timer = 100 
        
    def update(self):
        self.timer -= 1
        if self.timer == 0:
            return RoamState(self.monkey)
        return self

    def draw(self):
        self.monkey.setPixmap(self.monkey.sprites["idle"])

class RoamState(MonkeyState):
    def __init__(self):
        super().__init__()
        self.timer = random.randint(50, 100)
        self.monkey.direction = random.choice([-1, 1]) 

    def update(self):
        if self.monkey.sees("mouse"):
            return FollowMouseState(self.monkey)  # Cambio de estado
        elif self.monkey.sees("window"):
            return WindowRoamState(self.monkey)  # Cambio de estado
        else:
            new_x = self.monkey.x() + (self.monkey.velocity_x * self.monkey.direction)
            if 0 <= new_x <= self.monkey.window_width - self.monkey.width():
                return IdleState(self.monkey)  # se choco con la pared
            self.timer -= 1
            if self.timer == 0:
                random_state = random.choice([IdleState, RoamState], p=[0.3, 0.7])
                return random_state(self.monkey)
        return self  # Mantiene el estado
        
    def draw(self):
        direction = self.monkey.direction
        sprite = self.monkey.sprites["walk_left"] if direction == -1 else self.monkey.sprites["walk_right"]
        self.monkey.setPixmap(sprite)

class GrabbedState(MonkeyState):
    def update(self):
        # Implementación del comportamiento en estado GRABBED
        return self

    def draw(self):
        self.monkey.setPixmap(self.monkey.sprites["grabbed"])

class FallingState(MonkeyState):
    def update(self):
        # Implementación del comportamiento en estado FALLING
        return self

    def draw(self):
        self.monkey.setPixmap(self.monkey.sprites["falling"])

class LandedState(MonkeyState):
    def update(self):
        # Implementación del comportamiento en estado LANDED
        return self

    def draw(self):
        self.monkey.setPixmap(self.monkey.sprites["landed"])

class ClimbState(MonkeyState):
    def update(self):
        # Implementación del comportamiento en estado CLIMB
        return self

    def draw(self):
        # Implementación del dibujo en estado CLIMB
        pass

class WindowRoamState(MonkeyState):
    def update(self):
        # Implementación del comportamiento en estado WINDOW_ROAM
        return self

    def draw(self):
        # Implementación del dibujo en estado WINDOW_ROAM
        pass

class FollowMouseState(MonkeyState):
    def update(self):
        if not self.monkey.sees("mouse"):
            return RoamState(self.monkey)  # Vuelve a roam
        return self

    def draw(self):
        # Implementación del dibujo en estado FOLLOW_MOUSE
        pass
