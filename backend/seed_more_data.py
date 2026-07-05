"""
Seed script: Populate the database with 60+ products.
Run this while the backend is running on port 8000.
"""
import json
import urllib.request
import urllib.error
import random
from datetime import datetime, timedelta

BASE = "http://127.0.0.1:8000"

def api(method, path, data=None, token=None):
    url = BASE + path
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  [HTTP {e.code}] {path}: {e.read().decode()[:200]}")
        return None

# 1. Login
print("Logging in...")
tok = api("POST", "/auth/login", {"email": "admin@nexus.ai", "password": "admin123"})
if not tok:
    print("ERROR: Could not login. Is backend running on 8000?")
    exit(1)
token = tok["access_token"]
print(f"  Token: {token[:30]}...")

# 2. Get or create categories
print("\nFetching categories...")
cats = api("GET", "/categories/", token=token)
cat_map = {c["name"]: c["_id"] for c in (cats or [])}
print(f"  Existing: {list(cat_map.keys())}")

new_cats = [
    {"name": "Networking", "description": "Routers, switches, cables and networking equipment"},
    {"name": "Tools", "description": "Power tools, hand tools and workshop equipment"},
    {"name": "Safety", "description": "PPE, safety gear and protective equipment"},
    {"name": "Clothing", "description": "Work uniforms and apparel"},
    {"name": "Food & Beverage", "description": "Pantry items, beverages and office kitchen supplies"},
    {"name": "Medical", "description": "First aid, medications and health supplies"},
    {"name": "IT Accessories", "description": "Cables, adapters, hubs and IT peripherals"},
]
for nc in new_cats:
    if nc["name"] not in cat_map:
        result = api("POST", "/categories/", nc, token=token)
        if result:
            cat_map[nc["name"]] = result["_id"]
            print(f"  Created category: {nc['name']}")

# 3. Get or create suppliers
print("\nFetching suppliers...")
sups = api("GET", "/suppliers/", token=token)
sup_map = {s["name"]: s["_id"] for s in (sups or [])}
print(f"  Existing: {list(sup_map.keys())}")

new_sups = [
    {"name": "TechCorp", "contact_email": "sales@techcorp.com", "contact_phone": "+1-555-1000", "address": "New York, USA", "rating": 4.8},
    {"name": "OfficeHub", "contact_email": "support@officehub.com", "contact_phone": "+1-555-2000", "address": "Chicago, USA", "rating": 4.5},
    {"name": "NetGear Pro", "contact_email": "orders@netgearpro.com", "contact_phone": "+1-555-3000", "address": "San Jose, CA", "rating": 4.7},
    {"name": "SafetyFirst", "contact_email": "sales@safetyfirst.com", "contact_phone": "+1-555-4000", "address": "Dallas, TX", "rating": 4.6},
    {"name": "MedSupply Co.", "contact_email": "orders@medsupply.com", "contact_phone": "+1-555-5000", "address": "Boston, MA", "rating": 4.9},
    {"name": "ToolMaster", "contact_email": "sales@toolmaster.com", "contact_phone": "+1-555-6000", "address": "Detroit, MI", "rating": 4.4},
    {"name": "UniCorp", "contact_email": "info@unicorp.com", "contact_phone": "+1-555-7000", "address": "Atlanta, GA", "rating": 4.3},
]
for ns in new_sups:
    if ns["name"] not in sup_map:
        result = api("POST", "/suppliers/", ns, token=token)
        if result:
            sup_map[ns["name"]] = result["_id"]
            print(f"  Created supplier: {ns['name']}")

# Helper
def cid(name):
    return cat_map.get(name, list(cat_map.values())[0])

def sid(name):
    return sup_map.get(name, list(sup_map.values())[0])

# 4. Check existing products
existing_products_resp = api("GET", "/products/", token=token)
existing_skus = {p["sku"] for p in (existing_products_resp or [])}
print(f"\nExisting products: {len(existing_skus)}")

