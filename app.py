import streamlit as st
import requests
from difflib import get_close_matches

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

TRANSLATIONS = {
    "English": {"title": "KitchenFlow", "lang": "Language", "continue": "Continue", "inventory": "Inventory", "recipes": "Recipes", "settings": "Settings", "add_item": "Add item", "cooked": "I cooked this", "users": "Household members", "locations": "Locations", "goals": "Goals & macros", "subs": "Substitutions", "reset": "Reset to defaults", "recalc": "Recalculate nutrition", "usda": "USDA API key (optional)"},
    "Español": {"title": "KitchenFlow", "lang": "Idioma", "continue": "Continuar", "inventory": "Inventario", "recipes": "Recetas", "settings": "Ajustes", "add_item": "Agregar", "cooked": "Cociné esto", "users": "Miembros", "locations": "Ubicaciones", "goals": "Metas", "subs": "Sustituciones", "reset": "Restablecer", "recalc": "Recalcular", "usda": "Clave USDA (opcional)"},
    "Français": {"title": "KitchenFlow", "lang": "Langue", "continue": "Continuer", "inventory": "Inventaire", "recipes": "Recettes", "settings": "Paramètres", "add_item": "Ajouter", "cooked": "Cuisiné", "users": "Membres", "locations": "Emplacements", "goals": "Objectifs", "subs": "Substitutions", "reset": "Réinitialiser", "recalc": "Recalculer", "usda": "Clé USDA (optionnel)"},
    "中文": {"title": "KitchenFlow", "lang": "语言", "continue": "继续", "inventory": "库存", "recipes": "食谱", "settings": "设置", "add_item": "添加", "cooked": "已做", "users": "成员", "locations": "位置", "goals": "目标", "subs": "替代", "reset": "重置", "recalc": "重新计算", "usda": "USDA 密钥（可选）"},
    "Português": {"title": "KitchenFlow", "lang": "Idioma", "continue": "Continuar", "inventory": "Inventário", "recipes": "Receitas", "settings": "Configurações", "add_item": "Adicionar", "cooked": "Cozinhei", "users": "Membros", "locations": "Locais", "goals": "Metas", "subs": "Substituições", "reset": "Redefinir", "recalc": "Recalcular", "usda": "Chave USDA (opcional)"},
    "العربية": {"title": "KitchenFlow", "lang": "اللغة", "continue": "متابعة", "inventory": "المخزون", "recipes": "وصفات", "settings": "إعدادات", "add_item": "إضافة", "cooked": "طبخت", "users": "أعضاء", "locations": "مواقع", "goals": "أهداف", "subs": "بدائل", "reset": "إعادة تعيين", "recalc": "إعادة الحساب", "usda": "مفتاح USDA (اختياري)"},
    "हिन्दी": {"title": "KitchenFlow", "lang": "भाषा", "continue": "जारी", "inventory": "इन्वेंटरी", "recipes": "रेसिपी", "settings": "सेटिंग्स", "add_item": "जोड़ें", "cooked": "पकाया", "users": "सदस्य", "locations": "स्थान", "goals": "लक्ष्य", "subs": "विकल्प", "reset": "रीसेट", "recalc": "पुनर्गणना", "usda": "USDA कुंजी (वैकल्पिक)"},
    "Русский": {"title": "KitchenFlow", "lang": "Язык", "continue": "Продолжить", "inventory": "Запасы", "recipes": "Рецепты", "settings": "Настройки", "add_item": "Добавить", "cooked": "Приготовил", "users": "Члены", "locations": "Места", "goals": "Цели", "subs": "Замены", "reset": "Сброс", "recalc": "Пересчитать", "usda": "Ключ USDA (необяз.)"},
    "한국어": {"title": "KitchenFlow", "lang": "언어", "continue": "계속", "inventory": "재고", "recipes": "레시피", "settings": "설정", "add_item": "추가", "cooked": "요리함", "users": "구성원", "locations": "위치", "goals": "목표", "subs": "대체", "reset": "초기화", "recalc": "재계산", "usda": "USDA 키 (선택)"},
    "Deutsch": {"title": "KitchenFlow", "lang": "Sprache", "continue": "Weiter", "inventory": "Inventar", "recipes": "Rezepte", "settings": "Einstellungen", "add_item": "Hinzufügen", "cooked": "Gekocht", "users": "Mitglieder", "locations": "Orte", "goals": "Ziele", "subs": "Ersatz", "reset": "Zurücksetzen", "recalc": "Neu berechnen", "usda": "USDA-Schlüssel (optional)"},
    "Tiếng Việt": {"title": "KitchenFlow", "lang": "Ngôn ngữ", "continue": "Tiếp", "inventory": "Kho", "recipes": "Công thức", "settings": "Cài đặt", "add_item": "Thêm", "cooked": "Đã nấu", "users": "Thành viên", "locations": "Địa điểm", "goals": "Mục tiêu", "subs": "Thay thế", "reset": "Đặt lại", "recalc": "Tính lại", "usda": "Khóa USDA (tùy chọn)"},
    "Tagalog": {"title": "KitchenFlow", "lang": "Wika", "continue": "Magpatuloy", "inventory": "Imbentaryo", "recipes": "Recipe", "settings": "Setting", "add_item": "Magdagdag", "cooked": "Niluto", "users": "Miyembro", "locations": "Lokasyon", "goals": "Layunin", "subs": "Kapalit", "reset": "I-reset", "recalc": "Kalkulahin muli", "usda": "USDA key (opsyonal)"},
    "日本語": {"title": "KitchenFlow", "lang": "言語", "continue": "続ける", "inventory": "在庫", "recipes": "レシピ", "settings": "設定", "add_item": "追加", "cooked": "作った", "users": "メンバー", "locations": "場所", "goals": "目標", "subs": "代替", "reset": "リセット", "recalc": "再計算", "usda": "USDAキー（任意）"},
    "Italiano": {"title": "KitchenFlow", "lang": "Lingua", "continue": "Continua", "inventory": "Inventario", "recipes": "Ricette", "settings": "Impostazioni", "add_item": "Aggiungi", "cooked": "Cucinato", "users": "Membri", "locations": "Luoghi", "goals": "Obiettivi", "subs": "Sostituzioni", "reset": "Ripristina", "recalc": "Ricalcola", "usda": "Chiave USDA (opzionale)"}
}

