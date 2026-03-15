# ==========================================
# config.py - SİMÜLASYON KONTROL PANELİ
# ==========================================

STARTUP_MODE = "RAIN" # "SNOW" veya "RAIN"

# --- EKRAN VE ÖLÇEK ---
SCALE_FACTOR = 4
LOGICAL_W = 320
LOGICAL_H = 180
SCREEN_WIDTH = LOGICAL_W * SCALE_FACTOR   
SCREEN_HEIGHT = LOGICAL_H * SCALE_FACTOR  

# --- FİZİK VE DÜNYA ---
MAX_WIND = 10                   
GRAVITY = 0.8  
BOX_WIDTH = 30 * SCALE_FACTOR             
BOX_HEIGHT = 30 * SCALE_FACTOR            

# --- KAR AYARLARI ---
MAX_SNOW_GROUND = 250           
MAX_SNOW_BOX = 100              
SNOW_MELT_PROBABILITY = 0.5     # Karın kendi kendine erime şansı (%)
RAIN_MELT_PROBABILITY = 15.0    # Yağmurda karın erime şansı (%)
RAIN_IMPACT_MELT_CHANCE = 0.1   # Yağmur damlası çarptığında erime şansı
MELT_INTERVAL_FRAMES = 10       
DYNAMIC_MELT_HIGH = 0.32        # Hızlı erime başlangıç oranı
DYNAMIC_MELT_LOW = 0.27         # Normal erimeye dönüş oranı

# --- YAĞIŞ YOĞUNLUĞU (1280px baz alınarak) ---
RAIN_DENSITY = 800
SNOW_DENSITY = 1500

# --- VEJETASYON (ÇİM VE ÇİÇEK) ---
GRASS_SPACING = 4               # Kaç pikselde bir çim çıksın
GRASS_PROBABILITY = 0.8         # Çim çıkma olasılığı
FLOWER_PROBABILITY = 0.08       # Çiçek olma olasılığı
MUTANT_PROBABILITY = 0.03       # Mutant olma olasılığı

# --- Sizin Ayarlarınız (Restored) ---
GRASS_BASE_HEIGHT = 22.0        # Çimlerin genel başlangıç boyu
GRASS_VARIATION = 6.0           # Bireysel boy farkı (random)
GRASS_ROLLING_AMP_1 = GRASS_BASE_HEIGHT // 2       # Büyük dalga genliği
GRASS_ROLLING_AMP_2 = GRASS_BASE_HEIGHT // 2.5       # Küçük detay dalga genliği
MUTANT_HEIGHT_MIN = GRASS_BASE_HEIGHT + 23
MUTANT_HEIGHT_MAX = GRASS_BASE_HEIGHT + 38

# --- Yeni Kontrol Değişkenleri ---
GRASS_ROLLING_FREQ_1 = 0.05     # Büyük dalga sıklığı
GRASS_ROLLING_FREQ_2 = 0.01     # Küçük dalga sıklığı
GRASS_GROWTH_SPEED = 0.2        # Yağmurda büyüme hızı
GRASS_BEND_FACTOR = 3.2         # Rüzgarda yatma şiddeti
GRASS_WIND_SPEED_MULT = 1.5     # Rüzgar hızının çime etki çarpanı
GRASS_OSCILLATION_AMP = 2.0     # Çimlerin kendi kendine sallanma şiddeti

# --- IŞIK VE ATMOSFER ---
AMBIENT_COLOR = (30, 40, 75)     
LAMP_COLOR = (255, 230, 180)     
LAMP_INTENSITY = 2.5             
LAMP_TOP_X = 53                  
LAMP_TOP_Y = 15     
LAMP_SPREAD = 550                
GLOW_RADIUS_FACTOR = 55         # SCALE_FACTOR ile çarpılır (Sizin Ayarınız)
GLOW_SOFTNESS = 3.0             # Yüksek değer = Daha yumuşak kenarlar

# --- RENKLER ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
ICE_BLUE = (200, 230, 255)