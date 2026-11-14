import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from difflib import get_close_matches
import requests

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

TRANSLATIONS = {
    "English": {
        "title": "🍳 KitchenFlow — Meal Prep & Inventory Assistant",
        "language": "Language",
        "measurements": "Measurement system",
        "us": "US (lbs, cups, ounces)",
        "metric": "Metric (kg, liters, grams)",
        "preferences": "Preferences",
        "show_nutrition": "Show nutrition details",
        "allow_subs": "Allow easy substitutions",
        "allergies": "Allergies / Restrictions",
        "add_allergy": "Add allergy or restriction",
        "add": "Add",
        "inventory": "Inventory",
        "meal_plan": "Meal Plan",
        "shopping_list": "Shopping List",
        "recipes": "Recipes",
        "helper": "Helper",
        "your_inventory": "Your Inventory",
        "item": "Item",
        "quantity": "Quantity",
        "unit": "Unit",
        "location": "Location",
        "expiration": "Expiration",
        "add_item": "Add Item",
        "fresh_frozen": "Fresh or Frozen",
        "fresh": "Fresh",
        "frozen": "Frozen",
        "delete": "Delete",
        "choose_recipe": "Search recipes",
        "ingredients": "Ingredients",
        "instructions": "Instructions",
        "use_instead": "Use this instead",
        "recommended": "Recommended",
        "acceptable": "Acceptable replacement you have",
        "missing_items": "Shopping List (missing items)",
        "helper_title": "Helper",
        "select_specific": "Select a specific item",
        "no_items": "No items in this location yet.",
        "current_place": "Current Place",
        "add_place": "Add new place (home, store, etc.)",
        "places": "Places",
        "search_recipes": "Type a recipe or ingredient to search the web",
        "nutrition_goals": "Nutrition Goals",
        "goal_note": "Goals help highlight suitable recipes"
    }
}

ITEM_SUGGESTIONS = {
    "chicken": ["chicken breast", "chicken thighs", "chicken wings", "chicken drumsticks", "whole chicken", "ground chicken"],
    "beef": ["ground beef", "beef steak", "beef roast", "beef stew meat"],
    "milk": ["whole milk", "2% milk", "skim milk", "almond milk"],
    "onion": ["yellow onion", "white onion", "red onion"],
    "pepper": ["bell pepper", "red bell pepper", "green bell pepper"]
}

KNOWN_ITEMS = [
    "chicken breast", "chicken thighs", "chicken wings", "chicken drumsticks", "whole chicken", "ground chicken",
    "ground beef", "beef", "milk", "whole milk", "broccoli", "onion", "yellow onion", "garlic", "rice",
    "soy sauce", "bell peppers", "tomato sauce", "eggs", "butter", "cheese", "bread", "soda", "chips",
    "salmon", "quinoa", "spinach", "sweet potato", "avocado", "oats"
]

def correct_spelling(word):
    if not word or len(word) < 3:
        return word
    matches = get_close_matches(word.lower(), KNOWN_ITEMS, n=1, cutoff=0.78)
    if matches and matches[0] != word.lower() and abs(len(matches[0]) - len(word)) <= 2:
        return matches[0]
    return word

def guess_unit(item_name):
    name = item_name.lower()
    if any(x in name for x in ["milk", "water", "juice", "oil", "soda"]):
        return "gallons" if st.session_state.get("measurement", "US") == "US" else "liters"
    if any(x in name for x in ["chicken", "beef", "pork", "meat", "fish", "salmon"]):
        return "lbs" if st.session_state.get("measurement", "US") == "US" else "kg"
    if "garlic" in name:
        return "cloves"
    if any(x in name for x in ["onion", "pepper", "egg", "apple", "banana", "potato", "bread", "avocado"]):
        return "count"
    return "count"