products = [
    # === ELECTRONICS ===
    {"sku": "LAP-DEL-15", "name": "Dell XPS 15 Laptop", "category_id": cid("Electronics"), "supplier_id": sid("TechCorp"), "quantity": 8, "reorder_threshold": 5, "unit_price": 1799.99, "cost_price": 1400.0, "location": "Warehouse A"},
    {"sku": "LAP-LEN-T14", "name": "Lenovo ThinkPad T14s", "category_id": cid("Electronics"), "supplier_id": sid("TechCorp"), "quantity": 3, "reorder_threshold": 5, "unit_price": 1299.00, "cost_price": 980.0, "location": "Warehouse A"},
    {"sku": "MON-LG-27", "name": "LG 27 inch 4K Monitor", "category_id": cid("Electronics"), "supplier_id": sid("TechCorp"), "quantity": 20, "reorder_threshold": 8, "unit_price": 549.00, "cost_price": 390.0, "location": "Warehouse A"},
    {"sku": "PHN-IPH-15", "name": "iPhone 15 Pro", "category_id": cid("Electronics"), "supplier_id": sid("TechCorp"), "quantity": 0, "reorder_threshold": 10, "unit_price": 999.00, "cost_price": 750.0, "location": "Warehouse A"},
    {"sku": "PHN-SAM-S24", "name": "Samsung Galaxy S24", "category_id": cid("Electronics"), "supplier_id": sid("TechCorp"), "quantity": 6, "reorder_threshold": 10, "unit_price": 799.00, "cost_price": 580.0, "location": "Warehouse A"},
    {"sku": "TAB-IPD-AIR", "name": "iPad Air M2", "category_id": cid("Electronics"), "supplier_id": sid("TechCorp"), "quantity": 12, "reorder_threshold": 6, "unit_price": 749.00, "cost_price": 550.0, "location": "Warehouse A"},
    {"sku": "KEY-LOG-MX", "name": "Logitech MX Keys", "category_id": cid("Electronics"), "supplier_id": sid("TechCorp"), "quantity": 35, "reorder_threshold": 15, "unit_price": 99.00, "cost_price": 65.0, "location": "Warehouse A"},
    {"sku": "WEB-LOG-C920", "name": "Logitech C920 Webcam", "category_id": cid("Electronics"), "supplier_id": sid("TechCorp"), "quantity": 2, "reorder_threshold": 8, "unit_price": 79.99, "cost_price": 55.0, "location": "Warehouse A"},
    {"sku": "PRN-HP-CLJ", "name": "HP Color LaserJet Pro", "category_id": cid("Electronics"), "supplier_id": sid("TechCorp"), "quantity": 4, "reorder_threshold": 3, "unit_price": 499.00, "cost_price": 360.0, "location": "Warehouse B"},
    {"sku": "SSD-SAM-1T", "name": "Samsung 1TB SSD External", "category_id": cid("Electronics"), "supplier_id": sid("TechCorp"), "quantity": 50, "reorder_threshold": 20, "unit_price": 89.00, "cost_price": 55.0, "location": "Warehouse A"},
    {"sku": "USB-HUB-7P", "name": "7-Port USB Hub", "category_id": cid("IT Accessories"), "supplier_id": sid("TechCorp"), "quantity": 0, "reorder_threshold": 10, "unit_price": 29.99, "cost_price": 15.0, "location": "Warehouse A"},
    {"sku": "CAB-HDMI-2M", "name": "HDMI 2.0 Cable 2m", "category_id": cid("IT Accessories"), "supplier_id": sid("TechCorp"), "quantity": 100, "reorder_threshold": 30, "unit_price": 12.99, "cost_price": 4.0, "location": "Warehouse A"},

    # === NETWORKING ===
    {"sku": "RTR-ASUS-AX6", "name": "ASUS AX6000 WiFi Router", "category_id": cid("Networking"), "supplier_id": sid("NetGear Pro"), "quantity": 7, "reorder_threshold": 5, "unit_price": 349.00, "cost_price": 240.0, "location": "Warehouse B"},
    {"sku": "SWT-CISCO-24", "name": "Cisco 24-Port Managed Switch", "category_id": cid("Networking"), "supplier_id": sid("NetGear Pro"), "quantity": 3, "reorder_threshold": 4, "unit_price": 899.00, "cost_price": 650.0, "location": "Warehouse B"},
    {"sku": "CAB-CAT6-30M", "name": "CAT6 Ethernet Cable 30m", "category_id": cid("Networking"), "supplier_id": sid("NetGear Pro"), "quantity": 200, "reorder_threshold": 50, "unit_price": 14.99, "cost_price": 5.0, "location": "Warehouse B"},
    {"sku": "NAS-SYN-4B", "name": "Synology 4-Bay NAS", "category_id": cid("Networking"), "supplier_id": sid("NetGear Pro"), "quantity": 2, "reorder_threshold": 3, "unit_price": 599.00, "cost_price": 430.0, "location": "Warehouse B"},
    {"sku": "WAP-UBIQ-AC", "name": "Ubiquiti UniFi AP AC", "category_id": cid("Networking"), "supplier_id": sid("NetGear Pro"), "quantity": 15, "reorder_threshold": 6, "unit_price": 179.00, "cost_price": 120.0, "location": "Warehouse B"},

    # === FURNITURE ===
    {"sku": "DSK-SIT-STD", "name": "Motorized Sit-Stand Desk", "category_id": cid("Furniture"), "supplier_id": sid("OfficeHub"), "quantity": 10, "reorder_threshold": 4, "unit_price": 695.00, "cost_price": 480.0, "location": "Warehouse C"},
    {"sku": "CHR-MESH-01", "name": "Mesh Back Office Chair", "category_id": cid("Furniture"), "supplier_id": sid("OfficeHub"), "quantity": 25, "reorder_threshold": 10, "unit_price": 249.00, "cost_price": 170.0, "location": "Warehouse C"},
    {"sku": "CAB-FILE-3D", "name": "3-Drawer Filing Cabinet", "category_id": cid("Furniture"), "supplier_id": sid("OfficeHub"), "quantity": 8, "reorder_threshold": 5, "unit_price": 149.00, "cost_price": 95.0, "location": "Warehouse C"},
    {"sku": "BSH-BOOK-5S", "name": "5-Shelf Bookcase", "category_id": cid("Furniture"), "supplier_id": sid("OfficeHub"), "quantity": 6, "reorder_threshold": 4, "unit_price": 189.00, "cost_price": 115.0, "location": "Warehouse C"},
    {"sku": "WHT-BOARD-L", "name": "Magnetic Whiteboard 120x90cm", "category_id": cid("Furniture"), "supplier_id": sid("OfficeHub"), "quantity": 14, "reorder_threshold": 5, "unit_price": 79.00, "cost_price": 45.0, "location": "Warehouse C"},
    {"sku": "SHF-STL-HVY", "name": "Heavy Duty Steel Shelving Unit", "category_id": cid("Furniture"), "supplier_id": sid("OfficeHub"), "quantity": 0, "reorder_threshold": 4, "unit_price": 219.00, "cost_price": 145.0, "location": "Warehouse C"},

    # === STATIONERY ===
    {"sku": "PPR-A4-500", "name": "A4 Copy Paper 500 Sheets", "category_id": cid("Stationery"), "supplier_id": sid("OfficeHub"), "quantity": 300, "reorder_threshold": 100, "unit_price": 8.99, "cost_price": 4.5, "location": "Storage Room 1"},
    {"sku": "PEN-BLK-BOX", "name": "Black Ballpoint Pens Box/50", "category_id": cid("Stationery"), "supplier_id": sid("OfficeHub"), "quantity": 40, "reorder_threshold": 20, "unit_price": 14.99, "cost_price": 7.0, "location": "Storage Room 1"},
    {"sku": "MKR-WHT-8PK", "name": "Whiteboard Markers 8-Pack", "category_id": cid("Stationery"), "supplier_id": sid("OfficeHub"), "quantity": 5, "reorder_threshold": 10, "unit_price": 11.99, "cost_price": 5.5, "location": "Storage Room 1"},
    {"sku": "FLD-MNL-50", "name": "Manila Folders Box/50", "category_id": cid("Stationery"), "supplier_id": sid("OfficeHub"), "quantity": 80, "reorder_threshold": 30, "unit_price": 18.99, "cost_price": 10.0, "location": "Storage Room 1"},
    {"sku": "STK-NOTE-YLW", "name": "Sticky Notes Yellow 6-Pack", "category_id": cid("Stationery"), "supplier_id": sid("OfficeHub"), "quantity": 3, "reorder_threshold": 15, "unit_price": 6.99, "cost_price": 2.5, "location": "Storage Room 1"},
    {"sku": "SCP-OFFCE-L", "name": "Office Scissors Large", "category_id": cid("Stationery"), "supplier_id": sid("OfficeHub"), "quantity": 22, "reorder_threshold": 10, "unit_price": 9.99, "cost_price": 4.0, "location": "Storage Room 1"},
    {"sku": "IK-STAMP-BL", "name": "Stamp Ink Pad Blue", "category_id": cid("Stationery"), "supplier_id": sid("OfficeHub"), "quantity": 18, "reorder_threshold": 10, "unit_price": 5.99, "cost_price": 2.0, "location": "Storage Room 1"},

    # === TOOLS ===
    {"sku": "DRL-BSCH-18", "name": "Bosch 18V Cordless Drill", "category_id": cid("Tools"), "supplier_id": sid("ToolMaster"), "quantity": 4, "reorder_threshold": 3, "unit_price": 179.00, "cost_price": 120.0, "location": "Workshop"},
    {"sku": "SAW-CIRCU-7", "name": "7 inch Circular Saw", "category_id": cid("Tools"), "supplier_id": sid("ToolMaster"), "quantity": 2, "reorder_threshold": 3, "unit_price": 149.00, "cost_price": 95.0, "location": "Workshop"},
    {"sku": "WRN-SET-MM", "name": "Metric Wrench Set 20Pc", "category_id": cid("Tools"), "supplier_id": sid("ToolMaster"), "quantity": 10, "reorder_threshold": 5, "unit_price": 69.99, "cost_price": 35.0, "location": "Workshop"},
    {"sku": "SCDR-KIT-68", "name": "Screwdriver Kit 68-Piece", "category_id": cid("Tools"), "supplier_id": sid("ToolMaster"), "quantity": 16, "reorder_threshold": 6, "unit_price": 49.99, "cost_price": 25.0, "location": "Workshop"},
    {"sku": "MLT-TESTM-AC", "name": "AC/DC Digital Multimeter", "category_id": cid("Tools"), "supplier_id": sid("ToolMaster"), "quantity": 0, "reorder_threshold": 4, "unit_price": 59.99, "cost_price": 30.0, "location": "Workshop"},
    {"sku": "TVL-LEVL-24", "name": "24 inch Spirit Level", "category_id": cid("Tools"), "supplier_id": sid("ToolMaster"), "quantity": 7, "reorder_threshold": 4, "unit_price": 39.99, "cost_price": 18.0, "location": "Workshop"},

    # === SAFETY ===
    {"sku": "PPE-GLOVE-L", "name": "Nitrile Work Gloves Size L Box/100", "category_id": cid("Safety"), "supplier_id": sid("SafetyFirst"), "quantity": 20, "reorder_threshold": 8, "unit_price": 22.99, "cost_price": 10.0, "location": "Safety Cabinet"},
    {"sku": "PPE-MASK-N95", "name": "N95 Respirator Masks Box/20", "category_id": cid("Safety"), "supplier_id": sid("SafetyFirst"), "quantity": 3, "reorder_threshold": 10, "unit_price": 34.99, "cost_price": 18.0, "location": "Safety Cabinet"},
    {"sku": "PPE-HLMT-YLW", "name": "Hard Hat Yellow", "category_id": cid("Safety"), "supplier_id": sid("SafetyFirst"), "quantity": 30, "reorder_threshold": 10, "unit_price": 19.99, "cost_price": 8.0, "location": "Safety Cabinet"},
    {"sku": "PPE-VEST-HV", "name": "High Visibility Safety Vest", "category_id": cid("Safety"), "supplier_id": sid("SafetyFirst"), "quantity": 45, "reorder_threshold": 15, "unit_price": 14.99, "cost_price": 5.5, "location": "Safety Cabinet"},
    {"sku": "PPE-GOGGL-S", "name": "Safety Goggles Clear", "category_id": cid("Safety"), "supplier_id": sid("SafetyFirst"), "quantity": 0, "reorder_threshold": 12, "unit_price": 12.99, "cost_price": 4.5, "location": "Safety Cabinet"},
    {"sku": "EXT-CO2-5KG", "name": "CO2 Fire Extinguisher 5kg", "category_id": cid("Safety"), "supplier_id": sid("SafetyFirst"), "quantity": 8, "reorder_threshold": 4, "unit_price": 89.99, "cost_price": 55.0, "location": "Safety Cabinet"},

    # === MEDICAL ===
    {"sku": "FAK-COMP-L", "name": "Large Comprehensive First Aid Kit", "category_id": cid("Medical"), "supplier_id": sid("MedSupply Co."), "quantity": 5, "reorder_threshold": 3, "unit_price": 59.99, "cost_price": 32.0, "location": "Medical Room"},
    {"sku": "MED-BNDGE-100", "name": "Adhesive Bandages 100-Pack", "category_id": cid("Medical"), "supplier_id": sid("MedSupply Co."), "quantity": 2, "reorder_threshold": 5, "unit_price": 16.99, "cost_price": 7.0, "location": "Medical Room"},
    {"sku": "MED-STZR-H", "name": "Hand Sanitizer 500ml", "category_id": cid("Medical"), "supplier_id": sid("MedSupply Co."), "quantity": 60, "reorder_threshold": 20, "unit_price": 6.99, "cost_price": 2.5, "location": "Medical Room"},
    {"sku": "MED-THERM-IR", "name": "Infrared Thermometer", "category_id": cid("Medical"), "supplier_id": sid("MedSupply Co."), "quantity": 4, "reorder_threshold": 3, "unit_price": 44.99, "cost_price": 22.0, "location": "Medical Room"},
    {"sku": "MED-GLOVE-M", "name": "Latex Medical Gloves M Box/100", "category_id": cid("Medical"), "supplier_id": sid("MedSupply Co."), "quantity": 0, "reorder_threshold": 10, "unit_price": 18.99, "cost_price": 8.0, "location": "Medical Room"},

    # === FOOD ===
    {"sku": "FBV-COFFEE-1K", "name": "Arabica Coffee Beans 1kg", "category_id": cid("Food & Beverage"), "supplier_id": sid("UniCorp"), "quantity": 10, "reorder_threshold": 5, "unit_price": 24.99, "cost_price": 14.0, "location": "Kitchen Store"},
    {"sku": "FBV-TEA-100", "name": "Assorted Tea Bags 100-Pack", "category_id": cid("Food & Beverage"), "supplier_id": sid("UniCorp"), "quantity": 30, "reorder_threshold": 10, "unit_price": 9.99, "cost_price": 4.0, "location": "Kitchen Store"},
    {"sku": "FBV-WTR-24", "name": "Mineral Water 500ml 24-Pack", "category_id": cid("Food & Beverage"), "supplier_id": sid("UniCorp"), "quantity": 2, "reorder_threshold": 8, "unit_price": 19.99, "cost_price": 10.0, "location": "Kitchen Store"},
    {"sku": "FBV-SUGAR-1K", "name": "White Sugar 1kg", "category_id": cid("Food & Beverage"), "supplier_id": sid("UniCorp"), "quantity": 15, "reorder_threshold": 5, "unit_price": 3.99, "cost_price": 1.5, "location": "Kitchen Store"},
    {"sku": "FBV-SNCK-MX", "name": "Assorted Snack Bars Box/30", "category_id": cid("Food & Beverage"), "supplier_id": sid("UniCorp"), "quantity": 4, "reorder_threshold": 10, "unit_price": 29.99, "cost_price": 15.0, "location": "Kitchen Store"},

    # === CLOTHING ===
    {"sku": "CLT-POLO-M", "name": "Company Polo Shirt Size M", "category_id": cid("Clothing"), "supplier_id": sid("UniCorp"), "quantity": 20, "reorder_threshold": 10, "unit_price": 34.99, "cost_price": 15.0, "location": "Storage Room 2"},
    {"sku": "CLT-POLO-L", "name": "Company Polo Shirt Size L", "category_id": cid("Clothing"), "supplier_id": sid("UniCorp"), "quantity": 5, "reorder_threshold": 10, "unit_price": 34.99, "cost_price": 15.0, "location": "Storage Room 2"},
    {"sku": "CLT-POLO-XL", "name": "Company Polo Shirt Size XL", "category_id": cid("Clothing"), "supplier_id": sid("UniCorp"), "quantity": 0, "reorder_threshold": 8, "unit_price": 34.99, "cost_price": 15.0, "location": "Storage Room 2"},
    {"sku": "CLT-JCKT-L", "name": "Company Fleece Jacket Size L", "category_id": cid("Clothing"), "supplier_id": sid("UniCorp"), "quantity": 12, "reorder_threshold": 6, "unit_price": 59.99, "cost_price": 28.0, "location": "Storage Room 2"},
    {"sku": "CLT-BOOTS-9", "name": "Steel Toe Safety Boots Size 9", "category_id": cid("Clothing"), "supplier_id": sid("SafetyFirst"), "quantity": 3, "reorder_threshold": 5, "unit_price": 119.99, "cost_price": 72.0, "location": "Storage Room 2"},
]

print(f"\nSeeding {len(products)} products...")
created = 0
skipped = 0
for p in products:
    if p["sku"] in existing_skus:
        skipped += 1
        continue
    now = datetime.utcnow().isoformat()
    p["created_at"] = now
    p["updated_at"] = now
    result = api("POST", "/products/", p, token=token)
    if result:
        created += 1
        print(f"  + [{p['sku']}] {p['name']} (qty: {p['quantity']})")
    else:
        print(f"  ! FAILED: {p['sku']} {p['name']}")

print(f"\n✅ Done! Created {created} products, skipped {skipped} already-existing products.")
print("\nProduct Summary:")
all_products = api("GET", "/products/", token=token) or []
out_of = sum(1 for p in all_products if p.get("quantity", 0) == 0)
low = sum(1 for p in all_products if 0 < p.get("quantity", 0) <= p.get("reorder_threshold", 10))
total_val = sum(p.get("quantity", 0) * p.get("unit_price", 0) for p in all_products)
print(f"  Total Products: {len(all_products)}")
print(f"  Out of Stock: {out_of}")
print(f"  Low Stock: {low}")
print(f"  Total Inventory Value: ${total_val:,.2f}")
