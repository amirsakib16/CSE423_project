from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_HELVETICA_18
# Window size
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GUNS = [
    {'name': 'Pistol', 'damage': 5, 'bullet_speed': 1, 'color': (1.0, 1.0, 0.0), 'size': 0.1},
    {'name': 'Rifle', 'damage': 8, 'bullet_speed': 0.55, 'color': (0.0, 1.0, 0.0), 'size': 0.15},
    {'name': 'Shotgun', 'damage': 20, 'bullet_speed': 2, 'color': (1.0, 0.0, 0.0), 'size': 0.2}
]
GUN_INDEX = 0
EXTRA_BOSS = False
TIMER_BOSS = 0
extra_bosses = []
PLAYER_SPEED = 0.15
BULLET_SPEED = 0.3
ENEMY_BULLET_SPEED = 0.25
MAX_ENEMIES_PER_LEVEL = [7, 10, 5]
ENEMY_SPEEDS = [0.03, 0.06, 0.09]
ENEMY_HEALTH_DECREASE_PER_BULLET = [10, 2, 5]
PLAYER_LIFE = 100
ENEMY_MAX_HEALTH = 10
BOSS_HEALTH = 10
BOSS_SPEED = 0.06
ENEMY_FIRE_DISTANCE = 5.0
BULLET_HIT_DISTANCE = 2.0
SHIELD_DURATION = 10.0  
ENEMY_FIRE_INTERVAL = 2.0
TILE_SIZE = 2.0
TILE_ROWS = 40
TILE_COLS = 40
player = None
enemies = []
bullets = []
enemy_bullets = []
walls = []
safe_shields = []
medical_kits = []
current_level = 1
score = 0
key_collected = False
win = False
game_over = False
shield_active = False
shield_activated_time = 0
key_spawned = False
key_position = (0,0,0)
gate_position = (12, 0, 12)
bombs = []
last_enemy_fire_time = 0
class Vector3:
    def __init__(self, x=0,y=0,z=0):
        self.x = x
        self.y = y
        self.z = z
    def __add__(self, other):
        return Vector3(self.x+other.x, self.y+other.y, self.z+other.z)
    def __sub__(self, other):
        return Vector3(self.x-other.x, self.y-other.y, self.z-other.z)
    def __mul__(self, scalar):
        return Vector3(self.x*scalar, self.y*scalar, self.z*scalar)
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector3()
        return Vector3(self.x/l, self.y/l, self.z/l)
class Bomb:
    def __init__(self, startPosition, direction, placeOfExplosion=7.0):
        self.startPosition = startPosition
        self.explosion_time = 0
        self.explosionDuration = 1.0  
        self.areaOfExplosion = 9.0
        self.direction = direction.normalize()
        self.placeOfExplosion = placeOfExplosion
        self.pos = startPosition
        self.throw_time = time.time()
        self.isExploded = False
    def update(self):
        global score
        current_time = time.time()
        if not self.isExploded:
            time_passed = current_time - self.throw_time
            distance_moved = self.findMIN(time_passed * 5, self.placeOfExplosion)
            self.pos = self.startPosition + (self.direction * distance_moved)
            if current_time - self.throw_time >= 3:
                self.isExploded = True
                self.explosion_time = current_time
                enemies_killed = 0
                for enemy in enemies:
                    if (enemy.pos - self.pos).length() <= self.areaOfExplosion:
                        enemy.health -= 10
                        if enemy.health <= 0 and enemy in enemies:
                            enemies.remove(enemy)
                            enemies_killed += 1
                score += enemies_killed*10
        else:
            if current_time - self.explosion_time > self.explosionDuration:
                bombs.remove(self)
    def findMIN(self,x,y):
        if x<y:
            return x
        else:
            return y
    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos.x, self.pos.y + 0.3, self.pos.z)
        if not self.isExploded:
            glColor3f(0.1, 0.1, 0.1)  
            glutSolidSphere(0.2, 10, 10)
        else:
            glColor4f(1, 1, 0, 0.5) 
            glutSolidSphere(self.areaOfExplosion, 20, 20)
        glPopMatrix()
