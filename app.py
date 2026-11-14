import streamlit as st
import requests

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

TRANSLATIONS = {
    "English": {"title": "KitchenFlow", "lang": "Language", "continue": "Continue", "inventory": "Inventory", "recipes": "Recipes", "settings": "Settings", "add_item": "Add item", "cooked": "I cooked this", "users": "Household members", "locations": "Locations", "goals": "Goals & macros"},
    "Español": {"title": "KitchenFlow", "lang": "Idioma", "continue": "Continuar", "inventory": "Inventario", "recipes": "Recetas", "settings": "Ajustes", "add_item": "Agregar artículo", "cooked": "Cociné esto", "users": "Miembros del hogar", "locations": "Ubicaciones", "goals": "Metas y macros"},
    "Français": {"title": "KitchenFlow", "lang": "Langue", "continue": "Continuer", "inventory": "Inventaire", "recipes": "Recettes", "settings": "Paramètres", "add_item": "Ajouter un article", "cooked": "J’ai cuisiné ceci", "users": "Membres du foyer", "locations": "Emplacements", "goals": "Objectifs et macros"},
    "中文": {"title": "KitchenFlow", "lang": "语言", "continue": "继续", "inventory": "库存", "recipes": "食谱", "settings": "设置", "add_item": "添加物品", "cooked": "我做了这道菜", "users": "家庭成员", "locations": "位置", "goals": "目标和宏量"},
    "Português": {"title": "KitchenFlow", "lang": "Idioma", "continue": "Continuar", "inventory": "Inventário", "recipes": "Receitas", "settings": "Configurações", "add_item": "Adicionar item", "cooked": "Eu cozinhei isto", "users": "Membros da casa", "locations": "Locais", "goals": "Metas e macros"},
    "العربية": {"title": "KitchenFlow", "lang": "اللغة", "continue": "متابعة", "inventory": "المخزون", "recipes": "الوصفات", "settings": "الإعدادات", "add_item": "إضافة عنصر", "cooked": "طبخت هذا", "users": "أفراد الأسرة", "locations": "المواقع", "goals": "الأهداف والماكروز"},
    "हिन्दी": {"title": "KitchenFlow", "lang": "भाषा", "continue": "जारी रखें", "inventory": "इन्वेंटरी", "recipes": "रेसिपी", "settings": "सेटिंग्स", "add_item": "आइटम जोड़ें", "cooked": "मैंने यह पकाया", "users": "घर के सदस्य", "locations": "स्थान", "goals": "लक्ष्य और मैक्रो"},
    "Русский": {"title": "KitchenFlow", "lang": "Язык", "continue": "Продолжить", "inventory": "Запасы", "recipes": "Рецепты", "settings": "Настройки", "add_item": "Добавить", "cooked": "Я приготовил это", "users": "Члены семьи", "locations": "Места", "goals": "Цели и макросы"},
    "한국어": {"title": "KitchenFlow", "lang": "언어", "continue": "계속", "inventory": "재고", "recipes": "레시피", "settings": "설정", "add_item": "항목 추가", "cooked": "이것을 요리했습니다", "users": "가족 구성원", "locations": "위치", "goals": "목표 및 매크로"},
    "Deutsch": {"title": "KitchenFlow", "lang": "Sprache", "continue": "Weiter", "inventory": "Inventar", "recipes": "Rezepte", "settings": "Einstellungen", "add_item": "Artikel hinzufügen", "cooked": "Ich habe das gekocht", "users": "Haushaltsmitglieder", "locations": "Standorte", "goals": "Ziele und Makros"},
    "Tiếng Việt": {"title": "KitchenFlow", "lang": "Ngôn ngữ", "continue": "Tiếp tục", "inventory": "Kho", "recipes": "Công thức", "settings": "Cài đặt", "add_item": "Thêm mục", "cooked": "Tôi đã nấu món này", "users": "Thành viên gia đình", "locations": "Địa điểm", "goals": "Mục tiêu và macro"},
    "Tagalog": {"title": "KitchenFlow", "lang": "Wika", "continue": "Magpatuloy", "inventory": "Imbentaryo", "recipes": "Mga recipe", "settings": "Mga setting", "add_item": "Magdagdag", "cooked": "Niluto ko ito", "users": "Mga miyembro ng bahay", "locations": "Mga lokasyon", "goals": "Mga layunin at macros"},
    "日本語": {"title": "KitchenFlow", "lang": "言語", "continue": "続ける", "inventory": "在庫", "recipes": "レシピ", "settings": "設定", "add_item": "アイテムを追加", "cooked": "これを作りました", "users": "世帯メンバー", "locations": "場所", "goals": "目標とマクロ"},
    "Italiano": {"title": "KitchenFlow", "lang": "Lingua", "continue": "Continua", "inventory": "Inventario", "recipes": "Ricette", "settings": "Impostazioni", "add_item": "Aggiungi elemento", "cooked": "Ho cucinato questo", "users": "Membri della famiglia", "locations": "Luoghi", "goals": "Obiettivi e macro"}
}

ITEM_SUGGESTIONS = {
    "chicken": ["chicken breast", "chicken thighs", "chicken wings", "ground chicken"],
    "beef": ["ground beef", "beef steak"],
    "tuna": ["canned tuna", "fresh tuna", "frozen tuna"],
    "onion": ["yellow onion", "red onion"],
    "milk": ["whole milk", "2% milk", "almond milk"]
}

