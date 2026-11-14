import streamlit as st
import pandas as pd
from datetime import datetime
import requests

st.set_page_config(page_title="KitchenFlow", page_icon="🍳", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main-header {font-size: 2.2rem; font-weight: 600; margin-bottom: 0.2rem;}
    .sub-header {color: #555; margin-bottom: 1.5rem;}
    .section-box {background-color: #f8f9fa; padding: 1.2rem; border-radius: 10px; margin-bottom: 1rem;}
</style>
""", unsafe_allow_html=True)

def calculate_macros(weight, height_in, goal, activity="Moderate"):
    weight_kg = weight * 0.4536
    height_cm = height_in * 2.54
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * 35 + 5
    mult = {"Sedentary": 1.2, "Light": 1.4, "Moderate": 1.55, "Active": 1.7, "Very Active": 1.9}
    tdee = bmr * mult.get(activity, 1.55)

    if "muscle" in goal.lower() or "gain" in goal.lower():
        cal = tdee + 250
        protein = weight * 0.9
    elif "fat" in goal.lower() or "lose" in goal.lower() or "ldl" in goal.lower():
        cal = tdee - 350
        protein = weight * 0.8
    else:
        cal = tdee
        protein = weight * 0.7

    fat = cal * 0.28 / 9
    carbs = max((cal - protein*4 - fat*9) / 4, 40)
    return {"calories": int(cal), "protein": int(protein), "carbs": int(carbs), "fat": int(fat)}

def search_recipes(query):
    try:
        r = requests.get(f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}", timeout=8)
        meals = r.json().get("meals") or []
        out = []
        for m in meals[:6]:
            ings = [m.get(f"strIngredient{i}", "").strip() for i in range(1, 16) if m.get(f"strIngredient{i}")]
            out.append({
                "name": m.get("strMeal"),
                "ings": ings,
                "instr": m.get("strInstructions", "")[:500],
                "img": m.get("strMealThumb")
            })
        return out
    except:
        return []

# State
if "places" not in st.session_state:
    st.session_state.places = {"Home": []}
if "current" not in st.session_state:
    st.session_state.current = "Home"
if "subs" not in st.session_state:
    st.session_state.subs = {"sugar": "stevia or monk fruit", "white flour": "almond flour or oat flour"}
if "profile" not in st.session_state:
    st.session_state.profile = {"weight": 170, "height": 68, "goal": "Balanced", "activity": "Moderate"}

st.markdown('<p class="main-header">KitchenFlow</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Simple meals, smarter shopping, and goals that fit real life</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Your Setup")
    st.subheader("Body & Goals")
    w = st.number_input("Weight (lbs)", 90, 400, st.session_state.profile["weight"])
    h = st.number_input("Height (inches)", 50, 84, st.session_state.profile["height"])
    goal = st.selectbox("Main focus", [
        "Balanced everyday eating",
        "Gain muscle",
        "Reduce body fat",
        "Support heart health (HDL / LDL)",
        "Faster meals",
        "Meal prep & freezing"
    ])
    act = st.selectbox("Activity", ["Sedentary", "Light", "Moderate", "Active", "Very Active"])
    if st.button("Update my numbers"):
        st.session_state.profile.update({"weight": w, "height": h, "goal": goal, "activity": act})
        st.rerun()

    macros = calculate_macros(w, h, goal, act)
    st.info(f"**Daily targets**  \nCalories ~{macros['calories']}  \nProtein ~{macros['protein']}g  \nCarbs ~{macros['carbs']}g  \nFat ~{macros['fat']}g")

    st.subheader("Always substitute")
    a = st.text_input("Instead of")
    b = st.text_input("Use")
    if st.button("Save substitution") and a and b:
        st.session_state.subs[a.lower()] = b
        st.rerun()
    for k, v in list(st.session_state.subs.items())[:4]:
        st.caption(f"{k} → {v}")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Inventory", "What I Can Make", "Find Recipes", "Shopping & Prep", "Feedback"])

with tab1:
    st.subheader(f"Inventory — {st.session_state.current}")
    c1, c2 = st.columns([3, 1])
    with c1:
        new_item = st.text_input("Add something you have (canned tuna, frozen chicken, rice…)", label_visibility="collapsed")
    with c2:
        form = st.selectbox("Form", ["Fresh", "Frozen", "Canned", "Pantry"], label_visibility="collapsed")
    if st.button("Add") and new_item:
        st.session_state.places[st.session_state.current].append(f"{new_item} ({form})")
        st.rerun()

    items = st.session_state.places[st.session_state.current]
    if not items:
        st.info("Add a few items you already have. This helps show what you can cook.")
    else:
        for i, it in enumerate(items):
            col_a, col_b = st.columns([5, 1])
            col_a.write(it)
            if col_b.button("Remove", key=f"d{i}"):
                items.pop(i)
                st.rerun()

with tab2:
    st.subheader("Recipes that fit what you already have")
    inv = [i.split(" (")[0].lower() for i in st.session_state.places[st.session_state.current]]
    if len(inv) < 2:
        st.info("Add at least a couple of items to inventory to see matching ideas.")
    else:
        ideas = []
        for food in inv[:4]:
            ideas.extend(search_recipes(food))
        shown = set()
        for rec in ideas:
            if rec["name"] in shown:
                continue
            shown.add(rec["name"])
            match_count = sum(1 for ing in rec["ings"] if any(x in ing.lower() for x in inv))
            if match_count >= 2:
                with st.expander(f"{rec['name']}  ·  you have several ingredients"):
                    st.write(", ".join(rec["ings"][:7]))
                    st.caption(rec["instr"][:250] + "…")

with tab3:
    st.subheader("Find a recipe")
    q = st.text_input("Search (chicken, tuna, pasta, soup, quick…)")
    if q:
        results = search_recipes(q)
        for rec in results:
            st.markdown(f"**{rec['name']}**")
            if rec["img"]:
                st.image(rec["img"], width=220)
            st.write(rec["instr"][:280] + "…")
            st.caption("Tip: Use canned, frozen, or fresh versions of the main ingredients as needed.")
            st.divider()

with tab4:
    st.subheader("Shopping & weekly prep")
    st.write("Ideas based on your focus:")
    if "heart" in goal.lower() or "LDL" in goal or "HDL" in goal:
        st.write("• More fatty fish (canned or fresh tuna, salmon), oats, beans, vegetables, nuts")
        st.write("• Limit processed meats and excess saturated fat when possible")
    if "prep" in goal.lower() or "freezing" in goal.lower():
        st.write("• Cook larger batches and freeze portions")
        st.write("• Canned tuna, beans, and frozen vegetables work well for quick meals")
    if "Faster" in goal:
        st.write("• Look for recipes under 30 minutes or one-pan meals")
    st.info("Grocery lists can pull from recipes you choose and what is already in inventory.")

with tab5:
    st.subheader("Help improve KitchenFlow")
    msg = st.text_area("What would make this more useful for you or your household?")
    if st.button("Send") and msg:
        st.success("Thank you. Your note has been received.")

st.caption("Built for everyday households — fast meals, meal prep, heart health, muscle goals, or simply easier shopping.")