class Player:
    def __init__(self):
        self.pos = Vector3(0,0,0)
        self.dir = 0  
        self.health = PLAYER_LIFE
        self.speed = PLAYER_SPEED
    def move(self, dx, dz):
        new_pos = Vector3(self.pos.x + dx, self.pos.y, self.pos.z + dz)
        if not check_collision_with_walls(new_pos):
            self.pos = new_pos
    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos.x, self.pos.y, self.pos.z)
        glRotatef(self.dir, 0, 1, 0)
        glColor3f(0, 0, 0)
        glPushMatrix()
        glTranslatef(0, 1.2, 0)
        glutSolidSphere(0.3, 20, 20)
        glPopMatrix()
        glColor3f(0.3, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(0, 0.75, 0)  
        glScalef(0.6, 0.8, 0.3)  
        glutSolidCube(1)
        glPopMatrix()
        glColor3f(1, 0, 0)
        glPushMatrix()
        glTranslatef(0, 0.75, 0.18)
        glScalef(0.3, 0.3, 0.1)
        glutSolidOctahedron()
        glPopMatrix()
        glColor3f(0.6, 0.6, 0.6)
        glPushMatrix()
        glTranslatef(-0.15, 0.25, 0)
        glScalef(0.3, 0.5, 0.3)
        glutSolidCube(1)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.15, 0.25, 0)
        glScalef(0.3, 0.5, 0.3)
        glutSolidCube(1)
        glPopMatrix()
        glColor3f(0, 0, 0)
        glPushMatrix()
        glTranslatef(-0.45, 0.9, 0)
        glRotatef(10, 0, 0, 1)
        glScalef(0.2, 0.6, 0.2)
        glutSolidCube(1)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.45, 0.9, 0)
        glRotatef(-10, 0, 0, 1)
        glScalef(0.2, 0.6, 0.2)
        glutSolidCube(1)
        glPopMatrix()
        glPopMatrix()
    def get_collision_box(self):
        return AABB(self.pos.x-0.3, self.pos.y, self.pos.z-0.3, self.pos.x+0.3, self.pos.y+1.3, self.pos.z+0.3)
def spawn_extra_bosses():
    global EXTRA_BOSS
    global TIMER_BOSS
    global extra_bosses
    for i in range(6):
        x = random.uniform(10, 115)
        z = random.uniform(10, 115)
        new_boss = Enemy(x, 0, z, level=3, is_boss=True)
        enemies.append(new_boss)
        extra_bosses.append(new_boss)
    TIMER_BOSS = time.time()
    EXTRA_BOSS = True
