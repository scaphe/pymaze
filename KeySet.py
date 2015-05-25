from PmzGraphics import *


class KeySet:
    def __init__(self, left, right, up, down):
        self.left = left
        self.right = right
        self.up = up
        self.down = down


class Constants:
    keySets = [
        # Left, right, up, down
        KeySet(pygame.K_z, pygame.K_x, pygame.K_f, pygame.K_c),
        KeySet(pygame.K_1, pygame.K_q, pygame.K_e, pygame.K_w),
        KeySet(pygame.K_b, pygame.K_n, pygame.K_i, pygame.K_j),
        KeySet(pygame.K_l, pygame.K_p, pygame.K_9, pygame.K_o)
    ]
