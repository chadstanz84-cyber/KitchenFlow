import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from difflib import get_close_matches

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

TRANSLATIONS = {
    "English": {
        "title": "🍳 KitchenFlow — Meal Prep & Grocery Assistant",
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
        "choose_recipe": "Choose a base recipe",
        "ingredients": "Ingredients",
        "use_instead": "Use this instead",
        "recommended": "Recommended",
        "acceptable": "Acceptable replacement you have",
        "missing_items": "Shopping List (missing items)",
        "helper_title": "Helper"
    }
}

KNOWN_ITEMS = [
    "chicken breast", "chicken thighs", "chicken", "ground beef", "beef",
    "milk", "broccoli", "onion", "onions", "garlic", "rice", "soy sauce",
    "bell peppers", "tomato sauce", "eggs", "butter", "cheese", "flour",
    "sugar", "pasta", "potatoes", "apples", "bananas"
]

def correct_spelling(word):
    if not word or len(word) < 3:
        return word
    matches = get_close_matches(word.lower(), KNOWN_ITEMS, n=1, cutoff=0.75)
    if matches and matches[0] != word.lower():
        # Only correct clear misspellings, not partial valid words
        if abs(len(matches[0]) - len(word)) <= 2:
            return matches[0]
    return word

def guess_unit(item_name):
    name = item_name.lower()
    if any(x in name for x in ["milk", "water", "juice", "oil"]):
        return "gallons" if st.session_state.get("measurement", "US") == "US" else "liters"
    if any(x in name for x in ["chicken", "beef", "pork", "meat", "fish"]):
        return "lbs" if st.session_state.get("measurement", "US") == "US" else "kg"
    if "garlic" in name:
        return "cloves"
    if any(x in name for x in ["onion", "pepper", "egg", "apple", "banana", "potato"]):
        return "count"
    return "count"

if "language" not in st.session_state:
    st.session_state.language = None
if "measurement" not in st.session_state:
    st.session_state.measurement = "US"
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=["Item", "Quantity", "Unit", "Location", "Expiration"])
if "allergies" not in st.session_state:
    st.session_state.allergies = []
if "allow_subs" not in st.session_state:
    st.session_state.allow_subs = True
if "show_nutrition" not in st.session_state:
    st.session_state.show_nutrition = False

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

SAMPLE_RECIPES = {
    "Simple Chicken Stir-Fry": {
        "ingredients": {
            "chicken breast": {"qty": 1.5, "unit": "lbs", "acceptable": ["chicken thighs", "chicken"]},
            "broccoli": {"qty": 2, "unit": "cups", "acceptable": []},
            "soy sauce": {"qty": 0.25, "unit": "cup", "acceptable": []},
            "garlic": {"qty": 3, "unit": "cloves", "acceptable": []},
            "rice": {"qty": 1.5, "unit": "cups", "acceptable": []}
        }
    }
}

with st.sidebar:
    st.header(t["preferences"])
    st.session_state.show_nutrition = st.toggle(t["show_nutrition"], value=st.session_state.show_nutrition)
    st.session_state.allow_subs = st.toggle(t["allow_subs"], value=st.session_state.allow_subs)
    meas = st.radio(t["measurements"], [t["us"], t["metric"]])
    st.session_state.measurement = "US" if "US" in meas else "Metric"

tab1, tab2, tab3, tab4, tab5 = st.tabs([t["inventory"], t["meal_plan"], t["shopping_list"], t["recipes"], t["helper"]])

with tab1:
    st.subheader(t["your_inventory"])
    raw_item = st.text_input(t["item"], key="raw_item")
    corrected = correct_spelling(raw_item) if raw_item else ""
    if corrected and corrected != raw_item.lower():
        st.info(f"Did you mean **{corrected}**? (using corrected spelling)")

    suggested = guess_unit(corrected or raw_item)
    default_idx = unit_options.index(suggested) if suggested in unit_options else 0

    with st.form("add_item"):
        c1, c2, c3, c4, c5 = st.columns(5)
        item = c1.text_input(t["item"], value=corrected or raw_item)
        qty = c2.number_input(t["quantity"], min_value=0.0, step=0.1, value=1.0)
        unit = c3.selectbox(t["unit"], unit_options, index=default_idx)
        loc = c4.selectbox(t["location"], ["Fridge", "Freezer", "Pantry"])
        exp = c5.date_input(t["expiration"], value=datetime.now() + timedelta(days=7))
        if st.form_submit_button(t["add_item"]) and item:
            final_item = correct_spelling(item)
            new_row = pd.DataFrame([{"Item": final_item, "Quantity": qty, "Unit": unit, "Location": loc, "Expiration": exp}])
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
            st.rerun()

    if not st.session_state.inventory.empty:
        st.data_editor(st.session_state.inventory, num_rows="dynamic", use_container_width=True)

with tab2:
    st.subheader(t["meal_plan"])
    recipe_name = st.selectbox(t["choose_recipe"], list(SAMPLE_RECIPES.keys()))
    recipe = SAMPLE_RECIPES[recipe_name]

    st.write(f"### {t['ingredients']}")
    inventory_items = [i.lower() for i in st.session_state.inventory["Item"].tolist()] if not st.session_state.inventory.empty else []

    for ing, details in recipe["ingredients"].items():
        st.write(f"**{t['recommended']}:** {ing}")
        found_replacement = None
        for acc in details.get("acceptable", []):
            if any(acc in inv for inv in inventory_items):
                found_replacement = acc
                break
        if found_replacement:
            st.success(f"**{t['acceptable']}:** {found_replacement}")
        else:
            st.write(f"• {details['qty']} {details['unit']} {ing}")

        if st.session_state.allow_subs:
            st.text_input(t["use_instead"], key=f"sub_{ing}", placeholder="optional")

with tab3:
    st.subheader(t["missing_items"])
    st.info("Shopping list will respect exact matches and the acceptable replacements shown above.")

with tab4:
    st.subheader(t["recipes"])
    st.write("Recipes show recommended ingredients and acceptable alternatives when you have them.")

with tab5:
    st.subheader(t["helper_title"])
    st.write("Type an item — clear misspellings will be corrected. Close-but-valid names are left alone.")

st.caption("Spelling correction + recommended vs acceptable replacements added.")
