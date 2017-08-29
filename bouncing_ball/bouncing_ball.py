import sys, pygame
pygame.init()

size = width, height = 1000, 1000
speed = [3, 10]
black = 0, 0, 0
accel = 0

screen = pygame.display.set_mode(size)

ball = pygame.image.load("ball.png")
background = pygame.image.load("sky.jpg").convert()
screen.blit(background, (0,0))
ballrect = ball.get_rect()
screen.blit(ball, ballrect)
pygame.display.update()
while 1:
    for event in pygame.event.get():
       if event.type == pygame.QUIT: sys.exit()
    speed[1] += accel
    screen.blit(background, ballrect, ballrect)
    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.blit(ball, ballrect)
    pygame.display.update()
    pygame.time.delay(10)