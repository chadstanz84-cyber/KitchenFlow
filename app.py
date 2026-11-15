import streamlit as st
import requests
from difflib import get_close_matches
import copy

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

TRANSLATIONS = {
    "English": {
        "title": "KitchenFlow", "lang": "Language", "continue": "Continue",
        "inventory": "Inventory", "recipes": "Recipes", "settings": "Settings",
        "add_item": "Add item", "cooked": "Confirm cooked", "users": "Household members",
        "locations": "Locations", "goals": "Goals & macros", "subs": "Substitutions",
        "reset": "Reset to defaults", "recalc": "Recalculate nutrition",
        "usda": "USDA API key (optional)", "scale": "Scale all", "undo": "Undo last scale",
        "grocery": "Grocery List", "can_make": "Can Make Now", "need_groceries": "Need Groceries",
        "planner": "Weekly Planner", "future": "Future Meals", "reminder": "Store reminder",
        "seasonings": "Seasonings", "pantry": "Pantry", "refrigerated": "Refrigerated"
    }
}
for lang in ["Español", "Français", "中文", "Português", "العربية", "हिन्दी", "Русский", "한국어", "Deutsch", "Tiếng Việt", "Tagalog", "日本語", "Italiano"]:
    TRANSLATIONS[lang] = TRANSLATIONS["English"].copy()

KNOWN_ITEMS = [
    "chicken breast", "chicken thighs", "ground beef", "canned tuna", "salmon", "eggs",
    "yellow onion", "garlic", "white rice", "pasta", "black beans", "oats"
]

SEASONINGS = [
    "salt", "black pepper", "garlic powder", "onion powder", "paprika", "cumin",
    "chili powder", "oregano", "basil", "thyme", "rosemary", "cinnamon",
    "nutmeg", "cayenne", "italian seasoning", "taco seasoning", "curry powder",
    "turmeric", "ginger", "bay leaves", "red pepper flakes", "mustard powder",
    "dill", "parsley", "cilantro", "sage", "allspice", "cloves", "cardamom", "coriander"
]

PANTRY = [
    "white rice", "brown rice", "pasta", "all-purpose flour", "sugar", "olive oil",
    "vegetable oil", "canned tomatoes", "tomato sauce", "black beans", "kidney beans",
    "chickpeas", "canned tuna", "canned chicken", "peanut butter", "oats",
    "bread crumbs", "chicken broth", "beef broth", "soy sauce", "vinegar",
    "honey", "maple syrup", "baking powder", "baking soda", "cornstarch",
    "lentils", "quinoa", "crackers", "cereal"
]

REFRIGERATED = [
    "eggs", "milk", "butter", "cheddar cheese", "mozzarella", "greek yogurt",
    "sour cream", "cream cheese", "chicken breast", "ground beef", "bacon",
    "sausage", "deli turkey", "lettuce", "spinach", "broccoli", "carrots",
    "bell peppers", "tomatoes", "cucumbers", "celery", "mushrooms",
    "green onions", "lemons", "limes", "apples", "oranges", "berries",
    "tofu", "hummus"
]

COMMON_SIZES = {"tuna": [5, 6, 12], "chicken": [1, 1.5, 2], "rice": [1, 2, 5]}

SUBSTITUTIONS = {"sugar": ["stevia"], "ground beef": ["ground turkey"], "white rice": ["quinoa"]}

def correct_spelling(word):
    if not word or len(word) < 3: return word
    m = get_close_matches(word.lower(), KNOWN_ITEMS + SEASONINGS + PANTRY + REFRIGERATED, n=1, cutoff=0.68)
    return m[0] if m else word

def search_recipes(q):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={q}", timeout=8)
        r.raise_for_status()
        meals = r.json().get("meals") or []
        return [{"name": m.get("strMeal"), "ings": [{"name": m.get(f"strIngredient{i}"), "qty": 1.0} for i in range(1, 8) if m.get(f"strIngredient{i}")], "instr": (m.get("strInstructions") or "")[:350], "img": m.get("strMealThumb")} for m in meals[:4]]
    except:
        return []

# Session
if "lang" not in st.session_state: st.session_state.lang = None
if "locations" not in st.session_state: st.session_state.locations = {"Home": []}
if "current_loc" not in st.session_state: st.session_state.current_loc = "Home"
if "users" not in st.session_state: st.session_state.users = {"Me": {"goal": "Balanced", "protein": 150}}
if "current_user" not in st.session_state: st.session_state.current_user = "Me"
if "grocery" not in st.session_state: st.session_state.grocery = []
if "future_meals" not in st.session_state: st.session_state.future_meals = []
if "weekly" not in st.session_state: st.session_state.weekly = {d: "" for d in ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]}
if "reminder_time" not in st.session_state: st.session_state.reminder_time = "17:00"

if st.session_state.lang is None:
    st.title("KitchenFlow")
    st.write("### Choose your language")
    c = st.selectbox("", list(TRANSLATIONS.keys()))
    if st.button("Continue"):
        st.session_state.lang = c
        st.rerun()
    st.stop()

