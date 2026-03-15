# ==========================================
# main.py - OYUN DÖNGÜSÜ VE RENDER
# ==========================================
import pygame
import ctypes
import os
import math
import random
from config import *
from physics import ParticleSystem, PhysicsBox, PhysicsCircle

if os.name == 'nt':
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass

def create_true_light_cone():
    #Yeşil Bölge Çözümü: Çekirdek (Core) ve Sündürülmüş Gradient (Fade) Mantığı
    
    log_w = LAMP_SPREAD
    log_h = LOGICAL_H
    
    surf = pygame.Surface((log_w, log_h), pygame.SRCALPHA)
    center_x = log_w // 2
    
    for y in range(log_h):
        top_w = 6 
        bot_w = log_w 
        current_w = top_w + (bot_w - top_w) * (y / float(log_h))
        half_w = current_w / 2.0
        
        # --- ASIL DÜZELTME BURADA ---
        # 0.6 yerine 3.0 kullanıyoruz. Işık aşağı indikçe hızla sönümlenecek.
        v_fade = 1.0 - (y / float(log_h))
        v_fade = math.pow(v_fade, 1.2) # 3 idi burası
        # ----------------------------
        
        start_x = max(0, int(center_x - half_w))
        end_x = min(log_w, int(center_x + half_w))
        
        for x in range(start_x, end_x):
            dist = abs(x - center_x)
            ratio = dist / half_w
            
            core_ratio = 0.20
            
            if ratio <= core_ratio:
                h_fade = 1.0
            else:
                fade_ratio = (ratio - core_ratio) / (1.0 - core_ratio)
                h_fade = math.pow(max(0.0, 1.0 - fade_ratio), 2.0)
            
            alpha = h_fade * v_fade * 255 * LAMP_INTENSITY
            alpha = max(0, min(255, int(alpha))) 
            
            if alpha > 0:
                surf.set_at((x, y), (LAMP_COLOR[0], LAMP_COLOR[1], LAMP_COLOR[2], alpha))
                
    scaled_surf = pygame.transform.smoothscale(surf, (LAMP_SPREAD * SCALE_FACTOR, SCREEN_HEIGHT))
    return scaled_surf