class Enemy:
    def __init__(self, x, y, z, level, is_boss=False):
        self.pos = Vector3(x,y,z)
        self.level = level
        self.health = None
        self.speed = None
        if is_boss==True:
            self.health = BOSS_HEALTH
            self.speed = BOSS_SPEED
        else:
            self.health = ENEMY_MAX_HEALTH
            self.speed = ENEMY_SPEEDS[level-1]
        self.is_boss = is_boss
        self.lastFireTime = 0
        self.bullets_fired = 0
    def move_towards_player(self, pl_pos):
        direction = pl_pos - self.pos
        distance = direction.length()
        if distance > 0.5:
            normalized_dir = direction.normalize()
            move_vec = normalized_dir * self.speed
            new_pos = self.pos + move_vec
            if not check_collision_with_walls(new_pos):
                self.pos = new_pos
    def fire_bullet(self, pl_pos):
        now = time.time()
        global EXTRA_BOSS, TIMER_BOSS, extra_bosses
        now = time.time()
        if now - self.lastFireTime >= ENEMY_FIRE_INTERVAL:
            distance = (pl_pos - self.pos).length()
            if self.is_boss or distance <= ENEMY_FIRE_DISTANCE:
                dir_vec = (pl_pos - self.pos).normalize()
                bullet_start = self.pos + dir_vec * 1.0
                enemy_bullets.append(Bullet(bullet_start.x,
                                             bullet_start.y+0.5,
                                               bullet_start.z,
                                                 dir_vec.x,
                                                   dir_vec.y,
                                                     dir_vec.z,
                                                       ENEMY_BULLET_SPEED,
                                                         False))
                self.lastFireTime = now
                if self.is_boss:
                    self.bullets_fired += 1
                    if self.bullets_fired >= 5:
                        self.speed *= 0.4  
                        self.bullets_fired = 0
                        spawn_extra_bosses()
        if EXTRA_BOSS and (time.time() - TIMER_BOSS >= 3):
            for boss in extra_bosses:
                if boss in enemies:
                    enemies.remove(boss)
            extra_bosses.clear()
            EXTRA_BOSS = False
    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos.x, self.pos.y, self.pos.z)
        if self.is_boss:
            glColor3f(0, 0, 0)
            glPushMatrix()
            glBegin(GL_TRIANGLES)
            glVertex3f(0.0, 1.5, 0.0)
            glVertex3f(-0.7, 0.5, 0.7)
            glVertex3f(0.7, 0.5, 0.7)
            glVertex3f(0.0, 1.5, 0.0)
            glVertex3f(0.7, 0.5, 0.7)
            glVertex3f(0.7, 0.5, -0.7)
            glVertex3f(0.0, 1.5, 0.0)
            glVertex3f(0.7, 0.5, -0.7)
            glVertex3f(-0.7, 0.5, -0.7)
            glVertex3f(0.0, 1.5, 0.0)
            glVertex3f(-0.7, 0.5, -0.7)
            glVertex3f(-0.7, 0.5, 0.7)
            glEnd()
            glPopMatrix()
            for x in [-0.3, 0.3]:
                        glPushMatrix()
                        glTranslatef(x, 1.3, 0.2)
                        glColor3f(1, 0, 0)
                        glutSolidSphere(0.1, 20, 20)
                        glPopMatrix()
            glColor3f(1, 0.6, 0.6)
            glPushMatrix()
            glTranslatef(0, 0, 0)
            glRotatef(-90, 1, 0, 0)
            glutSolidCone(1.0, 1.3, 20, 20)
            glPopMatrix()
            glColor3f(1, 0, 0)
            glPushMatrix()
            glTranslatef(0, 0.6, 0.1)
            glScalef(0.5, 0.5, 0.1)  
            glutSolidOctahedron()
            glPopMatrix()
        else:
            glColor3f(0.7, 0.7, 0.7)
            glPushMatrix()
            glTranslatef(0, 1.5, 0)
            glutSolidSphere(0.3, 20, 20)
            glPopMatrix()
            glColor3f(1, 0, 0)
            center_x, center_y, center_z = 0.0, 1.5, 0.0
            radius = 0.3
            angles = [0, math.pi/2, math.pi, 3*math.pi/2]
            for angle in angles:
                glBegin(GL_TRIANGLES)
                glVertex3f(center_x, center_y, center_z)
                glVertex3f(center_x + radius * math.cos(angle), center_y, center_z + radius * math.sin(angle))
                glVertex3f(center_x + radius * math.cos(angle + math.pi/4), center_y, center_z + radius * math.sin(angle + math.pi/4))
                glEnd()
            glColor3f(0, 0, 1)
            glPushMatrix()
            glTranslatef(0, 0.9, 0)
            glScalef(0.6, 0.8, 0.6)
            glutSolidCube(1.2)
            glPopMatrix()
            glColor3f(0, 0, 0)
            arm_length = 0.8
            arm_radius = 0.15
        glPopMatrix()
    def get_collision_box(self):
        scale = None
        if self.is_boss==True:
            scale = 1.5
        else:
            scale = 1.0
        return AABB(self.pos.x-0.3*scale,
                     self.pos.y,
                       self.pos.z-0.3*scale,
                         self.pos.x+0.3*scale,
                           self.pos.y+1.3*scale,
                             self.pos.z+0.3*scale)
class Bullet:
    def __init__(self, x, y, z, dx, dy, dz, speed, from_player=True, color=(1,1,0), size=0.1):
        self.pos = Vector3(x,y,z)
        self.dir = Vector3(dx, dy, dz).normalize()
        self.speed = speed
        self.from_player = from_player
        self.alive = True
        self.color = color
        self.size = size
    def update(self):
        self.pos = self.pos + self.dir * self.speed
    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos.x, self.pos.y, self.pos.z)
        glColor3f(*self.color)
        glutSolidSphere(self.size, 8, 8)
        glPopMatrix()
