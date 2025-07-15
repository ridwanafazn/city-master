import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("Workout Recommendation")

# ========== DATA (tabel referensi) ==========
BODY_PARTS = {
    "Neck": ["sternocleidomastoid", "splenius capitis", "splenius cervicis"],
    "Shoulders": ["front deltoids", "side deltoids", "rear deltoids"],
    "Chest": ["upper chest", "middle chest", "lower chest"],
    "Back": ["upper traps", "lower traps", "rotator cuff", "teres major", "lats", "erector spinae"],
    "Abs": ["rectus abdominis", "obliques", "serratus"],
    "Biceps": ["biceps brachii", "brachialis"],
    "Triceps": ["long head", "lateral head", "medial head"],
    "Forearms": ["brachioradialis", "flexors", "extensors"],
    "Glutes": ["gluteus maximus", "gluteus medius", "gluteus minimus"],
    "Quadriceps": ["rectus femoris", "vastus lateralis", "vastus medialis", "vastus intermedius"],
    "Hamstrings": ["biceps femoris", "semitendinosus", "semimembranosus"],
    "Calves": ["gastrocnemius", "soleus"],
    "Cardio": ["cardio"],
}

EQUIPMENTS = [
    "dumbbell", "barbell", "body weight", "cable", "smith machine",
    "leverage machine", "weighted", "kettlebell", "treadmill",
    "chest press machine", "exercise bike", "trap bar", "wheel roller",
    "ez barbell", "sled machine", "rope", "elliptical machine",
]

INJURY_OPTIONS = list(BODY_PARTS.keys())      # gunakan body‑part utama sebagai opsi cedera

def render_glossary():
    rows = []
    for bp, muscles in BODY_PARTS.items():
        badges = " ".join(
            f"<span class='copy-text' data-text='{m}'>{m.title()}</span>"
            for m in muscles
        )
        rows.append(f"<tr><td class='bp'>{bp}</td><td>{badges}</td></tr>")

    table_html = "<table class='glossary-table'>" + "".join(rows) + "</table>"

    components.html(
        f"""
        <style>
        .glossary-table {{
            border-collapse: collapse;
            width: 100%;
            color: #ffffff;
            font-size: 0.9rem;
        }}
        .glossary-table td {{
            border: 1px solid #ffffff33;
            padding: 6px 8px;
            vertical-align: top;
        }}
        .glossary-table .bp {{
            font-weight: bold;
            white-space: nowrap;
        }}
        .copy-text {{
            cursor: pointer;
            display: inline-block;
            margin: 2px 4px;
            padding: 4px 8px;
            border-radius: 5px;
            background: #333333;
            color: #ffffff;
            font-size: 0.9rem;
            transition: background 0.2s;
        }}
        .copy-text:hover {{
            background: #555555;
        }}
        .copy-text.copied {{
            background: #2ecc71;
            color: #000000;
        }}
        </style>

        <div id="glossary">{table_html}</div>

        <script>
        const items = document.querySelectorAll('#glossary .copy-text');
        items.forEach(el => {{
            el.addEventListener('click', () => {{
                const txt = el.dataset.text;
                navigator.clipboard.writeText(txt);
                el.classList.add('copied');
                const original = el.innerText;
                el.innerText = 'Copied!';
                setTimeout(() => {{
                    el.innerText = original.charAt(0).toUpperCase() + original.slice(1);
                    el.classList.remove('copied');
                }}, 1000);
            }});
        }});
        </script>
        """,
        height=400,
        scrolling=True,
    )

with st.expander("Muscle Glossary", expanded=False):
    render_glossary()


# ========== FORM ========== 
with st.form("input_form"):
    col1, col2 = st.columns(2)

    # ----- KIRI : User Data ----- 
    with col1:
        st.header("User Data")
        st.markdown("<hr style='margin-top: 0px; margin-bottom: 10px;'>", unsafe_allow_html=True) 
        gender_label = st.selectbox("Gender", ["Male", "Female"])
        gender = gender_label.lower()  # payload tetap: "male" / "female" 

        height_cm = st.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=165.0, step=0.5)
        weight_kg = st.number_input("Weight (kg)", min_value=35.0, max_value=200.0, value=55.0, step=0.5)

    # ----- KANAN : Exercise Preferences ----- 
    with col2:
        st.header("Exercise Preferences")
        st.markdown("<hr style='margin-top: 0px; margin-bottom: 10px;'>", unsafe_allow_html=True)

        preferred_body_part = st.multiselect(
            label="Preferred Body Parts (optional)",
            options=[bp.title() for bp in BODY_PARTS.keys()]
        )
        preferred_body_part = [bp.lower() for bp in preferred_body_part]

        preferred_equipment = st.multiselect(
            label="Preferred Equipment (optional)",
            options=[e.title() for e in EQUIPMENTS]
        )

        days_options = ["Choose..."] + [1, 2, 3, 4, 5]
        available_days_choice = st.selectbox(
            "Available days per week",
            options=days_options,
            index=0
        )

    # ----- Injuries: full width across both columns -----
    injuries_display = st.multiselect(
        label="Select injured areas (optional)",
        options=INJURY_OPTIONS
    )
    injuries = [i.lower().replace(" ", "_") for i in injuries_display]

    # ----- Submit: full width -----
    submitted = st.form_submit_button(
        "Get Recommendation",
        use_container_width=True      # ⬅️ tombol penuh 2 kolom
    )




