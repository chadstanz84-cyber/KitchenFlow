import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")
st.title("🍳 KitchenFlow — Meal Prep & Grocery Assistant")

# ---------- Session State ----------
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

# ---------- Sample Recipes ----------
SAMPLE_RECIPES = {
    "Simple Chicken Stir-Fry": {
        "main": "chicken",
        "base_qty": 1.5,
        "ingredients": {
            "chicken breast": 1.5,
            "broccoli": 2,
            "soy sauce": 0.25,
            "garlic": 3,
            "rice": 1.5
        },
        "units": {"chicken breast": "lbs", "broccoli": "cups", "soy sauce": "cup", "garlic": "cloves", "rice": "cups"},
        "nutrition_per_serving": {"protein": 35, "iron": 1.2, "magnesium": 40, "potassium": 450, "sodium": 650, "calories": 420}
    },
    "Beef & Vegetable Skillet": {
        "main": "beef",
        "base_qty": 1.0,
        "ingredients": {
            "ground beef": 1.0,
            "bell peppers": 2,
            "onion": 1,
            "tomato sauce": 1,
            "rice": 1
        },
        "units": {"ground beef": "lbs", "bell peppers": "count", "onion": "count", "tomato sauce": "cup", "rice": "cups"},
        "nutrition_per_serving": {"protein": 32, "iron": 3.1, "magnesium": 35, "potassium": 500, "sodium": 720, "calories": 480}
    }
}

def smart_display(qty, item, unit):
    item_lower = item.lower()
    if "onion" in item_lower:
        if qty <= 1.2:
            return "1 onion"
        elif qty <= 2.2:
            return "2 onions"
        else:
            return f"{round(qty)} onions"
    if "bell pepper" in item_lower or "pepper" in item_lower:
        n = round(qty)
        size = "medium" if n <= 2 else "large"
        return f"{n} {size} bell pepper{'s' if n > 1 else ''}"
    if "garlic" in item_lower:
        return f"{round(qty)} cloves garlic"
    if unit in ["lbs", "lb"]:
        if qty < 0.4:
            return f"about {qty:.1f} lb {item}"
        rounded = round(qty * 4) / 4
        if abs(rounded - qty) < 0.15:
            nice = str(rounded).replace(".0", "").replace(".5", "½").replace(".25", "¼").replace(".75", "¾")
            return f"about {nice} lbs {item}"
        return f"a little more than {round(qty,1)} lbs {item}"
    if unit in ["cups", "cup"]:
        rounded = round(qty * 4) / 4
        nice = str(rounded).replace(".0", "").replace(".5", "½").replace(".25", "¼").replace(".75", "¾")
        return f"about {nice} cup{'s' if rounded != 1 else ''} {item}"
    if unit == "count" or unit == "units":
        n = round(qty)
        return f"{n} {item}"
    return f"about {qty:.1f} {unit} {item}"

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Preferences")
    st.session_state.show_nutrition = st.toggle("Show nutrition details", value=st.session_state.show_nutrition)
    st.session_state.allow_subs = st.toggle("Allow easy substitutions", value=st.session_state.allow_subs)

    st.subheader("Allergies / Restrictions")
    new_allergy = st.text_input("Add allergy or restriction")
    if st.button("Add") and new_allergy:
        if new_allergy.lower() not in [a.lower() for a in st.session_state.allergies]:
            st.session_state.allergies.append(new_allergy)
    for a in st.session_state.allergies:
        col1, col2 = st.columns([3,1])
        col1.write(a)
        if col2.button("✕", key=f"del_{a}"):
            st.session_state.allergies.remove(a)
            st.rerun()

    st.subheader("Nutrition Goals (optional)")
    goals_options = ["Lower sodium", "Higher protein", "Higher iron", "Higher magnesium", "Higher potassium"]
    st.session_state.goals = st.multiselect("Active goals", goals_options, default=st.session_state.goals)

# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Inventory", "Meal Plan", "Shopping List", "Recipes", "Helper"])

