# ==========================================
# main.py - OYUN DÖNGÜSÜ VE RENDER
# ==========================================
import pygame
import ctypes
import os
import math
import random
from config import *
from physics import ParticleSystem, PhysicsBox

if os.name == 'nt':
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass

def create_true_light_cone():
    """
    Yeşil Bölge Çözümü: Çekirdek (Core) ve Sündürülmüş Gradient (Fade) Mantığı
    """
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
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("WindSim PC v3.2 - Layer Fixed & Gradient Stretched")
    
    clock = pygame.time.Clock()
    particles = ParticleSystem()
    box = PhysicsBox()

    scale_mode = "Retro_Scale"
    speed_level = 10 
    lamp_on = True 
    
    last_input_time = pygame.time.get_ticks()
    light_cone_texture = create_true_light_cone()

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
                        speed_level = max(0, speed_level - 1)

        speed_mult = speed_level * 0.064 

        box.update(mouse_pos, mouse_pressed, particles)
        if box.dragging and box.vy == 0:
             particles.snow_box = [max(0, h-2) for h in particles.snow_box]

        particles.update_physics(box, speed_mult)

        # =====================================================================
        # YENİ RENDER SIRALAMASI (KATMAN ÇÖZÜMÜ)
        # =====================================================================
        lamp_x = LAMP_TOP_X * SCALE_FACTOR
        lamp_y = LAMP_TOP_Y * SCALE_FACTOR

        # 1. EN ARKA: Lamba Direği ve Armatürü
        draw_retro_lamp(screen, lamp_x, lamp_y, SCALE_FACTOR)
        # Ekranın sağında simetrik bir sokak lambası
        lamp_x_right = SCREEN_WIDTH - lamp_x
        draw_retro_lamp(screen, lamp_x_right, lamp_y, SCALE_FACTOR)

        # 2. ORTA KATMAN: Karlar, Kutu ve Birikintiler (Artık direğin önündeler!)
        particles.draw_particles(screen, scale_mode)
        particles.draw_snow_accumulation(screen, box, scale_mode)
        box.draw(screen)
        particles.draw_splashes(screen, scale_mode)

        # 3. EN ÜST KATMAN: Işık ve Gece Maskesi (Multiply)
        night_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        night_overlay.fill(AMBIENT_COLOR) 

        if lamp_on:
            # Soldaki lamba için ışık konisi ve bloom
            light_rect = light_cone_texture.get_rect(midtop=(lamp_x, lamp_y))
            night_overlay.blit(light_cone_texture, light_rect)

            glass_h = 4 * SCALE_FACTOR
            center_y = lamp_y - (glass_h // 2)
            glow_radius = 12 * SCALE_FACTOR
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            for r in range(glow_radius, 0, -1):
                alpha = int(255 * (1.0 - (r / glow_radius)))
                pygame.draw.circle(glow_surf, (LAMP_COLOR[0], LAMP_COLOR[1], LAMP_COLOR[2], alpha), (glow_radius, glow_radius), r)
            night_overlay.blit(glow_surf, (lamp_x - glow_radius, center_y - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)

            # Sağdaki lamba için ışık konisi ve bloom
            lamp_x_right = SCREEN_WIDTH - lamp_x
            light_rect_right = light_cone_texture.get_rect(midtop=(lamp_x_right, lamp_y))
            night_overlay.blit(light_cone_texture, light_rect_right)

            center_y_right = lamp_y - (glass_h // 2)
            glow_surf_right = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            for r in range(glow_radius, 0, -1):
                alpha = int(255 * (1.0 - (r / glow_radius)))
                pygame.draw.circle(glow_surf_right, (LAMP_COLOR[0], LAMP_COLOR[1], LAMP_COLOR[2], alpha), (glow_radius, glow_radius), r)
            night_overlay.blit(glow_surf_right, (lamp_x_right - glow_radius, center_y_right - glow_radius), special_flags=pygame.BLEND_RGBA_ADD)

        screen.blit(night_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # 4. UI
        if current_time - last_input_time < 10000: 
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
                screen.blit(font.render(text, True, ui_color), (15, 15 + (i * 25)))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()