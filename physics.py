# ==========================================
# physics.py - FİZİK MOTORU VE SINIFLAR
# ==========================================
import pygame
import random
import math
from config import *

class ParticleSystem:
    def __init__(self):
        self.rain_drops = []
        self.snow_flakes = []
        self.splashes = []
        self.snow_ground = [0] * SCREEN_WIDTH
        self.snow_box = [0] * BOX_WIDTH 
        self.mode = "RAIN"
        self.wind_speed = 2.0
        self.frame_counter = 0
        self.is_rapid_melting = False
        self.current_melt_mult = 1.0

    def get_surface_y(self, x, current_y, box):
        ix = int(x)
        if ix < 0 or ix >= SCREEN_WIDTH:
            return SCREEN_HEIGHT
        if box.rect.left <= ix < box.rect.right and current_y <= box.rect.top:
            lx = ix - box.rect.left
            if 0 <= lx < len(self.snow_box):
                return box.rect.top - self.snow_box[lx]
        return SCREEN_HEIGHT - self.snow_ground[ix]

    def add_rain(self):
        buffer = SCREEN_WIDTH // 2
        x = random.uniform(-buffer, SCREEN_WIDTH + buffer)
        y = random.uniform(-100, 0)
        vy = random.uniform(16.0, 28.0) 
        self.rain_drops.append({'x': x, 'y': y, 'vy': vy})

    def add_snow(self):
        buffer = SCREEN_WIDTH // 2
        current_time = pygame.time.get_ticks()
        if random.random() < 0.3:
            gust_center = (math.sin(current_time * 0.0002) * (SCREEN_WIDTH / 2.5)) + (SCREEN_WIDTH / 2)
            x = random.gauss(gust_center, SCREEN_WIDTH / 4) 
        else:
            x = random.uniform(-buffer, SCREEN_WIDTH + buffer)
        y = random.uniform(-100, 0)
        phase = random.uniform(0, math.pi * 2)
        amp = random.uniform(0.3, 1.0)
        vy = random.uniform(2.0, 6.0)
        self.snow_flakes.append({'x': x, 'y': y, 'vy': vy, 'phase': phase, 'amp': amp})

    def add_splash(self, x, y, incoming_vx, incoming_vy):
        num_splashes = random.randint(2, 4)
        for _ in range(num_splashes):
            vx = (incoming_vx * 0.4) + random.uniform(-6.0, 6.0)
            vy = (-abs(incoming_vy) * random.uniform(0.1, 0.3))
            self.splashes.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'life': random.randint(10, 20)})

    def update_physics(self, box, speed_mult):
        self.frame_counter += 1
        current_time = pygame.time.get_ticks()
        max_snow_current = max(self.snow_ground) if self.snow_ground else 0
        current_snow_ratio = max_snow_current / MAX_SNOW_GROUND if MAX_SNOW_GROUND > 0 else 0

        if current_snow_ratio >= DYNAMIC_MELT_HIGH and not self.is_rapid_melting:
            self.is_rapid_melting = True
            self.current_melt_mult = random.uniform(20.0, 35.0) 
        elif current_snow_ratio <= DYNAMIC_MELT_LOW:
            self.is_rapid_melting = False
            self.current_melt_mult = 1.0

        if self.frame_counter % MELT_INTERVAL_FRAMES == 0:
            wind_melt_factor = 1.0 + (abs(self.wind_speed) * 0.2) 
            current_snow_melt_prob = SNOW_MELT_PROBABILITY * wind_melt_factor
            if self.is_rapid_melting and self.mode == "SNOW":
                current_snow_melt_prob *= self.current_melt_mult

            melt_chance = current_snow_melt_prob if self.mode == "SNOW" else RAIN_MELT_PROBABILITY
            for i in range(SCREEN_WIDTH):
                if self.snow_ground[i] > 0 and random.uniform(0, 100) < melt_chance:
                    self.snow_ground[i] -= 1
            for i in range(len(self.snow_box)):
                if self.snow_box[i] > 0 and random.uniform(0, 100) < melt_chance:
                    self.snow_box[i] -= 1

        if self.mode == "RAIN":
            while len(self.rain_drops) < 800:
                self.add_rain()
            for drop in self.rain_drops[:]:
                vx = self.wind_speed * 3.0 * speed_mult
                vy = drop['vy'] * speed_mult
                next_x = drop['x'] + vx
                next_y = drop['y'] + vy
                
                if box.rect.collidepoint(next_x, next_y):
                    self.add_splash(next_x, box.rect.top, self.wind_speed * 3.0, drop['vy'])
                    if drop['y'] <= box.rect.top:
                        lx = int(next_x) - box.rect.left
                        if 0 <= lx < len(self.snow_box) and self.snow_box[lx] > 0 and random.random() < RAIN_IMPACT_MELT_CHANCE:
                            self.snow_box[lx] = max(0, self.snow_box[lx] - 2)
                    self.rain_drops.remove(drop)
                    continue

                hit_y = self.get_surface_y(next_x, drop['y'], box)
                if next_y >= hit_y:
                    self.add_splash(next_x, hit_y, self.wind_speed * 3.0, drop['vy'])
                    ix = int(next_x)
                    if box.rect.left <= ix < box.rect.right and drop['y'] <= box.rect.top:
                        lx = ix - box.rect.left
                        if 0 <= lx < len(self.snow_box) and self.snow_box[lx] > 0 and random.random() < RAIN_IMPACT_MELT_CHANCE:
                            self.snow_box[lx] = max(0, self.snow_box[lx] - 2)
                    else:
                        if 0 <= ix < SCREEN_WIDTH and self.snow_ground[ix] > 0 and random.random() < RAIN_IMPACT_MELT_CHANCE:
                            self.snow_ground[ix] = max(0, self.snow_ground[ix] - 2)
                    self.rain_drops.remove(drop)
                else:
                    drop['x'] = next_x
                    drop['y'] = next_y

        elif self.mode == "SNOW":
            snow_speed_mult = speed_mult * 2.0  
            while len(self.snow_flakes) < 1500: 
                self.add_snow()

            for flake in self.snow_flakes[:]:
                flutter = math.sin(current_time * 0.002 + flake['phase']) * flake['amp']
                vx = (self.wind_speed * 1.5 + flutter) * snow_speed_mult
                vy = flake['vy'] * snow_speed_mult
                next_x = flake['x'] + vx
                next_y = flake['y'] + vy
                
                if next_x < 0: next_x += SCREEN_WIDTH
                if next_x >= SCREEN_WIDTH: next_x -= SCREEN_WIDTH

                if box.rect.collidepoint(next_x, next_y):
                    if flake['y'] <= box.rect.top + vy:
                        lx = int(next_x) - box.rect.left
                        if 0 <= lx < len(self.snow_box) and self.snow_box[lx] < MAX_SNOW_BOX:
                            self.snow_box[lx] += 1
                    else: 
                        if box.is_grounded:
                            if random.random() < 0.5: 
                                scatter = int(abs(random.gauss(0, 3 + abs(self.wind_speed))))
                                side_x = box.rect.left - 1 - scatter if vx > 0 else box.rect.right + scatter
                                if 0 <= side_x < SCREEN_WIDTH and self.snow_ground[side_x] < MAX_SNOW_GROUND:
                                    self.snow_ground[side_x] += 1
                    self.snow_flakes.remove(flake)
                    continue

                hit_y = self.get_surface_y(next_x, flake['y'], box)
                if next_y >= hit_y:
                    ix = int(next_x)
                    if box.rect.left <= ix < box.rect.right and flake['y'] <= box.rect.top:
                        lx = ix - box.rect.left
                        if 0 <= lx < len(self.snow_box) and self.snow_box[lx] < MAX_SNOW_BOX:
                            self.snow_box[lx] += 1
                    else:
                        if 0 <= ix < SCREEN_WIDTH and self.snow_ground[ix] < MAX_SNOW_GROUND:
                            self.snow_ground[ix] += 1
                    self.snow_flakes.remove(flake)
                else:
                    flake['x'] = next_x
                    flake['y'] = next_y

            self.simulate_snow_avalanche(self.snow_ground, SCREEN_WIDTH, box, is_ground=True)
            self.simulate_snow_avalanche(self.snow_box, box.rect.width, is_ground=False)

            if box.rect.left > 0 and self.snow_box[0] > 0:
                box_edge_world_y = box.rect.top - self.snow_box[0]
                spill_target = box.rect.left - 1
                if 0 <= spill_target < SCREEN_WIDTH:
                    ground_world_y = SCREEN_HEIGHT - self.snow_ground[spill_target]
                    if ground_world_y > box_edge_world_y + 2: 
                        self.snow_box[0] -= 1
                        scatter_x = max(0, box.rect.left - random.randint(1, 4))
                        self.snow_ground[scatter_x] += 1

            if box.rect.right < SCREEN_WIDTH and self.snow_box[-1] > 0:
                box_edge_world_y = box.rect.top - self.snow_box[-1]
                spill_target = box.rect.right
                if 0 <= spill_target < SCREEN_WIDTH:
                    ground_world_y = SCREEN_HEIGHT - self.snow_ground[spill_target]
                    if ground_world_y > box_edge_world_y + 2:
                        self.snow_box[-1] -= 1
                        scatter_x = min(SCREEN_WIDTH - 1, box.rect.right + random.randint(0, 3))
                        self.snow_ground[scatter_x] += 1

        for splash in self.splashes[:]:
            splash['vy'] += GRAVITY 
            splash['x'] += splash['vx'] 
            splash['y'] += splash['vy'] 
            splash['life'] -= 1 

            if box.rect.collidepoint(splash['x'], splash['y']):
                splash['vy'] = -abs(splash['vy']) * 0.5 
                splash['y'] = box.rect.top - 1

            hit_y = SCREEN_HEIGHT - self.snow_ground[int(splash['x'])] if 0 <= int(splash['x']) < SCREEN_WIDTH else SCREEN_HEIGHT
            if splash['y'] >= hit_y or splash['life'] <= 0:
                self.splashes.remove(splash)

    def simulate_snow_avalanche(self, arr, length, box=None, is_ground=False):
        for i in range(length):
            if arr[i] > 0:
                dirs = [-1, 1]
                random.shuffle(dirs)
                for d in dirs:
                    ni = i + d
                    if 0 <= ni < length:
                        if is_ground and box and box.is_grounded:
                            if not (box.rect.left <= i < box.rect.right) and (box.rect.left <= ni < box.rect.right):
                                snow_y = SCREEN_HEIGHT - arr[i]
                                if snow_y < box.rect.bottom:
                                    continue
                        repose = random.randint(1, 3) 
                        if is_ground and box and box.is_grounded:
                            if i == box.rect.left - 1 or i == box.rect.right:
                                repose = random.randint(4, 8) 
                        if arr[i] - arr[ni] > repose:  
                            if random.random() < 0.8:
                                arr[i] -= 1
                                arr[ni] += 1
                                break

    def draw_snow_accumulation(self, surface, box, scale_mode):
        sf = SCALE_FACTOR if scale_mode == "Retro_Scale" else 1
        for x in range(0, SCREEN_WIDTH, sf):
            chunk = self.snow_ground[x:x+sf]
            h = max(chunk) if chunk else 0
            if h > 0:
                if scale_mode == "Retro_Scale":
                    pygame.draw.rect(surface, WHITE, (x, SCREEN_HEIGHT - h, sf, h))
                else:
                    pygame.draw.line(surface, WHITE, (x, SCREEN_HEIGHT - h), (x, SCREEN_HEIGHT))
        for x in range(0, box.rect.width, sf):
            chunk = self.snow_box[x:x+sf]
            h = max(chunk) if chunk else 0
            if h > 0:
                world_x = box.rect.left + x
                if scale_mode == "Retro_Scale":
                    pygame.draw.rect(surface, WHITE, (world_x, box.rect.top - h, sf, h))
                else:
                    pygame.draw.line(surface, WHITE, (world_x, box.rect.top - h), (world_x, box.rect.top))

    def draw_particles(self, target_surface, scale_mode):
        sf = SCALE_FACTOR if scale_mode == "Retro_Scale" else 1
        for drop in self.rain_drops:
            draw_vx = self.wind_speed * 3.0
            draw_vy = drop['vy']
            x1, y1 = drop['x'], drop['y']
            x2, y2 = drop['x'] - draw_vx*0.5, drop['y'] - draw_vy*0.5
            if scale_mode == "Retro_Scale":
                x1, y1 = (int(x1)//sf)*sf, (int(y1)//sf)*sf
                x2, y2 = (int(x2)//sf)*sf, (int(y2)//sf)*sf
                pygame.draw.line(target_surface, ICE_BLUE, (x1, y1), (x2, y2), sf)
            else:
                pygame.draw.line(target_surface, ICE_BLUE, (int(x1), int(y1)), (int(x2), int(y2)), 1)
        for flake in self.snow_flakes:
            x, y = flake['x'], flake['y']
            if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                if scale_mode == "Retro_Scale":
                    pygame.draw.rect(target_surface, ICE_BLUE, ((int(x)//sf)*sf, (int(y)//sf)*sf, sf, sf))
                else:
                    target_surface.set_at((int(x), int(y)), ICE_BLUE)

    def draw_splashes(self, target_surface, scale_mode):
        sf = SCALE_FACTOR if scale_mode == "Retro_Scale" else 1
        for splash in self.splashes:
            x, y = splash['x'], splash['y']
            if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
                if scale_mode == "Retro_Scale":
                    pygame.draw.rect(target_surface, ICE_BLUE, ((int(x)//sf)*sf, (int(y)//sf)*sf, sf, sf))
                else:
                    target_surface.set_at((int(x), int(y)), ICE_BLUE)


class PhysicsBox:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - BOX_WIDTH // 2, SCREEN_HEIGHT - BOX_HEIGHT - 100, BOX_WIDTH, BOX_HEIGHT)
        self.vy = 0.0
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.is_grounded = False 

    def update(self, mouse_pos, mouse_pressed, particles):
        if mouse_pressed:
            if not self.dragging and self.rect.collidepoint(mouse_pos):
                self.dragging = True
                self.offset_x = self.rect.x - mouse_pos[0]
                self.offset_y = self.rect.y - mouse_pos[1]
                self.vy = 0
        else:
            self.dragging = False

        if self.dragging:
            self.rect.x = mouse_pos[0] + self.offset_x
            self.rect.y = mouse_pos[1] + self.offset_y
            self.vy = 0
            self.is_grounded = False 
            for x in range(self.rect.left, self.rect.right):
                if 0 <= x < SCREEN_WIDTH:
                    snow_top = SCREEN_HEIGHT - particles.snow_ground[x]
                    if snow_top < self.rect.bottom:
                        particles.snow_ground[x] = max(0, SCREEN_HEIGHT - self.rect.bottom)
        else:
            self.vy += GRAVITY
            in_snow = False
            for x in range(self.rect.left, self.rect.right):
                if 0 <= x < SCREEN_WIDTH:
                    if (SCREEN_HEIGHT - particles.snow_ground[x]) < self.rect.bottom:
                        in_snow = True
                        break
            if in_snow and self.vy > 1.0:
                self.vy *= 0.5

            self.rect.y += int(self.vy)
            floor_y = SCREEN_HEIGHT
            for x in range(self.rect.left, self.rect.right):
                if 0 <= x < SCREEN_WIDTH:
                    snow_top = SCREEN_HEIGHT - particles.snow_ground[x]
                    if snow_top < floor_y:
                        floor_y = snow_top

            if self.rect.bottom >= floor_y:
                self.rect.bottom = floor_y
                self.vy = 0
                self.is_grounded = True
            elif self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT
                self.vy = 0
                self.is_grounded = True
            else:
                self.is_grounded = False

            if self.vy == 0 and self.rect.bottom < SCREEN_HEIGHT:
                on_snow = False
                for x in range(self.rect.left, self.rect.right):
                    if 0 <= x < SCREEN_WIDTH and SCREEN_HEIGHT - particles.snow_ground[x] == self.rect.bottom:
                        on_snow = True
                        break
                if on_snow:
                    if random.random() < 0.2: 
                        self.rect.y += 1
                        self.rect.bottom = min(SCREEN_HEIGHT, self.rect.bottom)
            
            for x in range(self.rect.left, self.rect.right):
                if 0 <= x < SCREEN_WIDTH:
                    if SCREEN_HEIGHT - particles.snow_ground[x] < self.rect.bottom:
                        particles.snow_ground[x] = max(0, SCREEN_HEIGHT - self.rect.bottom)

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, GRAY, self.rect, 2)