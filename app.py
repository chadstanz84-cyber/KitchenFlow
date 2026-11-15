import streamlit as st
import requests
from difflib import get_close_matches
import copy
from datetime import datetime, timedelta

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
        "planner": "Weekly Planner", "future": "Future Meals", "reminder": "Store reminder"
    }
}

# (Other languages kept short for space — English is primary; expand as needed)
for lang in ["Español", "Français", "中文", "Português", "العربية", "हिन्दी", "Русский", "한국어", "Deutsch", "Tiếng Việt", "Tagalog", "日本語", "Italiano"]:
    TRANSLATIONS[lang] = TRANSLATIONS["English"].copy()

KNOWN_ITEMS = [
    "chicken breast", "chicken thighs", "ground chicken", "ground beef", "canned tuna", "salmon",
    "yellow onion", "garlic", "whole milk", "white rice", "brown rice", "pasta", "eggs",
    "broccoli", "spinach", "bell pepper", "tomato sauce", "black beans", "oats", "greek yogurt"
]

COMMON_SIZES = {"tuna": [5, 6, 12], "chicken": [1, 1.5, 2], "beef": [1, 1.5, 2], "rice": [1, 2, 5]}

SUBSTITUTIONS = {
    "sugar": ["stevia"], "ground beef": ["ground turkey"], "white rice": ["cauliflower rice", "quinoa"],
    "whole milk": ["almond milk"], "pasta": ["chickpea pasta"]
}

ITEM_SUGGESTIONS = {
    "chicken": ["chicken breast", "chicken thighs", "ground chicken"],
    "beef": ["ground beef"], "tuna": ["canned tuna"], "onion": ["yellow onion"]
}

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

def correct_spelling(word):
    if not word or len(word) < 3: return word
    m = get_close_matches(word.lower(), KNOWN_ITEMS, n=1, cutoff=0.68)
    return m[0] if m else word

def advanced_fuzzy(ing, custom):
    low = ing.lower()
    if low in custom: return custom[low]
    if low in SUBSTITUTIONS: return SUBSTITUTIONS[low][0]
    keys = list(SUBSTITUTIONS.keys()) + list(custom.keys())
    m = get_close_matches(low, keys, n=1, cutoff=0.6)
    return (custom.get(m[0]) or SUBSTITUTIONS.get(m[0], [None])[0]) if m else None

def guess_unit(name):
    n = name.lower()
    if any(x in n for x in ["milk", "oil"]): return "gallons"
    if any(x in n for x in ["chicken", "beef", "tuna"]): return "lbs"
    return "count"

def search_recipes(q):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={q}", timeout=8)
        r.raise_for_status()
        meals = r.json().get("meals") or []
        return [{"name": m.get("strMeal"), "ings": [{"name": m.get(f"strIngredient{i}"), "qty": 1.0} for i in range(1, 10) if m.get(f"strIngredient{i}")], "instr": (m.get("strInstructions") or "")[:400], "img": m.get("strMealThumb")} for m in meals[:5]]
    except:
        return []

# Session
if "lang" not in st.session_state: st.session_state.lang = None
if "locations" not in st.session_state: st.session_state.locations = {"Home": []}
if "current_loc" not in st.session_state: st.session_state.current_loc = "Home"
if "users" not in st.session_state: st.session_state.users = {"Me": {"goal": "Balanced", "protein": 150}}
if "current_user" not in st.session_state: st.session_state.current_user = "Me"
if "custom_subs" not in st.session_state: st.session_state.custom_subs = {}
if "edited_recipes" not in st.session_state: st.session_state.edited_recipes = {}
if "scale_history" not in st.session_state: st.session_state.scale_history = {}
if "grocery" not in st.session_state: st.session_state.grocery = []
if "future_meals" not in st.session_state: st.session_state.future_meals = []
if "weekly" not in st.session_state: st.session_state.weekly = {d: "" for d in DAYS}
if "reminder_time" not in st.session_state: st.session_state.reminder_time = "17:00"
if "usda_key" not in st.session_state: st.session_state.usda_key = ""

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

with st.sidebar:
    st.header(t["settings"])
    nl = st.selectbox(t["lang"], list(TRANSLATIONS.keys()), index=list(TRANSLATIONS.keys()).index(st.session_state.lang))
    if nl != st.session_state.lang:
        st.session_state.lang = nl
        st.rerun()

    st.subheader(t["reminder"])
    st.session_state.reminder_time = st.text_input("Remind me at (HH:MM)", st.session_state.reminder_time)
    st.caption(f"Reminder set for {st.session_state.reminder_time} — check the Grocery tab.")

    st.subheader(t["locations"])
    locs = list(st.session_state.locations.keys())
    sl = st.selectbox("Location", locs, index=locs.index(st.session_state.current_loc))
    if sl != st.session_state.current_loc:
        st.session_state.current_loc = sl
        st.rerun()

    st.subheader(t["users"])
    us = list(st.session_state.users.keys())
    su = st.selectbox("User", us)
    st.session_state.current_user = su
    uu = st.session_state.users[su]
    uu["goal"] = st.selectbox("Goal", ["Balanced", "Gain muscle", "Cut / Get lean", "Reduce fat", "Heart health"])
    uu["protein"] = st.number_input("Protein (g)", 40, 300, uu.get("protein", 150))

tabs = st.tabs([t["inventory"], t["can_make"], t["need_groceries"], t["grocery"], t["planner"], t["future"], t["recipes"]])

