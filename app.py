import streamlit as st
import requests
import sqlite3
import json
from datetime import datetime, date, time
from pathlib import Path

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

DB_PATH = Path("kitchenflow.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS app_data (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    conn.commit()
    conn.close()

def save_data(key, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO app_data (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    conn.commit()
    conn.close()

def load_data(key, default):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT value FROM app_data WHERE key = ?", (key,))
        row = c.fetchone()
        conn.close()
        return json.loads(row[0]) if row else default
    except:
        return default

init_db()

SEASONINGS = ["salt", "black pepper", "garlic powder", "paprika", "cumin", "oregano", "cinnamon"]
PANTRY_ITEMS = ["white rice", "pasta", "olive oil", "canned tomatoes", "black beans", "canned tuna", "oats", "flour", "sugar"]
FRIDGE_ITEMS = ["eggs", "milk", "butter", "cheddar cheese", "greek yogurt", "chicken breast", "ground beef", "spinach"]
FREEZER_ITEMS = ["frozen chicken", "frozen vegetables", "frozen berries"]

STORE_SEARCH = {
    "Walmart": "https://www.walmart.com/search?q=",
    "Kroger": "https://www.kroger.com/search?query=",
    "Target": "https://www.target.com/s?searchTerm=",
    "Aldi": "https://www.aldi.us/en/search/?q="
}

def search_recipes(q):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={q}", timeout=8)
        meals = r.json().get("meals") or []
        return [{"name": m.get("strMeal"), "ings": [m.get(f"strIngredient{i}") for i in range(1,7) if m.get(f"strIngredient{i}")], "instr": (m.get("strInstructions") or "")[:250]} for m in meals[:4]]
    except:
        return []

# Load data
if "loaded" not in st.session_state:
    st.session_state.locations = load_data("locations", {"Pantry": [], "Fridge": [], "Freezer": []})
    st.session_state.current_loc = load_data("current_loc", "Pantry")
    st.session_state.grocery = load_data("grocery", [])
    st.session_state.store = load_data("store", "Walmart")
    st.session_state.future_meals = load_data("future_meals", [])
    st.session_state.reminder_date = date.fromisoformat(load_data("reminder_date", str(date.today())))
    st.session_state.reminder_time = time.fromisoformat(load_data("reminder_time", "17:00:00"))
    st.session_state.time_format = load_data("time_format", "12-hour")
    st.session_state.loaded = True

def persist():
    save_data("locations", st.session_state.locations)
    save_data("current_loc", st.session_state.current_loc)
    save_data("grocery", st.session_state.grocery)
    save_data("store", st.session_state.store)
    save_data("future_meals", st.session_state.future_meals)
    save_data("reminder_date", str(st.session_state.reminder_date))
    save_data("reminder_time", str(st.session_state.reminder_time))
    save_data("time_format", st.session_state.time_format)

st.title("KitchenFlow")
st.caption("Water is always available.")

with st.sidebar:
    st.header("Settings")
    loc_names = list(st.session_state.locations.keys())
    new_loc = st.selectbox("Active location", loc_names, index=loc_names.index(st.session_state.current_loc) if st.session_state.current_loc in loc_names else 0)
    if new_loc != st.session_state.current_loc:
        st.session_state.current_loc = new_loc
        persist()
        st.rerun()

    add_loc = st.text_input("Add location")
    if st.button("Add") and add_loc and add_loc not in st.session_state.locations:
        st.session_state.locations[add_loc] = []
        st.session_state.current_loc = add_loc
        persist()
        st.rerun()

    st.subheader("Reminder")
    d = st.date_input("Date", st.session_state.reminder_date)
    t = st.time_input("Time", st.session_state.reminder_time)
    fmt = st.radio("Format", ["12-hour", "24-hour"])
    if d != st.session_state.reminder_date or t != st.session_state.reminder_time or fmt != st.session_state.time_format:
        st.session_state.reminder_date = d
        st.session_state.reminder_time = t
        st.session_state.time_format = fmt
        persist()

    fmt_str = "%I:%M %p" if st.session_state.time_format == "12-hour" else "%H:%M"
    st.info(f"Reminder: {st.session_state.reminder_date.strftime('%b %d')} at {st.session_state.reminder_time.strftime(fmt_str)}")

    store = st.selectbox("Store", list(STORE_SEARCH.keys()))
    if store != st.session_state.store:
        st.session_state.store = store
        persist()

tabs = st.tabs(["Inventory", "What I Have", "Recipes", "Grocery List", "Future Meals"])

with tabs[0]:
    st.subheader(f"Inventory — {st.session_state.current_loc}")
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.expander("Seasonings"):
            for item in SEASONINGS:
                if st.button(item, key=f"s{item}"):
                    st.session_state.locations[st.session_state.current_loc].append(item)
                    persist()
                    st.rerun()
    with c2:
        with st.expander("Pantry"):
            for item in PANTRY_ITEMS:
                if st.button(item, key=f"p{item}"):
                    st.session_state.locations[st.session_state.current_loc].append(item)
                    persist()
                    st.rerun()
    with c3:
        with st.expander("Fridge / Freezer"):
            for item in FRIDGE_ITEMS + FREEZER_ITEMS:
                if st.button(item, key=f"f{item}"):
                    st.session_state.locations[st.session_state.current_loc].append(item)
                    persist()
                    st.rerun()

    custom = st.text_input("Custom item")
    if st.button("Add custom") and custom:
        st.session_state.locations[st.session_state.current_loc].append(custom)
        persist()
        st.rerun()

    for loc, items in st.session_state.locations.items():
        if items:
            with st.expander(f"{loc} ({len(items)})"):
                for i, it in enumerate(items[:]):
                    col1, col2 = st.columns([5,1])
                    col1.write(it)
                    if col2.button("✕", key=f"del{loc}{i}"):
                        items.pop(i)
                        persist()
                        st.rerun()

with tabs[1]:
    st.subheader("What I Have")
    all_items = [item for items in st.session_state.locations.values() for item in items]
    st.write(", ".join(sorted(set(all_items))) if all_items else "Nothing yet.")

with tabs[2]:
    st.subheader("Recipes & Desserts")
    q = st.text_input("Search")
    inv_flat = [i.lower() for items in st.session_state.locations.values() for i in items]
    if q:
        for rec in search_recipes(q):
            with st.expander(rec["name"]):
                missing = [ing for ing in rec["ings"] if ing and not any(ing.lower() in x for x in inv_flat)]
                st.write(", ".join([i for i in rec["ings"] if i]))
                if missing and st.button("Add missing to grocery", key=f"m{rec['name']}"):
                    for m in missing:
                        if m not in st.session_state.grocery:
                            st.session_state.grocery.append(m)
                    persist()
                    st.rerun()
                if st.button("Add to Future", key=f"f{rec['name']}"):
                    st.session_state.future_meals.append(rec["name"])
                    persist()
                    st.rerun()

with tabs[3]:
    st.subheader("Grocery List")
    g = st.text_input("Add item")
    if st.button("Add") and g:
        st.session_state.grocery.append(g)
        persist()
        st.rerun()
    base = STORE_SEARCH.get(st.session_state.store, "")
    for i, item in enumerate(st.session_state.grocery[:]):
        c1, c2 = st.columns([4,1])
        c1.write(item)
        if base:
            st.markdown(f"[Search]({base}{item.replace(' ', '+')})")
        if c2.button("Remove", key=f"g{i}"):
            st.session_state.grocery.pop(i)
            persist()
            st.rerun()

with tabs[4]:
    st.subheader("Future Meals")
    for i, meal in enumerate(st.session_state.future_meals[:]):
        c1, c2 = st.columns([4,1])
        c1.write(meal)
        if c2.button("Done", key=f"done{i}"):
            st.session_state.future_meals.pop(i)
            persist()
            st.rerun()

st.caption("Fixed missing pytz · Persistent storage · Compact inventory")
