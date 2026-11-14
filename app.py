import streamlit as st
import requests
from difflib import get_close_matches

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

TRANSLATIONS = {
    "English": {"title": "KitchenFlow", "lang": "Language", "continue": "Continue", "inventory": "Inventory", "recipes": "Recipes", "settings": "Settings", "add_item": "Add item", "cooked": "I cooked this", "users": "Household members", "locations": "Locations", "goals": "Goals & macros", "subs": "Substitutions", "reset": "Reset to defaults"},
    "Español": {"title": "KitchenFlow", "lang": "Idioma", "continue": "Continuar", "inventory": "Inventario", "recipes": "Recetas", "settings": "Ajustes", "add_item": "Agregar", "cooked": "Cociné esto", "users": "Miembros", "locations": "Ubicaciones", "goals": "Metas", "subs": "Sustituciones", "reset": "Restablecer"},
    "Français": {"title": "KitchenFlow", "lang": "Langue", "continue": "Continuer", "inventory": "Inventaire", "recipes": "Recettes", "settings": "Paramètres", "add_item": "Ajouter", "cooked": "Cuisiné", "users": "Membres", "locations": "Emplacements", "goals": "Objectifs", "subs": "Substitutions", "reset": "Réinitialiser"},
    "中文": {"title": "KitchenFlow", "lang": "语言", "continue": "继续", "inventory": "库存", "recipes": "食谱", "settings": "设置", "add_item": "添加", "cooked": "已做", "users": "成员", "locations": "位置", "goals": "目标", "subs": "替代", "reset": "重置"},
    "Português": {"title": "KitchenFlow", "lang": "Idioma", "continue": "Continuar", "inventory": "Inventário", "recipes": "Receitas", "settings": "Configurações", "add_item": "Adicionar", "cooked": "Cozinhei", "users": "Membros", "locations": "Locais", "goals": "Metas", "subs": "Substituições", "reset": "Redefinir"},
    "العربية": {"title": "KitchenFlow", "lang": "اللغة", "continue": "متابعة", "inventory": "المخزون", "recipes": "وصفات", "settings": "إعدادات", "add_item": "إضافة", "cooked": "طبخت", "users": "أعضاء", "locations": "مواقع", "goals": "أهداف", "subs": "بدائل", "reset": "إعادة تعيين"},
    "हिन्दी": {"title": "KitchenFlow", "lang": "भाषा", "continue": "जारी", "inventory": "इन्वेंटरी", "recipes": "रेसिपी", "settings": "सेटिंग्स", "add_item": "जोड़ें", "cooked": "पकाया", "users": "सदस्य", "locations": "स्थान", "goals": "लक्ष्य", "subs": "विकल्प", "reset": "रीसेट"},
    "Русский": {"title": "KitchenFlow", "lang": "Язык", "continue": "Продолжить", "inventory": "Запасы", "recipes": "Рецепты", "settings": "Настройки", "add_item": "Добавить", "cooked": "Приготовил", "users": "Члены", "locations": "Места", "goals": "Цели", "subs": "Замены", "reset": "Сброс"},
    "한국어": {"title": "KitchenFlow", "lang": "언어", "continue": "계속", "inventory": "재고", "recipes": "레시피", "settings": "설정", "add_item": "추가", "cooked": "요리함", "users": "구성원", "locations": "위치", "goals": "목표", "subs": "대체", "reset": "초기화"},
    "Deutsch": {"title": "KitchenFlow", "lang": "Sprache", "continue": "Weiter", "inventory": "Inventar", "recipes": "Rezepte", "settings": "Einstellungen", "add_item": "Hinzufügen", "cooked": "Gekocht", "users": "Mitglieder", "locations": "Orte", "goals": "Ziele", "subs": "Ersatz", "reset": "Zurücksetzen"},
    "Tiếng Việt": {"title": "KitchenFlow", "lang": "Ngôn ngữ", "continue": "Tiếp", "inventory": "Kho", "recipes": "Công thức", "settings": "Cài đặt", "add_item": "Thêm", "cooked": "Đã nấu", "users": "Thành viên", "locations": "Địa điểm", "goals": "Mục tiêu", "subs": "Thay thế", "reset": "Đặt lại"},
    "Tagalog": {"title": "KitchenFlow", "lang": "Wika", "continue": "Magpatuloy", "inventory": "Imbentaryo", "recipes": "Recipe", "settings": "Setting", "add_item": "Magdagdag", "cooked": "Niluto", "users": "Miyembro", "locations": "Lokasyon", "goals": "Layunin", "subs": "Kapalit", "reset": "I-reset"},
    "日本語": {"title": "KitchenFlow", "lang": "言語", "continue": "続ける", "inventory": "在庫", "recipes": "レシピ", "settings": "設定", "add_item": "追加", "cooked": "作った", "users": "メンバー", "locations": "場所", "goals": "目標", "subs": "代替", "reset": "リセット"},
    "Italiano": {"title": "KitchenFlow", "lang": "Lingua", "continue": "Continua", "inventory": "Inventario", "recipes": "Ricette", "settings": "Impostazioni", "add_item": "Aggiungi", "cooked": "Cucinato", "users": "Membri", "locations": "Luoghi", "goals": "Obiettivi", "subs": "Sostituzioni", "reset": "Ripristina"}
}