class AABB:
    def __init__(self, minX, minY, minZ, maxX, maxY, maxZ):
        self.minX = minX
        self.minY = minY
        self.minZ = minZ
        self.maxX = maxX
        self.maxY = maxY
        self.maxZ = maxZ
    def intersects(self, other):
        return not (self.maxX < other.minX or self.minX > other.maxX or
                    self.maxY < other.minY or self.minY > other.maxY or
                    self.maxZ < other.minZ or self.minZ > other.maxZ)
class Wall:
    def __init__(self, x, y, z, sx, sy, sz, rotation_angle=0, rotation_axis=(0,1,0)):
        self.pos = Vector3(x, y, z)
        self.size = Vector3(sx, sy, sz)
        self.rotation_angle = rotation_angle 
        self.rotation_axis = rotation_axis    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.pos.x, self.pos.y + self.size.y / 2, self.pos.z)
        glRotatef(self.rotation_angle, *self.rotation_axis)
        glColor3f(1.0, 1.0, 0)
        glScalef(self.size.x, self.size.y, self.size.z)
        glutWireCube(1)
        glPopMatrix()
    def get_collision_box(self):
        return AABB(self.pos.x - self.size.x/2, self.pos.y, self.pos.z - self.size.z/2,
                    self.pos.x + self.size.x/2, self.pos.y + self.size.y, self.pos.z + self.size.z/2)
class PowerUp:
    def __init__(self, x, y, z, typeComponents):
        self.pos = Vector3(x,y,z)
        self.typeComponents = typeComponents
        self.is_collected = False
    def draw(self):
        if self.is_collected:
            return
        glPushMatrix()
        glTranslatef(self.pos.x, self.pos.y + 1, self.pos.z)
        if self.typeComponents == 'shield':
            glColor3f(0, 0, 1)
            glPushMatrix()
            glScalef(1.0, 1.5, 1.0)
            glutSolidSphere(0.3, 20, 20)
            glPopMatrix()
            glColor3f(1, 1, 1)
            glPushMatrix()
            glScalef(0.5, 0.5, 0.5)
            glutSolidOctahedron()
            glPopMatrix()
        else:
            glColor3f(1, 0, 0)
            glutSolidCube(0.6)
            glColor3f(1, 1, 1)
            glLineWidth(3.0)
            glBegin(GL_LINES)
            glVertex3f(-0.2, 0.0, 0.31)
            glVertex3f(0.2, 0.0, 0.31)
            glVertex3f(0.0, -0.2, 0.31)
            glVertex3f(0.0, 0.2, 0.31)
            glEnd()
        glPopMatrix()
    def get_collision_box(self):
        return AABB(self.pos.x-0.25, self.pos.y-0.25, self.pos.z-0.25,
                    self.pos.x+0.25, self.pos.y+0.25, self.pos.z+0.25)
def check_collision_with_walls(pos):
    point_box = AABB(pos.x, pos.y, pos.z, pos.x, pos.y, pos.z)
    for w in walls:
        if w.get_collision_box().intersects(point_box):
            return True
    return False
def aabb_collision(box1, box2):
    return box1.intersects(box2)
def draw_diamond():
    glBegin(GL_POLYGON)
    glVertex2f(0.0, 0.3)
    glVertex2f(-0.3, 0.0)
    glVertex2f(0.0, -0.3)
    glVertex2f(0.3, 0.0)
    glEnd()