KNOWN_ITEMS = [
    "chicken breast", "chicken thighs", "chicken wings", "ground chicken", "whole chicken",
    "ground beef", "beef steak", "beef roast", "canned tuna", "fresh tuna", "frozen tuna", "salmon", "cod",
    "yellow onion", "red onion", "white onion", "garlic", "shallot",
    "whole milk", "2% milk", "skim milk", "almond milk", "oat milk",
    "white rice", "brown rice", "jasmine rice", "quinoa", "pasta", "chickpea pasta",
    "all-purpose flour", "almond flour", "oat flour", "sugar", "brown sugar",
    "butter", "olive oil", "avocado oil", "eggs", "egg whites",
    "broccoli", "spinach", "kale", "bell pepper", "tomato", "tomato sauce", "black beans", "chickpeas",
    "oats", "greek yogurt", "cheddar cheese", "mozzarella", "bread", "tortilla"
]

COMMON_SIZES = {
    "tuna": [5, 6, 12], "chicken": [1, 1.5, 2, 3], "beef": [1, 1.5, 2],
    "milk": [0.5, 1], "rice": [1, 2, 5], "pasta": [12, 16], "sugar": [1, 2, 4], "flour": [2, 5]
}

SUBSTITUTIONS = {
    "sugar": ["stevia", "monk fruit", "erythritol"],
    "all-purpose flour": ["almond flour", "oat flour", "gluten-free blend"],
    "butter": ["olive oil", "avocado oil"],
    "ground beef": ["ground turkey", "ground chicken", "lentils"],
    "white rice": ["cauliflower rice", "quinoa", "brown rice"],
    "whole milk": ["almond milk", "oat milk", "2% milk"],
    "pasta": ["chickpea pasta", "zucchini noodles", "whole wheat pasta"],
    "soy sauce": ["coconut aminos", "low-sodium soy sauce"],
    "bread": ["lettuce wraps", "gluten-free bread"]
}

