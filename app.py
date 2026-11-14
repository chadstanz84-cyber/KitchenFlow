import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

# ---------- Translations ----------
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
        "goals": "Nutrition Goals (optional)",
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
        "use_soon": "Use soon",
        "choose_recipe": "Choose a base recipe",
        "ingredients": "Ingredients (exact recipe)",
        "use_instead": "Use this instead",
        "missing_items": "Shopping List (missing items)",
        "have_everything": "You have everything needed for the sample recipes!",
        "helper_title": "Helper",
        "add_inventory_first": "Add inventory items to get tips."
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
        "goals": "Metas nutricionales (opcional)",
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
        "use_soon": "Usar pronto",
        "choose_recipe": "Elige una receta base",
        "ingredients": "Ingredientes (receta exacta)",
        "use_instead": "Usar esto en su lugar",
        "missing_items": "Lista de compras (faltantes)",
        "have_everything": "¡Tienes todo lo necesario para las recetas de ejemplo!",
        "helper_title": "Ayuda",
        "add_inventory_first": "Agrega artículos al inventario para recibir consejos."
    },
    "Français": {
        "title": "🍳 KitchenFlow — Assistant repas et courses",
        "language": "Langue",
        "measurements": "Système de mesure",
        "us": "US (livres, tasses, onces)",
        "metric": "Métrique (kg, litres, grammes)",
        "preferences": "Préférences",
        "show_nutrition": "Afficher les détails nutritionnels",
        "allow_subs": "Autoriser les substitutions faciles",
        "allergies": "Allergies / Restrictions",
        "add_allergy": "Ajouter une allergie ou restriction",
        "add": "Ajouter",
        "goals": "Objectifs nutritionnels (optionnel)",
        "inventory": "Inventaire",
        "meal_plan": "Plan de repas",
        "shopping_list": "Liste de courses",
        "recipes": "Recettes",
        "helper": "Aide",
        "your_inventory": "Votre inventaire",
        "item": "Article",
        "quantity": "Quantité",
        "unit": "Unité",
        "location": "Emplacement",
        "expiration": "Expiration",
        "add_item": "Ajouter un article",
        "use_soon": "À utiliser bientôt",
        "choose_recipe": "Choisir une recette de base",
        "ingredients": "Ingrédients (recette exacte)",
        "use_instead": "Utiliser ceci à la place",
        "missing_items": "Liste de courses (manquants)",
        "have_everything": "Vous avez tout ce qu’il faut pour les recettes d’exemple !",
        "helper_title": "Aide",
        "add_inventory_first": "Ajoutez des articles à l’inventaire pour obtenir des conseils."
    }
}

# ---------- Session State ----------
if "language" not in st.session_state:
    st.session_state.language = None
if "measurement" not in st.session_state:
    st.session_state.measurement = "US"
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=["Item", "Quantity", "Unit", "Location", "Expiration"])
if "allergies" not in st.session_state:
    st.session_state.allergies = []
if "goals" not in st.session_state:
    st.session_state.goals = []
if "allow_subs" not in st.session_state:
    st.session_state.allow_subs = True
if "show_nutrition" not in st.session_state:
    st.session_state.show_nutrition = False
if "substitutions" not in st.session_state:
    st.session_state.substitutions = {}

# Language selection on first open
if st.session_state.language is None:
    st.title("KitchenFlow")
    st.write("### Choose your language / Elige tu idioma / Choisissez votre langue")
    lang = st.selectbox("Language", list(TRANSLATIONS.keys()))
    if st.button("Continue"):
        st.session_state.language = lang
        st.rerun()
    st.stop()

t = TRANSLATIONS[st.session_state.language]
st.title(t["title"])

# Measurement units based on system
if st.session_state.measurement == "US":
    unit_options = ["lbs", "cups", "count", "oz", "cloves", "gallons"]
else:
    unit_options = ["kg", "liters", "count", "grams", "cloves", "gallons"]