def init_game():
    global player
    global enemies
    global walls
    global safe_shields
    global medical_kits
    global current_level
    global key_collected
    global win
    global game_over
    global bullets
    global enemy_bullets
    global score
    global key_spawned
    player = Player()
    enemies.clear()
    bullets.clear()
    enemy_bullets.clear()
    key_collected = False
    win = False
    game_over = False
    key_spawned = False
    score = 0
    walls.clear()
    walls.append(Wall(-5, 0,55, 0.5, 3, 120)) 
    walls.append(Wall(115, 0,55, 0.5, 3, 120))
    safe_shields.clear()
    safe_shields.append(PowerUp(2, 0, 2, 'shield'))
    safe_shields.append(PowerUp(2, 0, 10, 'shield'))
    safe_shields.append(PowerUp(15, 0, 25, 'shield'))
    safe_shields.append(PowerUp(40, 0, 50, 'shield'))
    safe_shields.append(PowerUp(70, 0, 80, 'shield'))
    medical_kits.clear()
    medical_kits.append(PowerUp(-2, 0, -2, 'medkit'))
    medical_kits.append(PowerUp(-10, 0, -20, 'medkit'))
    medical_kits.append(PowerUp(20, 0, 15, 'medkit'))
    medical_kits.append(PowerUp(60, 0, 30, 'medkit'))
    medical_kits.append(PowerUp(90, 0, 95, 'medkit'))
    spawn_enemies(current_level)
def spawn_enemies(level):
    enemies.clear()
    enemy_count = MAX_ENEMIES_PER_LEVEL[level-1]
    for i in range(enemy_count):
        while True:
            x = random.uniform(12, 105)
            z = random.uniform(22, 107)
            dist = math.sqrt((x - player.pos.x)**2 + (z - player.pos.z)**2)
            if dist > 5:
                break
        enemies.append(Enemy(x, 0, z, level))
    if level == 3:
        enemies.append(Enemy(10, 0, 10, level, is_boss=True))
keys_pressed = set()
def special_key(key, x, y):
    if key == GLUT_KEY_UP:
        keys_pressed.add('up')
    elif key == GLUT_KEY_DOWN:
        keys_pressed.add('down')
    elif key == GLUT_KEY_LEFT:
        keys_pressed.add('left')
    elif key == GLUT_KEY_RIGHT:
        keys_pressed.add('right')
def special_key_up(key, x, y):
    if key == GLUT_KEY_UP:
        keys_pressed.discard('up')
    elif key == GLUT_KEY_DOWN:
        keys_pressed.discard('down')
    elif key == GLUT_KEY_LEFT:
        keys_pressed.discard('left')
    elif key == GLUT_KEY_RIGHT:
        keys_pressed.discard('right')
def keyboard(key, x, y):
    global shield_active
    global shield_activated_time
    global score
    global GUN_INDEX
    key = key.decode('utf-8').lower()
    if key == ' ':
        fire_player_bullet()
    elif key == 'c':
        GUN_INDEX = (GUN_INDEX + 1) % len(GUNS)
    elif key == 't':
        # Throw bomb
        direction_rad = math.radians(player.dir)
        dx = -math.sin(direction_rad)
        dz = -math.cos(direction_rad)
        bomb_start = player.pos + Vector3(dx * 1.0, 0.5, dz * 1.0)
        bombs.append(Bomb(bomb_start, Vector3(dx, 0, dz)))
    elif key == 'k':
        for shield in safe_shields:
            if not shield.is_collected and aabb_collision(player.get_collision_box(), shield.get_collision_box()):
                shield.is_collected = True
                shield_active = True
                shield_activated_time = time.time()
                return
        for medkit in medical_kits:
            if not medkit.is_collected and aabb_collision(player.get_collision_box(), medkit.get_collision_box()):
                medkit.is_collected = True
                player.health = min(player.health + 50, PLAYER_LIFE)
                return
def fire_player_bullet():
    global GUN_INDEX
    global GUNS
    gun = GUNS[GUN_INDEX]
    direction_rad = math.radians(player.dir)
    dx = -math.sin(direction_rad)
    dz = -math.cos(direction_rad)
    bullet_start = player.pos + Vector3(dx*1.0, 0.5, dz*1.0)
    bullets.append(
        Bullet(
            bullet_start.x, bullet_start.y, bullet_start.z,
            dx, 0, dz,
            gun['bullet_speed'],
            True,
            color=gun['color'],
            size=gun['size']
        )
    )
