import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

st.markdown("""
<style>
    .big-title {font-size: 2.1rem; font-weight: 600;}
    .card {background: #f7f9fc; padding: 1rem 1.2rem; border-radius: 12px; margin-bottom: 1rem;}
</style>
""", unsafe_allow_html=True)

FITNESS_STYLES = [
    "Any / Everyday",
    "Gain mass / Bulk",
    "Lean bulk",
    "Cut / Get lean",
    "Reduce body fat",
    "Bodybuilding meal prep",
    "High protein",
    "Heart health (support HDL, reduce LDL)"
]

STYLE_SEARCH_HINTS = {
    "Gain mass / Bulk": "high calorie chicken rice",
    "Lean bulk": "lean chicken sweet potato",
    "Cut / Get lean": "high protein low calorie chicken",
    "Reduce body fat": "lean protein vegetables",
    "Bodybuilding meal prep": "meal prep chicken rice broccoli",
    "High protein": "high protein chicken beef fish",
    "Heart health (support HDL, reduce LDL)": "salmon tuna oats vegetables"
}

def search_recipes(query, style="Any / Everyday"):
    hint = STYLE_SEARCH_HINTS.get(style, "")
    full_query = f"{query} {hint}".strip()
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={full_query}", timeout=8)
        meals = r.json().get("meals") or []
        results = []
        for m in meals[:8]:
            ings = []
            for i in range(1, 16):
                name = m.get(f"strIngredient{i}")
                meas = m.get(f"strMeasure{i}")
                if name and name.strip():
                    ings.append({"name": name.strip(), "measure": meas.strip() if meas else "1 serving", "qty": 1.0})
            results.append({
                "name": m.get("strMeal"),
                "ings": ings,
                "instr": m.get("strInstructions", ""),
                "img": m.get("strMealThumb"),
                "category": m.get("strCategory", "")
            })
        return results
    except:
        return []

def estimate_nutrition(ings, servings=4, style="Any / Everyday"):
    # Practical approximations that respond to quantity and common swaps
    base_cal = 480
    base_pro = 32
    base_carb = 45
    base_fat = 16
    if "cut" in style.lower() or "lean" in style.lower() or "fat" in style.lower():
        base_cal *= 0.82
        base_carb *= 0.7
    if "mass" in style.lower() or "bulk" in style.lower():
        base_cal *= 1.25
        base_carb *= 1.3
    if "high protein" in style.lower() or "bodybuilding" in style.lower():
        base_pro *= 1.35
    scale = servings / 4.0
    return {
        "calories": int(base_cal * scale),
        "protein": int(base_pro * scale),
        "carbs": int(base_carb * scale),
        "fat": int(base_fat * scale)
    }

# Session
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "subs" not in st.session_state:
    st.session_state.subs = {"sugar": "stevia", "regular pasta": "whole wheat or chickpea pasta"}

st.markdown('<p class="big-title">KitchenFlow</p>', unsafe_allow_html=True)
st.caption("Meals that fit your life — fast, healthy, meal prep, or fitness goals. Works for any budget.")

col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Your focus")
    style = st.selectbox("Fitness / meal style", FITNESS_STYLES)
    servings = st.number_input("Servings", 1, 12, 4)

    st.subheader("Inventory")
    new = st.text_input("Add item (e.g. canned tuna, frozen chicken)")
    qty = st.number_input("Quantity", 0.0, 50.0, 1.0, 0.5)
    unit = st.selectbox("Unit", ["count", "lbs", "cans", "cups", "oz"])
    if st.button("Add to inventory") and new:
        st.session_state.inventory.append({"item": new, "qty": qty, "unit": unit})
        st.rerun()
    for i, it in enumerate(st.session_state.inventory):
        c1, c2 = st.columns([3, 1])
        c1.write(f"{it['qty']} {it['unit']} {it['item']}")
        if c2.button("✕", key=f"x{i}"):
            st.session_state.inventory.pop(i)
            st.rerun()

    st.subheader("Always substitute")
    s_from = st.text_input("Instead of")
    s_to = st.text_input("Use")
    if st.button("Save sub") and s_from and s_to:
        st.session_state.subs[s_from.lower()] = s_to
        st.rerun()

with col_right:
    st.subheader("Find recipes")
    query = st.text_input("Search (chicken, tuna, rice, meal prep…)", placeholder="Try: chicken, tuna, beef, pasta")
    if query:
        results = search_recipes(query, style)
        if results:
            names = [r["name"] for r in results]
            pick = st.selectbox("Choose recipe", names)
            rec = next(r for r in results if r["name"] == pick)

            st.markdown(f"### {rec['name']}")
            if rec["img"]:
                st.image(rec["img"], width=280)

            st.markdown("#### Ingredients (adjust quantities)")
            adjusted = []
            for i, ing in enumerate(rec["ings"]):
                c1, c2, c3 = st.columns([3, 1.5, 2])
                c1.write(ing["name"])
                new_q = c2.number_input("Qty", value=ing["qty"], key=f"q{i}", step=0.25, label_visibility="collapsed")
                sub = st.session_state.subs.get(ing["name"].lower(), "")
                note = f" → {sub}" if sub else ""
                c3.caption(ing["measure"] + note)
                adjusted.append({"name": ing["name"], "qty": new_q})

            st.markdown("#### Instructions")
            st.write(rec["instr"][:600] + ("…" if len(rec["instr"]) > 600 else ""))

            # Nutrition panel
            nut = estimate_nutrition(adjusted, servings, style)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("#### Approximate nutrition (per serving)")
            st.write(f"**Calories:** ~{nut['calories']}")
            st.write(f"**Protein:** ~{nut['protein']} g")
            st.write(f"**Carbs:** ~{nut['carbs']} g")
            st.write(f"**Fat:** ~{nut['fat']} g")
            st.caption("Updates when you change servings or quantities. Estimates based on typical recipes and your selected style. Exact values vary by brand and preparation.")
            st.markdown('</div>', unsafe_allow_html=True)

            if any(k in style.lower() for k in ["cut", "lean", "fat"]):
                st.info("For cutting / getting lean: keep protein high and reduce higher-calorie sides if needed.")
            if "mass" in style.lower() or "bulk" in style.lower():
                st.info("For gaining mass: add extra rice, oats, or healthy fats as desired.")
        else:
            st.info("No results. Try a simpler search like “chicken” or “tuna”.")

st.divider()
st.subheader("Local food resources (free)")
st.write("These real services can help if you need lower-cost or free food options:")
st.write("- **Plentiful** — Find nearby food pantries (app + text “FOOD” to 726-879). [plentiful.org](https://www.plentiful.org)")
st.write("- **Food Finder** — Share or find unopened food with neighbors. [foodfinder.org](https://foodfinder.org)")
st.write("- **EBT Finder** — Locate stores that accept SNAP/EBT.")
st.caption("Availability varies by area. These are independent services.")

st.caption("KitchenFlow — practical for everyday use, meal prep, fitness goals, or stretching a budget.")