def search_web_recipes(query):
    """Pull recipes from TheMealDB free API"""
    if not query or len(query) < 2:
        return []
    try:
        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
        response = requests.get(url, timeout=10)
        data = response.json()
        meals = data.get("meals")
        if not meals:
            return []
        results = []
        for meal in meals[:8]:  # Limit to 8 results
            ingredients = []
            for i in range(1, 21):
                ing = meal.get(f"strIngredient{i}")
                measure = meal.get(f"strMeasure{i}")
                if ing and ing.strip():
                    ingredients.append(f"{measure.strip() if measure else ''} {ing.strip()}".strip())
            results.append({
                "name": meal.get("strMeal", "Unknown"),
                "category": meal.get("strCategory", ""),
                "area": meal.get("strArea", ""),
                "ingredients": ingredients,
                "instructions": meal.get("strInstructions", "No instructions available."),
                "image": meal.get("strMealThumb", "")
            })
        return results
    except Exception as e:
        st.error(f"Could not fetch recipes: {e}")
        return []

# ---------- Session State ----------
if "language" not in st.session_state:
    st.session_state.language = None
if "measurement" not in st.session_state:
    st.session_state.measurement = "US"
if "places" not in st.session_state:
    st.session_state.places = {"Home": pd.DataFrame(columns=["Item", "Quantity", "Unit", "Fresh/Frozen", "Location", "Expiration"])}
if "current_place" not in st.session_state:
    st.session_state.current_place = "Home"
if "allergies" not in st.session_state:
    st.session_state.allergies = []
if "allow_subs" not in st.session_state:
    st.session_state.allow_subs = True
if "show_nutrition" not in st.session_state:
    st.session_state.show_nutrition = False
if "goals" not in st.session_state:
    st.session_state.goals = []

if st.session_state.language is None:
    st.title("KitchenFlow")
    lang = st.selectbox("Choose your language", list(TRANSLATIONS.keys()))
    if st.button("Continue"):
        st.session_state.language = lang
        st.rerun()
    st.stop()

t = TRANSLATIONS[st.session_state.language]
st.title(t["title"])

unit_options = ["lbs", "cups", "count", "oz", "cloves", "gallons"] if st.session_state.measurement == "US" else ["kg", "liters", "count", "grams", "cloves", "gallons"]

# ---------- Sidebar ----------
with st.sidebar:
    st.header(t["preferences"])
    st.subheader(t["places"])
    place_list = list(st.session_state.places.keys())
    selected = st.selectbox(t["current_place"], place_list, index=place_list.index(st.session_state.current_place))
    if selected != st.session_state.current_place:
        st.session_state.current_place = selected
        st.rerun()

    new_place = st.text_input(t["add_place"])
    if st.button("Add Place") and new_place and new_place not in st.session_state.places:
        st.session_state.places[new_place] = pd.DataFrame(columns=["Item", "Quantity", "Unit", "Fresh/Frozen", "Location", "Expiration"])
        st.session_state.current_place = new_place
        st.rerun()

    st.subheader(t["nutrition_goals"])
    goal_options = ["Gain weight", "Lose weight", "Higher protein", "Add potassium", "Cut sodium", "Cut sugars", "Higher fiber", "Lower saturated fat"]
    st.session_state.goals = st.multiselect("Select your goals", goal_options, default=st.session_state.goals)
    if st.session_state.goals:
        st.caption(t["goal_note"])

    st.session_state.show_nutrition = st.toggle(t["show_nutrition"], value=st.session_state.show_nutrition)
    st.session_state.allow_subs = st.toggle(t["allow_subs"], value=st.session_state.allow_subs)
    meas = st.radio(t["measurements"], [t["us"], t["metric"]])
    st.session_state.measurement = "US" if "US" in meas else "Metric"

    st.subheader(t["allergies"])
    new_allergy = st.text_input(t["add_allergy"])
    if st.button(t["add"]) and new_allergy:
        if new_allergy.lower() not in [a.lower() for a in st.session_state.allergies]:
            st.session_state.allergies.append(new_allergy)
            st.rerun()

current_inv = st.session_state.places[st.session_state.current_place]

tab1, tab2, tab3, tab4, tab5 = st.tabs([t["inventory"], t["meal_plan"], t["shopping_list"], t["recipes"], t["helper"]])

