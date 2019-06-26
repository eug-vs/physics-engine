from Classes import *
from cfg import border_h, border_bot, WIDTH, HEIGHT
pygame.display.set_caption('Physics Engine Environment')
RUNNING = True
cfg.PAUSE = False

# Natural forces
WIND = Vector(0, 1)
GRAVITY = Vector(0, -cfg.G)

# User interface
init_mass = 200
mouse = Vector(0, 0)

# TODO: define objects here
# Body(Vector(20, 10), 12)  # TEST CASE DO NOT DELETE!!! (AIR = 0.00005 SURFACE = 0.1 sticky bug)
Body(Vector(120, 80), 2000)
#for x in range(10):
Body(Vector(80, 20), 1).vel = Vector(0, 0.5)

#Body(Vector(10, 10), 20).vel = Vector(0, 0.01)

# Mainloop
while RUNNING:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            RUNNING = False
        if e.type == pygame.MOUSEMOTION:
            mouse = Vector(pygame.mouse.get_pos()[0], (HEIGHT - pygame.mouse.get_pos()[1]))/cfg.UNIT
        if e.type == pygame.MOUSEBUTTONDOWN:
            print(e)
            if e.button == 1:
                for body in BODIES:
                    body.apply(-WIND)
            elif e.button == 3:
                for body in BODIES:
                    body.apply(WIND)
            elif e.button == 2:
                Body(mouse, init_mass)
            elif e.button == 4:
                if pygame.key.get_pressed()[pygame.K_LCTRL]:
                    # cfg.UNIT += 2
                    pass
                else:
                    init_mass += 0.5
            elif e.button == 5:
                if pygame.key.get_pressed()[pygame.K_LCTRL]:
                    # cfg.UNIT -= 2
                    pass
                else:
                    if init_mass > 0.5:
                        init_mass -= 0.5
        if e.type == pygame.KEYDOWN:
            print(e)
            if e.key == 97:
                toggle_air()
            elif e.key == 115:
                toggle_surf()
            elif e.key == 111:
                for body in BODIES:
                    print(body)
            elif e.key == 32:
                cfg.PAUSE = not cfg.PAUSE
            elif e.key == 100:
                cfg.DEBUG = not cfg.DEBUG

    if not cfg.PAUSE:
        # Physics
        for body in BODIES:
            body.apply(GRAVITY * body.mass)  # Gravity force: pointing straight down mg units.

            if body.vel.magnitude() > cfg.AIR/body.mass:
                # Air friction
                body.friction(cfg.AIR)

                # Border collisions & energy loss (implemented as surface friction)
                if body.location.y < border_bot + body.radius or \
                        body.location.y > HEIGHT/cfg.UNIT - (border_bot + body.radius):
                    body.bounce(0, 1)
                if (WIDTH/cfg.UNIT - border_h - body.radius) < body.location.x or \
                        body.location.x < (border_h + body.radius):
                    body.bounce(1, 0)

            # Processing collisions
            A = body
            for other in BODIES:
                if other != body:
                    B = other
                    if (A.location - B.location).magnitude() < A.radius + B.radius:
                        body.collide(other)
                    # UNIVERSAL ATTRACTION
                    F = 0.001 * (A.mass * B.mass) / (A.location - B.location).magnitude()**2
                    A.apply((B.location - A.location).setmag(F))
                    B.apply((A.location - B.location).setmag(F))

    # Rendering
    render_grid()
    pygame.draw.circle(screen, LIGHTGREY, pygame.mouse.get_pos(), int(cfg.UNIT * init_mass ** (1 / 3) / 2), 1)

    for body in BODIES:
        body.upd_vel() if cfg.PAUSE else body.update()
        body.render(BLACK)

    # Calculating total energy of a system
    if cfg.DEBUG:
        E = 0
        for body in BODIES:
            E += body.energy()
        Text((20, 20), 'Total ' + str(len(BODIES)) + ' objects', 25, BLACK).render(screen)
        Text((20, 40), 'Energy of a system: ' + str(round(E, 2)) + ' mass*(distance per tick)^2 / 2', 25,
             BLACK).render(screen)

    window.blit(screen, (0, 0))
    pygame.display.flip()