# ========== SUBMIT & DISPLAY ==========
if submitted:
    if available_days_choice == "Choose...":
        st.warning("Please choose how many days you can train per week before submitting.")
        st.stop()
    else:
        available_days = int(available_days_choice)

    payload = {
        "gender": gender,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "injuries": injuries,
        "available_days": available_days,
        "preferred_body_part": preferred_body_part,
        "preferred_equipment": preferred_equipment,
    }

    try:
        res = requests.post(
            "http://127.0.0.1:8000/api/v1/recommendation/",
            json=payload,
            timeout=30,
        )
        res.raise_for_status()
        st.session_state.recommendation = res.json()      # ⬅️  simpan ke state
    except Exception as e:
        st.error(f"Request failed: {e}")
        st.stop()

# ---------- TAMPILKAN HASIL BILA ADA ----------
if "recommendation" in st.session_state:
    data = st.session_state.recommendation

    # ----------- RESULT SUMMARY -----------
    st.markdown("## <span style='color: white;'>Result Summary</span>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid white; margin-top: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("BMI", f"{data['bmi']:.1f}")
    c2.metric("Category", data["bmi_category"].title())
    c3.metric("Split Type", data["split_type"].title().replace(" ", ""))

    # ----------- WEEKLY SCHEDULE -----------
    st.markdown("### <span style='color: white;'>Weekly Focus</span>", unsafe_allow_html=True)
    schedule_df = pd.DataFrame(
        [(k.replace('day_', 'Day '), v.title()) for k, v in data["schedule"].items()],
        columns=["Day", "Focus"]
    )
    st.dataframe(
        schedule_df.style.set_properties(**{
            'text-align': 'left',
            'color': 'white',
            'background-color': '#0e1117',
            'border-color': 'white',
            'font-size': '0.95rem'
        }),
        hide_index=True,
        use_container_width=True
    )

    # ----------- DAILY SPLIT OVERVIEW -----------
    st.markdown("### <span style='color: white;'>📅 Training Split Overview</span>", unsafe_allow_html=True)

    # Map Day → data
    day_map    = {f"Day {d['day']}": d for d in data["days"]}
    day_labels = list(day_map.keys())

    # Dropdown (placeholder “Choose Day…”)
    default_day = st.session_state.get("chosen_day", "Choose Day…")
    day_choice  = st.selectbox(
        "Select a day to view details",
        options=["Choose Day…"] + day_labels,
        index=0 if default_day == "Choose Day…" else day_labels.index(default_day) + 1,
    )
    st.session_state.chosen_day = day_choice  # simpan pilihan

    # Hanya render jika user sudah memilih day
    if day_choice != "Choose Day…":
        selected_day = day_map[day_choice]

        st.markdown(
            f"#### <span style='color: white;'>{day_choice}: "
            f"{selected_day['day_focus'].title()}</span>",
            unsafe_allow_html=True,
        )

        # --------- siapkan baris tabel + thumbnail ----------
        table_rows_html = ""
        for ex in selected_day["exercises"]:
            table_rows_html += f"""
            <tr>
            <td>{ex['exercise_name'].title()}</td>
            <td>{ex['body_part'].title()}</td>
            <td>{', '.join(eq.title() for eq in ex['equipment'])}</td>
            <td>{', '.join(m.title() for m in ex['primary_muscle'])}</td>
            <td>{', '.join(m.title() for m in ex['secondary_muscle'])}</td>
            <td style='text-align:center;'><img src="{ex['exercise_image']}" width="240"></td>
            </tr>
            """

        # --------- render tabel HTML ----------
        st.markdown(
            f"""
            <style>
            table.exercise-table {{
                border-collapse: collapse; width: 100%;
            }}
            .exercise-table th, .exercise-table td {{
                border: 1px solid #444;
                padding: 6px 8px;
                font-size: 0.9rem;
                color: #fff;
                vertical-align: top;
            }}
            .exercise-table th {{ background: #222; }}
            </style>

            <table class="exercise-table">
            <thead>
                <tr>
                <th>Exercise</th>
                <th>Body Part</th>
                <th>Equipment</th>
                <th>Primary</th>
                <th>Secondary</th>
                <th>Image</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
            </table>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Select a day from the dropdown to see its workout details.")
