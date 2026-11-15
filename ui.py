"""
FitCoach AI — Streamlit UI
Run locally:  streamlit run ui.py
Cloud:        Deployed via Streamlit Community Cloud (GitHub)
              FastAPI starts automatically in a background thread.
"""
import os
import streamlit as st
import requests
import json
import threading
import time

# ── Load secrets (Streamlit Cloud) or fall back to .env (local) ──────────────
try:
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    if "PINECONE_API_KEY" in st.secrets:
        os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
    if "DB_PATH" in st.secrets:
        os.environ["DB_PATH"] = st.secrets["DB_PATH"]
except Exception:
    pass  # local dev: keys already loaded via .env / environment

# ── Auto-start FastAPI in background thread (Streamlit Cloud) ─────────────────
def _start_api():
    import uvicorn
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="error")

if "api_thread_started" not in st.session_state:
    t = threading.Thread(target=_start_api, daemon=True)
    t.start()
    st.session_state["api_thread_started"] = True
    time.sleep(2)  # give FastAPI time to initialise

API = "http://localhost:8080"

st.set_page_config(
    page_title="FitCoach AI",
    page_icon="🏋️",
    layout="wide",
)

# ── Global CSS (beige palette + card polish) ──────────────────────────────────
st.markdown("""
<style>
/* ---- page & sidebar ---- */
[data-testid="stAppViewContainer"] { background:#F5EDD6; }
[data-testid="stSidebar"]          { background:#E8D5B5 !important; }
[data-testid="stSidebar"] * { color:#3D2E1A !important; }

/* ---- main heading accent ---- */
h1, h2, h3 { color:#3D2E1A !important; }
h1 { border-bottom: 3px solid #B5793C; padding-bottom:8px; }

/* ---- cards ---- */
.fc-card {
  background:#FFFBF2;
  border:1px solid #DFC99A;
  border-radius:12px;
  padding:18px 20px;
  margin-bottom:14px;
}
.fc-card h4 { color:#B5793C !important; margin:0 0 6px; font-size:15px; }

/* ---- stat tiles ---- */
.stat-row { display:flex; gap:12px; margin-bottom:16px; flex-wrap:wrap; }
.stat-tile {
  flex:1; min-width:130px;
  background:#FFFBF2;
  border:1px solid #DFC99A;
  border-radius:10px;
  padding:14px 16px;
  text-align:center;
}
.stat-tile .val { font-size:26px; font-weight:700; color:#B5793C; }
.stat-tile .lbl { font-size:11px; color:#8B6F47; text-transform:uppercase; letter-spacing:.05em; }
.stat-tile .chg { font-size:11px; margin-top:3px; }
.up { color:#5C8A5C; } .dn { color:#C05050; }

/* ---- tag pills ---- */
.tag {
  display:inline-block;
  padding:3px 10px;
  border-radius:14px;
  font-size:11px;
  font-weight:700;
  margin:2px 3px 2px 0;
}
.tag-hi  { background:#D4EDD4; color:#2D6A2D; }
.tag-med { background:#FDE8C4; color:#7A4800; }
.tag-lo  { background:#FFECEC; color:#B00;    }

/* ---- buttons ---- */
.stButton > button {
  background:#B5793C !important;
  color:#fff !important;
  border:none !important;
  border-radius:8px !important;
  font-weight:600 !important;
}
.stButton > button:hover { background:#8B5C2A !important; }

/* ---- chat bubbles ---- */
.bubble-wrap { display:flex; flex-direction:column; gap:8px; }
.bubble {
  padding:10px 14px;
  border-radius:12px;
  font-size:13px;
  line-height:1.5;
  max-width:80%;
}
.b-agent { background:#EDE0C8; color:#3D2E1A; border-bottom-left-radius:3px; }
.b-user  { background:#B5793C; color:#fff;    border-bottom-right-radius:3px; margin-left:auto; }
.b-lbl   { font-size:10px; color:#8B6F47; margin-bottom:2px; }

/* ---- hide Streamlit chrome ---- */
#MainMenu, footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── SVG cartoons ──────────────────────────────────────────────────────────────
CART = {
"welcome": """<svg viewBox="0 0 120 120" width="110" xmlns="http://www.w3.org/2000/svg">
  <circle cx="60" cy="28" r="16" fill="#B5793C"/>
  <ellipse cx="60" cy="75" rx="22" ry="28" fill="#E8D5B5" stroke="#B5793C" stroke-width="2"/>
  <line x1="38" y1="60" x2="15" y2="85" stroke="#B5793C" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="82" y1="60" x2="105" y2="85" stroke="#B5793C" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="48" y1="100" x2="42" y2="118" stroke="#B5793C" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="72" y1="100" x2="78" y2="118" stroke="#B5793C" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="53" cy="27" r="3" fill="#3D2E1A"/>
  <circle cx="67" cy="27" r="3" fill="#3D2E1A"/>
  <path d="M53 36 Q60 42 67 36" stroke="#3D2E1A" stroke-width="2" fill="none" stroke-linecap="round"/>
</svg>""",

"squat": """<svg viewBox="0 0 120 100" width="90" xmlns="http://www.w3.org/2000/svg">
  <circle cx="60" cy="12" r="10" fill="#B5793C"/>
  <line x1="25" y1="40" x2="95" y2="40" stroke="#8B5C28" stroke-width="7" stroke-linecap="round"/>
  <circle cx="18" cy="40" r="8" fill="#5C8A5C" stroke="#8B5C28" stroke-width="2"/>
  <circle cx="102" cy="40" r="8" fill="#5C8A5C" stroke="#8B5C28" stroke-width="2"/>
  <line x1="60" y1="22" x2="60" y2="40" stroke="#B5793C" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="40" y1="32" x2="80" y2="32" stroke="#B5793C" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="60" y1="40" x2="42" y2="72" stroke="#B5793C" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="60" y1="40" x2="78" y2="72" stroke="#B5793C" stroke-width="3.5" stroke-linecap="round"/>
  <ellipse cx="42" cy="73" rx="5" ry="3" fill="#B5793C"/>
  <ellipse cx="78" cy="73" rx="5" ry="3" fill="#B5793C"/>
</svg>""",

"run": """<svg viewBox="0 0 120 100" width="90" xmlns="http://www.w3.org/2000/svg">
  <circle cx="75" cy="14" r="10" fill="#B5793C"/>
  <line x1="75" y1="24" x2="65" y2="52" stroke="#B5793C" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="55" y1="34" x2="85" y2="38" stroke="#B5793C" stroke-width="3" stroke-linecap="round"/>
  <line x1="55" y1="34" x2="38" y2="28" stroke="#B5793C" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="85" y1="38" x2="100" y2="30" stroke="#B5793C" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="65" y1="52" x2="45" y2="72" stroke="#B5793C" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="65" y1="52" x2="82" y2="68" stroke="#B5793C" stroke-width="3.5" stroke-linecap="round"/>
  <line x1="45" y1="72" x2="30" y2="65" stroke="#B5793C" stroke-width="3" stroke-linecap="round"/>
  <line x1="82" y1="68" x2="98" y2="78" stroke="#B5793C" stroke-width="3" stroke-linecap="round"/>
  <path d="M10 88 Q60 80 110 88" stroke="#DFC99A" stroke-width="2" fill="none" stroke-dasharray="4,3"/>
</svg>""",

"meal": """<svg viewBox="0 0 120 110" width="90" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="60" cy="72" rx="40" ry="28" fill="#FFFBF2" stroke="#DFC99A" stroke-width="2"/>
  <ellipse cx="60" cy="68" rx="32" ry="22" fill="#F5EDD6"/>
  <circle cx="50" cy="62" r="8" fill="#5C8A5C"/>
  <circle cx="68" cy="58" r="6" fill="#B5793C"/>
  <circle cx="60" cy="74" r="5" fill="#E8C84A"/>
  <circle cx="44" cy="74" r="4" fill="#C05050"/>
  <line x1="20" y1="44" x2="20" y2="72" stroke="#8B6F47" stroke-width="3" stroke-linecap="round"/>
  <line x1="20" y1="44" x2="15" y2="36" stroke="#8B6F47" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="20" y1="44" x2="20" y2="36" stroke="#8B6F47" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="20" y1="44" x2="25" y2="36" stroke="#8B6F47" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="100" y1="36" x2="100" y2="72" stroke="#8B6F47" stroke-width="3" stroke-linecap="round"/>
  <path d="M96 36 Q100 50 104 36" stroke="#8B6F47" stroke-width="2.5" fill="none"/>
</svg>""",

"progress": """<svg viewBox="0 0 120 100" width="90" xmlns="http://www.w3.org/2000/svg">
  <line x1="15" y1="85" x2="110" y2="85" stroke="#DFC99A" stroke-width="2"/>
  <line x1="15" y1="85" x2="15" y2="15" stroke="#DFC99A" stroke-width="2"/>
  <polyline points="20,75 40,60 60,50 80,38 100,22"
    fill="none" stroke="#B5793C" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M20,75 40,60 60,50 80,38 100,22 110,85 10,85 Z"
    fill="#B5793C" opacity=".12"/>
  <circle cx="20"  cy="75" r="4" fill="#B5793C" stroke="#FFFBF2" stroke-width="1.5"/>
  <circle cx="40"  cy="60" r="4" fill="#B5793C" stroke="#FFFBF2" stroke-width="1.5"/>
  <circle cx="60"  cy="50" r="4" fill="#B5793C" stroke="#FFFBF2" stroke-width="1.5"/>
  <circle cx="80"  cy="38" r="4" fill="#B5793C" stroke="#FFFBF2" stroke-width="1.5"/>
  <circle cx="100" cy="22" r="5" fill="#5C8A5C" stroke="#FFFBF2" stroke-width="2"/>
  <text x="93" y="17" font-size="9" fill="#5C8A5C" font-weight="700">↓1.6kg</text>
</svg>""",

"chat": """<svg viewBox="0 0 120 100" width="90" xmlns="http://www.w3.org/2000/svg">
  <rect x="8"  y="8"  width="68" height="40" rx="10" fill="#EDE0C8" stroke="#DFC99A" stroke-width="1.5"/>
  <polygon points="18,48 8,62 28,48" fill="#EDE0C8" stroke="#DFC99A" stroke-width="1.5"/>
  <circle cx="30" cy="28" r="4" fill="#B5793C"/>
  <circle cx="44" cy="28" r="4" fill="#B5793C"/>
  <circle cx="58" cy="28" r="4" fill="#B5793C"/>
  <rect x="44" y="50" width="68" height="36" rx="10" fill="#B5793C"/>
  <polygon points="102,86 112,98 92,86" fill="#B5793C"/>
  <line x1="54" y1="63" x2="102" y2="63" stroke="#FFFBF2" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="54" y1="73" x2="88"  y2="73" stroke="#FFFBF2" stroke-width="2.5" stroke-linecap="round"/>
</svg>""",

"sync": """<svg viewBox="0 0 120 100" width="90" xmlns="http://www.w3.org/2000/svg">
  <rect x="30" y="10" width="60" height="80" rx="10" fill="#FFFBF2" stroke="#DFC99A" stroke-width="2"/>
  <rect x="38" y="22" width="44" height="36" rx="4" fill="#F5EDD6"/>
  <polyline points="42,48 52,36 60,44 70,30 78,38"
    fill="none" stroke="#C05050" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="60" cy="75" r="5" fill="#DFC99A"/>
  <circle cx="18" cy="50" r="10" fill="#5C8A5C" opacity=".2" stroke="#5C8A5C" stroke-width="1.5"/>
  <text x="13" y="54" font-size="11" fill="#5C8A5C" font-weight="700">♡</text>
  <circle cx="102" cy="38" r="8" fill="#B5793C" opacity=".2" stroke="#B5793C" stroke-width="1.5"/>
  <text x="97"  y="43" font-size="10" fill="#B5793C" font-weight="700">👣</text>
</svg>""",
}

# ── helpers ───────────────────────────────────────────────────────────────────
def svg(key, center=False):
    align = "text-align:center;" if center else ""
    st.markdown(f'<div style="{align}">{CART[key]}</div>', unsafe_allow_html=True)

def post(path, body):
    try:
        r = requests.post(f"{API}{path}", json=body, timeout=30)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def get(path):
    try:
        r = requests.get(f"{API}{path}", timeout=10)
        return r.json(), r.status_code
    except Exception as e:
        return {"error": str(e)}, 500

def card(content_fn):
    st.markdown('<div class="fc-card">', unsafe_allow_html=True)
    content_fn()
    st.markdown('</div>', unsafe_allow_html=True)

def render_workout(workout: dict):
    """Render workout plan as readable day-by-day cards."""
    if not workout:
        st.info("No workout plan available.")
        return
    days = workout.get("days", workout)
    week_start = workout.get("week_start", "")
    if week_start:
        st.caption(f"Week starting {week_start}")
    for day, sessions in days.items():
        with st.expander(f"📅 {day}", expanded=False):
            if not isinstance(sessions, list):
                sessions = [sessions]
            for session in sessions:
                muscle = session.get("muscle_group", "").replace("_", " ").title()
                exercises = session.get("exercises", [])
                if muscle:
                    st.markdown(f"**💪 {muscle}**")
                for ex in exercises:
                    name  = ex.get("name", "Exercise")
                    sets  = ex.get("sets", "")
                    reps  = ex.get("reps", "")
                    rest  = ex.get("rest_sec", "")
                    parts = []
                    if sets: parts.append(f"{sets} sets")
                    if reps: parts.append(f"{reps} reps")
                    if rest: parts.append(f"{rest}s rest")
                    detail = " · ".join(parts)
                    st.markdown(
                        f'<div class="fc-card" style="padding:10px 14px;margin-bottom:6px;">'
                        f'<strong>{name}</strong>'
                        f'<span style="color:#8B6F47;font-size:12px;margin-left:10px;">{detail}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

def render_meals(meals: dict):
    """Render meal plan as readable cards."""
    if not meals:
        st.info("No meal plan available.")
        return
    meal_icons = {"breakfast": "🌅", "lunch": "☀️", "dinner": "🌙", "snack": "🍎"}
    for meal_name, meal_data in meals.items():
        icon = meal_icons.get(meal_name.lower(), "🍽️")
        label = meal_name.replace("_", " ").title()
        if isinstance(meal_data, dict):
            items = meal_data.get("items", [])
            kcal  = meal_data.get("kcal", meal_data.get("calories", ""))
        elif isinstance(meal_data, list):
            items = meal_data
            kcal  = ""
        else:
            items = [str(meal_data)]
            kcal  = ""
        foods = ", ".join(items) if items else "—"
        kcal_str = f" · **{kcal} kcal**" if kcal else ""
        st.markdown(
            f'<div class="fc-card" style="padding:12px 16px;margin-bottom:8px;">'
            f'<span style="font-size:18px;">{icon}</span> '
            f'<strong style="color:#B5793C;">{label}</strong>{kcal_str}<br>'
            f'<span style="font-size:13px;color:#3D2E1A;">{foods}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

def render_plan(plan: dict):
    """Render a full plan (workout + meals) side by side."""
    workout = plan.get("workout", {})
    meals   = plan.get("meals", plan.get("nutrition", {}))
    # If plan itself looks like a workout (has "days") use it directly
    if "days" in plan and not workout:
        workout = plan
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏋️ Workout Plan")
        render_workout(workout)
    with col2:
        st.subheader("🥗 Meal Plan")
        render_meals(meals)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏋️ FitCoach AI")
    st.caption("AI-based Exercise & Diet Planning")
    st.divider()
    user_id = st.text_input("User ID", value="user1", key="uid")
    page = st.radio("Navigate", [
        "🚀  Onboard",
        "📋  My Plan",
        "❤️  Health Sync",
        "🏋️  Log Workout",
        "🥗  Log Meal",
        "📊  Progress",
        "💬  Coach Chat",
    ])
    st.divider()
    try:
        requests.get(f"{API}/health", timeout=2)
        st.success("Server online ✓")
    except Exception:
        st.error("Server offline — run: uvicorn main:app --reload")

# ══════════════════════════════════════════════════════════════════════════════
if "🚀" in page:
    col_img, col_hd = st.columns([1, 5])
    with col_img: svg("welcome")
    with col_hd:
        st.title("Onboard a New User")
        st.caption("Creates profile, generates workout + meal plan with GPT-4o, sends welcome nudge.")

    with st.form("onboard"):
        c1, c2, c3 = st.columns(3)
        with c1:
            uid   = st.text_input("User ID", value=user_id)
            name  = st.text_input("Full Name", value="Jey")
            age   = st.number_input("Age", 10, 100, 30)
        with c2:
            weight = st.number_input("Weight (kg)", 30.0, 250.0, 70.0, 0.5)
            height = st.number_input("Height (cm)", 100.0, 250.0, 165.0, 0.5)
            sex    = st.selectbox("Sex", ["female", "male"])
        with c3:
            goal     = st.selectbox("Goal", ["lose_weight", "build_muscle", "maintain", "endurance"])
            activity = st.selectbox("Activity Level", ["sedentary", "light", "moderate", "active", "very_active"])
            restrict = st.multiselect("Dietary Restrictions", ["vegetarian", "vegan", "gluten_free", "dairy_free", "nut_free"])
        injury = st.text_area("Injury Notes (optional)", height=60)
        submitted = st.form_submit_button("🚀 Create User & Generate Plan", use_container_width=True)

    if submitted:
        body = {"id": uid, "name": name, "age": age, "weight_kg": weight,
                "height_cm": height, "sex": sex, "goal": goal, "activity": activity,
                "dietary_restrictions": restrict, "injury_notes": injury or ""}
        with st.spinner("GPT-4o agents are generating your plan…"):
            data, code = post("/users", body)
        if code == 200:
            st.success(f"✅ {data.get('message', 'User created!')}  — switch to **My Plan** to view your full plan.")
            plan = data.get("plan", {})
            if plan:
                st.session_state["cached_plan"] = plan
                render_plan(plan)
        else:
            st.error(f"Error {code}: {data}")

# ══════════════════════════════════════════════════════════════════════════════
elif "📋" in page:
    col_img, col_hd = st.columns([1, 5])
    with col_img: svg("squat")
    with col_hd:
        st.title("My Current Plan")
        st.caption("Workout + meal plan generated by GPT-4o Planner & Nutrition agents.")

    # Show cached plan from onboarding, or fetch fresh
    if "cached_plan" in st.session_state:
        render_plan(st.session_state["cached_plan"])

    if st.button("🔄 Refresh Plan", use_container_width=False):
        data, code = get(f"/users/{user_id}/plan")
        if code == 200:
            plan = data.get("plan") or data
            st.session_state["cached_plan"] = plan
            render_plan(plan)
            st.caption(f"Plan created: {data.get('created_at', 'unknown')}")
        else:
            st.error(f"Error {code}: {data}")

# ══════════════════════════════════════════════════════════════════════════════
elif "❤️" in page:
    col_img, col_hd = st.columns([1, 5])
    with col_img: svg("sync")
    with col_hd:
        st.title("Health Sync")
        st.caption("Simulates an hourly push from HealthKit (iOS) / Health Connect (Android).")

    st.markdown("""
    <div class="stat-row">
      <div class="stat-tile"><div class="val">👣</div><div class="lbl">Steps</div></div>
      <div class="stat-tile"><div class="val">❤️</div><div class="lbl">Heart Rate</div></div>
      <div class="stat-tile"><div class="val">😴</div><div class="lbl">Sleep</div></div>
      <div class="stat-tile"><div class="val">🔥</div><div class="lbl">Cal Burned</div></div>
    </div>""", unsafe_allow_html=True)

    with st.form("sync"):
        c1, c2 = st.columns(2)
        with c1:
            steps    = st.number_input("Steps", 0, 50000, 4200)
            hr       = st.number_input("Heart Rate (bpm)", 30, 220, 72)
        with c2:
            sleep    = st.number_input("Sleep (hours)", 0.0, 24.0, 6.5, 0.5)
            calories = st.number_input("Calories Burned", 0, 5000, 320)
        hrv = st.number_input("HRV (ms, optional — 0 to skip)", 0, 200, 0)
        submitted = st.form_submit_button("❤️ Sync Health Data", use_container_width=True)

    if submitted:
        body = {"steps": steps, "heart_rate_bpm": hr, "sleep_hours": sleep, "calories_burned": calories}
        if hrv: body["hrv_ms"] = hrv
        with st.spinner("Progress Tracker analysing data with GPT-4o…"):
            data, code = post(f"/users/{user_id}/health-sync", body)
        if code == 200:
            st.success("Sync complete")
            st.json(data)
        else:
            st.error(f"Error {code}: {data}")

# ══════════════════════════════════════════════════════════════════════════════
elif "🏋️" in page:
    col_img, col_hd = st.columns([1, 5])
    with col_img: svg("run")
    with col_hd:
        st.title("Log Workout")
        st.caption("Injury keywords trigger automatic plan adaptation by the GPT-4o Planner Agent.")

    st.markdown("""
    <div style="display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap;">
      <span class="tag tag-hi">HIGH autonomy: plan adapt</span>
      <span class="tag tag-lo">LOW autonomy: health alert</span>
      <span class="tag tag-med">MEDIUM: coaching nudge</span>
    </div>""", unsafe_allow_html=True)

    with st.form("log_workout"):
        skipped  = st.toggle("Skipped workout?", False)
        reason   = st.text_input("Skip reason", placeholder="e.g. knee pain, feeling tired") if skipped else ""
        duration = 0 if skipped else st.slider("Duration (minutes)", 10, 180, 45)
        ex_done  = [] if skipped else st.text_area(
            "Exercises completed (one per line)", "Push-ups x3\nPull-ups x3\nPlank 60s"
        ).splitlines()
        intensity = st.select_slider("Perceived Intensity", ["easy", "moderate", "hard", "max"], "moderate")
        notes     = st.text_area("Notes", height=55)
        submitted = st.form_submit_button("🏋️ Log Workout", use_container_width=True)

    if submitted:
        body = {"skipped": skipped, "skip_reason": reason, "duration_minutes": duration,
                "exercises_completed": ex_done, "perceived_intensity": intensity, "notes": notes}
        with st.spinner("Agent processing…"):
            data, code = post(f"/users/{user_id}/log-workout", body)
        if code == 200:
            st.success("Workout logged!")
            st.json(data)
        else:
            st.error(f"Error {code}: {data}")

# ══════════════════════════════════════════════════════════════════════════════
elif "🥗" in page:
    col_img, col_hd = st.columns([1, 5])
    with col_img: svg("meal")
    with col_hd:
        st.title("Log Meal")
        st.caption("Nutrition Agent checks your daily calorie target and sends a nudge if you're under.")

    with st.form("log_meal"):
        meal_type = st.selectbox("Meal", ["breakfast", "lunch", "dinner", "snack"])
        items     = st.text_area("Foods eaten (one per line)", "oats with berries\nprotein shake").splitlines()
        kcal      = st.number_input("Estimated Calories", 0, 3000, 450)
        notes     = st.text_area("Notes", height=55)
        submitted = st.form_submit_button("🥗 Log Meal", use_container_width=True)

    if submitted:
        body = {"meal_type": meal_type, "items": items, "estimated_calories": kcal, "notes": notes}
        with st.spinner("Nutrition Agent processing…"):
            data, code = post(f"/users/{user_id}/log-meal", body)
        if code == 200:
            st.success("Meal logged!")
            st.json(data)
        else:
            st.error(f"Error {code}: {data}")

# ══════════════════════════════════════════════════════════════════════════════
elif "📊" in page:
    col_img, col_hd = st.columns([1, 5])
    with col_img: svg("progress")
    with col_hd:
        st.title("Progress")
        st.caption("Workout logs, meal logs, health signals, and agent notifications.")

    days = st.slider("Days to look back", 1, 30, 7)
    if st.button("📊 Load Progress", use_container_width=False):
        data, code = get(f"/users/{user_id}/progress?days={days}")
        if code == 200:
            tabs = st.tabs(["🏋️ Workouts", "🥗 Meals", "❤️ Health Signals", "🔔 Notifications"])
            with tabs[0]:
                logs = data.get("workout_logs", [])
                st.write(f"**{len(logs)}** workout log(s)")
                for l in logs:
                    with st.expander(f"{l.get('logged_at','?')} — {'⏭ skipped' if l.get('skipped') else '✅ completed'}"):
                        st.json(l)
            with tabs[1]:
                logs = data.get("meal_logs", [])
                st.write(f"**{len(logs)}** meal log(s)")
                for l in logs:
                    with st.expander(f"{l.get('logged_at','?')} — {l.get('meal_type','?')}"):
                        st.json(l)
            with tabs[2]:
                sigs = data.get("health_signals", [])
                st.write(f"**{len(sigs)}** health signal(s)")
                for s in sigs:
                    with st.expander(f"{s.get('recorded_at','?')}"):
                        st.json(s)
            with tabs[3]:
                notifs, nc = get(f"/users/{user_id}/notifications")
                if nc == 200:
                    for n in notifs:
                        icon = "🔴" if n.get("level") == "low" else "🟡" if n.get("level") == "medium" else "🟢"
                        st.markdown(f"{icon} **{n.get('type','').replace('_',' ').title()}** · `{n.get('sent_at','')}`")
                        st.caption(n.get("message",""))
        else:
            st.error(f"Error {code}: {data}")

# ══════════════════════════════════════════════════════════════════════════════
elif "💬" in page:
    col_img, col_hd = st.columns([1, 5])
    with col_img: svg("chat")
    with col_hd:
        st.title("Chat with Your Coach")
        st.caption("GPT-4o Coach Agent — context-aware replies using your plan, logs and health signals.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Render history as styled bubbles
    bubbles_html = '<div class="bubble-wrap">'
    for m in st.session_state.messages:
        if m["role"] == "user":
            bubbles_html += f'<div class="b-lbl" style="text-align:right">You</div><div class="bubble b-user">{m["content"]}</div>'
        else:
            bubbles_html += f'<div class="b-lbl">🤖 FitCoach AI</div><div class="bubble b-agent">{m["content"]}</div>'
    bubbles_html += '</div>'
    st.markdown(bubbles_html, unsafe_allow_html=True)

    prompt = st.chat_input("Ask your coach anything…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("Coach is thinking…"):
            data, code = post(f"/users/{user_id}/chat", {"message": prompt})
        reply = data.get("reply", str(data)) if code == 200 else f"Error {code}: {data}"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()