def guess_unit(name):
    n = name.lower()
    if any(x in n for x in ["milk", "water", "juice", "oil"]): return "gallons"
    if any(x in n for x in ["chicken", "beef", "pork", "fish", "tuna"]): return "lbs"
    if "garlic" in n: return "cloves"
    return "count"

def search_recipes(q):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={q}", timeout=8)
        meals = r.json().get("meals") or []
        out = []
        for m in meals[:6]:
            ings = [{"name": m.get(f"strIngredient{i}", "").strip(), "qty": 1.0} for i in range(1, 12) if m.get(f"strIngredient{i}")]
            out.append({"name": m.get("strMeal"), "ings": ings, "instr": m.get("strInstructions", "")[:500], "img": m.get("strMealThumb")})
        return out
    except:
        return []

# Session
if "lang" not in st.session_state:
    st.session_state.lang = None
if "locations" not in st.session_state:
    st.session_state.locations = {"Home": []}
if "current_loc" not in st.session_state:
    st.session_state.current_loc = "Home"
if "users" not in st.session_state:
    st.session_state.users = {"Me": {"goal": "Balanced", "protein": 150, "calories": 2200}}
if "current_user" not in st.session_state:
    st.session_state.current_user = "Me"

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
    new_lang = st.selectbox(t["lang"], list(TRANSLATIONS.keys()), index=list(TRANSLATIONS.keys()).index(st.session_state.lang))
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.subheader(t["locations"])
    locs = list(st.session_state.locations.keys())
    sel_loc = st.selectbox("Current location", locs, index=locs.index(st.session_state.current_loc))
    if sel_loc != st.session_state.current_loc:
        st.session_state.current_loc = sel_loc
        st.rerun()
    new_loc = st.text_input("Add location")
    if st.button("Add loc") and new_loc and new_loc not in st.session_state.locations:
        st.session_state.locations[new_loc] = []
        st.session_state.current_loc = new_loc
        st.rerun()

    st.subheader(t["users"])
    users = list(st.session_state.users.keys())
    sel_user = st.selectbox("Active user", users, index=users.index(st.session_state.current_user))
    if sel_user != st.session_state.current_user:
        st.session_state.current_user = sel_user
        st.rerun()
    new_user = st.text_input("Add household member")
    if st.button("Add user") and new_user and new_user not in st.session_state.users:
        st.session_state.users[new_user] = {"goal": "Balanced", "protein": 120, "calories": 2000}
        st.session_state.current_user = new_user
        st.rerun()

    st.subheader(t["goals"] + f" — {st.session_state.current_user}")
    u = st.session_state.users[st.session_state.current_user]
    u["goal"] = st.selectbox("Goal", ["Balanced", "Gain muscle", "Cut / Get lean", "Reduce fat", "Heart health"], index=0)
    u["protein"] = st.number_input("Daily protein target (g)", 50, 300, u.get("protein", 150))
    u["calories"] = st.number_input("Daily calorie target", 1200, 5000, u.get("calories", 2200))

tab_inv, tab_rec = st.tabs([t["inventory"], t["recipes"]])

with tab_inv:
    st.subheader(f"{t['inventory']} — {st.session_state.current_loc}")
    raw = st.text_input("Type item")
    suggestions = []
    for k, opts in ITEM_SUGGESTIONS.items():
        if k in raw.lower():
            suggestions = opts
            break
    selected = st.selectbox("Exact item", suggestions) if suggestions else raw
    unit_guess = guess_unit(selected)
    units = ["lbs", "count", "cups", "oz", "cloves", "gallons", "cans"]
    c1, c2 = st.columns(2)
    qty = c1.number_input("Quantity", 0.0, 100.0, 1.0, 0.5)
    unit = c2.selectbox("Unit", units, index=units.index(unit_guess) if unit_guess in units else 0)
    if st.button(t["add_item"]) and selected:
        st.session_state.locations[st.session_state.current_loc].append({"item": selected, "qty": qty, "unit": unit})
        st.rerun()

    inv = st.session_state.locations[st.session_state.current_loc]
    for i, it in enumerate(inv):
        cols = st.columns([4, 1.5, 1])
        cols[0].write(f"**{it['item']}**")
        newq = cols[1].number_input("qty", value=float(it["qty"]), key=f"q{i}", label_visibility="collapsed")
        if cols[2].button("Remove", key=f"r{i}"):
            inv.pop(i)
            st.rerun()
        if newq != it["qty"]:
            inv[i]["qty"] = newq
            st.rerun()

with tab_rec:
    st.subheader(f"Recipes for {st.session_state.current_user} using {st.session_state.current_loc} inventory")
    st.caption(f"Goal: {st.session_state.users[st.session_state.current_user]['goal']} · Protein target ~{st.session_state.users[st.session_state.current_user]['protein']}g")
    q = st.text_input("Search recipes")
    if q:
        recs = search_recipes(q)
        for rec in recs:
            with st.expander(rec["name"]):
                if rec["img"]:
                    st.image(rec["img"], width=200)
                st.write(rec["instr"])
                if st.button(t["cooked"], key=rec["name"]):
                    # Simple inventory reduction
                    for ing in rec["ings"]:
                        for item in inv:
                            if ing["name"].lower() in item["item"].lower() or item["item"].lower() in ing["name"].lower():
                                item["qty"] = max(0, item["qty"] - 0.5)
                    st.success("Inventory updated for items used.")
                    st.rerun()

st.caption("Language on start · Multiple users & locations · Inventory updates when you cook · Goals in settings")