ITEM_SUGGESTIONS = {
    "chicken": ["chicken breast", "chicken thighs", "chicken wings", "ground chicken", "whole chicken"],
    "beef": ["ground beef", "beef steak", "beef roast"],
    "tuna": ["canned tuna", "fresh tuna", "frozen tuna"],
    "onion": ["yellow onion", "red onion", "white onion"],
    "milk": ["whole milk", "2% milk", "almond milk", "oat milk"],
    "rice": ["white rice", "brown rice", "jasmine rice"]
}

def correct_spelling(word):
    if not word or len(word) < 3: return word
    matches = get_close_matches(word.lower(), KNOWN_ITEMS, n=1, cutoff=0.68)
    return matches[0] if matches else word

def advanced_fuzzy(ingredient, custom_subs):
    low = ingredient.lower().strip()
    if low in custom_subs: return custom_subs[low]
    if low in SUBSTITUTIONS: return SUBSTITUTIONS[low][0]
    all_keys = list(set(list(SUBSTITUTIONS.keys()) + list(custom_subs.keys()) + KNOWN_ITEMS))
    matches = get_close_matches(low, all_keys, n=1, cutoff=0.58)
    if matches:
        return custom_subs.get(matches[0]) or SUBSTITUTIONS.get(matches[0], [None])[0]
    for key in all_keys:
        if any(t in low for t in key.split() if len(t) > 3):
            return custom_subs.get(key) or SUBSTITUTIONS.get(key, [None])[0]
    return None

def guess_unit(name):
    n = name.lower()
    if any(x in n for x in ["milk", "water", "juice", "oil"]): return "gallons"
    if any(x in n for x in ["chicken", "beef", "tuna", "salmon", "fish", "pork"]): return "lbs"
    if "garlic" in n: return "cloves"
    return "count"

def get_common_sizes(item):
    for k, sizes in COMMON_SIZES.items():
        if k in item.lower(): return sizes
    return [1]

def usda_nutrition(query, api_key):
    if not api_key:
        return None
    try:
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {"query": query, "api_key": api_key, "pageSize": 1}
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        foods = r.json().get("foods", [])
        if not foods:
            return None
        food = foods[0]
        nutrients = {n["nutrientName"]: n.get("value", 0) for n in food.get("foodNutrients", [])}
        return {
            "calories": nutrients.get("Energy", 0),
            "protein": nutrients.get("Protein", 0),
            "carbs": nutrients.get("Carbohydrate, by difference", 0),
            "fat": nutrients.get("Total lipid (fat)", 0)
        }
    except:
        return None

def estimate_nutrition(ingredients, servings=4, usda_key=None):
    total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    used_usda = False
    for ing in ingredients:
        name = ing.get("name", "")
        qty = ing.get("qty", 1)
        usda = usda_nutrition(name, usda_key) if usda_key else None
        if usda:
            used_usda = True
            for k in total:
                total[k] += usda.get(k, 0) * qty * 0.3  # rough per-serving scaling
        else:
            # Fallback estimate
            total["calories"] += 80 * qty
            total["protein"] += 6 * qty
            total["carbs"] += 8 * qty
            total["fat"] += 3 * qty
    scale = servings / 4.0
    result = {k: int(v * scale) for k, v in total.items()}
    result["source"] = "USDA" if used_usda else "estimate"
    return result