def update(value=None):
    global current_level
    global key_collected
    global win
    global game_over
    global shield_active
    global shield_activated_time
    global score, key_spawned

    if game_over or win:
        glutPostRedisplay()
        glutTimerFunc(16, update, 0)
        return
    dx = 0
    dz = 0
    if 'up' in keys_pressed:
        dx += -math.sin(math.radians(player.dir)) * player.speed
        dz += -math.cos(math.radians(player.dir)) * player.speed
    if 'down' in keys_pressed:
        dx += math.sin(math.radians(player.dir)) * player.speed
        dz += math.cos(math.radians(player.dir)) * player.speed
    if 'left' in keys_pressed:
        player.dir = (player.dir + 3) % 360
    if 'right' in keys_pressed:
        player.dir = (player.dir - 3) % 360
    player.move(dx, dz)
    for i in bullets:
        i.update()
    bulletLst = []
    for i in bullets:
        if i.alive == True:
            bulletLst.append(i)
    bullets[:] = bulletLst
    for j in enemy_bullets:
        j.update()
    enemyBulletLst = []
    for j in enemy_bullets:
        if j.alive==True:
            enemyBulletLst.append(j)
    enemy_bullets[:] = enemyBulletLst
    for enemy in enemies:
        enemy.move_towards_player(player.pos)
        enemy.fire_bullet(player.pos)
    for bomb in bombs:
        bomb.update()
    for bullet in bullets:
        for enemy in enemies:
            if aabb_collision(AABB(bullet.pos.x-0.15, bullet.pos.y-0.15, bullet.pos.z-0.15,
                                bullet.pos.x+0.15, bullet.pos.y+0.15, bullet.pos.z+0.15),
                            enemy.get_collision_box()):
                bullet.alive = False
                damage = GUNS[GUN_INDEX]['damage']
                if enemy.is_boss:
                    damage = 1
                enemy.health -= damage
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    score += 10
                break
    if len(enemies) == 0 and not key_spawned:
        global key_position
        key_position = (gate_position[0], 0.5, gate_position[2])
        key_spawned = True
        key_collected = False
    if key_spawned:
        key_box = AABB(key_position[0]-0.2, key_position[1]-0.2, key_position[2]-0.2,
                       key_position[0]+0.2, key_position[1]+0.2, key_position[2]+0.2)
        if aabb_collision(player.get_collision_box(), key_box):
            key_collected = True
            key_spawned = False
    gate_box = AABB(gate_position[0]-1, 0, gate_position[2]-1,
                    gate_position[0]+1, 3, gate_position[2]+1)
    for eb in enemy_bullets:
        if aabb_collision(AABB(eb.pos.x-0.15, eb.pos.y-0.15, eb.pos.z-0.15,
                               eb.pos.x+0.15, eb.pos.y+0.15, eb.pos.z+0.15),
                          player.get_collision_box()):
            eb.alive = False
            if not shield_active:
                player.health -= 10
                if player.health <= 0:
                    game_over = True
    if shield_active and (time.time() - shield_activated_time >= SHIELD_DURATION):
        shield_active = False
    if key_spawned:
        key_box = AABB(key_position[0]-0.2, key_position[1]-0.2, key_position[2]-0.2,
                       key_position[0]+0.2, key_position[1]+0.2, key_position[2]+0.2)
        if aabb_collision(player.get_collision_box(), key_box):
            key_collected = True
            key_spawned = False
            win = True
    gate_box = AABB(gate_position[0]-1, 0, gate_position[2]-1,
                    gate_position[0]+1, 3, gate_position[2]+1)
    if aabb_collision(player.get_collision_box(), gate_box):
        if key_collected:
            if current_level < 3:
                current_level += 1
                spawn_enemies(current_level)
                key_collected = False
                key_spawned = False
                win = False
            else:
                if key_collected:
                    win = True
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)
def draw_walls():
    for w in walls:
        glPushMatrix()
        glTranslatef(w.pos.x, w.pos.y + w.size.y/2, w.pos.z)
        glColor3f(0, 0.6, 0)
        glScalef(w.size.x, w.size.y, w.size.z)
        glutSolidCube(1)
        glPopMatrix()
