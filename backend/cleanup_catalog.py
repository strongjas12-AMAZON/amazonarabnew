#!/usr/bin/env python3
"""
Cleanup old products and seed 150 unique products
Run this from backend directory with: python3 cleanup_catalog.py
"""
import os
import sys
from supabase import create_client
import uuid
from datetime import datetime

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 150 Unique Products
PRODUCTS = [
    ("Apple iPhone 15 Pro Max 256GB", "Latest flagship smartphone with titanium design, A17 Pro chip, ProMotion display, and advanced triple camera system with 5x optical zoom", 1199.99, "electronics", "https://images.unsplash.com/photo-1678685888221-cda773a3dcdb?w=500"),
    ("Samsung Galaxy S24 Ultra", "Premium Android flagship featuring 200MP camera with AI enhancement, built-in S Pen stylus, and powerful Snapdragon processor", 1299.99, "electronics", "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500"),
    ("Sony WH-1000XM5 Headphones", "Industry-leading noise cancellation wireless over-ear headphones with 30-hour battery life and exceptional audio quality", 399.99, "electronics", "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500"),
    ("MacBook Pro 16-inch M3 Max", "Professional laptop with powerful M3 Max chip, stunning Liquid Retina XDR display, and up to 22 hours battery life", 2499.99, "electronics", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500"),
    ("Dell XPS 15 Laptop", "Premium Windows laptop featuring InfinityEdge 4K display, 13th Gen Intel Core i7, and NVIDIA RTX graphics", 1899.99, "electronics", "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500"),
    ("iPad Pro 12.9-inch M2", "Powerful tablet with M2 chip, Liquid Retina XDR display, Apple Pencil compatibility for creative professionals", 1099.99, "electronics", "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500"),
    ("Samsung Galaxy Tab S9 Ultra", "Premium Android tablet with expansive 14.6-inch display, S Pen included, water-resistant design", 799.99, "electronics", "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=500"),
    ("Apple Watch Series 9 GPS", "Advanced fitness smartwatch with always-on Retina display, health monitoring, crash detection, and ECG app", 399.99, "electronics", "https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?w=500"),
    ("Fitbit Charge 6 Tracker", "Fitness band with built-in GPS, continuous heart rate monitoring, SpO2 tracking, and 7-day battery life", 159.99, "electronics", "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=500"),
    ("Canon EOS R6 Mark II Camera", "Professional mirrorless camera with 24.2MP full-frame sensor, 40fps continuous shooting, advanced autofocus", 2499.99, "electronics", "https://images.unsplash.com/photo-1606980623314-459e0c5c9de8?w=500"),
    ("Sony Alpha A7 IV Mirrorless", "Full-frame 33MP camera with 4K 60p video recording, fast hybrid autofocus, and professional features", 2498.00, "electronics", "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=500"),
    ("GoPro Hero 12 Black Action Camera", "Waterproof 5.3K action camera with HyperSmooth stabilization, voice control, and live streaming", 399.99, "electronics", "https://images.unsplash.com/photo-1585508889330-ee6c8e1fb0c7?w=500"),
    ("DJI Mini 4 Pro Drone 4K", "Compact foldable drone with 4K HDR video, 34-minute flight time, omnidirectional obstacle sensing", 759.00, "electronics", "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=500"),
    ("Nintendo Switch OLED Model", "Gaming console with vibrant 7-inch OLED screen, enhanced audio, 64GB storage, Joy-Con controllers", 349.99, "electronics", "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=500"),
    ("PlayStation 5 Digital Edition", "Next-gen console with lightning-fast SSD, ray tracing graphics, DualSense haptic feedback controller", 449.99, "electronics", "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=500"),
    ("Xbox Series X 1TB Console", "Most powerful Xbox with 4K gaming at 120fps, quick resume, backward compatibility", 499.99, "electronics", "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=500"),
    ("Bose QuietComfort Earbuds II", "True wireless earbuds with world-class noise cancellation, custom sound profiles, all-day comfort", 299.00, "electronics", "https://images.unsplash.com/photo-1590658165737-15a047b7a744?w=500"),
    ("AirPods Pro 2nd Generation", "Active noise cancellation earbuds with Adaptive Audio, USB-C charging, H2 chip for superior sound", 249.00, "electronics", "https://images.unsplash.com/photo-1606841837239-c5a1a4a07af7?w=500"),
    ("Samsung Galaxy Buds2 Pro", "Premium wireless earbuds with intelligent ANC, 360 Audio with head tracking, Hi-Fi sound", 229.99, "electronics", "https://images.unsplash.com/photo-1598331668826-20cecc596b86?w=500"),
    ("Amazon Kindle Paperwhite Signature", "Premium e-reader with 6.8-inch glare-free display, auto-adjusting warm light, wireless charging", 139.99, "electronics", "https://images.unsplash.com/photo-1592503254549-d83d24a4dfab?w=500"),
    ("LG C3 65-inch OLED TV", "Stunning OLED television with self-lit pixels, α9 AI processor 4K, Dolby Vision IQ, perfect for gaming", 1799.99, "electronics", "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500"),
    ("Samsung 55-inch QLED 4K TV", "Quantum dot television with 100% color volume, Object Tracking Sound, gaming hub with 120Hz", 997.99, "electronics", "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=500"),
    ("Sonos Beam Gen 2 Soundbar", "Compact smart soundbar with Dolby Atmos, voice control, room calibration, streaming services", 449.00, "electronics", "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=500"),
    ("Logitech MX Master 3S Mouse", "Ergonomic wireless mouse with MagSpeed scrolling, 8K DPI sensor, multi-device pairing", 99.99, "electronics", "https://images.unsplash.com/photo-1527814050087-3793815479db?w=500"),
    ("Corsair K95 RGB Mechanical Keyboard", "Premium gaming keyboard with Cherry MX switches, per-key RGB, dedicated macro keys", 199.99, "electronics", "https://images.unsplash.com/photo-1595225476474-87563907a212?w=500"),
    
    # Fashion (30 products)
    ("Levi's 501 Original Fit Jeans", "Iconic straight-leg denim jeans with button fly closure, shrink-to-fit design, timeless American style", 98.00, "fashion", "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500"),
    ("Nike Air Max 270 React Sneakers", "Lifestyle sneakers featuring large Max Air unit, React foam cushioning, breathable mesh upper", 150.00, "fashion", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500"),
    ("Adidas Ultraboost 22 Running Shoes", "Premium running shoes with responsive Boost midsole, Primeknit+ upper, Continental rubber outsole", 180.00, "fashion", "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=500"),
    ("Ray-Ban Aviator Classic Sunglasses", "Timeless metal aviator sunglasses with gradient lenses, adjustable nose pads, 100% UV protection", 154.00, "fashion", "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500"),
    ("Gucci Signature Leather Belt", "Luxury Italian leather belt with iconic double-G buckle, adjustable sizing, premium craftsmanship", 450.00, "fashion", "https://images.unsplash.com/photo-1624222247344-550fb60583bb?w=500"),
    ("100% Pure Cashmere V-Neck Sweater", "Luxuriously soft cashmere pullover with classic v-neck design, lightweight warmth, elegant drape", 189.00, "fashion", "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500"),
    ("Wool Blend Double-Breasted Peacoat", "Classic naval-inspired coat in premium wool blend, anchor buttons, warm quilted lining", 249.00, "fashion", "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=500"),
    ("Genuine Leather Moto Jacket", "Rugged biker jacket in authentic cowhide leather, asymmetric zipper, multiple pockets", 399.00, "fashion", "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500"),
    ("Pure Silk Midi Dress", "Elegant dress in 100% mulberry silk with flowing A-line silhouette, adjustable spaghetti straps", 225.00, "fashion", "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500"),
    ("Tailored Wool Blazer Navy", "Structured single-breasted blazer in Italian wool, notch lapels, two-button closure", 279.00, "fashion", "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500"),
    ("Slim Fit Chino Pants", "Versatile cotton twill chinos with stretch comfort, flat front, multiple color options", 79.00, "fashion", "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=500"),
    ("Oxford Cotton Button-Down Shirt", "Classic dress shirt in premium Oxford cotton, button-down collar, wrinkle-resistant", 69.00, "fashion", "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500"),
    ("Merino Wool Cardigan Sweater", "Fine gauge cardigan in 100% merino wool, button front, perfect for layering", 119.00, "fashion", "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=500"),
    ("Down Puffer Jacket Waterproof", "Warm insulated jacket with 700-fill down, water-resistant shell, packable design", 299.00, "fashion", "https://images.unsplash.com/photo-1539533113208-f6df8cc8b543?w=500"),
    ("High-Waist Yoga Leggings", "Performance leggings with moisture-wicking fabric, four-way stretch, hidden pocket", 58.00, "fashion", "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=500"),
    ("Women's Athletic Tank Top", "Breathable workout tank with built-in shelf bra, racerback design, quick-dry fabric", 32.00, "fashion", "https://images.unsplash.com/photo-1578342976795-062a1b744f37?w=500"),
    ("Men's Running Shorts", "Lightweight athletic shorts with inner liner, reflective details, zippered pocket", 45.00, "fashion", "https://images.unsplash.com/photo-1519505907962-0a6cb0167c73?w=500"),
    ("Chelsea Leather Ankle Boots", "Sleek leather boots with elastic side panels, cushioned insole, durable rubber sole", 185.00, "fashion", "https://images.unsplash.com/photo-1582897085656-c636d006a246?w=500"),
    ("White Canvas Low-Top Sneakers", "Classic canvas sneakers with vulcanized rubber sole, timeless design, all-day comfort", 55.00, "fashion", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=500"),
    ("Merino Wool Beanie Hat", "Cozy knit beanie in soft merino wool, fold-up cuff, one size fits all", 35.00, "fashion", "https://images.unsplash.com/photo-1576871337622-98d48d1cf531?w=500"),
    ("Cotton Crew Neck T-Shirt 3-Pack", "Essential t-shirts in premium cotton, pre-shrunk fabric, classic fit, basic colors", 45.00, "fashion", "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500"),
    ("Classic Denim Jacket", "Timeless jean jacket with button closure, chest pockets, medium wash finish", 89.00, "fashion", "https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=500"),
    ("Trench Coat Water-Resistant", "Classic double-breasted trench in water-resistant fabric, belted waist, removable liner", 329.00, "fashion", "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=500"),
    ("Cotton Blend Hoodie", "Comfortable pullover hoodie with kangaroo pocket, drawstring hood, fleece-lined interior", 55.00, "fashion", "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500"),
    ("Classic Pique Polo Shirt", "Traditional polo in cotton pique, ribbed collar and cuffs, three-button placket", 59.00, "fashion", "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=500"),
    
    # Home & Living (30 products)
    ("Queen Memory Foam Mattress", "Gel-infused memory foam mattress with cooling technology, pressure point relief, 10-year warranty", 699.00, "home", "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=500"),
    ("Egyptian Cotton Sheet Set", "Luxury bedding in 800-thread count Egyptian cotton, deep pocket fitted sheet, silky finish", 149.00, "home", "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=500"),
    ("Down Alternative Comforter", "Hypoallergenic all-season comforter with box-stitch construction, machine washable", 89.00, "home", "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?w=500"),
    ("16-Piece Ceramic Dinnerware Set", "Modern stoneware set for 4 with dinner plates, salad plates, bowls, mugs", 129.00, "home", "https://images.unsplash.com/photo-1578500351865-d3f37e4cdd7e?w=500"),
    ("Stainless Steel Cookware 10-Piece", "Professional tri-ply cookware with aluminum core, riveted handles, oven-safe to 500°F", 399.00, "home", "https://images.unsplash.com/photo-1585515320310-259814833e62?w=500"),
    ("KitchenAid Artisan Stand Mixer", "Iconic 5-quart stand mixer with tilt-head design, 10 speeds, multiple attachments available", 379.00, "home", "https://images.unsplash.com/photo-1588013273468-315fd88ea51c?w=500"),
    ("Instant Pot Duo 7-in-1", "Multi-cooker with pressure cook, slow cook, rice cooker, steamer, sauté, yogurt functions", 99.00, "home", "https://images.unsplash.com/photo-1585515320310-259814833e62?w=500"),
    ("Dyson V15 Detect Cordless Vacuum", "Intelligent stick vacuum with laser dust detection, HEPA filtration, up to 60 minutes runtime", 649.00, "home", "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=500"),
    ("Robot Vacuum with Self-Empty", "Smart vacuum with LiDAR navigation, automatic dirt disposal, app control, voice commands", 349.00, "home", "https://images.unsplash.com/photo-1612832021499-0a2d6f3b70e8?w=500"),
    ("True HEPA Air Purifier", "Large room air purifier removes 99.97% of allergens, activated carbon filter, quiet operation", 229.00, "home", "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=500"),
    ("Top Grain Leather Sofa", "Contemporary 3-seater sofa in genuine leather, hardwood frame, deep cushions", 1899.00, "home", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500"),
    ("Modular Sectional Sofa", "L-shaped sectional with chaise, reversible cushions, stain-resistant performance fabric", 1499.00, "home", "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500"),
    ("Velvet Accent Armchair", "Mid-century modern chair in soft velvet, gold-finished legs, comfortable seating", 349.00, "home", "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=500"),
    ("Marble Top Coffee Table", "Modern living room table with genuine marble top, gold metal base, easy assembly", 449.00, "home", "https://images.unsplash.com/photo-1532372576444-dda954194ad0?w=500"),
    ("Industrial 5-Tier Bookshelf", "Open bookcase with metal frame, rustic wood shelves, sturdy construction", 189.00, "home", "https://images.unsplash.com/photo-1594620302200-9a762244a156?w=500"),
    ("Solid Oak Dining Table", "Farmhouse-style table seats 6-8, solid wood construction, natural finish", 899.00, "home", "https://images.unsplash.com/photo-1617806118233-18e1de247200?w=500"),
    ("Electric Height-Adjustable Desk", "Standing desk with memory presets, spacious work surface, cable management", 599.00, "home", "https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=500"),
    ("Ergonomic Mesh Office Chair", "Executive chair with lumbar support, adjustable arms, breathable mesh back", 299.00, "home", "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=500"),
    ("Handwoven Wool Area Rug 8x10", "Contemporary geometric pattern rug, 100% New Zealand wool, non-slip pad included", 399.00, "home", "https://images.unsplash.com/photo-1574418797047-f0c1c3d17f2b?w=500"),
    ("Modern Ceramic Table Lamp", "Decorative lamp with linen drum shade, 3-way switch, ambient bedroom lighting", 79.00, "home", "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=500"),
    ("Arc Floor Lamp with Marble Base", "Statement lighting piece with adjustable arched arm, heavy marble base, LED compatible", 189.00, "home", "https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=500"),
    ("Full-Length Wall Mirror", "Large decorative mirror with metal frame, vertical or horizontal mount", 149.00, "home", "https://images.unsplash.com/photo-1618219908412-a29a1bb7b86e?w=500"),
    ("Velvet Throw Pillow Set of 4", "Decorative cushions with hidden zippers, plush polyester fill, assorted colors", 65.00, "home", "https://images.unsplash.com/photo-1584100936595-c0654b55a2e2?w=500"),
    ("Weighted Blanket 15 lbs", "Therapeutic blanket with glass beads, breathable cotton duvet cover, promotes better sleep", 89.00, "home", "https://images.unsplash.com/photo-1607193748683-46c48bf23135?w=500"),
    ("Thermal Blackout Curtains", "Room-darkening window panels with grommet top, energy-efficient, noise-reducing", 45.00, "home", "https://images.unsplash.com/photo-1594476274913-1a1fdb3ed5e7?w=500"),
    
    # Beauty & Personal Care (20 products)
    ("Luxury Skincare 5-Piece Set", "Complete routine with cleanser, toner, vitamin C serum, moisturizer, eye cream", 189.00, "beauty", "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=500"),
    ("20% Vitamin C Face Serum", "Brightening serum with hyaluronic acid, ferulic acid, antioxidant protection", 35.00, "beauty", "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=500"),
    ("Retinol Anti-Aging Night Cream", "Overnight treatment with 2.5% retinol, peptides, ceramides, reduces fine lines", 49.00, "beauty", "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=500"),
    ("Hyaluronic Acid Moisturizer", "Hydrating face cream with multi-weight HA, niacinamide, non-comedogenic formula", 32.00, "beauty", "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=500"),
    ("Detoxifying Clay Face Mask", "Purifying mask with kaolin and bentonite clay, charcoal, tea tree oil", 24.00, "beauty", "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=500"),
    ("Sonic Facial Cleansing Brush", "Waterproof brush with 5 speed settings, silicone bristles, USB rechargeable", 129.00, "beauty", "https://images.unsplash.com/photo-1519824145371-296894a0daa9?w=500"),
    ("LED Light Therapy Face Mask", "Professional device with red, blue, green LED modes, anti-aging and acne treatment", 199.00, "beauty", "https://images.unsplash.com/photo-1612817288484-6f916006741a?w=500"),
    ("Jade Roller and Gua Sha Set", "Authentic jade stone facial tools for lymphatic drainage, reduces puffiness", 29.00, "beauty", "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=500"),
    ("18-Color Eyeshadow Palette", "Neutral matte and shimmer shades, highly pigmented, blendable formula", 45.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    ("Full Coverage Liquid Foundation", "Long-wear foundation with SPF 15, buildable coverage, multiple undertones", 42.00, "beauty", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=500"),
    ("Matte Liquid Lipstick Set", "5-piece collection of transfer-proof lipsticks, comfortable wear, rich color", 55.00, "beauty", "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=500"),
    ("Volumizing Mascara", "Lengthening formula with curved brush, smudge-proof, ophthalmologist tested", 24.00, "beauty", "https://images.unsplash.com/photo-1631214524020-7e18db7f7a00?w=500"),
    ("Professional Makeup Brush Set", "15 brushes with synthetic bristles, ergonomic handles, vegan and cruelty-free", 79.00, "beauty", "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=500"),
    ("Luxury Eau de Parfum 100ml", "Signature floral fragrance with notes of jasmine, rose, sandalwood, long-lasting", 89.00, "beauty", "https://images.unsplash.com/photo-1541643600914-78b084683601?w=500"),
    ("Ionic Hair Dryer Professional", "2000W dryer with ionic technology, ceramic coating, cool shot button", 79.00, "beauty", "https://images.unsplash.com/photo-1522338140262-f46f5913618a?w=500"),
    ("3-Barrel Curling Iron Set", "Interchangeable ceramic barrels, adjustable temperature, heat-resistant glove", 59.00, "beauty", "https://images.unsplash.com/photo-1519699047748-de8e457a634e?w=500"),
    ("Ceramic Flat Iron Straightener", "1-inch plates with digital temperature control, auto shut-off, dual voltage", 69.00, "beauty", "https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=500"),
    ("Organic Argan Oil Hair Treatment", "100% pure argan oil for hair and skin, cold-pressed, vitamin E rich", 28.00, "beauty", "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=500"),
    ("Keratin Shampoo and Conditioner", "Sulfate-free duo repairs damaged hair, color-safe, adds shine and smoothness", 45.00, "beauty", "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=500"),
    ("Rechargeable Electric Toothbrush", "Sonic technology with 5 modes, pressure sensor, 2-week battery, travel case", 99.00, "beauty", "https://images.unsplash.com/photo-1607613009820-a29f7bb81c04?w=500"),
    
    # Sports & Fitness (20 products)
    ("Adjustable Dumbbell Set 5-52.5 lbs", "Space-saving dumbbells with quick-select dial, replaces 15 sets, includes stand", 349.00, "sports", "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500"),
    ("Premium Yoga Mat 6mm", "Non-slip TPE mat with alignment marks, eco-friendly, includes carrying strap", 45.00, "sports", "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500"),
    ("Resistance Bands Set of 5", "Exercise bands with handles, door anchor, ankle straps, workout guide included", 29.00, "sports", "https://images.unsplash.com/photo-1598971861713-54ad16a5c72e?w=500"),
    ("High-Density Foam Roller", "Muscle recovery roller for deep tissue massage, trigger point therapy, 36-inch", 25.00, "sports", "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500"),
    ("Cast Iron Kettlebell 20 lbs", "Powder-coated finish for grip, flat base, wide handle for two-handed swings", 39.00, "sports", "https://images.unsplash.com/photo-1517963628607-235ccdd5476c?w=500"),
    ("Indoor Cycling Exercise Bike", "Magnetic resistance with 8 levels, LCD monitor, adjustable seat and handlebars", 299.00, "sports", "https://images.unsplash.com/photo-1576678927484-cc907957088c?w=500"),
    ("Folding Treadmill with Incline", "Compact treadmill with 12 programs, 3-level incline, heart rate sensors", 599.00, "sports", "https://images.unsplash.com/photo-1591068316116-c6089e9d5da2?w=500"),
    ("Magnetic Rowing Machine", "Full-body workout machine with digital monitor, 16 resistance levels, foldable", 449.00, "sports", "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=500"),
    ("Doorway Pull-Up Bar", "No-screw installation, multiple grip positions, supports up to 300 lbs", 35.00, "sports", "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500"),
    ("Ab Roller Wheel with Knee Pad", "Core strength trainer with dual wheels, non-slip handles, stability guaranteed", 22.00, "sports", "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500"),
    ("Speed Jump Rope", "Adjustable length with ball-bearing handles, tangle-free cable, cardio training", 15.00, "sports", "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?w=500"),
    ("Adjustable Weight Bench", "Heavy-duty bench with 7 back positions, leg developer, 600 lbs capacity", 179.00, "sports", "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=500"),
    ("Medicine Ball 10 lbs", "Textured rubber surface for grip, ideal for strength and core training", 35.00, "sports", "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=500"),
    ("Yoga Blocks Set of 2", "High-density foam blocks for support and balance, lightweight, multiple colors", 18.00, "sports", "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500"),
    ("Large Gym Duffle Bag", "Water-resistant bag with shoe compartment, multiple pockets, adjustable strap", 42.00, "sports", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500"),
    ("Hydration Backpack 2L", "Running pack with water bladder, lightweight, reflective strips, multiple pockets", 49.00, "sports", "https://images.unsplash.com/photo-1622260614927-7eb6aa15bb44?w=500"),
    ("BlenderBottle Shaker 28oz", "Leak-proof bottle with wire whisk ball, BPA-free, dishwasher safe", 12.00, "sports", "https://images.unsplash.com/photo-1622484211013-c2ca949e1090?w=500"),
    ("Fitness Tracker Smart Band", "Activity tracker with heart rate monitor, sleep tracking, 7-day battery", 79.00, "sports", "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=500"),
    ("Boxing Training Gloves 12oz", "Ventilated gloves with wrist support, synthetic leather, shock absorption", 45.00, "sports", "https://images.unsplash.com/photo-1517467139951-f5a925c9f9de?w=500"),
    ("Heavy Bag 100 lbs", "Filled punching bag with reinforced stitching, includes chain and swivel", 129.00, "sports", "https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=500"),
    
    # Books & Stationery (15 products)
    ("Contemporary Fiction Bestseller", "Award-winning novel with compelling narrative, memorable characters, over 500 pages", 18.99, "books", "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500"),
    ("Personal Development Guide", "Practical strategies for success, habit formation, mindset transformation", 24.99, "books", "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500"),
    ("Mediterranean Cookbook", "200+ authentic recipes with full-color photos, nutritional information", 29.99, "books", "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=500"),
    ("Business Leadership Manual", "Modern leadership techniques, case studies from Fortune 500 companies", 26.99, "books", "https://images.unsplash.com/photo-1589998059171-988d887df646?w=500"),
    ("Illustrated Children's Book", "Vibrant artwork, timeless story, teaches important life lessons, ages 3-8", 14.99, "books", "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=500"),
    ("Mystery Thriller Novel", "Page-turner with plot twists, suspenseful narrative, international bestseller", 17.99, "books", "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500"),
    ("Science Fiction Epic Series", "First book in trilogy, dystopian future, thought-provoking themes", 21.99, "books", "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=500"),
    ("Biography of Historical Figure", "Comprehensive life story, extensively researched, includes rare photographs", 22.99, "books", "https://images.unsplash.com/photo-1510172951991-856a654063f9?w=500"),
    ("European Travel Guide 2024", "Updated guidebook with maps, insider tips, budget recommendations", 27.99, "books", "https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=500"),
    ("Art History Illustrated", "Renaissance to contemporary art movements, 400 color reproductions", 39.99, "books", "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=500"),
    ("Poetry Collection Anthology", "Modern poems exploring love, loss, identity, critically acclaimed", 16.99, "books", "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500"),
    ("Fantasy Novel Box Set", "Complete trilogy with maps, epic quest, dragons and magic", 44.99, "books", "https://images.unsplash.com/photo-1535905557558-afc4877a26fc?w=500"),
    ("Historical Fiction Novel", "Victorian era setting, meticulously researched, vivid characters", 19.99, "books", "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500"),
    ("Philosophy for Beginners", "Introduction to major philosophers, accessible explanations, discussion questions", 25.99, "books", "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=500"),
    ("Psychology Textbook", "Comprehensive introduction to psychological science, research methods, applications", 59.99, "books", "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500"),
]

def cleanup_and_seed():
    print("="*70)
    print("PRODUCT CATALOG CLEANUP & SEEDING")
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
    print(f"\n🌱 Step 4: Seeding {len(PRODUCTS)} new unique products...")
    added_count = 0
    error_count = 0
    
    for idx, (name, desc, price, category, image) in enumerate(PRODUCTS, 1):
        try:
            data = {
                'id': str(uuid.uuid4()),
                'name': name,
                'description': desc,
                'price': price,
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
    print(f"  ✅ Added: {added_count} new products")
    print(f"  ❌ Errors: {error_count}")
    print(f"  📊 Total Catalog Size: {len(in_use_ids) + added_count}")
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
        print(f"\n✨ Success! Catalog is now ready with unique products.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