KNOWN_ITEMS = [
    "chicken breast", "chicken thighs", "chicken wings", "ground chicken", "ground beef", "beef steak",
    "canned tuna", "fresh tuna", "frozen tuna", "salmon", "yellow onion", "red onion", "garlic",
    "whole milk", "2% milk", "almond milk", "white rice", "brown rice", "pasta", "all-purpose flour",
    "sugar", "butter", "olive oil", "eggs", "broccoli", "spinach", "bell pepper", "tomato sauce",
    "black beans", "quinoa", "oats", "greek yogurt", "cheddar cheese"
]

COMMON_SIZES = {
    "canned tuna": [5, 6, 12], "chicken breast": [1, 1.5, 2, 3], "ground beef": [1, 1.5, 2],
    "milk": [0.5, 1], "rice": [1, 2, 5], "pasta": [12, 16], "sugar": [1, 2, 4], "flour": [2, 5], "butter": [1, 2]
}

SUBSTITUTIONS = {
    "sugar": ["stevia", "monk fruit", "erythritol"],
    "all-purpose flour": ["almond flour", "oat flour", "gluten-free flour blend"],
    "butter": ["olive oil", "avocado oil"],
    "ground beef": ["ground turkey", "ground chicken", "lentils"],
    "white rice": ["cauliflower rice", "quinoa", "brown rice"],
    "whole milk": ["almond milk", "oat milk"],
    "pasta": ["chickpea pasta", "zucchini noodles"],
    "soy sauce": ["coconut aminos", "low-sodium soy sauce"]
}

ITEM_SUGGESTIONS = {
    "chicken": ["chicken breast", "chicken thighs", "chicken wings", "ground chicken"],
    "beef": ["ground beef", "beef steak"],
    "tuna": ["canned tuna", "fresh tuna", "frozen tuna"],
    "onion": ["yellow onion", "red onion"],
    "milk": ["whole milk", "2% milk", "almond milk"]
}

def correct_spelling(word):
    if not word or len(word) < 3: return word
    matches = get_close_matches(word.lower(), KNOWN_ITEMS, n=1, cutoff=0.72)
    return matches[0] if matches else word

def guess_unit(name):
    n = name.lower()
    if any(x in n for x in ["milk", "water", "juice", "oil"]): return "gallons"
    if any(x in n for x in ["chicken", "beef", "pork", "tuna", "salmon"]): return "lbs"
    if "garlic" in n: return "cloves"
    return "count"

def get_common_sizes(item):
    for k, sizes in COMMON_SIZES.items():
        if k in item.lower(): return sizes
    return [1, 2]

def fuzzy_sub(ingredient, custom_subs):
    low = ingredient.lower()
    if low in custom_subs: return custom_subs[low]
    if low in SUBSTITUTIONS: return SUBSTITUTIONS[low][0]
    # Fuzzy match against known substitution keys
    keys = list(SUBSTITUTIONS.keys()) + list(custom_subs.keys())
    matches = get_close_matches(low, keys, n=1, cutoff=0.65)
    if matches:
        key = matches[0]
        return custom_subs.get(key) or SUBSTITUTIONS.get(key, [None])[0]
    return None

def convert_unit(qty, from_unit, to_unit):
    # Simple practical conversions
    conversions = {
        ("oz", "lbs"): 1/16, ("lbs", "oz"): 16,
        ("cups", "ml"): 236.6, ("ml", "cups"): 1/236.6,
        ("tbsp", "tsp"): 3, ("tsp", "tbsp"): 1/3
    }
    factor = conversions.get((from_unit.lower(), to_unit.lower()))
    return round(qty * factor, 2) if factor else None

