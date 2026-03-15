# ==========================================
# main.py - OYUN DÖNGÜSÜ VE RENDER
# ==========================================
import pygame
import ctypes
import os
import math
import random # Fizik için gerekli

if os.name == 'nt':
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass

# =====================================================================
# --- INTEGRATED CONFIG (SADECE MAIN'E ÖZEL) ---
# =====================================================================
# Ekran ve Ölçek Ayarları
SCALE_FACTOR = 4
LOGICAL_W = 320
LOGICAL_H = 180
SCREEN_WIDTH = LOGICAL_W * SCALE_FACTOR   
SCREEN_HEIGHT = LOGICAL_H * SCALE_FACTOR  

# Kutu Ayarları
BOX_WIDTH = 30 * SCALE_FACTOR             
BOX_HEIGHT = 30 * SCALE_FACTOR            

# Fizik Ayarları
MAX_WIND = 10                   
GRAVITY = 0.8  

# Kar Birikme Limitleri
MAX_SNOW_GROUND = 250           
MAX_SNOW_BOX = 100              

# Erime Ayarları
MELT_INTERVAL_FRAMES = 10       
SNOW_MELT_PROBABILITY = 0.5     
RAIN_MELT_PROBABILITY = 15.0    
RAIN_IMPACT_MELT_CHANCE = 0.1   

# Dinamik Erime (Kullanıcı Ayarları) - BURAYA SENİN DEĞERLERİNİ YAZDIM!
DYNAMIC_MELT_HIGH = 0.32        
DYNAMIC_MELT_LOW = 0.27         

# --- GÜNCELLENDİ: GERÇEK PHOTOSHOP IŞIK VE GECE AYARLARI ---
# Gece ortamının rengi (Donuk gri değil, sıcak sapsarı ışığı canlandıracak Koyu Lacivert)
AMBIENT_COLOR = (20, 40, 100)     

# Sokak lambasının ANA RENGİ (Sıcak sapsarı).
LAMP_COLOR = (255, 230, 0)     
# Işık şiddeti (Ekranda 3.5 gibi sature bir sarı için bunu artırabilirsin)
LAMP_INTENSITY = 12.5             

# Lamba Konumu (Piksel değil, mantıksal koordinat)
LAMP_TOP_X = 53 #LOGICAL_W // 2      # Ekranın tam ortası
LAMP_TOP_Y = 15                  # Tepeden biraz aşağıda
LAMP_SPREAD = 280                # Işığın yere vurduğundaki taban genişliği
# -----------------------------------

# Klasik Renkler (Çizim için temel renkler, ışık filtresi bunları değiştirecek)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
ICE_BLUE = (200, 230, 255)

# =====================================================================
# --- FİZİK VE PARTİKÜL SINIFLARI (DOKUNMA) ---
# =====================================================================
from physics import ParticleSystem, PhysicsBox

# =====================================================================
# --- PHOTOSHOP BLEND MAGIC MOTORU ---
# =====================================================================

