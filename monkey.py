import math
import os
import sys
import random
import pygetwindow as gw
from PyQt6.QtWidgets import QApplication, QLabel, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QPixmap, QTransform, QIcon, QCursor
from PyQt6.QtCore import Qt, QTimer, QPoint

from states import MonkeyState, IdleState, RoamState, GrabbedState, FallingState, LandedState, ClimbState, FollowState, JumpState

def resource_path(filename):
    """ Get absolute path to resource inside the assets folder. """
    if getattr(sys, 'frozen', False):
        base_path = os.path.join(sys._MEIPASS, "assets")  # PyInstaller bundle
    else:
        base_path = os.path.abspath("assets")  # Normal execution
    return os.path.join(base_path, filename)


class MonkeyPet(QLabel):
    def __init__(self):
        print("MonkeyPet")
        super().__init__()
        self.initialize_monkey()
        print("MonkeyPet initialized")
        self.previous_positions = []

    def initialize_monkey(self):
        self.load_sprites()
        self.setup_window()
        self.setup_screen_geometry()
        self.setup_movement()
        self.setup_tray_icon()
        self.setup_timers()
        self.state = IdleState(self)

    def setup_screen_geometry(self):
        """Inicializa la geometría de la pantalla."""
        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.geometry()
        self.available_geometry = screen.availableGeometry()

    def setup_timers(self):
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)  # Timer para update_state()
        self.update_timer.start(50)  # 20 fps

        self.draw_timer = QTimer(self)
        self.draw_timer.timeout.connect(self.draw)  # Timer para draw_state()
        self.draw_timer.start(50)  # 20 fps

    def load_sprites(self):
        """Carga los sprites en un diccionario."""
        self.sprites = {
            "idle": QPixmap(resource_path("idle.png")),
            "walk": QPixmap(resource_path("walk.png")),
            "grabbed": QPixmap(resource_path("grabbed.png")),
            "falling": QPixmap(resource_path("falling.png")),
            "landed": QPixmap(resource_path("landed.png")),
            'takeoff': QPixmap(resource_path("takeoff.png")),
            'jump': QPixmap(resource_path("jump.png"))
        }
        self.width = 100
        self.height = 100

    def setup_window(self):
        """Configura la ventana del mono."""
        self.setPixmap(self.sprites["idle"])
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setScaledContents(True)
        self.resize(self.width, self.height)

    def setup_movement(self):
        """Inicializa la posición y el movimiento."""
        self.walk_speed=5
        self.direction = 0  # Dirección de a donde mira el mono
        self.velocity_x = 0
        self.gravity = 0.5
        self.velocity_y = 0
        self.sight_distance = 500
        self.takeoff_distance = 300
        self.on_ground = True
        self.ground_y = self.available_geometry.height() - self.height  # Suelo
        self.move(random.randint(self.width, self.available_geometry.width() - self.width), self.ground_y) #Posicion inicial

    def update(self):
        """Maneja movimiento, interacciones y cambios de estado"""
        #fisicas del mono
        new_x,new_y=self.x()+self.velocity_x,self.y()+self.velocity_y
        if new_x<0 or new_x>self.available_geometry.width()-self.width:
            self.velocity_x*=-1
        if new_y<0 or new_y>self.available_geometry.height()-self.height:
            self.velocity_y*=-1
        self.move(new_x,new_y)
        # Cambiar de estado
        new_state = self.state.update()  # El estado decide si cambiar
        if isinstance(new_state, MonkeyState) and new_state is not self.state:
            print(f"Cambiando de {self.state.__class__.__name__} a {new_state.__class__.__name__}")
            self.state = new_state  # Asignar el nuevo estado

    def draw(self):45
        """Dibuja el estado actual"""
        self.state.draw(direction=self.direction)


    def walk(self):
        """Moves the monkey based on velocity & direction, reversing at screen edges."""

        self.x_velocity = self.walk_speed * self.direction  # Calculate X velocity
        screen_width = self.available_geometry.width()

        # If the monkey hits the screen edge, reverse direction
        if self.x_velocity > 0:
            self.direction = 1
        else:
            self.direction = -1

    def sees(self):
        """Deteca si el cursor esta cerca del mono"""
        cursor_x, cursor_y = QCursor.pos().x(), QCursor.pos().y()
        monkey_x, monkey_y = self.x(), self.y()
        monkey_width, monkey_height = self.width, self.height

        if (monkey_x - self.sight_distance <= cursor_x <= monkey_x + monkey_width + self.sight_distance and
            monkey_y - self.sight_distance <= cursor_y <= monkey_y + monkey_height + self.sight_distance):
            print("[DEBUG] Mono VE el cursor")
            return "cursor"

        """Detecta si hay una ventana cerca del mono."""
        monkey_x, monkey_y = self.x(), self.y()
        monkey_width, monkey_height = self.width, self.height
        print(f"[DEBUG] Mono en ({monkey_x}, {monkey_y}), tamaño ({monkey_width}x{monkey_height})")
        for window in gw.getWindowsWithTitle(''):  # Obtiene todas las ventanas visibles
            print(f"Ventana detectada: {window.title}, visible: {window.visible}")
            if not window.visible:
                continue  # Si la ventana no es visible, la ignoramos
            if window.title == "Configuración":
                continue

            win_left, win_top, win_right, win_bottom = window.left, window.top, window.right, window.bottom
            if win_top > self.available_geometry.bottom():
                continue # Si la ventana está en la barra de tareas, la ignoramos
            print(self.available_geometry.bottom())
            print(f"[DEBUG] Ventana detectada en ({win_left}, {win_top}) - ({win_right}, {win_bottom})")

            inside_x = win_left <= monkey_x <= win_right - monkey_width
            inside_y = win_top <= monkey_y <= win_bottom - monkey_height
            if inside_x and inside_y:
                continue  # Si el mono está dentro de la ventana, la ignoramos

            near_x = (win_left - self.sight_distance <= monkey_x + monkey_width <= win_right + self.sight_distance)
            near_y = (win_top - self.sight_distance <= monkey_y + monkey_height <= win_bottom + self.sight_distance)

            if near_x and near_y:
                print("[DEBUG] Mono VE esta ventana")
                return window.title
        print("[DEBUG] Ninguna ventana cerca")
        return False 
    
    def walk_towards(self, target_x, target_y):
        """Moves towards target, stops when close, and returns full distance."""
        monkey_center_x = self.x() + (self.width // 2)  # Centro en X
        monkey_center_y = self.y() + (self.height // 2)  # Centro en Y
        
        distance_x = target_x - monkey_center_x
        distance_y = target_y - monkey_center_y
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)
        

        if distance <= self.takeoff_distance or distance_x <= self.width:
            self.direction = 0  # Detenerse si está lo suficientemente cerca
            return distance  

        if target_x < monkey_center_x:
            self.direction = -1  # Mover a la izquierda
        elif target_x > monkey_center_x:
            self.direction = 1   # Mover a la derecha

        self.walk()
        return distance

    def jump_towards(self,target_x,target_y):
        if not self.on_ground:
            new_x = self.x() + self.velocity_x  # Move in X
            new_y = self.y() + self.velocity_y  # Move in Y
            self.velocity_y += self.gravity  # Apply gravity
            self.move(int(new_x), int(new_y))  # Update position

            # Stop when reaching the ground
            if self.y() >= self.ground_y:  
                self.move(self.x(), self.ground_y)  # Snap to ground
                self.velocity_y = 0
                self.velocity_x = self.temp
                self.on_ground = True  # Ready for next jump
                return False
            return True
        self.temp = self.velocity_x
        distance_x = target_x - self.x()
        distance_y = target_y - self.y()

        if abs(distance_x) > self.takeoff_distance:
            distance_x = math.copysign(self.takeoff_distance, distance_x)

        self.velocity_x = distance_x / 20
        self.velocity_y = -20
        self.on_ground = False
        return True



    def is_shaken(self):
        """Detecta si el mono está siendo sacudido."""
        current_position = self.pos()
        self.previous_positions.append(current_position)

        if len(self.previous_positions) > 5:
            self.previous_positions.pop(0)

        if len(self.previous_positions) < 5:
            return False

        distances = [
            (self.previous_positions[i] - self.previous_positions[i - 1]).manhattanLength()
            for i in range(1, len(self.previous_positions))
        ]

        return all(distance > 20 for distance in distances)

    def is_placed_down(self):
        """Detecta si el mono está colocado en el suelo y el mouse está quieto."""
        # Implementación para detectar si el mono está colocado en el suelo y el mouse está quieto
        return False  # Placeholder, implementar según sea necesario

    def setup_tray_icon(self):
        """Crea el icono de la bandeja del sistema."""
        self.tray_icon = QSystemTrayIcon(QIcon(resource_path("monkey.png")), self)
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Mostrar/Ocultar")
        show_action.triggered.connect(self.toggle_visibility)

        exit_action = tray_menu.addAction("Salir")
        exit_action.triggered.connect(QApplication.quit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def toggle_visibility(self):
        """Muestra u oculta el mono."""
        self.setVisible(not self.isVisible())

    def mousePressEvent(self, event):
        """Detecta cuando el mono es agarrado."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_state(GrabbedState(self))
            self.offset = event.pos()  # Guarda la posición relativa del click

    def mouseMoveEvent(self, event):
        """Mueve el mono mientras es arrastrado."""
        if isinstance(self.state, GrabbedState):
            new_x = int(event.globalPosition().x() - self.offset.x())
            new_y = int(event.globalPosition().y() - self.offset.y())
            self.move(new_x, new_y)

    def mouseReleaseEvent(self, event):
        if isinstance(self.state, GrabbedState):
            self.set_state(FallingState(self))  # Start falling when released

    def set_state(self, new_state):
        """Cambia el estado del mono."""
        self.state = new_state


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = MonkeyPet()
    pet.show()
    sys.exit(app.exec())