with tab1:
    st.subheader(f"{t['your_inventory']} — {st.session_state.current_place}")
    raw_item = st.text_input(t["item"], key="raw_item")
    corrected = correct_spelling(raw_item) if raw_item else ""

    suggestions = []
    for key, options in ITEM_SUGGESTIONS.items():
        if key in (corrected or raw_item).lower():
            suggestions = options
            break

    selected_item = corrected or raw_item
    if suggestions:
        selected_item = st.selectbox(t["select_specific"], suggestions, index=0)

    suggested_unit = guess_unit(selected_item)
    default_idx = unit_options.index(suggested_unit) if suggested_unit in unit_options else 0

    with st.form("add_item"):
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        item = c1.text_input(t["item"], value=selected_item)
        qty = c2.number_input(t["quantity"], min_value=0.0, step=0.1, value=1.0)
        unit = c3.selectbox(t["unit"], unit_options, index=default_idx)
        fresh_frozen = c4.selectbox(t["fresh_frozen"], [t["fresh"], t["frozen"]])
        loc = c5.selectbox(t["location"], ["Fridge", "Freezer", "Pantry", "Shelf", "Backroom"])
        exp = c6.date_input(t["expiration"], value=datetime.now() + timedelta(days=7))
        if st.form_submit_button(t["add_item"]) and item:
            final_item = correct_spelling(item)
            new_row = pd.DataFrame([{
                "Item": final_item,
                "Quantity": qty,
                "Unit": unit,
                "Fresh/Frozen": fresh_frozen,
                "Location": loc,
                "Expiration": exp
            }])
            st.session_state.places[st.session_state.current_place] = pd.concat([current_inv, new_row], ignore_index=True)
            st.rerun()

    st.write("---")
    st.write("### Current Items")
    inv = st.session_state.places[st.session_state.current_place]
    if inv.empty:
        st.info(t["no_items"])
    else:
        for idx, row in inv.iterrows():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.write(f"**{row['Item']}**")
            with col2:
                new_qty = st.number_input("Qty", value=float(row["Quantity"]), key=f"qty_{idx}", step=0.1, label_visibility="collapsed")
            with col3:
                st.write(f"{row['Unit']} | {row['Fresh/Frozen']}")
            with col4:
                if st.button(t["delete"], key=f"del_{idx}"):
                    st.session_state.places[st.session_state.current_place] = inv.drop(idx).reset_index(drop=True)
                    st.rerun()
            if new_qty != row["Quantity"]:
                st.session_state.places[st.session_state.current_place].at[idx, "Quantity"] = new_qty
                st.rerun()

with tab2:
    st.subheader(t["meal_plan"])
    if st.session_state.goals:
        st.info(f"Active goals: {', '.join(st.session_state.goals)}")

    search = st.text_input(t["search_recipes"], placeholder="e.g. chicken, pasta, salmon, soup...")
    if search:
        with st.spinner("Searching recipes..."):
            web_recipes = search_web_recipes(search)
        if web_recipes:
            recipe_names = [r["name"] for r in web_recipes]
            selected_name = st.selectbox("Select a recipe", recipe_names)
            selected = next(r for r in web_recipes if r["name"] == selected_name)
            st.write(f"**{selected['name']}**  ({selected['category']} — {selected['area']})")
            if selected["image"]:
                st.image(selected["image"], width=300)
            st.write(f"### {t['ingredients']}")
            for ing in selected["ingredients"]:
                st.write(f"• {ing}")
            st.write(f"### {t['instructions']}")
            st.write(selected["instructions"])
        else:
            st.info("No recipes found. Try a different search term (e.g. 'chicken', 'beef', 'pasta').")
    else:
        st.info("Type a recipe or main ingredient above to search the web.")

with tab3:
    st.subheader(t["missing_items"])
    st.info(f"Shopping list for **{st.session_state.current_place}** only.")

with tab4:
    st.subheader(t["recipes"])
    st.info("Use the Meal Plan tab to search and view recipes from the web.")

with tab5:
    st.subheader(t["helper_title"])
    st.write(f"Current place: **{st.session_state.current_place}**")
    st.write("Search recipes in the Meal Plan tab — they are pulled live from the web (TheMealDB).")
    st.write("Set nutrition goals in the sidebar.")

st.caption("Live web recipe search added (TheMealDB).")
