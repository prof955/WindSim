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
        flower_colors = [
            (255, 105, 180), # Sıcak Pembe
            (255, 215, 0),   # Sarı/Altın
            (147, 112, 219), # Mor
            (255, 69, 0),    # Turuncu/Kırmızı
            (135, 206, 235), # Gök Mavisi
            (255, 255, 255)  # Beyaz
        ]
        self.grass_blades = []
        for x in range(0, SCREEN_WIDTH, 4):
            if random.random() < 0.8:
                is_flower = random.random() < 0.08
                is_mutant = random.random() < 0.03
                
                target_height = random.uniform(35.0, 50.0) if is_mutant else random.uniform(12.0, 32.0)
                
                self.grass_blades.append({
                    'x': x,
                    't_h': target_height,
                    'c_h': random.uniform(0.1, 1.0),
                    'bend': 0.0,
                    'flower': is_flower or is_mutant,
                    'flower_color': random.choice(flower_colors) if (is_flower or is_mutant) else None,
                    'phase': random.uniform(0, math.pi * 2),
                    'is_mutant': is_mutant
                })
        self.mode = "SNOW"
        self.wind_speed = 0.0
        self.frame_counter = 0
        self.is_rapid_melting = False
        self.current_melt_mult = 1.0
        self.last_update_time = pygame.time.get_ticks()
        self.time_accumulator = 0

    def get_surface_y(self, x, current_y, boxes, exclude_box=None):
        ix = int(x)
        if ix < 0 or ix >= SCREEN_WIDTH:
            return SCREEN_HEIGHT, None
            
        highest_y = SCREEN_HEIGHT - self.snow_ground[ix]
        hit_box = None
        
        for box in boxes:
            if box is exclude_box: continue
            if box.rect.left <= ix < box.rect.right:
                lx = ix - box.rect.left
                if current_y <= box.get_bottom_y(lx):
                    if 0 <= lx < len(box.snow_box):
                        surf_y = box.get_base_y(lx) - box.snow_box[lx]
                        if surf_y < highest_y:
                            highest_y = surf_y
                            hit_box = box
                        
        return highest_y, hit_box

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

    def update_physics(self, boxes, speed_mult):
        self.frame_counter += 1
        current_time = pygame.time.get_ticks()
        max_snow_current = max(self.snow_ground) if self.snow_ground else 0
        current_snow_ratio = max_snow_current / MAX_SNOW_GROUND if MAX_SNOW_GROUND > 0 else 0

        if speed_mult > 0:
            if self.frame_counter % 5 == 0:
                for grass in self.grass_blades:
                    snow_h = self.snow_ground[grass['x']]
                    if self.mode == "RAIN" and grass['c_h'] < grass['t_h'] and snow_h < grass['c_h']:
                        grass['c_h'] += 0.2
                    if snow_h > grass['c_h'] + 2:
                        grass['c_h'] = max(0.5, grass['c_h'] - 0.1)

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
            for box in boxes:
                for i in range(len(box.snow_box)):
                    if box.snow_box[i] > 0 and random.uniform(0, 100) < melt_chance:
                        box.snow_box[i] -= 1

        if self.mode == "RAIN":
            while len(self.rain_drops) < 800:
                self.add_rain()
            for drop in self.rain_drops[:]:
                vx = self.wind_speed * 3.0 * speed_mult
                vy = drop['vy'] * speed_mult
                next_x = drop['x'] + vx
                next_y = drop['y'] + vy
                
                hit_box = None
                for box in boxes:
                    if box.collidepoint((next_x, next_y)):
                        hit_box = box
                        break

                if hit_box:
                    lx = int(next_x) - hit_box.rect.left
                    base_y = hit_box.get_base_y(lx)
                    self.add_splash(next_x, base_y, self.wind_speed * 3.0, drop['vy'])
                    if drop['y'] <= base_y:
                        if 0 <= lx < len(hit_box.snow_box) and hit_box.snow_box[lx] > 0 and random.random() < RAIN_IMPACT_MELT_CHANCE:
                            hit_box.snow_box[lx] = max(0, hit_box.snow_box[lx] - 2)
                    self.rain_drops.remove(drop)
                    continue

                hit_y, hit_box = self.get_surface_y(next_x, drop['y'], boxes)
                if next_y >= hit_y:
                    self.add_splash(next_x, hit_y, self.wind_speed * 3.0, drop['vy'])
                    ix = int(next_x)
                    if hit_box:
                        lx = ix - hit_box.rect.left
                        if 0 <= lx < len(hit_box.snow_box) and hit_box.snow_box[lx] > 0 and random.random() < RAIN_IMPACT_MELT_CHANCE:
                            hit_box.snow_box[lx] = max(0, hit_box.snow_box[lx] - 2)
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

                hit_box = None
                for box in boxes:
                    if box.collidepoint((next_x, next_y)):
                        hit_box = box
                        break

                if hit_box:
                    lx = int(next_x) - hit_box.rect.left
                    base_y = hit_box.get_base_y(lx)
                    if flake['y'] <= base_y + vy:
                        if 0 <= lx < len(hit_box.snow_box) and hit_box.snow_box[lx] < MAX_SNOW_BOX:
                            hit_box.snow_box[lx] += 1
                    else: 
                        if hit_box.is_grounded:
                            if random.random() < 0.5: 
                                scatter = int(abs(random.gauss(0, 3 + abs(self.wind_speed))))
                                side_x = hit_box.rect.left - 1 - scatter if vx > 0 else hit_box.rect.right + scatter
                                if 0 <= side_x < SCREEN_WIDTH and self.snow_ground[side_x] < MAX_SNOW_GROUND:
                                    self.snow_ground[side_x] += 1
                    self.snow_flakes.remove(flake)
                    continue

                hit_y, hit_box = self.get_surface_y(next_x, flake['y'], boxes)
                if next_y >= hit_y:
                    ix = int(next_x)
                    if hit_box:
                        lx = ix - hit_box.rect.left
                        if 0 <= lx < len(hit_box.snow_box) and hit_box.snow_box[lx] < MAX_SNOW_BOX:
                            hit_box.snow_box[lx] += 1
                    else:
                        if 0 <= ix < SCREEN_WIDTH and self.snow_ground[ix] < MAX_SNOW_GROUND:
                            self.snow_ground[ix] += 1
                    self.snow_flakes.remove(flake)
                else:
                    flake['x'] = next_x
                    flake['y'] = next_y

            self.simulate_snow_avalanche(self.snow_ground, SCREEN_WIDTH, boxes, is_ground=True)
            for box in boxes:
                self.simulate_snow_avalanche(box.snow_box, box.rect.width, boxes, is_ground=False)

                if box.rect.left > 0 and box.snow_box[0] > 0:
                    box_edge_world_y = box.get_base_y(0) - box.snow_box[0]
                    spill_target = box.rect.left - 1
                    if 0 <= spill_target < SCREEN_WIDTH:
                        hit_y, hit_b = self.get_surface_y(spill_target, SCREEN_HEIGHT, boxes, exclude_box=box)
                        if hit_y > box_edge_world_y + 2: 
                            box.snow_box[0] -= 1
                            scatter_x = max(0, box.rect.left - random.randint(1, 4))
                            _, s_box = self.get_surface_y(scatter_x, box_edge_world_y, boxes, exclude_box=box)
                            if s_box:
                                lx = scatter_x - s_box.rect.left
                                if 0 <= lx < len(s_box.snow_box) and s_box.snow_box[lx] < MAX_SNOW_BOX:
                                    s_box.snow_box[lx] += 1
                            else:
                                if self.snow_ground[scatter_x] < MAX_SNOW_GROUND:
                                    self.snow_ground[scatter_x] += 1

                if box.rect.right < SCREEN_WIDTH and box.snow_box[-1] > 0:
                    box_edge_world_y = box.get_base_y(box.rect.width - 1) - box.snow_box[-1]
                    spill_target = box.rect.right
                    if 0 <= spill_target < SCREEN_WIDTH:
                        hit_y, hit_b = self.get_surface_y(spill_target, SCREEN_HEIGHT, boxes, exclude_box=box)
                        if hit_y > box_edge_world_y + 2:
                            box.snow_box[-1] -= 1
                            scatter_x = min(SCREEN_WIDTH - 1, box.rect.right + random.randint(0, 3))
                            _, s_box = self.get_surface_y(scatter_x, box_edge_world_y, boxes, exclude_box=box)
                            if s_box:
                                lx = scatter_x - s_box.rect.left
                                if 0 <= lx < len(s_box.snow_box) and s_box.snow_box[lx] < MAX_SNOW_BOX:
                                    s_box.snow_box[lx] += 1
                            else:
                                if self.snow_ground[scatter_x] < MAX_SNOW_GROUND:
                                    self.snow_ground[scatter_x] += 1

        for splash in self.splashes[:]:
            splash['vy'] += GRAVITY 
            splash['x'] += splash['vx'] 
            splash['y'] += splash['vy'] 
            splash['life'] -= 1 

            hit_box = None
            for box in boxes:
                if box.collidepoint((splash['x'], splash['y'])):
                    hit_box = box
                    break

            if hit_box:
                splash['vy'] = -abs(splash['vy']) * 0.5 
                lx = int(splash['x']) - hit_box.rect.left
                splash['y'] = hit_box.get_base_y(lx) - 1

            hit_y, _ = self.get_surface_y(splash['x'], splash['y'], boxes)
            if splash['y'] >= hit_y or splash['life'] <= 0:
                self.splashes.remove(splash)

    def simulate_snow_avalanche(self, arr, length, boxes=None, is_ground=False):
        for i in range(length):
            if arr[i] > 0:
                dirs = [-1, 1]
                random.shuffle(dirs)
                for d in dirs:
                    ni = i + d
                    if 0 <= ni < length:
                        blocked = False
                        if is_ground and boxes:
                            for bx in boxes:
                                if bx.is_grounded:
                                    if not (bx.rect.left <= i < bx.rect.right) and (bx.rect.left <= ni < bx.rect.right):
                                        snow_y = SCREEN_HEIGHT - arr[i]
                                        lx_ni = ni - bx.rect.left
                                        if snow_y < bx.get_bottom_y(lx_ni):
                                            blocked = True
                                            break
                        if blocked:
                            continue
                            
                        repose = random.randint(1, 3) 
                        if is_ground and boxes:
                            for bx in boxes:
                                if bx.is_grounded:
                                    if i == bx.rect.left - 1 or i == bx.rect.right:
                                        repose = random.randint(4, 8) 
                                        break
                                        
                        if arr[i] - arr[ni] > repose:  
                            if random.random() < 0.8:
                                arr[i] -= 1
                                arr[ni] += 1
                                break

    def draw_snow_accumulation(self, surface, boxes, scale_mode):
        sf = SCALE_FACTOR if scale_mode == "Retro_Scale" else 1
        for x in range(0, SCREEN_WIDTH, sf):
            chunk = self.snow_ground[x:x+sf]
            h = max(chunk) if chunk else 0
            if h > 0:
                if scale_mode == "Retro_Scale":
                    pygame.draw.rect(surface, WHITE, (x, SCREEN_HEIGHT - h, sf, h))
                else:
                    pygame.draw.line(surface, WHITE, (x, SCREEN_HEIGHT - h), (x, SCREEN_HEIGHT))
                    
        for box in boxes:
            for x in range(0, box.rect.width, sf):
                chunk = box.snow_box[x:x+sf]
                h = max(chunk) if chunk else 0
                if h > 0:
                    world_x = box.rect.left + x
                    base_y = box.get_base_y(x)
                    
                    # Snow height shouldn't go through the bottom of another box
                    max_snow_top = base_y - h
                    for other in boxes:
                        if other is not box:
                            if other.rect.left <= world_x < other.rect.right:
                                lx_other = world_x - other.rect.left
                                bottom_other = other.get_bottom_y(lx_other)
                                if bottom_other < base_y and bottom_other > max_snow_top:
                                    max_snow_top = bottom_other
                                    
                    draw_height = base_y - max_snow_top
                    if draw_height > 0:
                        if scale_mode == "Retro_Scale":
                            pygame.draw.rect(surface, WHITE, (world_x, max_snow_top, sf, draw_height))
                        else:
                            pygame.draw.line(surface, WHITE, (world_x, max_snow_top), (world_x, int(base_y)))

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

    def draw_grass(self, surface, scale_mode, speed_mult):
        sf = SCALE_FACTOR if scale_mode == "Retro_Scale" else 1
        current_time = pygame.time.get_ticks()
        
        if speed_mult > 0:
            dt = current_time - self.last_update_time
            self.time_accumulator += dt
        self.last_update_time = current_time
        for grass in self.grass_blades:
            x = grass['x']
            snow_h = self.snow_ground[x]
            if snow_h >= grass['c_h'] * 1.5:
                continue 
            
            wind_effect = self.wind_speed * 1.5
            oscillation = math.sin(self.time_accumulator * 0.003 + grass['phase']) * 2.0
            
            snow_weight_bend = 0
            if snow_h > 0:
                snow_weight_bend = min(snow_h, grass['c_h']) * 0.5 * (1 if self.wind_speed >= 0 else -1)
                
            target_bend = wind_effect + oscillation + snow_weight_bend
            grass['bend'] += (target_bend - grass['bend']) * 0.1
            
            base_x = x
            base_y = SCREEN_HEIGHT
            
            h = grass['c_h']
            tip_dx = grass['bend']
            if abs(tip_dx) > h * 0.9:
                tip_dx = (h * 0.9) * (1 if tip_dx > 0 else -1)
                
            tip_dy = math.sqrt(h**2 - tip_dx**2)
            tip_x = base_x + tip_dx
            tip_y = base_y - tip_dy
            
            color = (34, 139, 34) 
            if h < 5:
                color = (107, 142, 35) 
                
            if scale_mode == "Retro_Scale":
                rx1, ry1 = (int(base_x)//sf)*sf, (int(base_y)//sf)*sf
                rx2, ry2 = (int(tip_x)//sf)*sf, (int(tip_y)//sf)*sf
                pygame.draw.line(surface, color, (rx1, ry1), (rx2, ry2), sf)
                
                # Çiçek
                if grass['flower'] and h > 8:
                    size_mult = 3 if grass['is_mutant'] else 2
                    offset = sf * (size_mult // 2)
                    pygame.draw.rect(surface, grass['flower_color'], (rx2 - offset, ry2 - offset, sf*size_mult, sf*size_mult))
            else:
                line_w = 2 if grass['is_mutant'] else 1
                pygame.draw.line(surface, color, (int(base_x), int(base_y)), (int(tip_x), int(tip_y)), line_w)
                # Çiçek
                if grass['flower'] and h > 8:
                    radius = 4 if grass['is_mutant'] else 2
                    pygame.draw.circle(surface, grass['flower_color'], (int(tip_x), int(tip_y)), radius)

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
    def __init__(self, start_x=None, start_y=None):
        if start_x is None:
            start_x = SCREEN_WIDTH // 2 - BOX_WIDTH // 2
        if start_y is None:
            start_y = SCREEN_HEIGHT - BOX_HEIGHT - 100
            
        self.rect = pygame.Rect(start_x, start_y, BOX_WIDTH, BOX_HEIGHT)
        self.vy = 0.0
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.is_grounded = False 
        self.snow_box = [0] * BOX_WIDTH

    def get_base_y(self, lx):
        return self.rect.top
        
    def get_bottom_y(self, lx):
        return self.rect.bottom

    def collidepoint(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, mouse_pos, particles, all_boxes):
        if self.dragging:
            self.rect.x = mouse_pos[0] + self.offset_x
            self.rect.y = mouse_pos[1] + self.offset_y
            self.vy = 0
            self.is_grounded = False 
            for x in range(self.rect.left, self.rect.right):
                if 0 <= x < SCREEN_WIDTH:
                    lx_self = x - self.rect.left
                    bottom_self = self.get_bottom_y(lx_self)
                    snow_top = SCREEN_HEIGHT - particles.snow_ground[x]
                    if snow_top < bottom_self:
                        particles.snow_ground[x] = max(0, int(SCREEN_HEIGHT - bottom_self))
                    if snow_top < bottom_self:
                        particles.snow_ground[x] = max(0, int(SCREEN_HEIGHT - bottom_self))
        else:
            self.vy += GRAVITY
            in_snow = False
            for x in range(self.rect.left, self.rect.right):
                if 0 <= x < SCREEN_WIDTH:
                    lx_self = x - self.rect.left
                    if (SCREEN_HEIGHT - particles.snow_ground[x]) < self.get_bottom_y(lx_self):
                        in_snow = True
                        break
            if in_snow and self.vy > 1.0:
                self.vy *= 0.5

            self.rect.y += int(self.vy)
            
            max_pen = -9999
            for x in range(self.rect.left, self.rect.right):
                if 0 <= x < SCREEN_WIDTH:
                    lx_self = x - self.rect.left
                    bottom_y = self.get_bottom_y(lx_self)
                    hit_y, hit_box = particles.get_surface_y(x, bottom_y, all_boxes, exclude_box=self)
                    pen = bottom_y - hit_y
                    if pen > max_pen:
                        max_pen = pen

            if max_pen >= 0:
                self.rect.y -= int(max_pen)
                self.vy = 0
                self.is_grounded = True
            else:
                self.is_grounded = False

            if self.vy == 0 and self.is_grounded:
                on_snow = False
                for x in range(self.rect.left, self.rect.right):
                    if 0 <= x < SCREEN_WIDTH:
                        lx_self = x - self.rect.left
                        hit_y, hit_box = particles.get_surface_y(x, self.get_bottom_y(lx_self), all_boxes, exclude_box=self)
                        if hit_y == self.get_bottom_y(lx_self):
                            on_snow = True
                            break
                if on_snow:
                    if random.random() < 0.2: 
                        self.rect.y += 1
            
            for x in range(self.rect.left, self.rect.right):
                if 0 <= x < SCREEN_WIDTH:
                    lx_self = x - self.rect.left
                    bottom_self = self.get_bottom_y(lx_self)
                    if SCREEN_HEIGHT - particles.snow_ground[x] < bottom_self:
                        particles.snow_ground[x] = max(0, int(SCREEN_HEIGHT - bottom_self))

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, GRAY, self.rect, 2)

class PhysicsCircle(PhysicsBox):
    def __init__(self, start_x=None, start_y=None, radius=None):
        if radius is None:
            radius = BOX_WIDTH // 2
        if start_x is None:
            start_x = SCREEN_WIDTH // 2 - radius
        if start_y is None:
            start_y = SCREEN_HEIGHT - radius * 2 - 100
            
        self.rect = pygame.Rect(start_x, start_y, radius * 2, radius * 2)
        self.radius = radius
        self.vy = 0.0
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.is_grounded = False 
        self.snow_box = [0] * (radius * 2)

    def get_base_y(self, lx):
        dx = lx - self.radius
        h2 = self.radius**2 - dx**2
        if h2 < 0: h2 = 0
        h = math.sqrt(h2)
        return self.rect.centery - h

    def get_bottom_y(self, lx):
        dx = lx - self.radius
        h2 = self.radius**2 - dx**2
        if h2 < 0: h2 = 0
        h = math.sqrt(h2)
        return self.rect.centery + h

    def collidepoint(self, pos):
        dx = pos[0] - self.rect.centerx
        dy = pos[1] - self.rect.centery
        return dx*dx + dy*dy <= self.radius**2

    def draw(self, surface):
        pygame.draw.circle(surface, BLACK, self.rect.center, self.radius)
        pygame.draw.circle(surface, GRAY, self.rect.center, self.radius, 2)