import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

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
        "missing_items": "Shopping List (missing items)",
        "helper_title": "Helper"
    },
    "Español": {
        "title": "🍳 KitchenFlow — Asistente de Comidas y Compras",
        "language": "Idioma",
        "measurements": "Sistema de medidas",
        "us": "EE.UU. (libras, tazas, onzas)",
        "metric": "Métrico (kg, litros, gramos)",
        "preferences": "Preferencias",
        "show_nutrition": "Mostrar detalles nutricionales",
        "allow_subs": "Permitir sustituciones fáciles",
        "allergies": "Alergias / Restricciones",
        "add_allergy": "Agregar alergia o restricción",
        "add": "Agregar",
        "inventory": "Inventario",
        "meal_plan": "Plan de comidas",
        "shopping_list": "Lista de compras",
        "recipes": "Recetas",
        "helper": "Ayuda",
        "your_inventory": "Tu inventario",
        "item": "Artículo",
        "quantity": "Cantidad",
        "unit": "Unidad",
        "location": "Ubicación",
        "expiration": "Caducidad",
        "add_item": "Agregar artículo",
        "choose_recipe": "Elige una receta base",
        "ingredients": "Ingredientes",
        "use_instead": "Usar esto en su lugar",
        "missing_items": "Lista de compras (faltantes)",
        "helper_title": "Ayuda"
    }
}

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
    st.write("### Choose your language")
    lang = st.selectbox("Language", list(TRANSLATIONS.keys()))
    if st.button("Continue"):
        st.session_state.language = lang
        st.rerun()
    st.stop()

t = TRANSLATIONS[st.session_state.language]
st.title(t["title"])

# Smart unit guessing
def guess_unit(item_name):
    name = item_name.lower().strip()
    if any(x in name for x in ["milk", "water", "juice", "oil", "vinegar"]):
        return "gallons" if st.session_state.measurement == "US" else "liters"
    if any(x in name for x in ["chicken", "beef", "pork", "turkey", "meat", "fish", "salmon"]):
        return "lbs" if st.session_state.measurement == "US" else "kg"
    if any(x in name for x in ["rice", "flour", "sugar", "pasta", "beans"]):
        return "lbs" if st.session_state.measurement == "US" else "kg"
    if any(x in name for x in ["onion", "pepper", "apple", "banana", "egg", "potato"]):
        return "count"
    if "garlic" in name:
        return "cloves"
    return "count"

if st.session_state.measurement == "US":
    unit_options = ["lbs", "cups", "count", "oz", "cloves", "gallons"]
else:
    unit_options = ["kg", "liters", "count", "grams", "cloves", "gallons"]

def smart_display(qty, item, unit):
    if unit in ["lbs", "kg"]:
        rounded = round(qty * 4) / 4
        nice = str(rounded).replace(".0", "").replace(".5", "½").replace(".25", "¼").replace(".75", "¾")
        return f"about {nice} {unit} {item}"
    if "onion" in item.lower():
        n = round(qty)
        return f"{n} onion" if n == 1 else f"{n} onions"
    return f"{round(qty)} {item}" if unit == "count" else f"about {qty:.1f} {unit} {item}"

with st.sidebar:
    st.header(t["preferences"])
    new_lang = st.selectbox(t["language"], list(TRANSLATIONS.keys()), index=list(TRANSLATIONS.keys()).index(st.session_state.language))
    if new_lang != st.session_state.language:
        st.session_state.language = new_lang
        st.rerun()
    meas = st.radio(t["measurements"], [t["us"], t["metric"]])
    st.session_state.measurement = "US" if meas == t["us"] else "Metric"
    st.session_state.show_nutrition = st.toggle(t["show_nutrition"], value=st.session_state.show_nutrition)
    st.session_state.allow_subs = st.toggle(t["allow_subs"], value=st.session_state.allow_subs)
    st.subheader(t["allergies"])
    new_allergy = st.text_input(t["add_allergy"])
    if st.button(t["add"]) and new_allergy:
        if new_allergy.lower() not in [a.lower() for a in st.session_state.allergies]:
            st.session_state.allergies.append(new_allergy)
            st.rerun()

SAMPLE_RECIPES = {
    "Simple Chicken Stir-Fry": {
        "ingredients": {"chicken breast": 1.5, "broccoli": 2, "soy sauce": 0.25, "garlic": 3, "rice": 1.5},
        "units": {"chicken breast": "lbs", "broccoli": "cups", "soy sauce": "cup", "garlic": "cloves", "rice": "cups"}
    }
}

tab1, tab2, tab3, tab4, tab5 = st.tabs([t["inventory"], t["meal_plan"], t["shopping_list"], t["recipes"], t["helper"]])

with tab1:
    st.subheader(t["your_inventory"])
    item_input = st.text_input(t["item"], key="item_input")
    suggested_unit = guess_unit(item_input) if item_input else unit_options[0]
    default_index = unit_options.index(suggested_unit) if suggested_unit in unit_options else 0

    with st.form("add_item"):
        c1, c2, c3, c4, c5 = st.columns(5)
        item = c1.text_input(t["item"], value=item_input)
        qty = c2.number_input(t["quantity"], min_value=0.0, step=0.1, value=1.0)
        unit = c3.selectbox(t["unit"], unit_options, index=default_index)
        loc = c4.selectbox(t["location"], ["Fridge", "Freezer", "Pantry"])
        exp = c5.date_input(t["expiration"], value=datetime.now() + timedelta(days=7))
        if st.form_submit_button(t["add_item"]) and item:
            new_row = pd.DataFrame([{"Item": item, "Quantity": qty, "Unit": unit, "Location": loc, "Expiration": exp}])
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
            st.rerun()

    if not st.session_state.inventory.empty:
        st.data_editor(st.session_state.inventory, num_rows="dynamic", use_container_width=True)
    else:
        st.info("Add items you currently have.")

with tab2:
    st.subheader(t["meal_plan"])
    st.write("Recipe view with exact ingredients + substitute boxes (expand as needed).")

with tab3:
    st.subheader(t["missing_items"])
    st.info("Shopping list will use your inventory and any substitutions.")

with tab4:
    st.subheader(t["recipes"])
    st.write("Sample recipes available.")

with tab5:
    st.subheader(t["helper_title"])
    st.write("Type an item name above and the unit will try to guess the most common one.")

st.caption("Smart unit suggestion added (milk → gallons, meat → lbs/kg, etc.).")
