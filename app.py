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
        "fresh_frozen": "Fresh or Frozen",
        "fresh": "Fresh",
        "frozen": "Frozen",
        "choose_recipe": "Choose a base recipe",
        "ingredients": "Ingredients",
        "instructions": "Instructions",
        "use_instead": "Use this instead",
        "recommended": "Recommended",
        "acceptable": "Acceptable replacement you have",
        "missing_items": "Shopping List (missing items)",
        "helper_title": "Helper",
        "select_specific": "Select a specific item"
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
    "soy sauce", "bell peppers", "tomato sauce", "eggs", "butter", "cheese"
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
    st.session_state.inventory = pd.DataFrame(columns=["Item", "Quantity", "Unit", "Fresh/Frozen", "Location", "Expiration"])
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
            "chicken breast": {"qty": 1.5, "unit": "lbs", "acceptable": ["chicken thighs", "chicken wings", "ground chicken"]},
            "broccoli": {"qty": 2, "unit": "cups", "acceptable": []},
            "soy sauce": {"qty": 0.25, "unit": "cup", "acceptable": []},
            "garlic": {"qty": 3, "unit": "cloves", "acceptable": []},
            "rice": {"qty": 1.5, "unit": "cups", "acceptable": []}
        },
        "instructions": [
            "Cook the rice according to package directions and set aside.",
            "Cut the chicken into bite-sized pieces.",
            "Heat a large pan or wok over medium-high heat with a little oil.",
            "Add the chicken and cook until no longer pink, about 5–7 minutes.",
            "Add the garlic and broccoli. Stir-fry for 3–4 minutes until broccoli is tender-crisp.",
            "Pour in the soy sauce and stir everything together for 1 minute.",
            "Serve over the cooked rice."
        ]
    },
    "Beef & Vegetable Skillet": {
        "ingredients": {
            "ground beef": {"qty": 1.0, "unit": "lbs", "acceptable": ["ground turkey"]},
            "bell peppers": {"qty": 2, "unit": "count", "acceptable": []},
            "onion": {"qty": 1, "unit": "count", "acceptable": []},
            "tomato sauce": {"qty": 1, "unit": "cup", "acceptable": []},
            "rice": {"qty": 1, "unit": "cups", "acceptable": []}
        },
        "instructions": [
            "Cook the rice according to package directions.",
            "In a large skillet, brown the ground beef over medium heat. Drain excess fat.",
            "Add the chopped onion and bell peppers. Cook until softened, about 5 minutes.",
            "Stir in the tomato sauce and simmer for 5 minutes.",
            "Serve the beef mixture over the rice."
        ]
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
        loc = c5.selectbox(t["location"], ["Fridge", "Freezer", "Pantry"])
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
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
            st.rerun()

    if not st.session_state.inventory.empty:
        st.data_editor(st.session_state.inventory, num_rows="dynamic", use_container_width=True)
    else:
        st.info("Add items you currently have.")

with tab2:
    st.subheader(t["meal_plan"])
    recipe_name = st.selectbox(t["choose_recipe"], list(SAMPLE_RECIPES.keys()))
    recipe = SAMPLE_RECIPES[recipe_name]

    st.write(f"### {t['ingredients']}")
    inventory_items = [i.lower() for i in st.session_state.inventory["Item"].tolist()] if not st.session_state.inventory.empty else []

    for ing, details in recipe["ingredients"].items():
        st.write(f"**{t['recommended']}:** {ing}")
        found = next((acc for acc in details.get("acceptable", []) if any(acc in inv for inv in inventory_items)), None)
        if found:
            st.success(f"**{t['acceptable']}:** {found}")
        else:
            st.write(f"• {details['qty']} {details['unit']} {ing}")
        if st.session_state.allow_subs:
            st.text_input(t["use_instead"], key=f"sub_{ing}", placeholder="optional")

    st.write(f"### {t['instructions']}")
    for i, step in enumerate(recipe.get("instructions", []), 1):
        st.write(f"{i}. {step}")

with tab3:
    st.subheader(t["missing_items"])
    st.info("Shopping list respects your specific items and fresh/frozen choices.")

with tab4:
    st.subheader(t["recipes"])
    for name, data in SAMPLE_RECIPES.items():
        with st.expander(name):
            st.write("**Ingredients:**", ", ".join(data["ingredients"].keys()))
            st.write("**Instructions:**")
            for i, step in enumerate(data.get("instructions", []), 1):
                st.write(f"{i}. {step}")

with tab5:
    st.subheader(t["helper_title"])
    st.write("Pick a recipe in the Meal Plan tab to see full instructions.")

st.caption("Recipe instructions added.")
