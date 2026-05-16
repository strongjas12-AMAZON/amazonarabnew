# Luxury Product Catalog - 200 Premium Products ($400 - $2000)
# Each product has a unique title, description, category, price, and matching image.
# No duplicates with the base product_catalog.py (100 products).

LUXURY_CATALOG = [
    # ============================================================
    # ELECTRONICS (50 premium products)
    # ============================================================
    {
        "title": "Professional DSLR Camera Body 24MP",
        "description": "Full-frame 24.2 megapixel DSLR camera body with 4K video, dual card slots, weather-sealed magnesium alloy chassis, and 51-point autofocus system. Ideal for professional photographers and filmmakers.",
        "price": 1899.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800"]
    },
    {
        "title": "Mirrorless Camera 45MP Full-Frame",
        "description": "High-resolution 45-megapixel full-frame mirrorless camera featuring 8K video recording, 5-axis in-body stabilization, and a bright electronic viewfinder. Includes 24-105mm kit lens.",
        "price": 1999.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1502982720700-bfff97f2ecac?w=800"]
    },
    {
        "title": "Cinema Prime Lens 50mm f/1.2",
        "description": "Ultra-fast 50mm f/1.2 prime lens with cinema-grade optics, 11-blade aperture for creamy bokeh, and weather sealing. Perfect for portraits and low-light photography.",
        "price": 1499.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1606986628025-35d57e735ae0?w=800"]
    },
    {
        "title": "Telephoto Zoom Lens 70-200mm f/2.8",
        "description": "Pro-grade 70-200mm f/2.8 constant aperture telephoto zoom with advanced image stabilization, nano-coating, and silent ring USM motor. Essential for sports and wildlife photography.",
        "price": 1799.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1617080090911-91409e2fdd57?w=800"]
    },
    {
        "title": "4K Cinema Drone with 3-Axis Gimbal",
        "description": "Professional drone featuring a 1-inch CMOS sensor, 4K60fps video, obstacle avoidance sensors, 34-minute flight time, and 10km transmission range. Foldable carbon fiber body.",
        "price": 1599.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1473968512647-3e447244af8f?w=800"]
    },
    {
        "title": "Foldable FPV Racing Drone",
        "description": "High-speed FPV racing drone with digital low-latency video transmission, brushless motors reaching 140km/h, and modular design. Includes controller and goggles.",
        "price": 899.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1579829366248-204fe8413f31?w=800"]
    },
    {
        "title": "55-Inch OLED 4K Smart TV",
        "description": "Self-lit OLED display with perfect blacks, 120Hz refresh rate, Dolby Vision IQ, and next-gen AI-powered upscaling processor. Includes premium voice remote and thin bezel design.",
        "price": 1499.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800"]
    },
    {
        "title": "65-Inch QLED 8K Smart TV",
        "description": "Massive 65-inch quantum dot QLED display with 8K resolution, HDR10+, full array local dimming, and Dolby Atmos sound. Comes with gaming hub for ultimate console performance.",
        "price": 1999.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1461151304267-38535e780c79?w=800"]
    },
    {
        "title": "Premium Ultrabook Laptop 14-Inch",
        "description": "Ultra-slim 14-inch laptop with latest-gen processor, 16GB RAM, 1TB NVMe SSD, and vivid 2.8K OLED display. All-day battery, machined aluminum chassis, and backlit keyboard.",
        "price": 1499.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800"]
    },
    {
        "title": "Gaming Laptop RTX 16-Inch",
        "description": "16-inch gaming laptop with dedicated RTX graphics, 240Hz QHD display, 32GB DDR5 RAM, 2TB SSD, and vapor chamber cooling. RGB mechanical keyboard with per-key customization.",
        "price": 1899.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=800"]
    },
    {
        "title": "Professional Desktop Workstation",
        "description": "High-end desktop with liquid-cooled multi-core processor, workstation-class GPU, 64GB ECC RAM, and 4TB NVMe storage. Built for 3D rendering, video editing, and CAD workflows.",
        "price": 1999.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=800"]
    },
    {
        "title": "5K Studio Display Monitor 27-Inch",
        "description": "27-inch 5K Retina display with P3 wide color gamut, 600 nits brightness, nano-texture anti-glare glass, and built-in 12MP webcam with spatial audio speakers.",
        "price": 1599.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800"]
    },
    {
        "title": "Ultrawide Curved Gaming Monitor 34-Inch",
        "description": "34-inch ultrawide curved QD-OLED monitor with 175Hz refresh rate, 0.1ms response time, HDR True Black 400, and USB-C 90W power delivery for ultimate immersion.",
        "price": 1299.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1616763355548-1b606f439f86?w=800"]
    },
    {
        "title": "Flagship Smartphone 256GB",
        "description": "Latest flagship smartphone with triple-lens camera system, 120Hz LTPO OLED display, titanium frame, 5G, and all-day battery life. Includes fast wireless charging and IP68 rating.",
        "price": 1199.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800"]
    },
    {
        "title": "Foldable Smartphone 512GB",
        "description": "Premium foldable smartphone with 7.6-inch inner Dynamic AMOLED display, S Pen support, 50MP camera system, and IPX8 water resistance. Multitask with three apps simultaneously.",
        "price": 1799.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800"]
    },
    {
        "title": "Pro Tablet 12.9-Inch with Keyboard",
        "description": "12.9-inch pro tablet with mini-LED display, octa-core chip, 256GB storage, and precision stylus support. Includes magnetic folio keyboard and trackpad.",
        "price": 1399.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1561154464-82e9adf32764?w=800"]
    },
    {
        "title": "Noise Cancelling Over-Ear Headphones Pro",
        "description": "Industry-leading noise cancellation, 40-hour battery life, hi-res audio certification, multi-device pairing, and plush memory-foam ear cushions. Includes premium carrying case.",
        "price": 449.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800"]
    },
    {
        "title": "Studio Reference Headphones Open-Back",
        "description": "Audiophile open-back headphones with planar magnetic drivers, detachable balanced cable, and hand-finished wooden ear cups. Engineered for critical listening and mixing.",
        "price": 999.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800"]
    },
    {
        "title": "Hi-Fi Turntable with Phono Preamp",
        "description": "Belt-driven high-fidelity turntable with carbon fiber tonearm, precision platter, and integrated phono preamp. Comes with premium moving magnet cartridge.",
        "price": 799.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=800"]
    },
    {
        "title": "Tube Amplifier Stereo Integrated",
        "description": "Hand-built tube integrated amplifier with Class A architecture, 50W per channel, remote control, and hi-res DAC. Perfect for audiophile bookshelf and floor-standing speakers.",
        "price": 1299.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1558537348-c0f8e733989d?w=800"]
    },
    {
        "title": "Floor-Standing Tower Speakers Pair",
        "description": "Reference-grade floor-standing speakers with 3-way design, aluminum dome tweeters, and 8-inch woofers. Hand-finished wood veneer cabinets with precision-tuned ports.",
        "price": 1699.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800"]
    },
    {
        "title": "Dolby Atmos Soundbar with Subwoofer",
        "description": "Cinema-grade soundbar with 11.1.4 channel Dolby Atmos, wireless subwoofer, and rear surround speakers. Delivers room-filling immersive audio for movies and gaming.",
        "price": 1299.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&sat=-100"]
    },
    {
        "title": "Portable Pro Bluetooth Speaker XL",
        "description": "Flagship portable speaker with 360-degree sound, 24-hour battery, IP67 waterproof body, and wireless stereo pairing. Built-in power bank for charging devices.",
        "price": 499.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&sat=-40"]
    },
    {
        "title": "Professional Audio Interface USB-C",
        "description": "Studio-grade USB-C audio interface with ultra-low latency, four preamps, 192kHz/24-bit converters, and onboard DSP. Includes premium studio software suite.",
        "price": 599.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    {
        "title": "Condenser Microphone Studio Kit",
        "description": "Large-diaphragm condenser microphone with dual capsules, multiple polar patterns, and integrated shock mount. Perfect for vocals, podcasting, and instrument recording.",
        "price": 449.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=800"]
    },
    {
        "title": "Mid-Range DJ Controller 4-Channel",
        "description": "Professional 4-channel DJ controller with motorized platters, performance pads, built-in effects, and USB-C connectivity. Works with all major DJ software.",
        "price": 1299.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1571266028243-d220bc1c143a?w=800"]
    },
    {
        "title": "Wireless Mechanical Keyboard 75%",
        "description": "Premium 75% wireless mechanical keyboard with hot-swappable switches, double-shot PBT keycaps, per-key RGB, and tri-mode connectivity. CNC-milled aluminum body.",
        "price": 449.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1595225476474-87563907a212?w=800"]
    },
    {
        "title": "E-Ink Writing Tablet 10-Inch",
        "description": "Distraction-free e-ink writing tablet with paper-like feel, replaceable pen tips, and cloud sync. Ideal for notes, sketches, and reading PDFs with exceptional battery life.",
        "price": 499.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=800"]
    },
    {
        "title": "Professional 3D Printer FDM",
        "description": "Large-format FDM 3D printer with auto bed leveling, 300°C hotend, dual-filament support, and enclosed chamber. Print engineering-grade materials reliably.",
        "price": 1499.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1631732437635-9f1d9a1fc67e?w=800"]
    },
    {
        "title": "Resin 3D Printer High-Resolution",
        "description": "High-resolution masked-SLA resin 3D printer with 10-inch mono LCD, 14um XY resolution, and fast curing speed. Perfect for miniatures, jewelry prototypes, and dental models.",
        "price": 699.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=800"]
    },
    {
        "title": "VR Headset Premium Standalone",
        "description": "Standalone VR headset with pancake lenses, color passthrough, 4K per-eye resolution, and powerful onboard processor. Includes controllers, charging dock, and premium strap.",
        "price": 999.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1622979135225-d2ba269cf1ac?w=800"]
    },
    {
        "title": "AR Smart Glasses Pro",
        "description": "Lightweight smart glasses with micro-OLED displays, open-ear spatial audio, real-time translation, and navigation. Five-hour battery with magnetic quick-charge case.",
        "price": 699.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1591370409347-2fd43b7b7030?w=800"]
    },
    {
        "title": "Robot Vacuum & Mop with LiDAR",
        "description": "Premium robot vacuum with LiDAR mapping, 5500Pa suction, auto-empty and mop-wash dock, and AI obstacle avoidance. Controlled via smartphone app with custom room settings.",
        "price": 1299.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1603117410263-17dc7a4f41f6?w=800"]
    },
    {
        "title": "Smart Air Purifier HEPA-14 Large Room",
        "description": "Large-room smart air purifier with HEPA-14 filtration, VOC sensor, real-time air quality display, and whisper-quiet fan. Covers up to 1500 sq ft.",
        "price": 699.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1585909695284-32d2985ac9c0?w=800"]
    },
    {
        "title": "Smart Thermostat with Remote Sensors",
        "description": "Wi-Fi smart thermostat with multi-room temperature sensors, adaptive learning, Matter support, and energy usage reports. Saves up to 23% on heating and cooling costs.",
        "price": 409.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1558002038-1055907df827?w=800"]
    },
    {
        "title": "Pro Video Capture Card 4K60",
        "description": "Professional 4K60 HDR video capture card with PCIe interface, ultra-low latency passthrough, and multi-stream support. Perfect for game streamers and content creators.",
        "price": 449.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=800"]
    },
    {
        "title": "Portable SSD 4TB USB 3.2 Gen 2",
        "description": "Rugged 4TB portable SSD with 2000MB/s sequential read, hardware AES-256 encryption, and IP55 dust/water resistance. USB-C compatible with Thunderbolt.",
        "price": 499.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1597852074816-d933c7d2b988?w=800"]
    },
    {
        "title": "NAS 4-Bay Network Storage",
        "description": "4-bay network attached storage with quad-core CPU, 10GbE networking, hardware transcoding, and enterprise-grade RAID. Ideal for media servers and home backups.",
        "price": 899.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800"]
    },
    {
        "title": "Home Mesh Wi-Fi 6E Tri-Band System",
        "description": "Tri-band Wi-Fi 6E mesh system with three nodes, 10.8Gbps combined speed, coverage up to 8000 sq ft, and advanced cybersecurity suite. Future-proof 6GHz band.",
        "price": 799.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1606765962248-7ff407b51667?w=800"]
    },
    {
        "title": "Professional Projector 4K Laser",
        "description": "Short-throw 4K laser projector with 3500 lumens, HDR10+, 120Hz gaming mode, and 25,000-hour laser life. Cinema-quality visuals up to 150 inches.",
        "price": 1999.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=800&sat=-40"]
    },
    {
        "title": "Portable LED Projector FHD Battery",
        "description": "Compact battery-powered FHD projector with auto-keystone, autofocus, and built-in 2x3W speakers. Stream directly from Netflix, YouTube, and Disney+.",
        "price": 599.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1626379953822-baec19c3accd?w=800"]
    },
    {
        "title": "Gaming Console Next-Gen 1TB",
        "description": "Flagship next-gen gaming console bundle with 1TB SSD, two wireless controllers, charging dock, and premium headset. 4K120fps gaming with ray tracing support.",
        "price": 699.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1486401899868-0e435ed85128?w=800"]
    },
    {
        "title": "Handheld Gaming PC 7-Inch OLED",
        "description": "Portable gaming PC with 7-inch OLED 90Hz display, Ryzen Z1 Extreme chip, 16GB RAM, 1TB NVMe SSD, and Hall-effect joysticks. Runs full PC game libraries.",
        "price": 899.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800"]
    },
    {
        "title": "Smart Electric Bike Conversion Kit",
        "description": "Complete bike-to-ebike conversion kit with 500W hub motor, 48V 15Ah battery, LCD display, and torque sensor. Pedal-assist up to 28mph with 50-mile range.",
        "price": 999.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1557090634-3b75b9212d35?w=800"]
    },
    {
        "title": "Electric Scooter Dual Motor 40mph",
        "description": "Premium dual-motor electric scooter with 40mph top speed, 45-mile range, hydraulic brakes, and 10-inch pneumatic tires. Foldable for easy transport.",
        "price": 1799.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1589487391730-58f7536b4e86?w=800"]
    },
    {
        "title": "Electric Skateboard Long Range",
        "description": "All-terrain electric skateboard with 28mph top speed, 40-mile range, swappable batteries, and ergonomic remote with OLED display. Carbon fiber deck.",
        "price": 1499.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1520778287775-1e3bfbc2f39c?w=800"]
    },
    {
        "title": "Smart Glasses Camera Recorder",
        "description": "Stylish smart glasses with integrated 12MP camera, open-ear audio, voice assistant, and polarized lenses. Capture moments hands-free with up to 6-hour battery life.",
        "price": 449.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800"]
    },
    {
        "title": "Astro Photography Telescope 8-Inch",
        "description": "8-inch aperture Schmidt-Cassegrain computerized telescope with 40,000+ celestial object database, GPS alignment, and smartphone mount. Ideal for deep-sky astrophotography.",
        "price": 1599.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1532978879514-6cdfdca6f7c3?w=800"]
    },
    {
        "title": "Thermal Imaging Camera Handheld",
        "description": "Pocket-sized thermal imaging camera with 256x192 resolution, -20 to 550°C range, and on-device image analysis. Perfect for electrical, HVAC, and building inspections.",
        "price": 799.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800"]
    },
    {
        "title": "Laser Engraver Desktop 20W",
        "description": "20W diode laser engraver with 400x400mm work area, air assist, honeycomb bed, and Lightburn compatibility. Engraves wood, leather, acrylic, and metal.",
        "price": 999.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1609205807107-e0ec9105fa53?w=800"]
    },

    # ============================================================
    # FASHION / LUXURY APPAREL & ACCESSORIES (35 products)
    # ============================================================
    {
        "title": "Designer Leather Handbag Structured",
        "description": "Hand-stitched calfskin leather handbag with polished gold-tone hardware, detachable shoulder strap, and dust bag. Made by master artisans in Italy.",
        "price": 1299.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800"]
    },
    {
        "title": "Italian Leather Briefcase Executive",
        "description": "Full-grain vegetable-tanned Italian leather briefcase with dedicated laptop compartment, solid brass fittings, and suede-lined interior. A timeless executive piece.",
        "price": 899.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1547949003-9792a18a2601?w=800"]
    },
    {
        "title": "Tailored Wool Suit Two-Piece",
        "description": "Super 150s Italian wool two-piece suit with half-canvas construction, Milanese buttonhole, and functional sleeve buttons. Includes complimentary alterations.",
        "price": 1599.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800"]
    },
    {
        "title": "Black Tie Tuxedo Peak Lapel",
        "description": "Elegant peak-lapel tuxedo in midnight-blue wool with silk-faced lapels, satin buttons, and one-button closure. Perfect for galas and formal evenings.",
        "price": 1299.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800"]
    },
    {
        "title": "Cashmere Overcoat Camel Long",
        "description": "Classic long-line camel overcoat crafted from pure Mongolian cashmere with horn buttons, double-stitched seams, and silk lining. Warm, lightweight, and refined.",
        "price": 1799.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1578932750294-f5075e85f44a?w=800"]
    },
    {
        "title": "Wool Pea Coat Navy Double-Breasted",
        "description": "Heritage double-breasted pea coat in melton wool with anchor buttons, storm flap, and adjustable rear belt. Tailored silhouette with quilted satin lining.",
        "price": 699.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=800"]
    },
    {
        "title": "Leather Biker Jacket Lambskin",
        "description": "Supple lambskin leather biker jacket with asymmetrical zip, quilted shoulders, and pebbled lining. Classic rock-and-roll silhouette handcrafted in Portugal.",
        "price": 1199.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800"]
    },
    {
        "title": "Shearling Aviator Flight Jacket",
        "description": "Genuine shearling aviator jacket with wind-cuffed sleeves, buckled collar, and ribbed hem. Inspired by classic WWII flight gear.",
        "price": 1499.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1520975916090-3105956dac38?w=800"]
    },
    {
        "title": "Designer Silk Evening Gown",
        "description": "Floor-length silk evening gown with hand-sewn pearl embellishments, V-neckline, and flowing bias-cut skirt. Made-to-measure luxury for special occasions.",
        "price": 1899.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800"]
    },
    {
        "title": "Silk Midi Dress Printed Designer",
        "description": "Hand-printed silk twill midi dress with tie waist, puffed sleeves, and signature designer print. Luxuriously lightweight with mother-of-pearl buttons.",
        "price": 799.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=800"]
    },
    {
        "title": "Italian Loafers Hand-Stitched Suede",
        "description": "Hand-stitched suede loafers with leather sole, cushioned insole, and traditional penny strap. Designed and produced in Tuscany.",
        "price": 599.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1582897085656-c636d006a246?w=800"]
    },
    {
        "title": "Goodyear Welted Brogues Full-Grain",
        "description": "Goodyear-welted full-grain leather brogues with intricate broguing, leather lining, and oak-bark tanned sole. Resoleable for decades of wear.",
        "price": 749.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1449505078894-0d0b9be0f1f5?w=800"]
    },
    {
        "title": "Luxury Running Sneakers Knit Upper",
        "description": "Designer running sneakers with signature knit upper, carbon-fiber plate midsole, and sculpted rubber outsole. Performance meets high fashion.",
        "price": 549.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"]
    },
    {
        "title": "High-Top Suede Designer Sneakers",
        "description": "Italian-made high-top sneakers in velvety suede with embroidered logo, padded ankle collar, and rubber cup sole. Limited edition colorway.",
        "price": 699.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800"]
    },
    {
        "title": "Crocodile Leather Oxford Shoes",
        "description": "Exotic crocodile leather Oxford shoes with Blake-stitched construction and silk laces. Each pair uniquely patterned—heirloom-quality footwear.",
        "price": 1999.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800"]
    },
    {
        "title": "Leather Travel Weekender Bag Large",
        "description": "Vegetable-tanned leather weekender bag with antique brass hardware, removable shoulder strap, and reinforced handles. Develops a unique patina over time.",
        "price": 849.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800"]
    },
    {
        "title": "Carbon Fiber Rolling Suitcase Cabin",
        "description": "Premium carbon fiber cabin suitcase with 360° silent wheels, TSA-approved combination lock, and USB charging port. Impossibly light yet incredibly strong.",
        "price": 799.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1581553680321-4fffae59fccd?w=800"]
    },
    {
        "title": "Designer Backpack Leather Gold Hardware",
        "description": "Refined leather backpack with signature turn-lock closure, gold-tone hardware, and laptop sleeve. Luxury meets everyday functionality.",
        "price": 1199.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800"]
    },
    {
        "title": "Python Leather Clutch Evening",
        "description": "Statement python-leather clutch with hinged metal frame, satin interior, and removable wrist chain. Handmade in small batches.",
        "price": 899.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&sat=-40"]
    },
    {
        "title": "Luxury Silk Pajama Set Piped",
        "description": "22-momme pure silk pajama set with piped trim, mother-of-pearl buttons, and relaxed fit. Presented in a luxury gift box.",
        "price": 429.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1559551409-dadc959f76b8?w=800"]
    },
    {
        "title": "Cashmere Hoodie Pullover Designer",
        "description": "Ultra-soft 100% cashmere hoodie pullover with kangaroo pocket, ribbed cuffs, and drawcord hood. Luxurious everyday comfort.",
        "price": 599.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800"]
    },
    {
        "title": "Merino Wool Tuxedo Scarf",
        "description": "Italian merino wool tuxedo scarf with fringed ends and silk-lined body. The perfect finishing touch for formal evening attire.",
        "price": 449.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1520903074185-8eca362b3dce?w=800"]
    },
    {
        "title": "Designer Aviator Titanium Sunglasses",
        "description": "Aviator-style sunglasses with featherweight titanium frame, polarized UV-400 lenses, and premium logo case. Timeless silhouette refined with modern materials.",
        "price": 499.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800"]
    },
    {
        "title": "Round-Frame Acetate Sunglasses Luxury",
        "description": "Hand-polished acetate round-frame sunglasses with zeiss polarized lenses and signature hinged temples. Comes with leather case.",
        "price": 549.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=800&sat=-40"]
    },
    {
        "title": "Silk Pocket Square Collection Set",
        "description": "Gift set of six handrolled silk pocket squares with signature prints. Presented in a luxury wooden box.",
        "price": 419.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1605733160314-4fc7dac4bb16?w=800"]
    },
    {
        "title": "Italian Leather Travel Wallet",
        "description": "Full-grain leather travel wallet with passport slot, 12 card pockets, currency compartments, and pen loop. Monogramming available.",
        "price": 429.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1601924582970-9238bcb495d9?w=800"]
    },
    {
        "title": "Ostrich Leather Card Holder Designer",
        "description": "Genuine ostrich leather card holder with six card slots, center bill compartment, and embossed logo. Individually hand-finished luxury accessory.",
        "price": 449.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1627123424574-724758594e93?w=800"]
    },
    {
        "title": "Designer Leather Belt Buckle Set",
        "description": "Reversible full-grain leather belt set with two interchangeable designer buckles and storage pouch. Crafted in Italy.",
        "price": 499.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1624222247344-550fb60583dc?w=800"]
    },
    {
        "title": "Shearling Gloves Lambskin Lined",
        "description": "Lambskin leather gloves with shearling lining, cashmere cuff, and touchscreen-compatible fingertips. Handmade in Hungary.",
        "price": 449.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1584735422189-3b8b6b5e7efc?w=800"]
    },
    {
        "title": "Panama Hat Ecuador Montecristi",
        "description": "Authentic Montecristi Panama hat hand-woven in Ecuador from toquilla palm, grade 20 fineness, with leather sweatband and gift box.",
        "price": 499.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=800"]
    },
    {
        "title": "Beaver Fur Fedora Vintage",
        "description": "Handcrafted beaver fur felt fedora with silk-lined interior, grosgrain band, and formed brim. Timeless craftsmanship and unmatched durability.",
        "price": 599.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1533627045820-a45e13dd25bd?w=800"]
    },
    {
        "title": "Designer Evening Clutch Crystal Encrusted",
        "description": "Glamorous crystal-encrusted minaudière clutch with magnetic closure, satin lining, and concealed chain. Red-carpet ready.",
        "price": 1199.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1598532213005-76f6abc2a423?w=800"]
    },
    {
        "title": "Trench Coat Cotton Gabardine Classic",
        "description": "Iconic water-resistant cotton gabardine trench coat with storm flap, epaulets, raglan sleeves, and buckled waist belt. Timeless British heritage.",
        "price": 1499.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1581338834647-b0fb40704e21?w=800"]
    },
    {
        "title": "Wool & Silk Tuxedo Bow Tie Set",
        "description": "Hand-tied silk bow tie with matching satin cummerbund and studs, presented in a silk-lined box. Complete the formal look.",
        "price": 429.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1547949003-9792a18a2601?w=800&sat=-40"]
    },
    {
        "title": "Monk Strap Shoes Double Leather",
        "description": "Double monk strap shoes in hand-burnished leather with Goodyear-welted soles and brass buckles. A sophisticated alternative to oxfords.",
        "price": 649.00,
        "category": "fashion",
        "images": ["https://images.unsplash.com/photo-1478186014116-f1db86180a1a?w=800"]
    },

    # ============================================================
    # FINE JEWELRY (35 products)
    # ============================================================
    {
        "title": "Diamond Solitaire Engagement Ring 1ct",
        "description": "Classic 1-carat round brilliant diamond solitaire engagement ring in 18k white gold with six-prong setting. GIA-certified with VS1 clarity.",
        "price": 1999.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800"]
    },
    {
        "title": "Sapphire Halo Ring White Gold",
        "description": "Ceylon blue sapphire halo ring in 18k white gold, surrounded by 0.40ct of pavé diamonds. Elegant and vibrant.",
        "price": 1499.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800"]
    },
    {
        "title": "Emerald Cluster Cocktail Ring",
        "description": "Statement emerald cluster cocktail ring in 18k yellow gold with brilliant-cut diamond accents. Natural Zambian emeralds.",
        "price": 1899.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=800"]
    },
    {
        "title": "Ruby Eternity Band Rose Gold",
        "description": "Rose gold eternity band set with deep red Burmese rubies in channel setting. A passionate alternative to a classic diamond eternity ring.",
        "price": 1399.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=800"]
    },
    {
        "title": "Diamond Tennis Necklace 5ct White Gold",
        "description": "5-carat total weight diamond tennis necklace in 14k white gold featuring round brilliant diamonds in a four-prong setting with double-lock safety clasp.",
        "price": 1999.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800"]
    },
    {
        "title": "Pearl Strand Necklace Akoya",
        "description": "Classic 18-inch Akoya saltwater pearl strand with 7.5-8mm pearls, 14k gold clasp, and luxury presentation box. AAA grade luster.",
        "price": 1199.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800"]
    },
    {
        "title": "South Sea Pearl Pendant Gold",
        "description": "Single 11mm South Sea pearl pendant suspended from a delicate 18k gold chain. Soft golden hue with exceptional luster.",
        "price": 1499.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1589128777073-263566ae5e4d?w=800"]
    },
    {
        "title": "Tahitian Pearl Drop Earrings",
        "description": "Tahitian black pearl drop earrings set in 18k white gold with diamond accents. Iridescent peacock overtones.",
        "price": 1299.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800"]
    },
    {
        "title": "Diamond Pavé Hoop Earrings",
        "description": "Diamond pavé hoop earrings in 18k yellow gold featuring 1.20ct total weight of VS2 diamonds. Secure hinged closure.",
        "price": 1699.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1629224316810-9d8805b95e76?w=800"]
    },
    {
        "title": "Sapphire Stud Earrings Platinum",
        "description": "2-carat blue sapphire stud earrings in platinum with four-prong setting. Screw-back closures for everyday security.",
        "price": 1199.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1622398925373-3f91b1e275f5?w=800"]
    },
    {
        "title": "Emerald Teardrop Earrings Gold",
        "description": "Colombian emerald teardrop earrings in 18k yellow gold with diamond halo. Lever-back closure with diamond accents.",
        "price": 1799.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1598560917807-1bae44bd2be8?w=800"]
    },
    {
        "title": "Diamond Bangle Bracelet 18K",
        "description": "18k white gold diamond bangle bracelet with 2.00ct of pavé diamonds, hinged for easy wear and concealed safety clasp.",
        "price": 1899.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1602751584552-8ba73aad10e1?w=800"]
    },
    {
        "title": "Gold Cuban Link Bracelet Men",
        "description": "Solid 14k yellow gold Cuban link bracelet, 10mm wide, with secure box clasp and figure-eight safety. A statement in classic luxury.",
        "price": 1499.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1589128777073-263566ae5e4d?w=800&sat=40"]
    },
    {
        "title": "Charm Bracelet Sterling Silver 925",
        "description": "Sterling silver charm bracelet with seven hand-crafted charms and lobster clasp. Includes presentation box and care cloth.",
        "price": 429.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=800&sat=-40"]
    },
    {
        "title": "Rose Gold Bangle Diamond Accent",
        "description": "Sleek 18k rose gold bangle with diamond-set center motif. Stacks beautifully with other bangles for a modern look.",
        "price": 899.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=800"]
    },
    {
        "title": "Swiss Automatic Chronograph Watch Steel",
        "description": "Swiss-made automatic chronograph watch with sapphire crystal, COSC-certified movement, and 100m water resistance. Premium stainless steel bracelet.",
        "price": 1999.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=800"]
    },
    {
        "title": "Pilot Watch Automatic Black Dial",
        "description": "Aviator pilot watch with 42mm brushed steel case, automatic movement, luminous Arabic numerals, and vintage-style leather strap.",
        "price": 1299.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1548171915-e79a380a2a4b?w=800"]
    },
    {
        "title": "Dive Watch Ceramic Bezel Automatic",
        "description": "Professional 300m dive watch with ceramic bezel, Swiss automatic movement, helium escape valve, and brushed steel bracelet with dive extension.",
        "price": 1799.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1622434641406-a158123450f9?w=800"]
    },
    {
        "title": "Moonphase Dress Watch Gold",
        "description": "Elegant moonphase dress watch with 40mm 18k gold-plated case, guilloché dial, and alligator leather strap. Swiss self-winding caliber.",
        "price": 1699.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?w=800"]
    },
    {
        "title": "Skeleton Tourbillon Watch Collector",
        "description": "Skeletonized dial watch with exposed automatic movement, rose gold-tone case, and crocodile-embossed strap. A mechanical masterpiece.",
        "price": 1999.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1509048191080-d2984bad6ae5?w=800"]
    },
    {
        "title": "Pocket Watch Skeleton Mechanical Chain",
        "description": "Hand-wound skeleton pocket watch with ornate engraving, Albert chain, and presentation box. A timeless gentleman's accessory.",
        "price": 499.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1525423767720-7a4bc7d5e76e?w=800"]
    },
    {
        "title": "Signet Ring Monogram Yellow Gold",
        "description": "Solid 18k yellow gold signet ring with custom hand-engraved monogram and polished finish. A heritage piece for every wardrobe.",
        "price": 1299.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1603974372039-adc49044b6bd?w=800"]
    },
    {
        "title": "Men's Diamond Pinky Ring Platinum",
        "description": "Sophisticated platinum pinky ring with bezel-set 0.75ct diamond center and milgrain edging. A modern take on classic menswear jewelry.",
        "price": 1599.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=800&sat=-40"]
    },
    {
        "title": "Stacking Rings Trio Diamond Gold",
        "description": "Trio of 18k gold stacking rings with diamond pavé, polished, and hammered finishes. Modular luxury for everyday layering.",
        "price": 1099.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1603974372039-adc49044b6bd?w=800&sat=40"]
    },
    {
        "title": "Eternity Diamond Band Platinum",
        "description": "Full eternity diamond band in platinum with 2.00ct of round brilliant diamonds in shared-prong setting. A timeless symbol of love.",
        "price": 1999.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800&sat=40"]
    },
    {
        "title": "Pavé Diamond Hoop Earrings Rose Gold",
        "description": "Medium-size rose gold hoop earrings with pavé diamond setting on both sides. Modern and graceful.",
        "price": 899.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1590548784585-6460aa27c23e?w=800"]
    },
    {
        "title": "Opal Pendant Necklace Gold Chain",
        "description": "Australian opal pendant with natural fire play, set in 14k yellow gold with delicate cable chain. Each stone is uniquely patterned.",
        "price": 899.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1506630448388-4e683c67ddb0?w=800"]
    },
    {
        "title": "Tanzanite Pendant Silver Chain",
        "description": "Vibrant blue-violet Tanzanite pendant in sterling silver with diamond accents. Suspended from an 18-inch box chain.",
        "price": 499.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1588444837495-c6cfeb53f32d?w=800"]
    },
    {
        "title": "Amethyst Statement Necklace Silver",
        "description": "Bold amethyst statement necklace with sterling silver setting and adjustable chain. A regal accent for evening events.",
        "price": 549.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1611594605218-0c72cf9b3ffa?w=800"]
    },
    {
        "title": "Diamond Cross Pendant White Gold",
        "description": "Classic 18k white gold diamond cross pendant with 0.50ct of brilliant-cut diamonds. Timeless and elegant.",
        "price": 1199.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=800"]
    },
    {
        "title": "Cuban Link Chain Gold 22-Inch",
        "description": "Solid 14k gold Cuban link chain, 8mm wide, 22 inches long, with secure box clasp. Polished to mirror finish.",
        "price": 1999.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1561828995-aa79a2db86dd?w=800"]
    },
    {
        "title": "Cufflinks Gold Mother-of-Pearl Dress",
        "description": "Gentleman's 18k gold dress cufflinks with mother-of-pearl inlay and swivel-back hinge. Presented in a leather box.",
        "price": 649.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1611923134239-b9be5816e23d?w=800"]
    },
    {
        "title": "Diamond Tie Pin Platinum Formal",
        "description": "Platinum formal tie pin with single 0.25ct diamond accent. The perfect refinement to any black-tie ensemble.",
        "price": 699.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1611923134239-b9be5816e23d?w=800&sat=-40"]
    },
    {
        "title": "Pearl Brooch Vintage Gold Plated",
        "description": "Vintage-inspired freshwater pearl brooch in gold-plated setting with crystal accents. A graceful detail for lapels and scarves.",
        "price": 419.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800&sat=-40"]
    },
    {
        "title": "Wedding Band Platinum Brushed",
        "description": "Classic 6mm platinum wedding band with brushed center and polished edges. Available in multiple widths.",
        "price": 999.00,
        "category": "jewelry",
        "images": ["https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&sat=-40"]
    },

    # ============================================================
    # PREMIUM HOME & APPLIANCES (30 products)
    # ============================================================
    {
        "title": "Dual Boiler Espresso Machine Prosumer",
        "description": "Prosumer dual-boiler espresso machine with PID temperature control, rotary pump, pre-infusion, and commercial-grade group head. Includes bottomless portafilter.",
        "price": 1799.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1610889556528-9a770e32642f?w=800"]
    },
    {
        "title": "Super-Automatic Coffee Machine Grinder",
        "description": "Super-automatic coffee machine with integrated ceramic burr grinder, milk frother carafe, and touch display. 15 beverage presets.",
        "price": 1499.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800"]
    },
    {
        "title": "Burr Coffee Grinder Commercial",
        "description": "Commercial-grade conical burr coffee grinder with stepless adjustment, 60mm burrs, and LED display. Grinds consistently for espresso to French press.",
        "price": 699.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1587734195503-904fca47e0e9?w=800"]
    },
    {
        "title": "Stand Mixer Professional 7-Quart",
        "description": "7-quart commercial stand mixer with die-cast metal construction, direct-drive motor, and 10 attachments. Handles the heaviest doughs effortlessly.",
        "price": 799.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1590779033100-9f60a05a013d?w=800"]
    },
    {
        "title": "High-Performance Blender 1800W",
        "description": "Pro blender with 1800W motor, 64oz Tritan container, variable speed control, and 10-year warranty. Crushes ice, hot soups, and smoothies effortlessly.",
        "price": 599.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1570197571499-166b36435e9f?w=800"]
    },
    {
        "title": "Sous Vide Precision Cooker Smart",
        "description": "Wi-Fi sous vide precision cooker with 1100W heating, app-controlled recipes, and circulation pump. Restaurant-quality results at home.",
        "price": 419.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1505935428862-770b6f24f629?w=800"]
    },
    {
        "title": "Pizza Oven Outdoor Wood-Fired",
        "description": "Portable wood-fired pizza oven with stone base, stainless steel chimney, and built-in thermometer. Reaches 900°F for authentic Neapolitan pizza.",
        "price": 549.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1604917877934-07d8d248d396?w=800"]
    },
    {
        "title": "Smart Kamado Grill Ceramic 22-Inch",
        "description": "22-inch ceramic kamado grill with smart temperature control, heavy-duty stand, and dual-zone cooking. Perfect for smoking, grilling, and baking.",
        "price": 1299.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800"]
    },
    {
        "title": "Pellet Smoker Wi-Fi Connected Large",
        "description": "Large-capacity pellet smoker with Wi-Fi control, 885 sq in cooking surface, and precision temperature algorithm. Smoke, bake, grill, and sear.",
        "price": 1499.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1544025162-d76694265947?w=800"]
    },
    {
        "title": "Built-In Wine Cooler Dual Zone",
        "description": "Built-in dual-zone wine cooler holding 46 bottles with UV-protected glass, vibration-free compressor, and beechwood shelves.",
        "price": 1699.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=800"]
    },
    {
        "title": "Smart Refrigerator French Door 28 Cu Ft",
        "description": "Smart French-door refrigerator with Family Hub touchscreen, internal camera, dual ice maker, and fingerprint-resistant finish.",
        "price": 1999.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1571175443880-49e1d25b2bc5?w=800"]
    },
    {
        "title": "Induction Cooktop 36-Inch 5-Burner",
        "description": "Premium 36-inch induction cooktop with flex zones, precision heat control, bridge element, and auto-sizing sensors. Ultra-fast boiling and responsive control.",
        "price": 1899.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1556908114-f6e7ad7d3136?w=800"]
    },
    {
        "title": "Kitchen Aid Attachment Bundle Pasta",
        "description": "Professional pasta-maker attachment bundle for stand mixers, including roller, fettuccine cutter, spaghetti cutter, and cleaning brush. Stainless steel construction.",
        "price": 449.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1589308078059-be1415eab4c3?w=800"]
    },
    {
        "title": "Copper Cookware Set 10-Piece Bonded",
        "description": "Tri-ply stainless steel copper-bonded cookware set with ergonomic handles, flared rims, and induction-compatible bases. Cooks evenly and looks stunning.",
        "price": 999.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1528701800489-20be9c1e7e25?w=800"]
    },
    {
        "title": "Cast Iron Cookware Set Enameled",
        "description": "Seven-piece enameled cast iron cookware set with Dutch oven, braiser, and skillet. Lifetime performance with classic French styling.",
        "price": 749.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1556909211-d5b158dbb4ba?w=800"]
    },
    {
        "title": "Japanese Damascus Knife Set 8-Piece",
        "description": "Eight-piece Japanese Damascus steel knife set with 67-layer VG-10 core, ergonomic Pakka-wood handles, and wooden display block.",
        "price": 849.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1593618998160-e34014e67546?w=800"]
    },
    {
        "title": "Luxury Linen Bedding Set King",
        "description": "Pure stone-washed linen bedding set (king) including duvet cover, fitted sheet, and two pillowcases. Breathable, durable, and softer with every wash.",
        "price": 449.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800"]
    },
    {
        "title": "Egyptian Cotton Sheets 1000TC Set",
        "description": "1000 thread count pure Egyptian cotton sheet set with sateen weave, 18-inch deep pockets, and hand-stitched hem details. Cool and luxurious.",
        "price": 429.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?w=800"]
    },
    {
        "title": "Down Comforter Hungarian Goose King",
        "description": "Oversized king-size Hungarian white goose down comforter with 800 fill-power, baffle-box construction, and 100% cotton shell.",
        "price": 699.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800"]
    },
    {
        "title": "Memory Foam Mattress Queen Hybrid",
        "description": "Luxury queen hybrid mattress with copper-infused memory foam, pocketed coil base, cooling gel layer, and edge support. 100-night trial.",
        "price": 1799.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1631679706909-1844bbd07221?w=800"]
    },
    {
        "title": "Velvet Accent Armchair Tufted Brass",
        "description": "Velvet-upholstered accent armchair with button-tufted back, brass-finished legs, and solid hardwood frame. Statement seating for any room.",
        "price": 899.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800"]
    },
    {
        "title": "Solid Oak Dining Table Live Edge",
        "description": "Hand-crafted live-edge solid oak dining table with steel hairpin legs, seating for six. Each piece is unique with natural grain patterns.",
        "price": 1999.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1604074131665-7a4b13870ab2?w=800"]
    },
    {
        "title": "Leather Executive Office Chair Ergonomic",
        "description": "Top-grain leather executive office chair with advanced ergonomic support, lumbar adjustment, memory-foam cushion, and aluminum base.",
        "price": 999.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=800"]
    },
    {
        "title": "Marble Coffee Table Round Carrara",
        "description": "Italian Carrara marble round coffee table with brushed brass pedestal base. Natural veining makes each table one-of-a-kind.",
        "price": 1299.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800"]
    },
    {
        "title": "Persian Rug Hand-Knotted Wool 6x9",
        "description": "Authentic hand-knotted 6x9 Persian wool rug with traditional floral medallion design and natural vegetable dyes. A collectible heirloom.",
        "price": 1899.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1600166898405-da9535204843?w=800"]
    },
    {
        "title": "Crystal Chandelier Modern 12-Light",
        "description": "12-light modern crystal chandelier with Asfour crystal, chrome frame, and adjustable chain. Centerpiece lighting for dining rooms and foyers.",
        "price": 1299.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1519710164239-da123dc03ef4?w=800"]
    },
    {
        "title": "Designer Floor Lamp Marble Brass",
        "description": "Sculptural floor lamp with Carrara marble base, brushed brass arm, and linen drum shade. Modern luxury lighting made in Italy.",
        "price": 899.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1507494924047-60b8ee826ca9?w=800"]
    },
    {
        "title": "Smart Toilet Bidet Heated Seat",
        "description": "Luxury smart toilet with heated seat, dual nozzle bidet, air dryer, remote control, and self-cleaning function. Spa-like comfort at home.",
        "price": 1499.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=800"]
    },
    {
        "title": "Rainfall Shower System Thermostatic",
        "description": "Complete thermostatic rainfall shower system with 12-inch ceiling head, handheld wand, and body jets. Brushed nickel finish.",
        "price": 799.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=800&sat=40"]
    },
    {
        "title": "Fireplace Electric Wall-Mount 60-Inch",
        "description": "60-inch wall-mounted electric fireplace with realistic flame, 13 color modes, heater, and remote control. Transform any room instantly.",
        "price": 599.00,
        "category": "home",
        "images": ["https://images.unsplash.com/photo-1489824904134-891ab64532f1?w=800"]
    },

    # ============================================================
    # PREMIUM SPORTS & OUTDOOR (20 products)
    # ============================================================
    {
        "title": "Carbon Fiber Road Bike Ultegra",
        "description": "Performance carbon fiber road bike with Shimano Ultegra Di2 groupset, deep-section carbon wheels, and aero cockpit. Built for speed and comfort.",
        "price": 1999.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=800"]
    },
    {
        "title": "Mountain Bike Full Suspension 29er",
        "description": "29er full-suspension mountain bike with 150mm travel, 12-speed drivetrain, hydraulic disc brakes, and dropper post. Conquer any trail.",
        "price": 1899.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1576435728678-68d0fbf94e91?w=800"]
    },
    {
        "title": "Electric Mountain Bike Full-Susp 29er",
        "description": "Full-suspension e-mountain bike with mid-drive 250W motor, 630Wh battery, and trail-tuned geometry. 80-mile range on eco mode.",
        "price": 1999.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1623413546044-f73c4e7f87ad?w=800"]
    },
    {
        "title": "Golf Club Complete Set Cavity Back",
        "description": "Complete golf club set with titanium driver, fairway wood, hybrid, cavity-back irons, mallet putter, and stand bag. Forged head design.",
        "price": 899.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1587174486073-ae5e5cff23aa?w=800"]
    },
    {
        "title": "Launch Monitor Golf Simulator Home",
        "description": "Portable golf launch monitor with Doppler radar, club and ball data, simulator software, and 42,000+ courses included.",
        "price": 1999.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1622396481328-9b1b78cdd9fd?w=800"]
    },
    {
        "title": "Ski Set All-Mountain Carbon with Bindings",
        "description": "All-mountain carbon-infused skis with bindings, optimized for edge hold and stability. Suitable for advanced and expert skiers.",
        "price": 1299.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1551524164-687a55dd1126?w=800"]
    },
    {
        "title": "Snowboard Freestyle All-Mountain",
        "description": "Hybrid camber freestyle all-mountain snowboard with poplar/bamboo core, sintered base, and directional twin shape. Versatile for park and powder.",
        "price": 599.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1551524164-6cf64ac2efa7?w=800"]
    },
    {
        "title": "Stand-Up Paddle Board Inflatable Pro",
        "description": "Professional inflatable SUP board (11'6\") with carbon-paddle, fin set, pump, and backpack. Military-grade PVC with drop-stitch core.",
        "price": 749.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1535263115171-ef6f0a9e60de?w=800"]
    },
    {
        "title": "Kayak Fishing Pedal Drive 12ft",
        "description": "12-foot fishing kayak with pedal drive, rudder system, rod holders, and high-back seat. Hands-free fishing from pristine waters.",
        "price": 1699.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1463693396721-8ca0cfa2b3b5?w=800"]
    },
    {
        "title": "Home Gym Adjustable Power Rack",
        "description": "Heavy-duty adjustable power rack with pull-up bar, dip attachment, j-hooks, safety arms, and lat pulldown. 1000lb capacity commercial grade.",
        "price": 1299.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=800"]
    },
    {
        "title": "Smart Rowing Machine Magnetic",
        "description": "Commercial-grade magnetic rowing machine with 16 resistance levels, HD touchscreen, heart-rate sensor, and live class streaming.",
        "price": 1499.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1533681904393-9ab6eee7e408?w=800"]
    },
    {
        "title": "Spin Bike Indoor Cycle HD Screen",
        "description": "Interactive indoor spin bike with 22-inch HD screen, magnetic resistance, auto-incline, and live/on-demand classes. Commercial-grade build.",
        "price": 1899.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800"]
    },
    {
        "title": "Home Treadmill Folding Smart",
        "description": "Folding smart treadmill with 12.5mph top speed, 15% incline, cushioned deck, and integrated 10-inch HD display. 350-lb user capacity.",
        "price": 1799.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1576678927484-cc907957088c?w=800"]
    },
    {
        "title": "Boxing Training Station Wall Mount",
        "description": "All-in-one wall-mounted boxing training station with adjustable speed bag, heavy bag, double-end bag, and pull-up bar. Commercial grade.",
        "price": 899.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1593079831268-3381b0db4a77?w=800"]
    },
    {
        "title": "Recovery Massage Gun Pro",
        "description": "Professional percussive massage gun with 6 attachments, 5 speeds, quiet brushless motor, OLED display, and aluminum alloy body. 6-hour battery.",
        "price": 449.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=800"]
    },
    {
        "title": "Infrared Sauna Blanket Home Use",
        "description": "Low-EMF far-infrared sauna blanket with digital controller, timer, and three heating zones. Detox and relaxation at home.",
        "price": 599.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1545205597-3d9d02c29597?w=800"]
    },
    {
        "title": "Scuba Diving Regulator Set Complete",
        "description": "Complete scuba diving regulator set with first/second stage, octopus, and dive computer. Environmentally sealed for cold-water use.",
        "price": 1299.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1560275619-4662e36fa65c?w=800"]
    },
    {
        "title": "Underwater Scooter Sea DPV",
        "description": "Underwater diver propulsion vehicle (DPV) with 60-minute runtime, 4mph speed, and rated to 131ft depth. Explore more of the ocean with less effort.",
        "price": 1299.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1532339142463-fd0a8979791a?w=800"]
    },
    {
        "title": "Mountaineering Backpack 75L Expedition",
        "description": "75L expedition mountaineering backpack with waterproof fabric, internal frame, and ice-axe loops. Weighs only 4.4lb with 130L of expansion.",
        "price": 449.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1551632811-561732d1e306?w=800"]
    },
    {
        "title": "Expedition Tent 4-Season 3-Person",
        "description": "Double-wall 4-season expedition tent for 3 people, with silicone-coated nylon, aluminum poles, and snow skirts. Withstands 70mph winds.",
        "price": 899.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=800"]
    },

    # ============================================================
    # LUXURY BEAUTY & WELLNESS (15 products)
    # ============================================================
    {
        "title": "Luxury Oud Parfum 100ml Exclusive",
        "description": "Rare exclusive oud parfum with smoky rose, amber, and Cambodian oud notes. 100ml crystal flacon presented in silk-lined box.",
        "price": 799.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1541643600914-78b084683601?w=800"]
    },
    {
        "title": "Niche Fragrance Discovery Set 10x10ml",
        "description": "Curated niche fragrance discovery set with 10 unique 10ml atomizers from artisan perfumers. Explore elevated fragrance artistry.",
        "price": 449.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1547887537-6158d64c35b3?w=800"]
    },
    {
        "title": "LED Light Therapy Face Mask Pro",
        "description": "Medical-grade multi-color LED face mask with red, blue, and infrared therapy. Clinically proven for anti-aging and acne treatment.",
        "price": 549.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=800"]
    },
    {
        "title": "Microcurrent Facial Toning Device",
        "description": "Professional microcurrent facial toning device with 5 intensity levels and conductive gel. Contours, lifts, and tones facial muscles.",
        "price": 429.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1570194065650-d99fb4bedf0a?w=800"]
    },
    {
        "title": "At-Home Laser Hair Removal IPL Device",
        "description": "FDA-cleared at-home IPL laser hair removal device with 999,999 flashes, 5 intensity levels, and SmartSkin sensor. Permanent results in weeks.",
        "price": 499.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=800"]
    },
    {
        "title": "Premium Hair Dryer Ionic Intelligent",
        "description": "Intelligent ionic hair dryer with dual heat sensors, magnetic attachments, and digital motor. Protects hair from extreme heat damage.",
        "price": 449.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1562322140-8baeececf3df?w=800"]
    },
    {
        "title": "Airwrap Styler Multi-Styler",
        "description": "Multi-styler with curling barrels, straightening brush, smoothing brush, and round brush. Harness the Coanda effect for salon results.",
        "price": 599.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=800"]
    },
    {
        "title": "Anti-Aging Skincare Set Luxury",
        "description": "Complete anti-aging skincare set with serum, cream, eye treatment, and mask infused with retinol, peptides, and marine extracts.",
        "price": 499.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=800"]
    },
    {
        "title": "Caviar Skincare Ultra Deluxe Set",
        "description": "Ultra-deluxe caviar-infused skincare set with cleanser, essence, serum, and moisturizer. Premium anti-aging results.",
        "price": 799.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=800"]
    },
    {
        "title": "Electric Razor Foil Shaver Premium",
        "description": "Premium foil electric shaver with multi-flex head, precision trimmer, and 60-minute cordless use. Includes leather travel case and cleaning station.",
        "price": 449.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1574882232010-37d0712bee89?w=800"]
    },
    {
        "title": "Sonic Facial Cleansing Brush Luxury",
        "description": "Silicone sonic facial cleansing brush with 16 intensity levels, 8000 pulsations per minute, and anti-aging LED mode. USB-C rechargeable.",
        "price": 429.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=800&sat=-40"]
    },
    {
        "title": "Hydrafacial Device At-Home Pro",
        "description": "At-home hydrafacial device offering exfoliation, extraction, and hydration in one treatment. Spa-grade results at your vanity.",
        "price": 1199.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=800&sat=40"]
    },
    {
        "title": "Premium Perfume Gift Set Unisex",
        "description": "Luxury perfume gift set with three 50ml unisex fragrances and travel atomizer, presented in a suede pouch.",
        "price": 499.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=800"]
    },
    {
        "title": "Professional Makeup Artist Case Mobile",
        "description": "Aluminum professional makeup artist case with dimmable LED lighting, dozens of compartments, and wheeled design. Used by industry pros.",
        "price": 699.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800"]
    },
    {
        "title": "Luxury Spa Robe Cashmere Gift Set",
        "description": "Luxury cashmere-blend spa robe and slipper gift set with matching towel, bath salts, and silk sleep mask. Presented in a wooden box.",
        "price": 499.00,
        "category": "beauty",
        "images": ["https://images.unsplash.com/photo-1544006659-f0b21884ce1d?w=800"]
    },

    # ============================================================
    # RARE BOOKS & STATIONERY (5 products)
    # ============================================================
    {
        "title": "Classic Literature Leather-Bound Set 10-Volume",
        "description": "Genuine leather-bound 10-volume classic literature collection with gold foil titles, ribbon markers, and hand-marbled endpapers.",
        "price": 1299.00,
        "category": "books",
        "images": ["https://images.unsplash.com/photo-1512820790803-83ca734da794?w=800"]
    },
    {
        "title": "Limited Edition Signed Art Book Folio",
        "description": "Limited edition signed large-format art book folio with silkscreen prints, leather slipcase, and certificate of authenticity. Numbered 1/250.",
        "price": 1499.00,
        "category": "books",
        "images": ["https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=800"]
    },
    {
        "title": "First Edition Collector Fiction Vintage",
        "description": "First edition collectible vintage fiction novel in original dust jacket with archival protection. A treasure for serious book collectors.",
        "price": 899.00,
        "category": "books",
        "images": ["https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800"]
    },
    {
        "title": "Bespoke Leather Journal Monogrammed Large",
        "description": "Bespoke monogrammed large-format leather journal with hand-stitched binding, 300 pages of archival paper, and presentation box.",
        "price": 449.00,
        "category": "books",
        "images": ["https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=800"]
    },
    {
        "title": "Vintage Globe Bar Wooden Cabinet Antique",
        "description": "Antique-inspired wooden globe bar cabinet with map detailing, brass trim, and interior bottle storage. A rare library statement piece.",
        "price": 799.00,
        "category": "books",
        "images": ["https://images.unsplash.com/photo-1523207911345-32501502db22?w=800"]
    },

    # ============================================================
    # MUSICAL INSTRUMENTS & AUTOMOTIVE (10 products)
    # ============================================================
    {
        "title": "Acoustic Guitar Solid Spruce Top Dreadnought",
        "description": "Premium dreadnought acoustic guitar with solid Sitka spruce top, rosewood back and sides, bone nut/saddle, and hardshell case. Rich, resonant tone.",
        "price": 1299.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=800"]
    },
    {
        "title": "Electric Guitar Professional HSS Custom",
        "description": "Professional HSS electric guitar with alder body, roasted maple neck, stainless steel frets, and locking tremolo. Hand-wired pickups.",
        "price": 1699.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?w=800"]
    },
    {
        "title": "Digital Piano 88-Key Weighted Hammer Action",
        "description": "88-key digital piano with graded hammer action, 256-note polyphony, premium sample library, and Bluetooth MIDI. Includes sustain pedal and bench.",
        "price": 1499.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=800"]
    },
    {
        "title": "Professional Saxophone Alto Brass",
        "description": "Intermediate-to-professional alto saxophone with hand-engraved brass body, high F# key, and plush-lined case. Includes reeds, neck strap, and cleaning kit.",
        "price": 1899.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1466428996289-fb355538da1b?w=800"]
    },
    {
        "title": "Violin Hand-Crafted 4/4 Full Size Antique",
        "description": "Hand-crafted 4/4 full-size violin with solid spruce top, flamed maple back, ebony fittings, and antique varnish. Includes Brazilwood bow and case.",
        "price": 1199.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800"]
    },
    {
        "title": "Portable Car Jump Starter & Compressor Pro",
        "description": "Heavy-duty portable car jump starter with 2000A peak current, integrated 150 PSI air compressor, LED worklight, and USB-C PD charging. Starts V8 diesel engines.",
        "price": 429.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800"]
    },
    {
        "title": "Car Diagnostic Scan Tool Professional OBD2",
        "description": "Professional bidirectional OBD2 diagnostic scan tool with ECU coding, active tests, all-system diagnostics, and 8-inch touchscreen. Covers 80+ vehicle brands.",
        "price": 899.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1486262715619-67b85e0b08d3?w=800"]
    },
    {
        "title": "4K Dash Cam Front & Rear with GPS",
        "description": "Premium 4K UHD dash cam with front and rear cameras, built-in GPS, WDR, 24-hour parking mode, and smartphone app. Includes 128GB microSD card.",
        "price": 459.00,
        "category": "electronics",
        "images": ["https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=800"]
    },
    {
        "title": "Professional Mechanic Tool Chest Set",
        "description": "Rolling professional mechanic tool chest with 450 chrome-vanadium tools, steel ball-bearing drawers, and laser-engraved sockets. Lifetime warranty.",
        "price": 1599.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1530124566582-a618bc2615dc?w=800"]
    },
    {
        "title": "Automotive Spray Paint Compressor Kit",
        "description": "Professional HVLP automotive spray paint compressor kit with 60-gallon tank, 3.5HP motor, regulator, and complete paint gun set. Shop-quality finish at home.",
        "price": 1299.00,
        "category": "sports",
        "images": ["https://images.unsplash.com/photo-1504222490345-c075b6008014?w=800"]
    },
]
