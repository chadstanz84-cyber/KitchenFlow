import streamlit as st
import requests
from difflib import get_close_matches
from datetime import datetime, date, time
import pytz

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

SEASONINGS = ["salt", "black pepper", "garlic powder", "onion powder", "paprika", "cumin", "chili powder", "oregano", "basil", "cinnamon"]
PANTRY = ["white rice", "pasta", "olive oil", "canned tomatoes", "black beans", "canned tuna", "oats", "peanut butter", "flour", "sugar"]
REFRIGERATED = ["eggs", "milk", "butter", "cheddar cheese", "chicken breast", "ground beef", "spinach", "broccoli", "greek yogurt"]

STORE_SEARCH = {
    "Walmart": "https://www.walmart.com/search?q=",
    "Kroger": "https://www.kroger.com/search?query=",
    "Target": "https://www.target.com/s?searchTerm=",
    "Aldi": "https://www.aldi.us/en/search/?q="
}

PRICE_ESTIMATES = {
    "chicken breast": "$3.50–5.50/lb", "ground beef": "$4–6.50/lb", "eggs": "$2.50–4.50/dozen",
    "milk": "$3–4.50/gal", "white rice": "$1–2/lb", "canned tuna": "$1–1.80/can"
}

TIMEZONES = ["US/Eastern", "US/Central", "US/Mountain", "US/Pacific", "US/Alaska", "US/Hawaii", "UTC", "Europe/London", "Europe/Paris", "Asia/Tokyo"]

def search_recipes(q):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={q}", timeout=8)
        meals = r.json().get("meals") or []
        return [{"name": m.get("strMeal"), "ings": [m.get(f"strIngredient{i}") for i in range(1, 8) if m.get(f"strIngredient{i}")], "instr": (m.get("strInstructions") or "")[:300]} for m in meals[:4]]
    except:
        return []

# Session
if "locations" not in st.session_state: st.session_state.locations = {"Home": []}
if "current_loc" not in st.session_state: st.session_state.current_loc = "Home"
if "grocery" not in st.session_state: st.session_state.grocery = []
if "store" not in st.session_state: st.session_state.store = "Walmart"
if "future_meals" not in st.session_state: st.session_state.future_meals = []
if "reminder_date" not in st.session_state: st.session_state.reminder_date = date.today()
if "reminder_time" not in st.session_state: st.session_state.reminder_time = time(17, 0)
if "time_format" not in st.session_state: st.session_state.time_format = "12-hour"
if "timezone" not in st.session_state: st.session_state.timezone = "US/Central"

st.title("KitchenFlow")
st.caption("Water is always available.")

with st.sidebar:
    st.header("Settings")
    st.subheader("Store reminder")
    st.session_state.reminder_date = st.date_input("Reminder date", st.session_state.reminder_date)
    st.session_state.reminder_time = st.time_input("Reminder time", st.session_state.reminder_time)
    st.session_state.time_format = st.radio("Time format", ["12-hour", "24-hour"], index=0 if st.session_state.time_format == "12-hour" else 1)
    st.session_state.timezone = st.selectbox("Timezone", TIMEZONES, index=TIMEZONES.index(st.session_state.timezone))

    # Display formatted reminder
    dt = datetime.combine(st.session_state.reminder_date, st.session_state.reminder_time)
    try:
        tz = pytz.timezone(st.session_state.timezone)
        dt_tz = tz.localize(dt)
        if st.session_state.time_format == "12-hour":
            formatted = dt_tz.strftime("%A, %B %d, %Y at %I:%M %p %Z")
        else:
            formatted = dt_tz.strftime("%A, %B %d, %Y at %H:%M %Z")
        st.info(f"Reminder: {formatted}")
    except:
        st.info("Reminder set.")

    st.session_state.store = st.selectbox("Default store", list(STORE_SEARCH.keys()))
    locs = list(st.session_state.locations.keys())
    st.session_state.current_loc = st.selectbox("Location", locs)

tabs = st.tabs(["Inventory", "Grocery List", "Recipes", "Future Meals"])

with tabs[0]:
    st.subheader(f"Inventory — {st.session_state.current_loc}")
    with st.expander("Seasonings"):
        cols = st.columns(3)
        for i, item in enumerate(SEASONINGS):
            if cols[i%3].button(item, key=f"s{item}"):
                st.session_state.locations[st.session_state.current_loc].append({"item": item, "qty": 1})
                st.rerun()
    with st.expander("Pantry"):
        cols = st.columns(3)
        for i, item in enumerate(PANTRY):
            if cols[i%3].button(item, key=f"p{item}"):
                st.session_state.locations[st.session_state.current_loc].append({"item": item, "qty": 1})
                st.rerun()
    with st.expander("Refrigerated"):
        cols = st.columns(3)
        for i, item in enumerate(REFRIGERATED):
            if cols[i%3].button(item, key=f"r{item}"):
                st.session_state.locations[st.session_state.current_loc].append({"item": item, "qty": 1})
                st.rerun()
    custom = st.text_input("Custom item")
    if st.button("Add custom") and custom:
        st.session_state.locations[st.session_state.current_loc].append({"item": custom, "qty": 1})
        st.rerun()
    for i, it in enumerate(st.session_state.locations[st.session_state.current_loc]):
        c1, c2 = st.columns([5,1])
        c1.write(it["item"])
        if c2.button("Remove", key=f"d{i}"):
            st.session_state.locations[st.session_state.current_loc].pop(i)
            st.rerun()

with tabs[1]:
    st.subheader("Grocery List")
    st.info(f"Reminder set for {formatted if 'formatted' in dir() else st.session_state.reminder_time}")
    new = st.text_input("Add item")
    if st.button("Add to list") and new:
        st.session_state.grocery.append(new)
        st.rerun()
    store_base = STORE_SEARCH.get(st.session_state.store, "")
    for i, item in enumerate(st.session_state.grocery):
        c1, c2, c3 = st.columns([3,2,1])
        c1.write(f"**{item}**")
        c2.caption(PRICE_ESTIMATES.get(item.lower(), ""))
        if store_base:
            c3.markdown(f"[Search]({store_base}{item.replace(' ', '+')})")
        if st.button("Remove", key=f"gr{i}"):
            st.session_state.grocery.pop(i)
            st.rerun()

with tabs[2]:
    st.subheader("Recipes")
    q = st.text_input("Search recipes")
    inv = [i["item"].lower() for i in st.session_state.locations[st.session_state.current_loc]]
    if q:
        for rec in search_recipes(q):
            with st.expander(rec["name"]):
                missing = [ing for ing in rec["ings"] if ing and not any(ing.lower() in x or x in ing.lower() for x in inv)]
                st.write("Ingredients:", ", ".join(rec["ings"]))
                if missing:
                    st.warning(f"Missing: {', '.join(missing)}")
                    if st.button(f"Add missing items to grocery list?", key=f"miss{rec['name']}"):
                        for m in missing:
                            if m not in st.session_state.grocery:
                                st.session_state.grocery.append(m)
                        st.success("Added to grocery list")
                        st.rerun()
                if st.button("Plan this meal", key=f"plan{rec['name']}"):
                    st.session_state.future_meals.append(rec)
                    st.success("Added to Future Meals")

with tabs[3]:
    st.subheader("Future Meals")
    for i, meal in enumerate(st.session_state.future_meals):
        st.write(f"**{meal['name']}**")
        if st.button("Confirm cooked", key=f"conf{i}"):
            st.session_state.future_meals.pop(i)
            st.rerun()

st.caption("Date/time/timezone reminders · 12/24-hour format · Ask to add missing recipe items to grocery list")
