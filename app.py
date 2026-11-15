import streamlit as st
import requests
from datetime import datetime, date, time
import pytz

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

SEASONINGS = ["salt", "black pepper", "garlic powder", "paprika", "cumin", "oregano", "cinnamon", "chili powder"]
PANTRY_ITEMS = ["white rice", "pasta", "olive oil", "canned tomatoes", "black beans", "canned tuna", "oats", "flour", "sugar", "peanut butter"]
FRIDGE_ITEMS = ["eggs", "milk", "butter", "cheddar cheese", "greek yogurt", "chicken breast", "ground beef", "spinach", "broccoli"]
FREEZER_ITEMS = ["frozen chicken", "frozen vegetables", "frozen berries", "ice cream", "frozen pizza"]

STORE_SEARCH = {
    "Walmart": "https://www.walmart.com/search?q=",
    "Kroger": "https://www.kroger.com/search?query=",
    "Target": "https://www.target.com/s?searchTerm=",
    "Aldi": "https://www.aldi.us/en/search/?q="
}

TIMEZONES = ["US/Eastern", "US/Central", "US/Mountain", "US/Pacific", "UTC"]

def search_recipes(q):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={q}", timeout=8)
        meals = r.json().get("meals") or []
        return [{"name": m.get("strMeal"), "ings": [m.get(f"strIngredient{i}") for i in range(1,7) if m.get(f"strIngredient{i}")], "instr": (m.get("strInstructions") or "")[:250]} for m in meals[:4]]
    except:
        return []

# Session
if "locations" not in st.session_state:
    st.session_state.locations = {"Pantry": [], "Fridge": [], "Freezer": []}
if "current_loc" not in st.session_state:
    st.session_state.current_loc = "Pantry"
if "grocery" not in st.session_state:
    st.session_state.grocery = []
if "store" not in st.session_state:
    st.session_state.store = "Walmart"
if "future_meals" not in st.session_state:
    st.session_state.future_meals = []
if "reminder_date" not in st.session_state:
    st.session_state.reminder_date = date.today()
if "reminder_time" not in st.session_state:
    st.session_state.reminder_time = time(17, 0)
if "time_format" not in st.session_state:
    st.session_state.time_format = "12-hour"
if "timezone" not in st.session_state:
    st.session_state.timezone = "US/Central"

st.title("KitchenFlow")
st.caption("Water is always available.")

with st.sidebar:
    st.header("Settings")
    st.subheader("Locations")
    loc_names = list(st.session_state.locations.keys())
    st.session_state.current_loc = st.selectbox("Active location", loc_names, index=loc_names.index(st.session_state.current_loc))
    new_name = st.text_input("Rename or add location")
    if st.button("Save location name") and new_name:
        if new_name not in st.session_state.locations:
            st.session_state.locations[new_name] = []
        st.session_state.current_loc = new_name
        st.rerun()

    st.subheader("Reminder")
    st.session_state.reminder_date = st.date_input("Date", st.session_state.reminder_date)
    st.session_state.reminder_time = st.time_input("Time", st.session_state.reminder_time)
    st.session_state.time_format = st.radio("Format", ["12-hour", "24-hour"])
    st.session_state.timezone = st.selectbox("Timezone", TIMEZONES)
    try:
        tz = pytz.timezone(st.session_state.timezone)
        dt = tz.localize(datetime.combine(st.session_state.reminder_date, st.session_state.reminder_time))
        fmt = "%I:%M %p" if st.session_state.time_format == "12-hour" else "%H:%M"
        st.info(dt.strftime(f"%b %d, %Y at {fmt} %Z"))
    except:
        pass

    st.session_state.store = st.selectbox("Store", list(STORE_SEARCH.keys()))

tabs = st.tabs(["Inventory", "What I Have", "Recipes & Desserts", "Grocery List", "Future Meals"])

with tabs[0]:
    st.subheader("Inventory")
    st.write(f"**Adding to: {st.session_state.current_loc}**")

    col1, col2, col3 = st.columns(3)
    with col1:
        with st.expander("Seasonings", expanded=False):
            for item in SEASONINGS:
                if st.button(item, key=f"sea{item}"):
                    st.session_state.locations[st.session_state.current_loc].append(item)
                    st.rerun()
    with col2:
        with st.expander("Pantry staples", expanded=False):
            for item in PANTRY_ITEMS:
                if st.button(item, key=f"pan{item}"):
                    st.session_state.locations[st.session_state.current_loc].append(item)
                    st.rerun()
    with col3:
        with st.expander("Fridge / Freezer", expanded=False):
            for item in FRIDGE_ITEMS + FREEZER_ITEMS:
                if st.button(item, key=f"fr{item}"):
                    st.session_state.locations[st.session_state.current_loc].append(item)
                    st.rerun()

    custom = st.text_input("Custom item")
    if st.button("Add") and custom:
        st.session_state.locations[st.session_state.current_loc].append(custom)
        st.rerun()

    st.write("---")
    for loc, items in st.session_state.locations.items():
        if items:
            with st.expander(f"{loc} ({len(items)})", expanded=False):
                for i, it in enumerate(items):
                    c1, c2 = st.columns([5,1])
                    c1.write(it)
                    if c2.button("✕", key=f"x{loc}{i}"):
                        items.pop(i)
                        st.rerun()

with tabs[1]:
    st.subheader("What I Have for Cooking")
    all_items = []
    for loc, items in st.session_state.locations.items():
        all_items.extend(items)
    if all_items:
        st.write(", ".join(sorted(set(all_items))))
        st.caption(f"{len(set(all_items))} unique items across all locations.")
    else:
        st.info("Add items in the Inventory tab.")

with tabs[2]:
    st.subheader("Recipes & Desserts")
    q = st.text_input("Search (try: chicken, cake, cookie, pasta)")
    inv_flat = [i.lower() for items in st.session_state.locations.values() for i in items]
    if q:
        for rec in search_recipes(q):
            with st.expander(rec["name"]):
                missing = [ing for ing in rec["ings"] if ing and not any(ing.lower() in x for x in inv_flat)]
                st.write(", ".join(rec["ings"]))
                if missing:
                    st.warning("Missing: " + ", ".join(missing))
                    if st.button("Add missing to grocery list", key=f"m{rec['name']}"):
                        for m in missing:
                            if m not in st.session_state.grocery:
                                st.session_state.grocery.append(m)
                        st.rerun()
                if st.button("Add to Future Meals", key=f"fut{rec['name']}"):
                    st.session_state.future_meals.append(rec["name"])
                    st.rerun()

with tabs[3]:
    st.subheader("Grocery List")
    st.caption(f"Store: {st.session_state.store}")
    g = st.text_input("Add item")
    if st.button("Add to grocery") and g:
        st.session_state.grocery.append(g)
        st.rerun()
    base = STORE_SEARCH.get(st.session_state.store, "")
    for i, item in enumerate(st.session_state.grocery):
        c1, c2 = st.columns([4,1])
        c1.write(item)
        if base:
            st.markdown(f"[Search at store]({base}{item.replace(' ','+')})")
        if c2.button("Remove", key=f"gg{i}"):
            st.session_state.grocery.pop(i)
            st.rerun()

with tabs[4]:
    st.subheader("Future Meals")
    for i, meal in enumerate(st.session_state.future_meals):
        c1, c2 = st.columns([4,1])
        c1.write(meal)
        if c2.button("Done", key=f"done{i}"):
            st.session_state.future_meals.pop(i)
            st.rerun()

st.caption("Compact inventory by location · Custom locations · Desserts via search · What I Have overview")