def draw_battlefield():
    for i in range(20):
        for j in range(20):
            x_start = -5 + i * 6
            x_end = x_start + 6
            z_start = -5 + j * 6 
            z_end = z_start + 6
            tile_color = (i + j) % 2
            if tile_color == 0:
                glColor3f(0.4, 0.1,0.1)
            else:
                glColor3f(0.1, 0.2, 0.7)
            glBegin(GL_QUADS)
            glVertex3f(x_start, 0, z_start)
            glVertex3f(x_end, 0, z_start)
            glVertex3f(x_end, 0, z_end)
            glVertex3f(x_start, 0, z_end)
            glEnd()
def draw_key():
    if key_spawned:
        glPushMatrix()
        glTranslatef(*key_position)
        glColor3f(1, 1, 0)
        glutSolidTeapot(0.3)
        glPopMatrix()
def draw_gate():
    glPushMatrix()
    glTranslatef(gate_position[0], 2, gate_position[2])
    glColor3f(0.7, 0.7, 0.7)
    glScalef(2, 3, 0.5)
    glutSolidCube(1)
    glPopMatrix()
def draw_player_health_bar(player):
    length = 1.0 * (player.health / PLAYER_LIFE)
    glPushMatrix()
    glTranslatef(player.pos.x - 0.5, player.pos.y + 1.8, player.pos.z)
    glRotatef(0, 0, 1, 0)
    glColor3f(1, 0, 0)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(length, 0, 0)
    glVertex3f(length, 0.2, 0)
    glVertex3f(0, 0.2, 0)
    glEnd()
    glPopMatrix()
def draw_health_bar(x, y, z, current, maximum):
    length = 1.0 * (current / maximum)
    glPushMatrix()
    glTranslatef(x-0.5, y + 1.8, z)
    glColor3f(1, 0, 0)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(length, 0, 0)
    glVertex3f(length, 0.2, 0)
    glVertex3f(0, 0.2, 0)
    glEnd()
    glPopMatrix()
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    distance_behind = 6.0
    eye_x = player.pos.x + distance_behind * math.sin(math.radians(player.dir))
    eye_y = player.pos.y + 3.0
    eye_z = player.pos.z + distance_behind * math.cos(math.radians(player.dir))
    look_x = player.pos.x
    look_y = player.pos.y + 1.5
    look_z = player.pos.z
    gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 1, 0)
    draw_battlefield()
    draw_walls() 
    for w in walls:
        w.draw()
    player.draw()
    draw_player_health_bar(player)
    for enemy in enemies:
        enemy.draw()
        draw_health_bar(enemy.pos.x,
                         enemy.pos.y,
                           enemy.pos.z,
                             enemy.health,
                               BOSS_HEALTH if enemy.is_boss else ENEMY_MAX_HEALTH)
    for b in bullets:
        b.draw()
    for eb in enemy_bullets:
        eb.draw()
    for bomb in bombs:
        bomb.draw()
    for shield in safe_shields:
        shield.draw()
    for medkit in medical_kits:
        medkit.draw()
    draw_key()
    draw_gate()
    glColor3f(1, 1, 1)
    glWindowPos2i(10, SCREEN_HEIGHT - 20)
    show_text(f'Level: {current_level}  Score: {score}')
    glWindowPos2i(10, SCREEN_HEIGHT - 40)
    show_text(f'Health: {player.health}  Shield: {"Active" if shield_active else "Inactive"}')
    glWindowPos2i(10, SCREEN_HEIGHT - 60)
    show_text(f'Gun: {GUNS[GUN_INDEX]["name"]}')
    if win:
        glWindowPos2i(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2)
        show_text("You Win! Congratulations!")
    if game_over:
        glWindowPos2i(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2)
        show_text("Game Over! Try Again!")
    glutSwapBuffers()
def show_text(text):
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, float(w)/float(h), 0.1, 100)
    glMatrixMode(GL_MODELVIEW)
def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutCreateWindow(b'3D Battle Game')
    glEnable(GL_DEPTH_TEST)
    init_game()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_key)
    glutSpecialUpFunc(special_key_up)
    glutTimerFunc(16, update, 0)
    glutMainLoop()
if __name__ == "__main__":
    main()
