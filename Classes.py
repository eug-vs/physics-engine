from Constants import *
from math import pi as PI, sqrt, cos, sin
import cfg
from cfg import WIDTH, HEIGHT, border_bot, border_h, border_top


class Text:
    def __init__(self, pos, text, size, color):
        self.color = color
        self.display = font(size).render(str(text), 1, self.color)
        self.x = pos[0]
        self.y = pos[1]

    def center(self):
        textbox = self.display.get_rect()
        self.x -= textbox[2] / 2
        self.y -= textbox[3] / 2
        return self

    def render(self, surf):
        surf.blit(self.display, (self.x, self.y))


def render_grid():
    """Fills a canvas with white. Draws a grid with the step = UNIT pixels.
    Marks an origin with a big black dot.
    Highlights solid borders of the scene (specified by constants)."""
    screen.fill(WHITE)

    for row in range(0, WIDTH, cfg.UNIT):
        pygame.draw.line(screen, GREEN, (row, 0), (row, HEIGHT))
    for line in range(0, HEIGHT, cfg.UNIT):
        pygame.draw.line(screen, GREEN, (0, line), (WIDTH, line))

    # Borders
    pygame.draw.line(screen, RED, (0, HEIGHT - border_bot * cfg.UNIT), (WIDTH, HEIGHT - border_bot * cfg.UNIT), 2)
    pygame.draw.line(screen, RED, (0, border_top * cfg.UNIT), (WIDTH, border_top * cfg.UNIT), 2)
    pygame.draw.line(screen, RED, (border_h * cfg.UNIT, 0), (border_h * cfg.UNIT, HEIGHT), 2)
    pygame.draw.line(screen, RED, (WIDTH - border_h * cfg.UNIT, 0), (WIDTH - border_h * cfg.UNIT, HEIGHT), 2)

    # Visualising ORIGIN
    pygame.draw.circle(screen, BLACK, ORIGIN.utopix(), 5)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        """Returns a copy a vector."""
        return Vector(self.x, self.y)

    def magnitude(self):
        """Calculates Euclidian magnitude of a vector."""
        return sqrt(self.x**2 + self.y**2)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def __str__(self):
        return 'Vector(' + str(self.x) + ', ' + str(self.y) + ')'

    def __bool__(self):
        return self != Vector(0, 0)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def normalize(self):
        """Sets a magnitude of a vector equal to 1 but preserves it's direction."""
        mag = self.magnitude()
        self.x /= mag
        self.y /= mag
        return self

    def setmag(self, scalar):
        """Sets a magnitude of a vector equal to a given number (preserves direction)."""
        self.normalize()
        self.x *= scalar
        self.y *= scalar
        return self

    def dot(self, other):
        """Dot product of vectors (returns scalar)."""
        return self.x*other.x + self.y*other.y

    def utopix(self):
        """Converts UNITs to pixels, flips the Y axis, returns pair of integers (tuple)."""
        return int(self.x * cfg.UNIT), cfg.HEIGHT - int(self.y * cfg.UNIT)

    def render(self, origin, color):
        """Renders vector of a certain color relative to specified origin."""
        pygame.draw.line(screen, color, origin.utopix(), (self+origin).utopix())
        pygame.draw.circle(screen, color, (self+origin).utopix(), 3)


ORIGIN = Vector(0, 0)
BODIES = []


class Body:
    def __init__(self, location, mass):
        # Body properties
        self.location = location
        self.mass = mass
        self.radius = self.mass ** (1 / 3) / 2
        # Dynamics
        self.vel = Vector(0, 0)
        self.force = Vector(0, 0)
        self.impulse = Vector(0, 0)
        # General
        BODIES.append(self)

    def __str__(self):
        return 'Body:\n' + '\tvelocity:' + str(self.vel)

    def apply(self, force):
        """Applies certain force to an object."""
        self.force += force

    def imp(self):
        """Calculates an impulse of an object."""
        return self.vel * self.mass

    def k_energy(self):
        return self.mass * self.vel.magnitude()**2 / 2

    def p_energy(self):
        return (self.location.y - border_bot) * self.mass * cfg.G

    def energy(self):
        return self.k_energy() + self.p_energy()

    def upd_vel(self):
        """Updates body's velocity and forces."""
        self.vel += self.force / self.mass
        self.force = Vector(0, 0)

    def update(self):
        """Fully updates object's state."""
        self.upd_vel()
        self.location += self.vel

    def friction(self, magnitude):
        """Applies a force with a given magnitude directing backwards relative to the current velocity."""
        friction = self.vel.copy()
        friction.setmag(-magnitude)
        self.apply(friction)

    def bounce(self, horizontal, vertical):
        """Applies bounce force. Literally flips object's speed around certain axis
        (specified by horizontal/vertical values). Used to bounce off the walls & floor."""
        if cfg.COLLISION:
            f = (-self.imp()*2*(1-cfg.SURFACE) - self.force)
            f = Vector(f.x * horizontal, f.y * vertical)
            self.apply(f)
            clack()

    def collide(self, other):
        if cfg.COLLISION:
            m1 = self.mass
            m2 = other.mass
            v1 = self.vel
            v2 = other.vel
            vb = (v2 * (m2 - m1) + v1 * 2 * m1) / (m1 + m2)
            va = (v1 * (m1 - m2) + v2 * 2 * m2) / (m1 + m2)
            self.vel = va
            other.vel = vb
            self.update()
            other.update()
            clack()

    def render(self, color):
        """Renders body as a ball of a given color.
        Attaches a velocity vector (multiplied by 15 for better visuals)."""
        pygame.draw.circle(screen, color, self.location.utopix(), int(self.radius * cfg.UNIT), 2)
        (self.vel * 15).render(self.location, RED)
        if cfg.DEBUG:
            (self.vel * self.mass).render(self.location, BLUE)
            if cfg.PAUSE:
                Text(self.location.utopix(), str(round(self.k_energy(), 2)) + '  ' + str(round(self.p_energy(), 2)), 20,
                     BLACK).center().render(screen)


airtog = 0
surftog = 0
def toggle_air():
    global AIR, airtog
    AIR, airtog = airtog, AIR
    print("Air friction: " + str(AIR))


def toggle_surf():
    global SURFACE, surftog
    SURFACE, surftog = surftog, SURFACE
    print("Surface friction: " + str(SURFACE))
