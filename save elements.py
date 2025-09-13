import requests
from bs4 import BeautifulSoup
import os
import time

def fetch_image(url):
    for attempt in range(3):
        try:
            r = session.get(url, timeout=10)
            r.raise_for_status()
            return r.content
        except requests.exceptions.RequestException:
            print(f"Attempt {attempt+1} failed for {url}")
            time.sleep(1)
    return None

# Folder to save images
save_folder = r"E:\Neels Programs\first lang\images"
os.makedirs(save_folder, exist_ok=True)

# Use a requests session for faster repeated requests
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

# --------------------
# Step 1: Download from main table (Hydrogen → Zinc)
# --------------------
main_table_url = "https://periodictableguide.com/bohr-model-of-all-elements/"
try:
    r = session.get(main_table_url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
except requests.exceptions.RequestException as e:
    print(f"Failed to fetch main table: {e}")
    soup = None

if soup:
    for tr in soup.select("tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 3:
            continue
        name_link = tds[1].find("a")
        if not name_link or not name_link.has_attr('href'):
            continue

        # Name
        name = name_link.text.strip().split('(')[0].strip()

        # Symbol from URL
        href = name_link['href'].rstrip('/').split('/')[-1]
        parts = href.split('-')
        if len(parts) >= 2:
            symbol = parts[1].capitalize()
        else:
            symbol = name[:2].capitalize()
            print(f"Warning: Could not parse symbol for {name}")

        # Bohr model image
        img_tag = tds[2].find("img")
        if not img_tag:
            continue
        img_url = img_tag['src']
        filename = os.path.join(save_folder, f"{name}.jpg")
        if os.path.exists(filename):
            continue
        try:
            img_data = fetch_image(img_url)
            if img_data:
             with open(filename, 'wb') as f:
              f.write(img_data)
             print(f"Saved: {filename}")
            else:
             print(f"Skipping {['name']} after 3 failed attempts")
        except requests.exceptions.RequestException as e:
            print(f"Failed to save {name}: {e}")
        time.sleep(0.3)  # polite delay

# --------------------
# Step 2: Download remaining elements using your array
# --------------------
elements = [
    {"name":"hydrogen","symbol":"H"},{"name":"helium","symbol":"He"},
    {"name":"lithium","symbol":"Li"},{"name":"beryllium","symbol":"Be"},
    {"name":"boron","symbol":"B"},{"name":"carbon","symbol":"C"},
    {"name":"nitrogen","symbol":"N"},{"name":"oxygen","symbol":"O"},
    {"name":"fluorine","symbol":"F"},{"name":"neon","symbol":"Ne"},
    {"name":"sodium","symbol":"Na"},{"name":"magnesium","symbol":"Mg"},
    {"name":"aluminum","symbol":"Al"},{"name":"silicon","symbol":"Si"},
    {"name":"phosphorus","symbol":"P"},{"name":"sulfur","symbol":"S"},
    {"name":"chlorine","symbol":"Cl"},{"name":"argon","symbol":"Ar"},
    {"name":"potassium","symbol":"K"},{"name":"calcium","symbol":"Ca"},
    {"name":"scandium","symbol":"Sc"},{"name":"titanium","symbol":"Ti"},
    {"name":"vanadium","symbol":"V"},{"name":"chromium","symbol":"Cr"},
    {"name":"manganese","symbol":"Mn"},{"name":"iron","symbol":"Fe"},
    {"name":"cobalt","symbol":"Co"},{"name":"nickel","symbol":"Ni"},
    {"name":"copper","symbol":"Cu"},{"name":"zinc","symbol":"Zn"},
    # Remaining elements
    {"name":"gallium","symbol":"Ga"},{"name":"germanium","symbol":"Ge"},
    {"name":"arsenic","symbol":"As"},{"name":"selenium","symbol":"Se"},
    {"name":"bromine","symbol":"Br"},{"name":"krypton","symbol":"Kr"},
    {"name":"rubidium","symbol":"Rb"},{"name":"strontium","symbol":"Sr"},
    {"name":"yttrium","symbol":"Y"},{"name":"zirconium","symbol":"Zr"},
    {"name":"niobium","symbol":"Nb"},{"name":"molybdenum","symbol":"Mo"},
    {"name":"technetium","symbol":"Tc"},{"name":"ruthenium","symbol":"Ru"},
    {"name":"rhodium","symbol":"Rh"},{"name":"palladium","symbol":"Pd"},
    {"name":"silver","symbol":"Ag"},{"name":"cadmium","symbol":"Cd"},
    {"name":"indium","symbol":"In"},{"name":"tin","symbol":"Sn"},
    {"name":"antimony","symbol":"Sb"},{"name":"tellurium","symbol":"Te"},
    {"name":"iodine","symbol":"I"},{"name":"xenon","symbol":"Xe"},
    {"name":"cesium","symbol":"Cs"},{"name":"barium","symbol":"Ba"},
    {"name":"lanthanum","symbol":"La"},{"name":"cerium","symbol":"Ce"},
    {"name":"praseodymium","symbol":"Pr"},{"name":"neodymium","symbol":"Nd"},
    {"name":"promethium","symbol":"Pm"},{"name":"samarium","symbol":"Sm"},
    {"name":"europium","symbol":"Eu"},{"name":"gadolinium","symbol":"Gd"},
    {"name":"terbium","symbol":"Tb"},{"name":"dysprosium","symbol":"Dy"},
    {"name":"holmium","symbol":"Ho"},{"name":"erbium","symbol":"Er"},
    {"name":"thulium","symbol":"Tm"},{"name":"ytterbium","symbol":"Yb"},
    {"name":"lutetium","symbol":"Lu"},{"name":"hafnium","symbol":"Hf"},
    {"name":"tantalum","symbol":"Ta"},{"name":"tungsten","symbol":"W"},
    {"name":"rhenium","symbol":"Re"},{"name":"osmium","symbol":"Os"},
    {"name":"iridium","symbol":"Ir"},{"name":"platinum","symbol":"Pt"},
    {"name":"gold","symbol":"Au"},{"name":"mercury","symbol":"Hg"},
    {"name":"thallium","symbol":"Tl"},{"name":"lead","symbol":"Pb"},
    {"name":"bismuth","symbol":"Bi"},{"name":"polonium","symbol":"Po"},
    {"name":"astatine","symbol":"At"},{"name":"radon","symbol":"Rn"},
    {"name":"francium","symbol":"Fr"},{"name":"radium","symbol":"Ra"},
    {"name":"actinium","symbol":"Ac"},{"name":"thorium","symbol":"Th"},
    {"name":"protactinium","symbol":"Pa"},{"name":"uranium","symbol":"U"},
    {"name":"neptunium","symbol":"Np"},{"name":"plutonium","symbol":"Pu"},
    {"name":"americium","symbol":"Am"},{"name":"curium","symbol":"Cm"},
    {"name":"berkelium","symbol":"Bk"},{"name":"californium","symbol":"Cf"},
    {"name":"einsteinium","symbol":"Es"},{"name":"fermium","symbol":"Fm"},
    {"name":"mendelevium","symbol":"Md"},{"name":"nobelium","symbol":"No"},
    {"name":"lawrencium","symbol":"Lr"},{"name":"rutherfordium","symbol":"Rf"},
    {"name":"dubnium","symbol":"Db"},{"name":"seaborgium","symbol":"Sg"},
    {"name":"bohrium","symbol":"Bh"},{"name":"hassium","symbol":"Hs"},
    {"name":"meitnerium","symbol":"Mt"},{"name":"darmstadtium","symbol":"Ds"},
    {"name":"roentgenium","symbol":"Rg"},{"name":"copernicium","symbol":"Cn"},
    {"name":"nihonium","symbol":"Nh"},{"name":"flerovium","symbol":"Fl"},
    {"name":"moscovium","symbol":"Mc"},{"name":"livermorium","symbol":"Lv"},
    {"name":"tennessine","symbol":"Ts"},{"name":"oganesson","symbol":"Og"},
]
for elem in elements:  # your existing elements array
    filename = os.path.join(save_folder, f"{elem['symbol']}_{elem['name']}.png")
    if os.path.exists(filename):
        continue  # Already downloaded

    name_cap = elem['name'].capitalize()
    url = f"https://periodictableguide.com/{name_cap}-{elem['symbol']}-element-periodic-table/"
    try:
        r = session.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Usually the first <img> is the Bohr model
        img_tag = soup.find("img")
        if img_tag:
            img_url = img_tag['src']
            try:
                img_data = session.get(img_url, timeout=10).content
                with open(filename, 'wb') as f:
                    f.write(img_data)
                print(f"Saved: {filename}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download image for {elem['name']}: {e}")
        else:
            print(f"Bohr image not found for {elem['name']}")

        time.sleep(0.5)  # polite delay

    except requests.exceptions.RequestException as e:
        print(f"Skipping {elem['name']}, error: {e}")