def search_recipes(q):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={q}", timeout=10)
        r.raise_for_status()
        meals = r.json().get("meals") or []
        return [{"name": m.get("strMeal"), "ings": [{"name": m.get(f"strIngredient{i}"), "qty": 1.0} for i in range(1, 12) if m.get(f"strIngredient{i}")], "instr": m.get("strInstructions", "")[:500], "img": m.get("strMealThumb")} for m in meals[:8]]
    except requests.RequestException as e:
        st.error(f"Could not load recipes: {e}")
        return []
    except Exception:
        st.error("Unexpected error loading recipes.")
        return []

# Session
if "lang" not in st.session_state: st.session_state.lang = None
if "locations" not in st.session_state: st.session_state.locations = {"Home": []}
if "current_loc" not in st.session_state: st.session_state.current_loc = "Home"
if "users" not in st.session_state: st.session_state.users = {"Me": {"goal": "Balanced", "protein": 150}}
if "current_user" not in st.session_state: st.session_state.current_user = "Me"
if "custom_subs" not in st.session_state: st.session_state.custom_subs = {}
if "edited_recipes" not in st.session_state: st.session_state.edited_recipes = {}
if "usda_key" not in st.session_state: st.session_state.usda_key = ""

if st.session_state.lang is None:
    st.title("KitchenFlow")
    st.write("### Choose your language")
    choice = st.selectbox("", list(TRANSLATIONS.keys()))
    if st.button("Continue"):
        st.session_state.lang = choice
        st.rerun()
    st.stop()

t = TRANSLATIONS.get(st.session_state.lang, TRANSLATIONS["English"])
st.title(t["title"])

with st.sidebar:
    st.header(t["settings"])
    nl = st.selectbox(t["lang"], list(TRANSLATIONS.keys()), index=list(TRANSLATIONS.keys()).index(st.session_state.lang))
    if nl != st.session_state.lang:
        st.session_state.lang = nl
        st.rerun()

    st.subheader(t["usda"])
    key_input = st.text_input("Paste free USDA key", value=st.session_state.usda_key, type="password")
    if st.button("Save key"):
        st.session_state.usda_key = key_input.strip()
        st.success("Key saved for this session.")

    st.subheader(t["locations"])
    locs = list(st.session_state.locations.keys())
    sl = st.selectbox("Location", locs, index=locs.index(st.session_state.current_loc))
    if sl != st.session_state.current_loc:
        st.session_state.current_loc = sl
        st.rerun()
    nloc = st.text_input("New location")
    if st.button("Add location") and nloc and nloc not in st.session_state.locations:
        st.session_state.locations[nloc] = []
        st.session_state.current_loc = nloc
        st.rerun()

    st.subheader(t["users"])
    us = list(st.session_state.users.keys())
    su = st.selectbox("User", us, index=us.index(st.session_state.current_user))
    if su != st.session_state.current_user:
        st.session_state.current_user = su
        st.rerun()
    nu = st.text_input("New member")
    if st.button("Add member") and nu and nu not in st.session_state.users:
        st.session_state.users[nu] = {"goal": "Balanced", "protein": 120}
        st.session_state.current_user = nu
        st.rerun()

    st.subheader(t["goals"])
    uu = st.session_state.users[st.session_state.current_user]
    uu["goal"] = st.selectbox("Goal", ["Balanced", "Gain muscle", "Cut / Get lean", "Reduce fat", "Gluten-free", "Heart health", "Keto"])
    uu["protein"] = st.number_input("Protein target (g)", 40, 350, uu.get("protein", 150))

    st.subheader(t["subs"])
    sf = st.text_input("Instead of")
    stt = st.text_input("Always use")
    if st.button("Save substitution") and sf and stt:
        st.session_state.custom_subs[sf.lower()] = stt
        st.rerun()

    if st.button(t["reset"] + " subs"):
        st.session_state.custom_subs = {}
        st.rerun()
    if st.button(t["reset"] + " goals"):
        st.session_state.users[st.session_state.current_user] = {"goal": "Balanced", "protein": 150}
        st.rerun()