def search_recipes(q):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={q}", timeout=8)
        meals = r.json().get("meals") or []
        return [{"name": m.get("strMeal"), "ings": [m.get(f"strIngredient{i}") for i in range(1,12) if m.get(f"strIngredient{i}")], "instr": m.get("strInstructions","")[:450], "img": m.get("strMealThumb")} for m in meals[:6]]
    except:
        return []

# Session
if "lang" not in st.session_state: st.session_state.lang = None
if "locations" not in st.session_state: st.session_state.locations = {"Home": []}
if "current_loc" not in st.session_state: st.session_state.current_loc = "Home"
if "users" not in st.session_state: st.session_state.users = {"Me": {"goal": "Balanced", "protein": 150}}
if "current_user" not in st.session_state: st.session_state.current_user = "Me"
if "custom_subs" not in st.session_state: st.session_state.custom_subs = {}

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

    st.subheader(t["reset"])
    if st.button("Clear my custom substitutions"):
        st.session_state.custom_subs = {}
        st.rerun()
    if st.button("Reset this user's goals"):
        st.session_state.users[st.session_state.current_user] = {"goal": "Balanced", "protein": 150}
        st.rerun()

tab1, tab2 = st.tabs([t["inventory"], t["recipes"]])

with tab1:
    st.subheader(f"{t['inventory']} — {st.session_state.current_loc}")
    raw = st.text_input("Type item (spell check active)")
    corrected = correct_spelling(raw)
    if corrected != raw.lower() and raw:
        st.caption(f"Corrected to: **{corrected}**")

    suggestions = []
    for k, opts in ITEM_SUGGESTIONS.items():
        if k in corrected: suggestions = opts; break
    selected = st.selectbox("Exact item", suggestions or [corrected]) if (suggestions or corrected) else corrected

    sizes = get_common_sizes(selected)
    unit_guess = guess_unit(selected)
    units = ["lbs", "oz", "count", "cups", "cans", "cloves", "gallons"]
    c1, c2, c3 = st.columns(3)
    size_choice = c1.selectbox("Common size", [f"{s}" for s in sizes] + ["Custom"])
    qty = c2.number_input("Quantity", 0.1, 100.0, float(sizes[0]) if size_choice != "Custom" else 1.0, 0.1)
    unit = c3.selectbox("Unit", units, index=units.index(unit_guess) if unit_guess in units else 0)

    if st.button(t["add_item"], use_container_width=True) and selected:
        st.session_state.locations[st.session_state.current_loc].append({"item": selected, "qty": qty, "unit": unit})
        st.rerun()

    inv = st.session_state.locations[st.session_state.current_loc]
    for i, it in enumerate(inv):
        cols = st.columns([3.5, 1.5, 1.2, 1])
        cols[0].write(f"**{it['item']}**")
        nq = cols[1].number_input(" ", value=float(it["qty"]), key=f"iq{i}", step=0.1, label_visibility="collapsed")
        # Simple conversion display
        if it["unit"] == "oz":
            cols[2].caption(f"≈ {convert_unit(it['qty'], 'oz', 'lbs')} lbs")
        elif it["unit"] == "lbs":
            cols[2].caption(f"≈ {convert_unit(it['qty'], 'lbs', 'oz')} oz")
        else:
            cols[2].write("")
        if cols[3].button("Remove", key=f"rm{i}"):
            inv.pop(i)
            st.rerun()
        if nq != it["qty"]:
            inv[i]["qty"] = nq
            st.rerun()

with tab2:
    st.subheader(f"Recipes — {st.session_state.current_user}")
    q = st.text_input("Search")
    if q:
        for rec in search_recipes(q):
            with st.expander(rec["name"]):
                if rec["img"]: st.image(rec["img"], width=180)
                st.write("**Ingredients**")
                for ing in rec["ings"]:
                    if not ing: continue
                    sub = fuzzy_sub(ing, st.session_state.custom_subs)
                    extra = f" → try **{sub}**" if sub else ""
                    st.write(f"• {ing}{extra}")
                st.write(rec["instr"])
                if st.button(t["cooked"], key=rec["name"]):
                    st.success("Marked as cooked.")

st.caption("Fuzzy substitutions · Unit conversion · Reset to defaults · TheMealDB recipe search")