# Inventory
with tabs[0]:
    st.subheader(f"Inventory — {st.session_state.current_loc}")
    st.write("**Quick start**")
    if st.button("Add common starter items"):
        starters = [("chicken breast", 2, "lbs"), ("eggs", 12, "count"), ("rice", 2, "lbs"), ("onion", 3, "count"), ("canned tuna", 4, "cans")]
        for name, q, u in starters:
            st.session_state.locations[st.session_state.current_loc].append({"item": name, "qty": q, "unit": u})
        st.rerun()

    raw = st.text_input("Add item")
    corrected = correct_spelling(raw)
    if raw and corrected != raw.lower():
        st.caption(f"Using: {corrected}")
    selected = corrected
    qty = st.number_input("Qty", 0.1, 50.0, 1.0)
    unit = st.selectbox("Unit", ["lbs", "count", "cans", "cups"])
    if st.button(t["add_item"]) and selected:
        st.session_state.locations[st.session_state.current_loc].append({"item": selected, "qty": qty, "unit": unit})
        st.rerun()

    inv = st.session_state.locations[st.session_state.current_loc]
    for i, it in enumerate(inv):
        c1, c2, c3 = st.columns([4, 1.5, 1])
        c1.write(f"**{it['item']}** — {it['qty']} {it['unit']}")
        if c3.button("Remove", key=f"rm{i}"):
            inv.pop(i)
            st.rerun()

# Can Make Now
with tabs[1]:
    st.subheader(f"Recipes you can mostly make — {st.session_state.current_user}")
    inv_names = [i["item"].lower() for i in st.session_state.locations[st.session_state.current_loc]]
    if inv_names:
        for term in list(set(inv_names))[:3]:
            for rec in search_recipes(term):
                match = sum(1 for ing in rec["ings"] if any(x in ing["name"].lower() for x in inv_names))
                if match >= 2:
                    with st.expander(f"{rec['name']} (matches {match} items)"):
                        st.write(", ".join([i["name"] for i in rec["ings"][:6]]))
                        if st.button("Add to Future Meals", key=f"fm{rec['name']}"):
                            st.session_state.future_meals.append(rec)
                            st.success("Added to Future Meals")

# Need Groceries
with tabs[2]:
    st.subheader("Recipes that fit your goal but need extra items")
    goal = st.session_state.users[st.session_state.current_user]["goal"]
    search_term = "chicken" if "muscle" in goal.lower() else "vegetable"
    for rec in search_recipes(search_term):
        with st.expander(rec["name"]):
            st.write(rec["instr"][:200])
            if st.button("Add missing to Grocery List", key=f"gl{rec['name']}"):
                for ing in rec["ings"]:
                    if not any(ing["name"].lower() in i for i in inv_names):
                        st.session_state.grocery.append(ing["name"])
                st.success("Missing items added to Grocery List")

# Grocery List
with tabs[3]:
    st.subheader(t["grocery"])
    st.info(f"Reminder set for {st.session_state.reminder_time}")
    new_g = st.text_input("Add to grocery list")
    if st.button("Add") and new_g:
        st.session_state.grocery.append(new_g)
        st.rerun()
    for i, g in enumerate(st.session_state.grocery):
        c1, c2 = st.columns([4, 1])
        c1.write(f"• {g}")
        if c2.button("Got it", key=f"gg{i}"):
            st.session_state.grocery.pop(i)
            st.rerun()
    if st.button("Clear grocery list"):
        st.session_state.grocery = []
        st.rerun()

# Weekly Planner
with tabs[4]:
    st.subheader(t["planner"] + " (Sunday – Saturday)")
    st.write("Plan meals and see freeze/thaw tips")
    for day in DAYS:
        st.session_state.weekly[day] = st.text_input(day, st.session_state.weekly[day])
    st.write("---")
    st.write("**Freeze / Thaw tips**")
    st.write("- Freeze cooked proteins up to 3 months.")
    st.write("- Thaw chicken or beef in the fridge 1 day before the planned meal.")
    st.write("- Canned items need no thawing.")
    if st.button("Build grocery list from weekly plan"):
        st.success("Review your weekly meals and add missing items to the Grocery tab.")

# Future Meals
with tabs[5]:
    st.subheader(t["future"])
    if not st.session_state.future_meals:
        st.info("Add recipes from the Can Make or Need Groceries tabs.")
    for i, meal in enumerate(st.session_state.future_meals):
        with st.expander(meal["name"]):
            st.write(meal["instr"][:250])
            if st.button(t["cooked"], key=f"conf{i}"):
                # Deduct inventory
                inv = st.session_state.locations[st.session_state.current_loc]
                for ing in meal["ings"]:
                    for item in inv:
                        if ing["name"].lower() in item["item"].lower():
                            item["qty"] = max(0, item["qty"] - 0.5)
                st.session_state.future_meals.pop(i)
                st.success("Meal confirmed — inventory updated.")
                st.rerun()

# Regular Recipes (search)
with tabs[6]:
    st.subheader("Search any recipe")
    q = st.text_input("Search")
    if q:
        for rec in search_recipes(q):
            st.write(f"**{rec['name']}**")
            if rec["img"]: st.image(rec["img"], width=160)
            st.caption(rec["instr"][:180])

st.caption("Grocery list + reminder · Weekly planner · Future meals with confirm-to-update inventory · Goal-based recipe ideas")