def smart_display(qty, item, unit):
    if unit in ["lbs", "kg"]:
        rounded = round(qty * 4) / 4
        nice = str(rounded).replace(".0", "").replace(".5", "½").replace(".25", "¼").replace(".75", "¾")
        return f"about {nice} {unit} {item}"
    if unit in ["cups", "liters"]:
        rounded = round(qty * 4) / 4
        nice = str(rounded).replace(".0", "").replace(".5", "½")
        return f"about {nice} {unit} {item}"
    if "onion" in item.lower():
        n = round(qty)
        return f"{n} onion" if n == 1 else f"{n} onions"
    return f"{round(qty)} {item}" if unit == "count" else f"about {qty:.1f} {unit} {item}"

# ---------- Sidebar ----------
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
    for a in list(st.session_state.allergies):
        col1, col2 = st.columns([3,1])
        col1.write(a)
        if col2.button("✕", key=f"del_{a}"):
            st.session_state.allergies.remove(a)
            st.rerun()

# ---------- Sample Recipes (kept simple) ----------
SAMPLE_RECIPES = {
    "Simple Chicken Stir-Fry": {
        "ingredients": {"chicken breast": 1.5, "broccoli": 2, "soy sauce": 0.25, "garlic": 3, "rice": 1.5},
        "units": {"chicken breast": "lbs", "broccoli": "cups", "soy sauce": "cup", "garlic": "cloves", "rice": "cups"}
    },
    "Beef & Vegetable Skillet": {
        "ingredients": {"ground beef": 1.0, "bell peppers": 2, "onion": 1, "tomato sauce": 1, "rice": 1},
        "units": {"ground beef": "lbs", "bell peppers": "count", "onion": "count", "tomato sauce": "cup", "rice": "cups"}
    }
}

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([t["inventory"], t["meal_plan"], t["shopping_list"], t["recipes"], t["helper"]])

with tab1:
    st.subheader(t["your_inventory"])
    with st.form("add_item"):
        c1, c2, c3, c4, c5 = st.columns(5)
        item = c1.text_input(t["item"])
        qty = c2.number_input(t["quantity"], min_value=0.0, step=0.1, value=1.0)
        unit = c3.selectbox(t["unit"], unit_options)
        loc = c4.selectbox(t["location"], ["Fridge", "Freezer", "Pantry"])
        exp = c5.date_input(t["expiration"], value=datetime.now() + timedelta(days=7))
        if st.form_submit_button(t["add_item"]) and item:
            new_row = pd.DataFrame([{"Item": item, "Quantity": qty, "Unit": unit, "Location": loc, "Expiration": exp}])
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
            st.rerun()

    if not st.session_state.inventory.empty:
        edited = st.data_editor(st.session_state.inventory, num_rows="dynamic", use_container_width=True)
        st.session_state.inventory = edited
    else:
        st.info("Add items you currently have.")

with tab2:
    st.subheader(t["meal_plan"])
    selected = st.selectbox(t["choose_recipe"], list(SAMPLE_RECIPES.keys()))
    recipe = SAMPLE_RECIPES[selected]
    st.write(f"### {t['ingredients']}")
    for ing, base in recipe["ingredients"].items():
        unit = recipe["units"].get(ing, "count")
        st.write(f"• {smart_display(base, ing, unit)}")
        if st.session_state.allow_subs:
            st.text_input(t["use_instead"], key=f"sub_{ing}", placeholder="")

with tab3:
    st.subheader(t["missing_items"])
    st.info("Shopping list logic can be expanded next. Substitutions are saved when you type them.")

with tab4:
    st.subheader(t["recipes"])
    for name in SAMPLE_RECIPES:
        with st.expander(name):
            st.write(", ".join(SAMPLE_RECIPES[name]["ingredients"].keys()))

with tab5:
    st.subheader(t["helper_title"])
    st.write(t["add_inventory_first"] if st.session_state.inventory.empty else "Use the Meal Plan tab to substitute ingredients.")

st.caption("Language selection + measurement system toggle added.")
