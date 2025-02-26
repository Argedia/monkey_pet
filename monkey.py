import os
import sys
import random
from PyQt6.QtWidgets import QApplication, QLabel, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QPixmap, QTransform, QIcon, QCursor
from PyQt6.QtCore import Qt, QTimer

from enum import Enum

def resource_path(filename):
    """ Get absolute path to resource inside the assets folder. """
    if getattr(sys, 'frozen', False):
        base_path = os.path.join(sys._MEIPASS, "assets")  # PyInstaller bundle
    else:
        base_path = os.path.abspath("assets")  # Normal execution
    return os.path.join(base_path, filename)


class MonkeyState(Enum):
    IDLE = 0
    WALKING = 1
    GRABBED = 2
    FALLING = 3
    LANDED = 4


class MonkeyPet(QLabel):
    def __init__(self):
        super().__init__()
        self.load_sprites()
        self.setup_window()
        self.setup_movement()
        self.setup_tray_icon()
        
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)  # Runs update(), which calls draw()
        self.update_timer.start(150)  # Adjust time as needed

    def load_sprites(self):
        """Carga los sprites en un diccionario."""
        self.sprites = {
            "idle": QPixmap(resource_path("idle.png")),
            "walk_left": QPixmap(resource_path("walk.png")),
            "walk_right": QPixmap(resource_path("walk.png")).transformed(QTransform().scale(-1, 1)),  # Imagen volteada
            "grabbed": QPixmap(resource_path("hang.png")),
            "falling": QPixmap(resource_path("falling.png")),
            "landed": QPixmap(resource_path("landed.png"))
        }
        self.width=100
        self.height=100

    def setup_window(self):
        """Configura la ventana del mono."""
        self.setPixmap(self.sprites["idle"])
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setScaledContents(True)
        self.resize(self.width, self.height)

    def setup_movement(self):
        self.direction_dict = {
            -1: self.sprites["walk_left"],
            0: self.sprites["idle"],
            1: self.sprites["walk_right"]
        }
        self.speed = 10
        self.fall_speed = 30
        """Inicializa la posición y el movimiento."""
        screen = QApplication.primaryScreen().geometry()
        self.ground_y = screen.height() - 120  # Suelo
        self.move(random.randint(self.width, screen.width() - self.width*2), self.ground_y)
        self.state = MonkeyState.WALKING

    def update(self):
        """Maneja movimiento, interacciones y cambios de estado"""
        if self.state == MonkeyState.GRABBED:
            self.setPixmap(self.sprites["grabbed"])
    
        if self.state == MonkeyState.WALKING:
            self.follow_cursor()
            self.move_monkey()
        
        elif self.state == MonkeyState.FALLING:
            if self.y() < self.ground_y:
                self.move(self.x(), self.y() + self.fall_speed)
                self.setPixmap(self.sprites["falling"])
            else:
                self.state = MonkeyState.LANDED  # Aterriza

        elif self.state == MonkeyState.LANDED:
            self.setPixmap(self.sprites["landed"])
            QTimer.singleShot(1000, lambda: setattr(self, "state", MonkeyState.WALKING))
        
    
    def move_monkey(self):
        """Mueve el mono de un lado a otro en el suelo."""
        screen_width = QApplication.primaryScreen().geometry().width()
        new_x = self.x() + (self.speed * self.direction)
        self.move(new_x, self.ground_y)

        self.setPixmap(self.direction_dict[self.direction])
        

    def follow_cursor(self):
        cursor_x = QCursor.pos().x()
        monkey_x = self.x()

        if abs(cursor_x - monkey_x-(self.width/2)) > self.width:  # Si está lejos, moverse
            self.direction = 1 if cursor_x > monkey_x else -1
        else:  # Si está cerca, quedarse idle
            self.direction = 0

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
            self.state = MonkeyState.GRABBED
            self.offset = event.pos()  # Guarda la posición relativa del click
            
    
    def mouseMoveEvent(self, event):
        """Mueve el mono mientras es arrastrado."""
        if self.state == MonkeyState.GRABBED:
            new_x = int(event.globalPosition().x() - self.offset.x())
            new_y = int(event.globalPosition().y() - self.offset.y())
            self.move(new_x, new_y)

    def mouseReleaseEvent(self, event):
        if self.state == MonkeyState.GRABBED:
            self.state = MonkeyState.FALLING  # Start falling when released



if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = MonkeyPet()
    pet.show()
    sys.exit(app.exec())