def draw_retro_lamp(surface, center_x, bottom_of_glass_y, scale):
    """
    Elektrik Direği ve Pixel Art Armatür Referanslarına Göre Çizim
    """
    # 1. Kalın Elektrik Direği (Aşağı kadar iner)
    pole_w = 4 * scale
    pole_x = center_x - pole_w // 2
    pygame.draw.rect(surface, (35, 35, 40), (pole_x, bottom_of_glass_y, pole_w, SCREEN_HEIGHT))
    # Direğe derinlik katmak için sağ tarafına 1px ince highlight
    pygame.draw.rect(surface, (55, 55, 60), (pole_x + pole_w - scale, bottom_of_glass_y, scale, SCREEN_HEIGHT))

    # 2. Armatür Tabanı (Camın altındaki metal parça)
    base_w = 8 * scale
    base_h = 2 * scale
    pygame.draw.rect(surface, (25, 25, 30), (center_x - base_w//2, bottom_of_glass_y, base_w, base_h))

    # 3. Parlayan Cam Bölümü
    glass_w = 6 * scale
    glass_h = 4 * scale
    glass_y = bottom_of_glass_y - glass_h
    pygame.draw.rect(surface, (255, 250, 220), (center_x - glass_w//2, glass_y, glass_w, glass_h))

    # 4. Şapka / Gövde Üstü (Geniş siyah kısım)
    hat_w = 12 * scale
    hat_h = 3 * scale
    hat_y = glass_y - hat_h
    pygame.draw.rect(surface, (15, 15, 20), (center_x - hat_w//2, hat_y, hat_w, hat_h))
    # Şapkanın en tepesindeki minik çıkıntı
    pygame.draw.rect(surface, (15, 15, 20), (center_x - 4*scale, hat_y - scale, 8*scale, scale))


def main():
    global SCREEN_WIDTH, SCREEN_HEIGHT, SCALE_FACTOR
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("WindSim PC v3.2 - Layer Fixed & Gradient Stretched")
    
    clock = pygame.time.Clock()
    particles = ParticleSystem()
    boxes = [
        PhysicsBox(SCREEN_WIDTH // 2 - 100), 
        PhysicsBox(SCREEN_WIDTH // 2 + 60),
        PhysicsCircle(SCREEN_WIDTH // 2 + 190)
    ]

    scale_mode = "Retro_Scale"
    speed_level = 10 
    lamp_on = True 
    
    last_input_time = pygame.time.get_ticks()
    light_cone_texture = create_true_light_cone()
    
    # Pre-render glow (downward semi-circle)
    # Pre-render glow (downward semi-circle) - CONFIG DRIVEN
    glow_radius = GLOW_RADIUS_FACTOR * SCALE_FACTOR
    glow_surf = pygame.Surface((glow_radius * 2, glow_radius), pygame.SRCALPHA)
    for y in range(glow_radius):
        for x in range(glow_radius * 2):
            dx = x - glow_radius
            dy = y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < glow_radius:
                ratio = dist / glow_radius
                # GLOW_SOFTNESS (power) ile kenarları yumuşat
                alpha_factor = math.pow(max(0.0, 1.0 - ratio), GLOW_SOFTNESS)
                alpha = int(alpha_factor * 255 * LAMP_INTENSITY * 0.4)
                alpha = max(0, min(255, alpha))
                if alpha > 0:
                    glow_surf.set_at((x, y), (LAMP_COLOR[0], LAMP_COLOR[1], LAMP_COLOR[2], alpha))

    # Pre-create night overlay surface for performance
    night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        screen.fill(BLACK)
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                last_input_time = current_time 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        if particles.mode != "SNOW":
                            particles.rain_drops.clear()
                            particles.splashes.clear()
                        particles.mode = "SNOW"
                    if event.key == pygame.K_r:
                        if particles.mode != "RAIN":
                            particles.snow_flakes.clear()
                            particles.splashes.clear()
                        particles.mode = "RAIN"
                    if event.key == pygame.K_TAB:
                        scale_mode = "New_Scale" if scale_mode == "Retro_Scale" else "Retro_Scale"
                    if event.key == pygame.K_l:  
                        lamp_on = not lamp_on
                    if event.key == pygame.K_RIGHT: 
                        particles.wind_speed = min(particles.wind_speed + 1.0, MAX_WIND)
                    if event.key == pygame.K_LEFT: 
                        particles.wind_speed = max(particles.wind_speed - 1.0, -MAX_WIND)
                    if event.key == pygame.K_UP:
                        speed_level = min(10, speed_level + 1)
                    if event.key == pygame.K_DOWN:
                        speed_level = max(-1, speed_level - 1)
            elif event.type == pygame.VIDEORESIZE:
                old_w, old_h = screen.get_size()
                new_w, new_h = event.w, event.h
                
                # Global (module-level) değişkenleri hemen güncelle
                SCREEN_WIDTH, SCREEN_HEIGHT = new_w, new_h
                
                # Config modülünü de güncelle (diğer dosyalar oradan okuyor)
                import config
                config.SCREEN_WIDTH = new_w
                config.SCREEN_HEIGHT = new_h
                config.SCALE_FACTOR = max(1, new_h // 180)
                SCALE_FACTOR = config.SCALE_FACTOR
                
                import physics
                physics.SCREEN_WIDTH = new_w
                physics.SCREEN_HEIGHT = new_h
                physics.SCALE_FACTOR = config.SCALE_FACTOR
                
                screen = pygame.display.set_mode((new_w, new_h), pygame.RESIZABLE)
                
                # Fizik dünyasını ve nesneleri uyar
                particles.resize(new_w, new_h, old_w, old_h, boxes)
                
                # Işıkları yeni boyutlara göre baştan render et
                light_cone_texture = create_true_light_cone()
                glow_radius = GLOW_RADIUS_FACTOR * SCALE_FACTOR
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius), pygame.SRCALPHA)
                for y in range(glow_radius):
                    for x in range(glow_radius * 2):
                        dx = x - glow_radius
                        dy = y
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < glow_radius:
                            ratio = dist / glow_radius
                            alpha_f = math.pow(max(0.0, 1.0 - ratio), GLOW_SOFTNESS)
                            alpha = int(alpha_f * 255 * LAMP_INTENSITY * 0.4)
                            alpha = max(0, min(255, alpha))
                            if alpha > 0:
                                glow_surf.set_at((x, y), (LAMP_COLOR[0], LAMP_COLOR[1], LAMP_COLOR[2], alpha))
                
                night_overlay = pygame.Surface((new_w, new_h))

        speed_mult = max(0, speed_level) * 0.064
        if speed_level == -1:
            particles.snow_flakes.clear()
            particles.rain_drops.clear()
            particles.splashes.clear() 

        if mouse_pressed and not any(b.dragging for b in boxes):
            for box in reversed(boxes):
                if box.collidepoint(mouse_pos):
                    box.dragging = True
                    box.offset_x = box.rect.x - mouse_pos[0]
                    box.offset_y = box.rect.y - mouse_pos[1]
                    box.vy = 0
                    break
        elif not mouse_pressed:
            for box in boxes:
                box.dragging = False

        for box in boxes:
            box.update(mouse_pos, particles, boxes)
            if box.dragging and box.vy == 0:
                 box.snow_box = [max(0, h-2) for h in box.snow_box]

        # --- AABB Collision (Kutu Etkileşim) ---
        for _ in range(3):
            for i in range(len(boxes)):
                for j in range(i + 1, len(boxes)):
                    b1 = boxes[i]
                    b2 = boxes[j]
                    if b1.rect.colliderect(b2.rect):
                        dx = b1.rect.centerx - b2.rect.centerx
                        dy = b1.rect.centery - b2.rect.centery
                        overlap_x = (b1.rect.width + b2.rect.width)/2 - abs(dx)
                        overlap_y = (b1.rect.height + b2.rect.height)/2 - abs(dy)
                        
                        if overlap_x > 0 and overlap_y > 0:
                            if overlap_x < overlap_y:
                                if b1.dragging and not b2.dragging: 
                                    b2.rect.x += int(overlap_x) if dx < 0 else -int(overlap_x)
                                elif b2.dragging and not b1.dragging: 
                                    b1.rect.x += int(overlap_x) if dx > 0 else -int(overlap_x)
                                else:
                                    sign = 1 if dx > 0 else -1
                                    b1.rect.x += int(overlap_x / 2) * sign
                                    b2.rect.x -= int(overlap_x / 2) * sign
                            else:
                                if b1.dragging and not b2.dragging:
                                    b2.rect.y += int(overlap_y) if dy < 0 else -int(overlap_y)
                                    b2.vy = 0
                                elif b2.dragging and not b1.dragging:
                                    b1.rect.y += int(overlap_y) if dy > 0 else -int(overlap_y)
                                    b1.vy = 0
                                else:
                                    sign = 1 if dy > 0 else -1
                                    b1.rect.y += int(overlap_y / 2) * sign
                                    b2.rect.y -= int(overlap_y / 2) * sign
                                    b1.vy = 0
                                    b2.vy = 0
        
        for box in boxes:
            if box.rect.left < 0: box.rect.left = 0
            if box.rect.right > SCREEN_WIDTH: box.rect.right = SCREEN_WIDTH

        particles.update_physics(boxes, speed_mult)

        # =====================================================================
        # YENİ RENDER SIRALAMASI (KATMAN ÇÖZÜMÜ)
        # =====================================================================
        # 218: lamp_x = (LAMP_TOP_X / 320) * SCREEN_WIDTH 
        # 219: lamp_y = (LAMP_TOP_Y / 180) * SCREEN_HEIGHT
        # Yerine daha kontrollü bir ölçekleme:
        lamp_x = LAMP_TOP_X * SCALE_FACTOR
        lamp_y = LAMP_TOP_Y * SCALE_FACTOR

        # 1. EN ARKA: Lamba Direği ve Armatürü
        draw_retro_lamp(screen, lamp_x, lamp_y, SCALE_FACTOR)
        # Ekranın sağında simetrik bir sokak lambası
        lamp_x_right = SCREEN_WIDTH - lamp_x
        draw_retro_lamp(screen, lamp_x_right, lamp_y, SCALE_FACTOR)

        # 2. ORTA KATMAN: Karlar, Kutu ve Birikintiler (Artık direğin önündeler!)
        particles.draw_particles(screen, scale_mode)
        particles.draw_grass(screen, scale_mode, speed_mult)
        particles.draw_snow_accumulation(screen, boxes, scale_mode)
        for box in boxes:
            box.draw(screen)
        particles.draw_splashes(screen, scale_mode)

        # 3. EN ÜST KATMAN: Işık ve Gece Maskesi (Multiply)
        night_overlay.fill(AMBIENT_COLOR)

        if lamp_on:
            # Soldaki lamba için ışık konisi ve bloom
            light_rect = light_cone_texture.get_rect(midtop=(lamp_x, lamp_y))
            night_overlay.blit(light_cone_texture, light_rect)

            glow_y = lamp_y - (4 * SCALE_FACTOR) + 8 # Camin ustu DEĞİL, ortası gibi.
            night_overlay.blit(glow_surf, (lamp_x - glow_radius, glow_y))

            # Sağdaki lamba için ışık konisi ve bloom
            lamp_x_right = SCREEN_WIDTH - lamp_x
            light_rect_right = light_cone_texture.get_rect(midtop=(lamp_x_right, lamp_y))
            night_overlay.blit(light_cone_texture, light_rect_right)
            night_overlay.blit(glow_surf, (lamp_x_right - glow_radius, glow_y))

        screen.blit(night_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # 4. UI
        if current_time - last_input_time < 1000: 
            font = pygame.font.SysFont("Courier New", 18, bold=True)
            ui_color = (150, 255, 150)
            
            max_snow = max(particles.snow_ground) if particles.snow_ground else 0
            snow_pct = int((max_snow / MAX_SNOW_GROUND) * 100) if MAX_SNOW_GROUND > 0 else 0
            
            if particles.is_rapid_melting:
                melt_status = f"RAPID ({particles.current_melt_mult:.1f}x)"
                ui_color = (255, 150, 150) 
            else:
                melt_status = "NORMAL"

            lamp_txt = "ON" if lamp_on else "OFF"
            texts = [
                f"MODE: {particles.mode} | WIND: {int(particles.wind_speed)} | SPEED: {speed_level}/10",
                f"SCALE: {scale_mode} (TAB) | ACCUM: %{snow_pct} | MELT: {melt_status}",
                f"LAMP: {lamp_txt} (Press L) | Arrows: Adjust | R/S: Weather"
            ]
            
            for i, text in enumerate(texts):
                txt_surf = font.render(text, True, ui_color)
                txt_rect = txt_surf.get_rect(center=(SCREEN_WIDTH // 2, 30 + (i * 25)))
                screen.blit(txt_surf, txt_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()