with tab1:
    st.subheader("Your Inventory")
    with st.form("add_item"):
        c1, c2, c3, c4, c5 = st.columns(5)
        item = c1.text_input("Item")
        qty = c2.number_input("Quantity", min_value=0.0, step=0.1, value=1.0)
        unit = c3.selectbox("Unit", ["lbs", "cups", "count", "oz", "cloves"])
        loc = c4.selectbox("Location", ["Fridge", "Freezer", "Pantry"])
        exp = c5.date_input("Expiration", value=datetime.now() + timedelta(days=7))
        if st.form_submit_button("Add Item") and item:
            new_row = pd.DataFrame([{"Item": item, "Quantity": qty, "Unit": unit, "Location": loc, "Expiration": exp}])
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
            st.rerun()

    if not st.session_state.inventory.empty:
        edited = st.data_editor(st.session_state.inventory, num_rows="dynamic", use_container_width=True)
        st.session_state.inventory = edited
        soon = edited[edited["Expiration"] <= (datetime.now().date() + timedelta(days=3))]
        if not soon.empty:
            st.warning("Use soon: " + ", ".join(soon["Item"].tolist()))
    else:
        st.info("Add items you currently have.")

with tab2:
    st.subheader("Meal Suggestions")
    selected_recipe = st.selectbox("Choose a base recipe", list(SAMPLE_RECIPES.keys()))
    recipe = SAMPLE_RECIPES[selected_recipe]

    excess_qty = recipe["base_qty"]
    if not st.session_state.inventory.empty:
        matches = st.session_state.inventory[st.session_state.inventory["Item"].str.contains(recipe["main"], case=False, na=False)]
        if not matches.empty:
            excess_qty = float(matches.iloc[0]["Quantity"])
            st.success(f"Using the {smart_display(excess_qty, matches.iloc[0]['Item'], 'lbs')} you already have.")

    scale = excess_qty / recipe["base_qty"] if recipe["base_qty"] else 1
    st.write("### Ingredients")
    for ing, base in recipe["ingredients"].items():
        scaled = base * scale
        unit = recipe["units"].get(ing, "units")
        if any(a.lower() in ing.lower() for a in st.session_state.allergies):
            st.error(f"⚠️ Contains {ing} (matches allergy)")
            continue
        display_ing = ing
        if st.session_state.allow_subs and "Lower sodium" in st.session_state.goals and "soy sauce" in ing:
            display_ing = "low-sodium soy sauce or coconut aminos"
        st.write(f"- {smart_display(scaled, display_ing, unit)}")

    if st.session_state.show_nutrition:
        st.write("### Approximate Nutrition (per serving)")
        for k, v in recipe["nutrition_per_serving"].items():
            st.write(f"{k.title()}: ~{v * scale:.0f}")

with tab3:
    st.subheader("Shopping List (missing items)")
    needed = {}
    for name, recipe in SAMPLE_RECIPES.items():
        for ing, base in recipe["ingredients"].items():
            if any(a.lower() in ing.lower() for a in st.session_state.allergies):
                continue
            have = 0
            if not st.session_state.inventory.empty:
                matches = st.session_state.inventory[st.session_state.inventory["Item"].str.contains(ing.split()[0], case=False, na=False)]
                if not matches.empty:
                    have = matches["Quantity"].sum()
            missing = max(0, base - have)
            if missing > 0.05:
                needed[ing] = needed.get(ing, 0) + missing

    if needed:
        for item, qty in needed.items():
            unit = SAMPLE_RECIPES["Simple Chicken Stir-Fry"]["units"].get(item, "count")
            if "beef" in item or "chicken" in item:
                unit = "lbs"
            st.write(f"• {smart_display(qty, item, unit)}")
    else:
        st.success("You have everything needed for the sample recipes!")

with tab4:
    st.subheader("Sample Recipes")
    for name, r in SAMPLE_RECIPES.items():
        with st.expander(name):
            st.write(f"Main protein base: {r['base_qty']} lbs")
            st.write("Ingredients:", ", ".join(r["ingredients"].keys()))

with tab5:
    st.subheader("Helper")
    st.write("Simple suggestions based on what you have:")
    if st.session_state.inventory.empty:
        st.info("Add some inventory items first and I’ll give you tips.")
    else:
        items = st.session_state.inventory["Item"].str.lower().tolist()
        if any("chicken" in i for i in items):
            st.write("• You have chicken — the stir-fry recipe can use it up.")
        if any("onion" in i for i in items):
            st.write("• Onion is useful in almost every recipe. Keep it.")
        if any("beef" in i for i in items):
            st.write("• Ground beef works well in the skillet recipe.")
        st.write("• Tip: Add more items to inventory and the shopping list will shrink.")

st.caption("Updated version — simpler measurements + basic helper.")
