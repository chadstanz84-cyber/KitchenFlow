import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide")

st.markdown("""
<style>
    .big-title {font-size: 2.1rem; font-weight: 600; margin-bottom: 0.3rem;}
    .card {background: #f7f9fc; padding: 1rem 1.2rem; border-radius: 12px; margin: 0.8rem 0;}
    .inv-item {padding: 0.4rem 0; border-bottom: 1px solid #eee;}
</style>
""", unsafe_allow_html=True)

ITEM_SUGGESTIONS = {
    "chicken": ["chicken breast", "chicken thighs", "chicken wings", "chicken drumsticks", "ground chicken", "whole chicken"],
    "beef": ["ground beef", "beef steak", "beef roast", "stew beef"],
    "tuna": ["canned tuna", "fresh tuna", "frozen tuna"],
    "onion": ["yellow onion", "white onion", "red onion"],
    "pepper": ["bell pepper", "red bell pepper", "green bell pepper"],
    "milk": ["whole milk", "2% milk", "skim milk", "almond milk"]
}

def guess_unit(name):
    n = name.lower()
    if any(x in n for x in ["milk", "water", "juice", "oil", "soda"]):
        return "gallons"
    if any(x in n for x in ["chicken", "beef", "pork", "turkey", "fish", "tuna", "salmon"]):
        return "lbs"
    if "garlic" in n:
        return "cloves"
    if any(x in n for x in ["onion", "pepper", "egg", "apple", "banana", "potato", "can"]):
        return "count"
    return "count"

def search_recipes(query):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}", timeout=8)
        meals = r.json().get("meals") or []
        results = []
        for m in meals[:8]:
            ings = []
            for i in range(1, 16):
                name = m.get(f"strIngredient{i}")
                meas = m.get(f"strMeasure{i}")
                if name and name.strip():
                    ings.append({"name": name.strip(), "measure": meas.strip() if meas else "to taste", "qty": 1.0})
            results.append({
                "name": m.get("strMeal"),
                "ings": ings,
                "instr": m.get("strInstructions", ""),
                "img": m.get("strMealThumb")
            })
        return results
    except:
        return []

def fuzzy_match(recipe_ings, inventory_items):
    inv_lower = [i["item"].lower() for i in inventory_items]
    matches = 0
    for ing in recipe_ings:
        ing_l = ing["name"].lower()
        if any(inv in ing_l or ing_l in inv for inv in inv_lower):
            matches += 1
    return matches, len(recipe_ings)

# Session
if "inventory" not in st.session_state:
    st.session_state.inventory = []
if "subs" not in st.session_state:
    st.session_state.subs = {"sugar": "stevia"}

st.markdown('<p class="big-title">KitchenFlow</p>', unsafe_allow_html=True)
st.caption("Clean inventory · Smart units · Recipes that match what you have")

left, right = st.columns([1, 1.6])

with left:
    st.subheader("Inventory")
    raw = st.text_input("Type an item", placeholder="chicken, milk, onion, tuna…")
    suggestions = []
    for key, opts in ITEM_SUGGESTIONS.items():
        if key in raw.lower():
            suggestions = opts
            break

    selected = raw
    if suggestions:
        selected = st.selectbox("Choose exact item", suggestions)

    unit_guess = guess_unit(selected)
    unit_opts = ["lbs", "count", "cups", "oz", "cloves", "gallons", "cans"]
    unit_idx = unit_opts.index(unit_guess) if unit_guess in unit_opts else 0

    c1, c2, c3 = st.columns(3)
    qty = c1.number_input("Qty", 0.0, 100.0, 1.0, 0.5)
    unit = c2.selectbox("Unit", unit_opts, index=unit_idx)
    form = c3.selectbox("Form", ["Fresh", "Frozen", "Canned", "Pantry"])

    if st.button("Add to inventory", use_container_width=True) and selected:
        st.session_state.inventory.append({
            "item": selected,
            "qty": qty,
            "unit": unit,
            "form": form
        })
        st.rerun()

    st.write("---")
    if not st.session_state.inventory:
        st.info("Add items you have. The unit will try to guess the most common one.")
    else:
        for i, it in enumerate(st.session_state.inventory):
            cols = st.columns([3, 1.2, 1])
            cols[0].write(f"**{it['item']}** ({it['form']})")
            new_q = cols[1].number_input(" ", value=float(it["qty"]), key=f"iq{i}", step=0.5, label_visibility="collapsed")
            if cols[2].button("Remove", key=f"rm{i}"):
                st.session_state.inventory.pop(i)
                st.rerun()
            if new_q != it["qty"]:
                st.session_state.inventory[i]["qty"] = new_q
                st.rerun()

    st.subheader("Always substitute")
    sf = st.text_input("Instead of")
    stt = st.text_input("Use")
    if st.button("Save") and sf and stt:
        st.session_state.subs[sf.lower()] = stt
        st.rerun()

with right:
    st.subheader("Recipes from your inventory")
    if st.session_state.inventory:
        # Fuzzy recipe ideas
        search_terms = list({it["item"].split()[0] for it in st.session_state.inventory})[:3]
        ideas = []
        for term in search_terms:
            ideas.extend(search_recipes(term))
        seen = set()
        shown = 0
        for rec in ideas:
            if rec["name"] in seen or shown >= 5:
                continue
            seen.add(rec["name"])
            match, total = fuzzy_match(rec["ings"], st.session_state.inventory)
            if total > 0 and match / total >= 0.35:
                with st.expander(f"{rec['name']} — matches ~{match} of your items"):
                    if rec["img"]:
                        st.image(rec["img"], width=200)
                    st.write("**Ingredients**")
                    for ing in rec["ings"][:8]:
                        sub = st.session_state.subs.get(ing["name"].lower(), "")
                        extra = f" (or {sub})" if sub else ""
                        st.write(f"• {ing['measure']} {ing['name']}{extra}")
                    st.write("**Instructions**")
                    st.write(rec["instr"][:400] + "…")
                shown += 1
        if shown == 0:
            st.info("Add a few more items to see recipe ideas that match your inventory.")
    else:
        st.info("Add inventory items on the left to see matching recipes.")

    st.subheader("Search any recipe")
    q = st.text_input("Search", placeholder="chicken, tuna, pasta…")
    if q:
        results = search_recipes(q)
        for rec in results[:4]:
            st.markdown(f"**{rec['name']}**")
            if rec["img"]:
                st.image(rec["img"], width=180)
            st.caption(rec["instr"][:200] + "…")
            st.divider()

st.caption("Smart unit guessing · Specific item choices · Fuzzy inventory matching for recipes")