tab1, tab2 = st.tabs([t["inventory"], t["recipes"]])

with tab1:
    st.subheader(f"{t['inventory']} — {st.session_state.current_loc}")
    raw = st.text_input("Type item")
    corrected = correct_spelling(raw)
    if raw and corrected != raw.lower():
        st.caption(f"Corrected to: **{corrected}**")
    suggestions = []
    for k, opts in ITEM_SUGGESTIONS.items():
        if k in corrected: suggestions = opts; break
    selected = st.selectbox("Exact item", suggestions or [corrected]) if corrected else ""
    sizes = get_common_sizes(selected)
    unit_guess = guess_unit(selected)
    units = ["lbs", "oz", "count", "cups", "cans", "cloves", "gallons"]
    c1, c2 = st.columns(2)
    qty = c1.number_input("Quantity", 0.1, 100.0, float(sizes[0]), 0.1)
    unit = c2.selectbox("Unit", units, index=units.index(unit_guess) if unit_guess in units else 0)
    if st.button(t["add_item"]) and selected:
        st.session_state.locations[st.session_state.current_loc].append({"item": selected, "qty": qty, "unit": unit})
        st.rerun()

    for i, it in enumerate(st.session_state.locations[st.session_state.current_loc]):
        cols = st.columns([4, 1.5, 1])
        cols[0].write(f"**{it['item']}**")
        nq = cols[1].number_input(" ", value=float(it["qty"]), key=f"iq{i}", label_visibility="collapsed")
        if cols[2].button("Remove", key=f"rm{i}"):
            st.session_state.locations[st.session_state.current_loc].pop(i)
            st.rerun()
        if nq != it["qty"]:
            st.session_state.locations[st.session_state.current_loc][i]["qty"] = nq
            st.rerun()

with tab2:
    st.subheader("Recipes")
    q = st.text_input("Search")
    if q:
        results = search_recipes(q)
        for rec in results:
            with st.expander(rec["name"]):
                if rec["img"]: st.image(rec["img"], width=200)
                st.write("**Edit ingredients**")
                edited = st.session_state.edited_recipes.get(rec["name"], rec["ings"])
                new_ings = []
                for i, ing in enumerate(edited):
                    c1, c2 = st.columns([3, 1])
                    name = c1.text_input("Ingredient", value=ing.get("name", ""), key=f"n{rec['name']}{i}")
                    qty = c2.number_input("Qty", value=float(ing.get("qty", 1)), key=f"q{rec['name']}{i}", step=0.25)
                    if name:
                        new_ings.append({"name": name, "qty": qty})
                        sub = advanced_fuzzy(name, st.session_state.custom_subs)
                        if sub: st.caption(f"Suggested: {sub}")
                add_name = st.text_input("Add ingredient", key=f"add{rec['name']}")
                if add_name:
                    new_ings.append({"name": add_name, "qty": 1.0})
                st.session_state.edited_recipes[rec["name"]] = new_ings

                servings = st.number_input("Servings", 1, 12, 4, key=f"s{rec['name']}")
                if st.button(t["recalc"], key=f"rc{rec['name']}"):
                    nut = estimate_nutrition(new_ings, servings, st.session_state.usda_key)
                    source = nut.pop("source", "estimate")
                    st.success(f"Nutrition ({source}):")
                    st.write(f"Calories ~{nut['calories']} · Protein ~{nut['protein']}g · Carbs ~{nut['carbs']}g · Fat ~{nut['fat']}g")
                    if source == "estimate":
                        st.caption("Add a free USDA API key in settings for more accurate values.")

                st.write("**Instructions**")
                st.write(rec["instr"])

st.caption("USDA integration (optional key) · Expanded ingredients · Stronger fuzzy matching · Editable recipes with recalculated nutrition")