def create_perfect_volumetric_cone():
    """
    Matematiksel olarak kusursuz, duvar etkisi yaratmayan ve 
    ışık gücünü koruyan volumetrik piksel motoru.
    """
    SAMPLING_W, SAMPLING_H = 400, 200
    surf = pygame.Surface((SAMPLING_W, SAMPLING_H))
    surf.fill((0, 0, 0)) # Additive blend için siyah arka plan.
    
    center_x = SAMPLING_W / 2.0
    
    # Koni en altta yüzeyin sınırlarına DEĞMEDEN bitsin ki duvar etkisi olmasın (%95'ini kullanıyoruz)
    MAX_RADIUS = (SAMPLING_W / 2.0) * 0.95 

    for y in range(SAMPLING_H):
        y_ratio = y / float(SAMPLING_H)
        
        # Yarıçap artık en altta MAX_RADIUS (yaklaşık 190 px) olacak. Yüzey dışına taşmaz.
        r = max(3.0, y_ratio * MAX_RADIUS)
        
        # Dikey sönümlenmeyi hafiflettik. Işık yere değdiğinde tamamen siyah olmasın, %40 gücünü korusun.
        v_fade = 1.0 - (y_ratio * 0.6) 
        
        for x in range(SAMPLING_W):
            dx = abs(x - center_x)
            if dx <= r:
                horizontal_ratio = dx / r
                
                # Yatay sönümlenme: 3.0 çok simsiyahtı, 2.0 (Karesel) daha pürüzsüz bir duman/sis etkisi verir
                h_fade = math.pow(1.0 - horizontal_ratio, 2.0) 
                
                # Işık kaynağı halesi (Lamba ampulü parlaması)
                halo_dist = math.sqrt(dx**2 + y**2)
                halo_fade = 0
                if halo_dist <= 15:
                    halo_fade = math.pow(1.0 - (halo_dist / 15.0), 1.5) * 1.5 # Haloyu biraz daha parlak yaptık
                
                # Parlaklığı hesapla. h_fade ve v_fade'i çarpmak yerine, ışığın hacmini korumak için 
                # formülü biraz açtık. (Base intensity ile)
                brightness = min(1.0, (h_fade * v_fade) + halo_fade) * LAMP_INTENSITY
                
                if brightness > 0.01: # Gereksiz sıfıra yakın pikselleri atla (optimizasyon)
                    c_r = min(255, int(LAMP_COLOR[0] * brightness))
                    c_g = min(255, int(LAMP_COLOR[1] * brightness))
                    c_b = min(255, int(LAMP_COLOR[2] * brightness))
                    
                    surf.set_at((x, y), (c_r, c_g, c_b))
                
    cone_w = LAMP_SPREAD * SCALE_FACTOR
    cone_h = SCREEN_HEIGHT * 1.2 
    
    smooth_cone = pygame.transform.smoothscale(surf, (int(cone_w), int(cone_h)))
    
    return smooth_cone, cone_w, cone_h
                
    # Bu kusursuz 200x200 dokuyu, ekrandaki gerçek lamba ebatlarına pürüzsüzce sündür
    cone_w = LAMP_SPREAD * SCALE_FACTOR
    cone_h = SCREEN_HEIGHT * 1.0 # Ekranın altına kadar uzansın
    
    # smoothscale kullanarak pikselleri mükemmel bir şekilde birbirine yedir
    smooth_cone = pygame.transform.smoothscale(surf, (int(cone_w), int(cone_h)))
    
    return smooth_cone, cone_w, cone_h

def main2():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("WindSim PC v2.6 - True Volumetric Blending (Fix)")
    
    clock = pygame.time.Clock()
    particles = ParticleSystem()
    box = PhysicsBox()

    scale_mode = "Retro_Scale"
    speed_level = 10 
    lamp_on = True 
    
    last_input_time = pygame.time.get_ticks()

    # Piksel motorunun yarattığı o kusursuz ışık konisini oyun başlamadan bir kere oluştur
    scaled_light, light_w, light_h = create_perfect_volumetric_cone()

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

        # 1. AŞAMA: Dünyayı bembeyaz çiz (Filtreden önceki ham hal)
        # Karlar, tanecikler ve BOX, hepsi gündüz gibi bembeyaz çizilir
        particles.draw_particles(screen, scale_mode)
        particles.draw_snow_accumulation(screen, box, scale_mode)
        box.draw(screen)
        particles.draw_splashes(screen, scale_mode)

        # 2. AŞAMA: Işık ve Gece Maskesi (Multiply Blending)
        lamp_x = LAMP_TOP_X * SCALE_FACTOR
        lamp_y = LAMP_TOP_Y * SCALE_FACTOR

        # Karanlık bir gece maskesi oluştur
        light_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # GÜNCELLENDİ: Sıcak sapsarı ışık için gece rengini soğuk bir lacivert yaptık (Lacivert+Sarı = Yeşilimsi Altın)
        light_surface.fill(AMBIENT_COLOR) # Koyu Lacivert

        if lamp_on:
            # Pürüzsüz konik ışığın tepe noktasını lambanın olduğu yere bağla (midtop)
            light_rect = scaled_light.get_rect(midtop=(lamp_x, lamp_y))
            # Siyah zemin üzerine çizdiğimiz ışığı karanlığa "TOPLA". (Add Modu: Siyahlar görünmez, sarılar parlar)
            light_surface.blit(scaled_light, light_rect, special_flags=pygame.BLEND_RGB_ADD)

        # Oluşan bu muhteşem lacivert ve sarı manzarayı bembeyaz dünyanın üzerine "ÇARP"
        screen.blit(light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # 3. AŞAMA: Lamba Direği ve Ampul (Maskeden SONRA çizilir)
        pygame.draw.line(screen, (80, 80, 80), (lamp_x, lamp_y), (lamp_x, SCREEN_HEIGHT), max(1, SCALE_FACTOR//2))
        
        if lamp_on:
            # Ampulün içindeki parlayan gerçek beyaz sıcak nokta
            pygame.draw.circle(screen, (255, 255, 255), (lamp_x, lamp_y), int(SCALE_FACTOR * 0.8))

        # 4. AŞAMA: UI
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
    main2()