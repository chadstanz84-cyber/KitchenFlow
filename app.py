import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from difflib import get_close_matches

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
        "choose_recipe": "Search or choose a recipe",
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
        "search_recipes": "Type to search recipes"
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
    "soy sauce", "bell peppers", "tomato sauce", "eggs", "butter", "cheese", "bread", "soda", "chips"
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
    if any(x in name for x in ["chicken", "beef", "pork", "meat", "fish"]):
        return "lbs" if st.session_state.get("measurement", "US") == "US" else "kg"
    if "garlic" in name:
        return "cloves"
    if any(x in name for x in ["onion", "pepper", "egg", "apple", "banana", "potato", "bread"]):
        return "count"
    return "count"

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
            "Brown the ground beef in a skillet and drain excess fat.",
            "Add chopped onion and bell peppers. Cook until soft.",
            "Stir in tomato sauce and simmer 5 minutes.",
            "Serve over rice."
        ]
    },
    "Garlic Butter Pasta": {
        "ingredients": {
            "pasta": {"qty": 1, "unit": "lbs", "acceptable": []},
            "garlic": {"qty": 4, "unit": "cloves", "acceptable": []},
            "butter": {"qty": 0.25, "unit": "cup", "acceptable": []},
            "cheese": {"qty": 0.5, "unit": "cup", "acceptable": []}
        },
        "instructions": [
            "Cook pasta according to package directions.",
            "Melt butter in a pan and add minced garlic. Cook 1 minute.",
            "Toss cooked pasta with the garlic butter.",
            "Top with cheese and serve."
        ]
    }
}

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

    st.session_state.show_nutrition = st.toggle(t["show_nutrition"], value=st.session_state.show_nutrition)
    st.session_state.allow_subs = st.toggle(t["allow_subs"], value=st.session_state.allow_subs)
    meas = st.radio(t["measurements"], [t["us"], t["metric"]])
    st.session_state.measurement = "US" if "US" in meas else "Metric"

# Current inventory (strictly separated by place)
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
    search = st.text_input(t["search_recipes"], placeholder="Type recipe name...")
    recipe_names = list(SAMPLE_RECIPES.keys())
    if search:
        filtered = [r for r in recipe_names if search.lower() in r.lower()]
    else:
        filtered = recipe_names

    if filtered:
        recipe_name = st.selectbox(t["choose_recipe"], filtered)
        recipe = SAMPLE_RECIPES[recipe_name]
        st.write(f"### {t['ingredients']}")
        inventory_items = [i.lower() for i in inv["Item"].tolist()] if not inv.empty else []
        for ing, details in recipe["ingredients"].items():
            st.write(f"**{t['recommended']}:** {ing}")
            found = next((acc for acc in details.get("acceptable", []) if any(acc in i for i in inventory_items)), None)
            if found:
                st.success(f"**{t['acceptable']}:** {found}")
            else:
                st.write(f"• {details['qty']} {details['unit']} {ing}")
            if st.session_state.allow_subs:
                st.text_input(t["use_instead"], key=f"sub_{ing}", placeholder="optional")
        st.write(f"### {t['instructions']}")
        for i, step in enumerate(recipe.get("instructions", []), 1):
            st.write(f"{i}. {step}")
    else:
        st.info("No recipes match your search.")

with tab3:
    st.subheader(t["missing_items"])
    st.info(f"Shopping list for **{st.session_state.current_place}** only.")

with tab4:
    st.subheader(t["recipes"])
    for name, data in SAMPLE_RECIPES.items():
        with st.expander(name):
            st.write("**Ingredients:**", ", ".join(data["ingredients"].keys()))
            for i, step in enumerate(data.get("instructions", []), 1):
                st.write(f"{i}. {step}")

with tab5:
    st.subheader(t["helper_title"])
    st.write(f"Current place: **{st.session_state.current_place}**")
    st.write("Inventory is completely separate for each place.")
    st.write("Use the search box in Meal Plan to find recipes by typing.")

st.caption("Recipe search + confirmed separate inventories per place.")
