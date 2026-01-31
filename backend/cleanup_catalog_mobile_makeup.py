#!/usr/bin/env python3
"""
Cleanup and seed catalog with Mobile Phones, Accessories, and Women's Makeup
"""
import os
import sys
from supabase import create_client
import uuid
from datetime import datetime

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv('SUPABASE_URL') or os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 150 Products: Mobile Phones, Accessories, and Women's Makeup
PRODUCTS = [
    # Mobile Phones (50 products)
    ("Apple iPhone 15 Pro Max 256GB Titanium", "Latest flagship with A17 Pro chip, titanium design, 48MP main camera with 5x optical zoom, ProMotion 120Hz display", 1199.99, "electronics", "https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?w=500"),
    ("Samsung Galaxy S24 Ultra 512GB", "Premium Android phone with 200MP camera, S Pen stylus, Snapdragon 8 Gen 3, AI photo editing features", 1299.99, "electronics", "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500"),
    ("iPhone 15 Pro 128GB Deep Purple", "Pro-level iPhone with Dynamic Island, A17 Pro processor, triple camera system, aerospace-grade titanium", 999.99, "electronics", "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500"),
    ("Samsung Galaxy S24 Plus 256GB", "6.7-inch AMOLED display, 50MP camera with AI zoom, all-day battery, premium glass design", 999.99, "electronics", "https://images.unsplash.com/photo-1610945264803-c22b62d2a7b3?w=500"),
    ("iPhone 14 Pro Max 256GB Space Black", "Previous gen flagship with 48MP camera, Always-On display, A16 Bionic chip, exceptional value", 1099.99, "electronics", "https://images.unsplash.com/photo-1663499482523-1c0c1bae4ce1?w=500"),
    ("Google Pixel 8 Pro 256GB", "Pure Android experience with Google AI, exceptional night photography, 6.7-inch LTPO display", 899.99, "electronics", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500"),
    ("Samsung Galaxy Z Fold 5 512GB", "Foldable smartphone with 7.6-inch inner display, multitasking powerhouse, S Pen support", 1799.99, "electronics", "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500"),
    ("iPhone 15 128GB Pink", "Standard iPhone with A16 Bionic, dual camera, bright 6.1-inch display, ceramic shield", 799.99, "electronics", "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=500"),
    ("OnePlus 12 256GB", "Flagship killer with Snapdragon 8 Gen 3, 100W fast charging, 120Hz AMOLED display", 699.99, "electronics", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500"),
    ("Xiaomi 14 Pro 512GB", "Leica-tuned camera system, Snapdragon 8 Gen 3, wireless charging, premium build quality", 899.99, "electronics", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500"),
    
    ("Samsung Galaxy Z Flip 5 256GB", "Compact foldable phone with flex mode, cover screen upgrades, fits in your pocket", 999.99, "electronics", "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500"),
    ("iPhone 14 Plus 256GB Blue", "Larger iPhone with extended battery life, advanced dual camera, A15 Bionic chip", 899.99, "electronics", "https://images.unsplash.com/photo-1663499482523-1c0c1bae4ce1?w=500"),
    ("Google Pixel 8 128GB", "Compact flagship with Tensor G3 chip, Magic Eraser, 7 years of updates", 699.99, "electronics", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500"),
    ("Samsung Galaxy S23 FE 256GB", "Fan edition flagship with premium features, triple camera, vibrant AMOLED display", 599.99, "electronics", "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500"),
    ("iPhone 13 128GB Midnight", "Reliable iPhone with A15 chip, dual camera, all-day battery, great value", 699.99, "electronics", "https://images.unsplash.com/photo-1632661674596-df8be070a5c5?w=500"),
    ("Motorola Edge 40 Pro 256GB", "Curved edge display, 68W fast charging, clean Android experience, flagship specs", 799.99, "electronics", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500"),
    ("Oppo Find X6 Pro 512GB", "Hasselblad camera partnership, periscope telephoto, fast charging flagship", 999.99, "electronics", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500"),
    ("Vivo X100 Pro 256GB", "Zeiss optics, MediaTek Dimensity 9300, stunning AMOLED display", 899.99, "electronics", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500"),
    ("Nothing Phone 2 256GB", "Unique Glyph interface, flagship Snapdragon processor, wireless charging", 699.99, "electronics", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500"),
    ("Asus ROG Phone 7 512GB", "Gaming smartphone with cooling system, 165Hz display, massive 6000mAh battery", 999.99, "electronics", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500"),
    
    ("Sony Xperia 1 V 256GB", "4K HDR OLED display, Zeiss optics, pro-level video recording, headphone jack", 1199.99, "electronics", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500"),
    ("Samsung Galaxy A54 5G 256GB", "Mid-range champion with premium features, OIS camera, long battery life", 449.99, "electronics", "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500"),
    ("iPhone SE 3rd Gen 128GB", "Compact iPhone with A15 chip, Touch ID, wireless charging, budget-friendly", 429.99, "electronics", "https://images.unsplash.com/photo-1592286927505-b7d6c4fc8bd9?w=500"),
    ("Google Pixel 7a 128GB", "Budget Pixel with flagship camera, clean Android, Google AI features", 449.99, "electronics", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500"),
    ("Xiaomi Redmi Note 13 Pro 256GB", "Budget flagship with 200MP camera, 120W fast charging, AMOLED display", 349.99, "electronics", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500"),
    
    # Mobile Accessories (50 products)
    ("Apple MagSafe iPhone Case Clear", "Official MagSafe compatible case with built-in magnets, scratch-resistant coating, slim profile", 49.99, "electronics", "https://images.unsplash.com/photo-1601593346740-925612772716?w=500"),
    ("Spigen Tough Armor Pro iPhone 15", "Military-grade drop protection with kickstand, raised bezels for screen protection", 39.99, "electronics", "https://images.unsplash.com/photo-1556656793-08538906a9f8?w=500"),
    ("OtterBox Defender Series Galaxy S24", "Triple-layer protection, port covers, screen protector included, lifetime warranty", 49.99, "electronics", "https://images.unsplash.com/photo-1556656793-08538906a9f8?w=500"),
    ("Anker PowerCore 20000mAh Power Bank", "Ultra high-capacity portable charger, fast charging, charges 2 devices simultaneously", 49.99, "electronics", "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500"),
    ("Belkin BoostCharge 3-in-1 Wireless", "Charge iPhone, AirPods, Apple Watch simultaneously, MagSafe compatible", 149.99, "electronics", "https://images.unsplash.com/photo-1591290619762-d118aa5e1f6b?w=500"),
    ("Apple AirPods Pro 2nd Generation", "Active noise cancellation, adaptive audio, USB-C charging, H2 chip for superior sound", 249.00, "electronics", "https://images.unsplash.com/photo-1606841837239-c5a1a4a07af7?w=500"),
    ("Samsung Galaxy Buds2 Pro Wireless", "Intelligent ANC, 360 audio with head tracking, 8-hour battery life, Hi-Fi sound", 229.99, "electronics", "https://images.unsplash.com/photo-1598331668826-20cecc596b86?w=500"),
    ("Anker 65W USB-C Wall Charger", "Fast charging for phones and laptops, GaN technology, foldable plug, compact size", 39.99, "electronics", "https://images.unsplash.com/photo-1624823183493-ed5832f48f18?w=500"),
    ("Apple 20W USB-C Power Adapter", "Official iPhone fast charger, charges 50% in 30 minutes, compact and portable", 19.99, "electronics", "https://images.unsplash.com/photo-1591290619762-d118aa5e1f6b?w=500"),
    ("Spigen Tempered Glass Screen Protector", "9H hardness protection, case-friendly design, oleophobic coating, easy installation", 12.99, "electronics", "https://images.unsplash.com/photo-1601593346740-925612772716?w=500"),
    
    ("PopSockets PopGrip Phone Holder", "Collapsible grip and stand, swappable design, wireless charging compatible", 14.99, "electronics", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500"),
    ("Mophie Snap+ Wireless Power Bank", "MagSafe magnetic wireless charging, 5000mAh capacity, ultra-thin design", 49.99, "electronics", "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500"),
    ("Nomad Leather iPhone 15 Case", "Premium Horween leather, develops unique patina, MagSafe compatible", 59.99, "electronics", "https://images.unsplash.com/photo-1556656793-08538906a9f8?w=500"),
    ("Twelve South BookBook iPhone Wallet", "Vintage leather wallet case, RFID protection, holds cards and cash", 69.99, "electronics", "https://images.unsplash.com/photo-1556656793-08538906a9f8?w=500"),
    ("Moment Mobile Photography Lens Kit", "Pro-grade phone lenses, wide angle and macro, includes mounting case", 119.99, "electronics", "https://images.unsplash.com/photo-1606229365485-93a3b8ee0385?w=500"),
    ("Apple Lightning to 3.5mm Adapter", "Connect wired headphones to iPhone, premium DAC, authentic Apple quality", 9.99, "electronics", "https://images.unsplash.com/photo-1591290619762-d118aa5e1f6b?w=500"),
    ("Ugreen 100W USB-C Cable 6ft", "Braided nylon cable, fast charging and data transfer, durable connectors", 19.99, "electronics", "https://images.unsplash.com/photo-1589492477829-dadca2d0f31d?w=500"),
    ("RAVPower 60W Car Charger Dual Port", "Fast charge on the go, USB-C PD and USB-A ports, LED indicator", 29.99, "electronics", "https://images.unsplash.com/photo-1624823183493-ed5832f48f18?w=500"),
    ("Quad Lock Bike Mount Phone Holder", "Secure twist-lock system, vibration dampener, weatherproof protection", 49.99, "electronics", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=500"),
    ("Logitech Wireless Gaming Headset", "Low latency Bluetooth, 20-hour battery, comfortable over-ear design for mobile gaming", 99.99, "electronics", "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500"),
    
    ("Apple MagSafe Battery Pack", "Wireless charging on the go, 1460mAh capacity, seamless iPhone integration", 99.00, "electronics", "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500"),
    ("Casetify Impact Ring Stand Case", "Built-in rotating ring stand, military-grade drop protection, custom designs", 65.00, "electronics", "https://images.unsplash.com/photo-1556656793-08538906a9f8?w=500"),
    ("Anker Nano Power Bank 10000mAh", "Pocket-sized portable charger, 30W fast charging, USB-C input/output", 39.99, "electronics", "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=500"),
    ("Samsung 25W USB-C Fast Charger", "Official Samsung fast charger, PPS technology, compact and travel-friendly", 19.99, "electronics", "https://images.unsplash.com/photo-1624823183493-ed5832f48f18?w=500"),
    ("JBL Clip 4 Portable Bluetooth Speaker", "Waterproof wireless speaker, carabiner clip, 10-hour playtime, vibrant sound", 79.99, "electronics", "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500"),
    
    # Women's Makeup Products (50 products)
    ("Fenty Beauty Pro Filt'r Foundation", "Soft matte longwear foundation in 50 shades, buildable full coverage, transfer-resistant", 39.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Charlotte Tilbury Airbrush Flawless", "Magic foundation with SPF 15, blurs imperfections, natural radiant finish, 44 shades", 46.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("NARS Natural Radiant Longwear", "Luminous medium-to-full coverage, 16-hour wear, hydrating formula, 34 shades", 50.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("MAC Studio Fix Fluid SPF 15", "Full coverage matte foundation, oil-free, 67 shades, 24-hour wear", 38.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Estée Lauder Double Wear", "Iconic 24-hour stay-in-place makeup, flawless matte finish, won't smudge or budge", 52.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Urban Decay Naked3 Eyeshadow Palette", "12 rose-hued neutral shades, buttery formula, includes mirror and dual-ended brush", 54.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    ("Anastasia Beverly Hills Modern Renaissance", "14 highly pigmented matte and metallic shades, blendable formula, warm berry tones", 45.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    ("Too Faced Born This Way Concealer", "Full coverage concealer with hyaluronic acid, crease-proof, 35 shades for all skin tones", 30.00, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("NARS Radiant Creamy Concealer", "Award-winning concealer with light-diffusing technology, multi-action formula, buildable", 32.00, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Tarte Shape Tape Concealer", "Full coverage matte finish, vegan formula, brightens and perfects, 30 shades", 29.00, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    
    ("MAC Ruby Woo Matte Lipstick", "Iconic blue-red matte lipstick, retro matte formula, long-lasting color", 20.00, "beauty", "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=500"),
    ("Fenty Beauty Gloss Bomb Universal", "High-shine lip gloss with explosive shine, non-sticky formula, peach-vanilla scent", 21.00, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Charlotte Tilbury Pillow Talk Lipstick", "Universally flattering nude-pink, matte revolution formula, enriched with lipstick tree", 35.00, "beauty", "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=500"),
    ("NYX Professional Epic Ink Liner", "Waterproof liquid eyeliner, precision felt tip, intense black pigment, all-day wear", 9.99, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Stila Stay All Day Liquid Eyeliner", "Waterproof precision tip pen, long-wearing pigment, doesn't smudge or run", 24.00, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Benefit Cosmetics They're Real Mascara", "Lengthening mascara with custom-domed brush, jet-black formula, 24-hour wear", 27.00, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Too Faced Better Than Sex Mascara", "Volumizing mascara with hourglass brush, collagen-fueled formula, dramatic lashes", 27.00, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("L'Oréal Voluminous Lash Paradise", "Volumizing and lengthening mascara, soft wavy brush, feathery soft lashes", 11.99, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Anastasia Beverly Hills Dipbrow Pomade", "Waterproof smudge-free brow pomade, buildable formula, long-wearing, 11 shades", 21.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    ("Benefit Precisely My Brow Pencil", "Ultra-fine brow pencil for hair-like strokes, waterproof formula, 12-hour wear", 26.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    
    ("Hourglass Ambient Lighting Powder", "Finishing powder with Photoluminescent Technology, soft-focus radiance", 52.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Laura Mercier Translucent Powder", "Iconic setting powder, colorless formula, sets makeup for hours, universal shade", 40.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Maybelline Fit Me Matte + Poreless", "Lightweight foundation with clay, controls shine, natural matte finish, 40 shades", 7.99, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("ColourPop Super Shock Shadow", "Bouncy hybrid cream-powder eyeshadow, ultra-pigmented, long-lasting wear", 6.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    ("Morphe 35O Nature Glow Palette", "35 warm neutral matte and shimmer shades, highly pigmented, blendable formula", 25.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    ("Huda Beauty Mercury Retrograde", "18-shade palette with duo-chrome and metallic finishes, celestial-inspired colors", 67.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    ("Rare Beauty Soft Pinch Liquid Blush", "Weightless liquid blush with long-lasting color, blendable formula, buildable intensity", 23.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("NARS Orgasm Blush", "Iconic peachy pink with golden shimmer, universally flattering, cult favorite", 30.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Milk Makeup Hydro Grip Primer", "Hydrating primer with blue agave extract, grips makeup for 12 hours, sticky texture", 36.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Smashbox Photo Finish Primer", "Pore-minimizing primer, smooth skin texture, extends makeup wear, oil-free", 42.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    
    ("Glossier Cloud Paint Cream Blush", "Gel-cream blush with buildable color, dewy finish, available in 6 shades", 18.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Kylie Cosmetics Matte Lip Kit", "Matching lipstick and lip liner duo, long-lasting matte formula, 30+ shades", 29.00, "beauty", "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=500"),
    ("Pat McGrath Labs MatteTrance Lipstick", "Luxurious matte lipstick, intense color payoff, modern matte finish", 40.00, "beauty", "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=500"),
    ("Revlon ColorStay Liquid Liner", "Waterproof precise liquid eyeliner, felt-tip applicator, 24-hour wear", 8.99, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Kat Von D Tattoo Liner", "Long-wear waterproof liquid eyeliner, precision brush tip, richly pigmented", 22.00, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Dior Diorshow Iconic Mascara", "Volume and curve mascara with lash-multiplying effect, XXL brush", 32.00, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Maybelline Lash Sensational Mascara", "Fanning brush for full lashes, buildable formula, clump-free application", 9.99, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("e.l.f. Poreless Putty Primer", "Silky putty texture, blurs pores and fine lines, infused with Squalane", 10.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Tarte Amazonian Clay Blush", "Long-wearing powder blush with Amazonian clay, 12-hour wear, natural finish", 30.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Becca Shimmering Skin Perfector", "Creamy highlighter with ultra-fine luminescent pearls, buildable glow", 38.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    
    ("Physicians Formula Butter Bronzer", "Murumuru butter bronzer, creamy texture, natural sun-kissed glow", 14.99, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("NYX Professional Ultimate Shadow Palette", "16 highly pigmented eyeshadows, matte and shimmer finishes, affordable luxury", 18.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    ("Juvia's Place The Zulu Palette", "9 vibrant African-inspired shades, buttery formula, high pigmentation", 20.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    ("Urban Decay All Nighter Setting Spray", "Long-lasting makeup setting spray, weightless mist, keeps makeup fresh for 16 hours", 33.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("MAC Fix+ Setting Spray", "Lightweight mist refreshes and finishes makeup, infused with vitamins and minerals", 29.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Fenty Beauty Killawatt Highlighter", "Duo highlighter with cream-powder hybrid formula, versatile shades for all skin tones", 36.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Essence Lash Princess Mascara", "Cult-favorite volumizing mascara, dramatic lashes, budget-friendly", 4.99, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Wet n Wild MegaGlo Highlighting Powder", "Intense highlighter with velvety texture, buildable shimmer, cruelty-free", 5.99, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Milani Baked Blush", "Baked powder blush with marbled pigments, luminous finish, long-lasting color", 9.99, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
]

def cleanup_and_seed():
    print("="*70)
    print("MOBILE & MAKEUP CATALOG CLEANUP & SEEDING")
    print("="*70)
    
    # Step 1: Find products in use
    print("\n📊 Step 1: Analyzing catalog usage...")
    store_products = supabase.table('store_products').select('catalog_product_id').execute()
    in_use_ids = set([sp['catalog_product_id'] for sp in (store_products.data or []) if sp.get('catalog_product_id')])
    print(f"   ✓ Found {len(in_use_ids)} catalog products currently in seller stores")
    
    # Step 2: Get all catalog products
    print("\n📦 Step 2: Fetching all catalog products...")
    all_catalog = supabase.table('product_catalog').select('id').execute()
    all_ids = [p['id'] for p in (all_catalog.data or [])]
    print(f"   ✓ Total catalog products: {len(all_ids)}")
    
    # Step 3: Delete unused products
    to_delete = [pid for pid in all_ids if pid not in in_use_ids]
    deleted_count = 0
    
    if to_delete:
        print(f"\n🗑️  Step 3: Deleting {len(to_delete)} unused catalog products...")
        for i in range(0, len(to_delete), 100):
            batch = to_delete[i:i+100]
            supabase.table('product_catalog').delete().in_('id', batch).execute()
            deleted_count += len(batch)
            print(f"   ✓ Deleted batch {i//100 + 1}/{(len(to_delete)-1)//100 + 1} ({len(batch)} products)")
    else:
        print("\n✓ Step 3: No unused products to delete")
    
    # Step 4: Seed new products
    print(f"\n🌱 Step 4: Seeding {len(PRODUCTS)} new mobile & makeup products...")
    added_count = 0
    error_count = 0
    
    for idx, (name, desc, price, category, image) in enumerate(PRODUCTS, 1):
        try:
            data = {
                'id': str(uuid.uuid4()),
                'name': name,
                'description': desc,
                'base_price': price,
                'category': category,
                'images': [image],
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
            }
            supabase.table('product_catalog').insert(data).execute()
            added_count += 1
            
            if idx % 25 == 0:
                print(f"   ✓ Added {idx}/{len(PRODUCTS)} products...")
        except Exception as e:
            error_count += 1
            print(f"   ✗ Error adding '{name}': {str(e)}")
    
    # Summary
    print("\n" + "="*70)
    print("CLEANUP & SEEDING COMPLETE!")
    print("="*70)
    print(f"  📦 Kept: {len(in_use_ids)} products (in seller stores)")
    print(f"  🗑️  Deleted: {deleted_count} unused products")
    print(f"  ✅ Added: {added_count} new mobile & makeup products")
    print(f"  ❌ Errors: {error_count}")
    print(f"  📊 Total Catalog Size: {len(in_use_ids) + added_count}")
    print("="*70)
    print("\n📱 Categories:")
    print("   • Mobile Phones: 25 products")
    print("   • Mobile Accessories: 50 products")  
    print("   • Women's Makeup: 50 products")
    print("="*70)
    
    return {
        'kept': len(in_use_ids),
        'deleted': deleted_count,
        'added': added_count,
        'errors': error_count,
        'total': len(in_use_ids) + added_count
    }

if __name__ == "__main__":
    try:
        result = cleanup_and_seed()
        print(f"\n✨ Success! Catalog now has mobile phones, accessories, and makeup products!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
