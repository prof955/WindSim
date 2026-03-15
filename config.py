# ==========================================
# config.py - DOĞA VE FİZİK AYARLARI
# ==========================================

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

# Dinamik Erime
DYNAMIC_MELT_HIGH = 0.32        
DYNAMIC_MELT_LOW = 0.27         

# --- IŞIK VE GECE AYARLARI ---
# Gece ortamının rengi (Senin harika sinematik seçimin)
AMBIENT_COLOR = (30, 40, 75)     

# Sokak lambasının ANA RENGİ (Sıcak Beyaz/Sarı)
LAMP_COLOR = (255, 230, 180)     

# Işık Şiddeti
LAMP_INTENSITY = 2.5             

# Lamba Konumu
LAMP_TOP_X = 53                  
LAMP_TOP_Y = 15     

# YENİ: Yeşil ok ile gösterdiğin o uzun sönümlenmenin (gradientin) 
# ekrana sığabilmesi için taban genişliğini artırdık.
LAMP_SPREAD = 550                
# -----------------------------------

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
ICE_BLUE = (200, 230, 255)