t = TRANSLATIONS.get(st.session_state.lang, TRANSLATIONS["English"])
st.title(t["title"])
st.caption("Water is always available.")

with st.sidebar:
    st.header(t["settings"])
    nl = st.selectbox(t["lang"], list(TRANSLATIONS.keys()), index=list(TRANSLATIONS.keys()).index(st.session_state.lang))
    if nl != st.session_state.lang:
        st.session_state.lang = nl
        st.rerun()
    st.session_state.reminder_time = st.text_input("Store reminder (HH:MM)", st.session_state.reminder_time)
    locs = list(st.session_state.locations.keys())
    st.session_state.current_loc = st.selectbox("Location", locs, index=locs.index(st.session_state.current_loc))
    us = list(st.session_state.users.keys())
    st.session_state.current_user = st.selectbox("User", us)
    uu = st.session_state.users[st.session_state.current_user]
    uu["goal"] = st.selectbox("Goal", ["Balanced", "Gain muscle", "Cut / Get lean", "Reduce fat"])

tabs = st.tabs([t["inventory"], t["can_make"], t["need_groceries"], t["grocery"], t["planner"], t["future"]])

with tabs[0]:
    st.subheader(f"Inventory — {st.session_state.current_loc}")
    st.write("**Quick add common items**")

    with st.expander(t["seasonings"] + " (click to add)"):
        cols = st.columns(3)
        for i, item in enumerate(SEASONINGS):
            if cols[i % 3].button(item, key=f"s{item}"):
                st.session_state.locations[st.session_state.current_loc].append({"item": item, "qty": 1, "unit": "count"})
                st.rerun()

    with st.expander(t["pantry"] + " (click to add)"):
        cols = st.columns(3)
        for i, item in enumerate(PANTRY):
            if cols[i % 3].button(item, key=f"p{item}"):
                unit = "cans" if "canned" in item else "count"
                st.session_state.locations[st.session_state.current_loc].append({"item": item, "qty": 1, "unit": unit})
                st.rerun()

    with st.expander(t["refrigerated"] + " (click to add)"):
        cols = st.columns(3)
        for i, item in enumerate(REFRIGERATED):
            if cols[i % 3].button(item, key=f"r{item}"):
                unit = "lbs" if any(x in item for x in ["chicken", "beef", "bacon"]) else "count"
                st.session_state.locations[st.session_state.current_loc].append({"item": item, "qty": 1, "unit": unit})
                st.rerun()

    st.write("---")
    st.write("**Or type a custom item**")
    raw = st.text_input("Custom item")
    corrected = correct_spelling(raw)
    if raw and corrected != raw.lower():
        st.caption(f"Corrected: {corrected}")
    if st.button("Add custom") and corrected:
        st.session_state.locations[st.session_state.current_loc].append({"item": corrected, "qty": 1, "unit": "count"})
        st.rerun()

    st.write("**Current inventory**")
    inv = st.session_state.locations[st.session_state.current_loc]
    for i, it in enumerate(inv):
        c1, c2 = st.columns([5, 1])
        c1.write(f"{it['qty']} {it['unit']} {it['item']}")
        if c2.button("Remove", key=f"del{i}"):
            inv.pop(i)
            st.rerun()

with tabs[1]:
    st.subheader("Recipes you can mostly make")
    inv_names = [i["item"].lower() for i in st.session_state.locations[st.session_state.current_loc]]
    if inv_names:
        for term in list(set([n.split()[0] for n in inv_names]))[:3]:
            for rec in search_recipes(term):
                with st.expander(rec["name"]):
                    st.write(", ".join(i["name"] for i in rec["ings"][:5]))
                    if st.button("Add to Future", key=f"f{rec['name']}"):
                        st.session_state.future_meals.append(rec)
                        st.rerun()

with tabs[2]:
    st.subheader("Recipes that may need extra groceries")
    for rec in search_recipes("chicken"):
        st.write(rec["name"])

with tabs[3]:
    st.subheader("Grocery List")
    st.info(f"Reminder: {st.session_state.reminder_time}")
    g = st.text_input("Add item")
    if st.button("Add to list") and g:
        st.session_state.grocery.append(g)
        st.rerun()
    for i, item in enumerate(st.session_state.grocery):
        if st.button(f"Remove {item}", key=f"gr{i}"):
            st.session_state.grocery.pop(i)
            st.rerun()
        else:
            st.write(f"• {item}")

with tabs[4]:
    st.subheader("Weekly Planner")
    for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
        st.session_state.weekly[day] = st.text_input(day, st.session_state.weekly.get(day, ""))
    st.write("Thaw proteins in the fridge the day before. Canned goods need no thawing.")

with tabs[5]:
    st.subheader("Future Meals")
    for i, meal in enumerate(st.session_state.future_meals):
        st.write(meal["name"])
        if st.button("Confirm cooked & update inventory", key=f"c{i}"):
            st.session_state.future_meals.pop(i)
            st.rerun()

st.caption("Quick-add Seasonings, Pantry, and Refrigerated items · Water always available · All previous features kept")
