import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import base64


st.set_page_config(
    page_title="Jymz",        
    page_icon="💪"
)

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

INJURY_OPTIONS = list(BODY_PARTS.keys())

# def render_glossary():
#     rows = []
#     for bp, muscles in BODY_PARTS.items():
#         badges = " ".join(
#             f"<span class='copy-text' data-text='{m}'>{m.title()}</span>"
#             for m in muscles
#         )
#         rows.append(f"<tr><td class='bp'>{bp}</td><td>{badges}</td></tr>")

#     table_html = "<table class='glossary-table'>" + "".join(rows) + "</table>"

#     components.html(
#         f"""
#         <style>
#         .glossary-table {{
#             border-collapse: collapse;
#             width: 100%;
#             color: #ffffff;
#             font-size: 0.9rem;
#         }}
#         .glossary-table td {{
#             border: 1px solid #ffffff33;
#             padding: 6px 8px;
#             vertical-align: top;
#         }}
#         .glossary-table .bp {{
#             font-weight: bold;
#             white-space: nowrap;
#         }}
#         .copy-text {{
#             cursor: pointer;
#             display: inline-block;
#             margin: 2px 4px;
#             padding: 4px 8px;
#             border-radius: 5px;
#             background: #333333;
#             color: #ffffff;
#             font-size: 0.9rem;
#             transition: background 0.2s;
#         }}
#         .copy-text:hover {{
#             background: #555555;
#         }}
#         .copy-text.copied {{
#             background: #2ecc71;
#             color: #000000;
#         }}
#         </style>

#         <div id="glossary">{table_html}</div>

#         <script>
#         const items = document.querySelectorAll('#glossary .copy-text');
#         items.forEach(el => {{
#             el.addEventListener('click', () => {{
#                 const txt = el.dataset.text;
#                 navigator.clipboard.writeText(txt);
#                 el.classList.add('copied');
#                 const original = el.innerText;
#                 el.innerText = 'Copied!';
#                 setTimeout(() => {{
#                     el.innerText = original.charAt(0).toUpperCase() + original.slice(1);
#                     el.classList.remove('copied');
#                 }}, 1000);
#             }});
#         }});
#         </script>
#         """,
#         height=400,
#         scrolling=True,
#     )

# with st.expander("Muscle Glossary", expanded=False):
#     render_glossary()

VALID_FOCUS = ["fullbody","upper", "lower", "legs", "push", "pull", "cardio", "neck", "shoulders", "chest", "back", "abs", "biceps", "triceps",
    "forearms", "glutes", "quadriceps", "hamstrings", "calves"]

# State untuk simpan tipe rekomendasi yang dipilih
if "recommendation_type" not in st.session_state:
    st.session_state.recommendation_type = None

mode_options = [
    "Choose generate mode ...",
    "Weekly schedule program",
    "Single focus day"
]

selected_mode = st.selectbox("Generate Program", mode_options)

if selected_mode != "Choose generate mode ...":
    st.session_state.recommendation_type = selected_mode
else:
    st.session_state.recommendation_type = None

# Reset rekomendasi jika user mengganti mode
if "last_selected_mode" not in st.session_state:
    st.session_state.last_selected_mode = None

if selected_mode != st.session_state.last_selected_mode:
    if "recommendation" in st.session_state:
        del st.session_state.recommendation  # Hapus hasil lama
    st.session_state.last_selected_mode = selected_mode

# ========== FORM ========== 
with st.form("input_form"):
    # col1, col2 = st.columns(2)

    # # Tombol Weekly Schedule di kolom kiri
    # with col1:
    #     if st.form_submit_button("Weekly Schedule"):
    #         st.session_state.recommendation_type = "Weekly Schedule"
    # # Tombol Daily by Focus di kolom kanan
    # with col2:
    #     if st.form_submit_button("Daily by Focus"):
    #         st.session_state.recommendation_type = "Daily by Focus"


    # Jika sudah pilih tipe rekomendasi, tampilkan form input data dan preferensi
    if st.session_state.recommendation_type is not None:

        # ----- KIRI : User Data -----
        if st.session_state.recommendation_type == "Weekly schedule program":
            gender_label = st.selectbox("Gender", ["Male", "Female"])
            gender = gender_label.lower()

        height_cm = st.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=165.0, step=0.5)
        weight_kg = st.number_input("Weight (kg)", min_value=35.0, max_value=200.0, value=55.0, step=0.5)

        # ----- KANAN : Exercise Preferences -----
        preferred_body_part = st.multiselect(
            label="Preferred Body Parts (optional)",
            options=[bp.title() for bp in BODY_PARTS.keys()]
        )
        preferred_body_part = [bp.lower() for bp in preferred_body_part]

        preferred_equipment = st.multiselect(
            label="Preferred Equipment (optional)",
            options=[e.title() for e in EQUIPMENTS]
        )

        if st.session_state.recommendation_type == "Weekly schedule program":
            days_options = ["Choose..."] + [1, 2, 3, 4, 5]
            available_days_choice = st.selectbox(
                "Available days per week",
                options=days_options,
                index=0
            )
        else:
            focus_options = ["Choose an option..."] + [f.title() for f in VALID_FOCUS]
            selected_focus = st.selectbox("Select Day Focus", focus_options)
            if selected_focus == "Choose an option...":
                day_focus = None
            else:
                day_focus = selected_focus.lower()

        injuries_display = st.multiselect(
            label="Select injured areas (optional)",
            options=INJURY_OPTIONS
        )
        injuries = [i.lower().replace(" ", "_") for i in injuries_display]

        # Tombol submit utama
        submitted = st.form_submit_button("Get Recommendation")

        if submitted:
            if st.session_state.recommendation_type == "Single focus day" and day_focus is None:
                st.warning("Please select a focus area for your single day workout.")
                st.stop()
            bmi = weight_kg / ((height_cm / 100) ** 2)

            if st.session_state.recommendation_type == "Weekly schedule program":
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
                    "preferred_equipment": [e.lower() for e in preferred_equipment],
                }

                with st.spinner("Generating weekly recommendation..."):
                    try:
                        res = requests.post(
                            "http://127.0.0.1:8000/api/v1/recommendation/",
                            json=payload,
                            timeout=30,
                        )
                        res.raise_for_status()
                        st.session_state.recommendation = res.json()
                    except Exception as e:
                        st.error(f"Request failed: {e}")
                        st.stop()

            elif st.session_state.recommendation_type == "Single focus day":
                payload = {
                    "day_focus": day_focus,
                    "injuries": injuries,
                    "preferred_body_part": preferred_body_part,
                    "preferred_equipment": [e.lower() for e in preferred_equipment],
                    "bmi": bmi
                }

                with st.spinner("Generating daily recommendation..."):
                    try:
                        res = requests.post(
                            "http://127.0.0.1:8000/api/v1/recommendation/by-focus",
                            json=payload,
                            timeout=30,
                        )
                        res.raise_for_status()
                        st.session_state.recommendation = res.json()
                    except Exception as e:
                        st.error(f"Request failed: {e}")
                        st.stop()

# ---------- TAMPILKAN HASIL BILA ADA ----------
if "recommendation" in st.session_state:
    data = st.session_state.recommendation

    is_daily = "day_focus" in data and "exercises" in data
    is_weekly = "schedule" in data and "days" in data


    if is_weekly:
        st.markdown("## <span style='color: white;'>Summary</span>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid white; margin-top: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)

        summary_data = {
            "BMI": [f"{data['bmi']:.1f}"],
            "Category": [data["bmi_category"].title()],
            "Split Type": [data["split_type"].title().replace(" ", "")]
        }

        for k, v in data["schedule"].items():
            day = k.replace("day_", "Day ")
            summary_data[day] = [v.title()]

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(
            summary_df.style.set_properties(**{
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
        for selected_day in data["days"]:
            day_title = f"Day {selected_day['day']} {selected_day['day_focus'].title()}"

            st.markdown(
                f"#### <span style='color: white;'>{day_title}</span>",
                unsafe_allow_html=True,
            )

            table_rows_html = ""
            for ex in selected_day["exercises"]:
                table_rows_html += f"""
                <tr>
                    <td>{ex['exercise_name'].title()}</td>
                    <td>{ex['body_part'].title()}</td>
                    <td>{', '.join(eq.title() for eq in ex['equipment'])}</td>
                    <td>{', '.join(m.title() for m in ex['primary_muscle'])}</td>
                    <td>{', '.join(m.title() for m in ex['secondary_muscle'])}</td>
                    <td style='text-align:center;'><img src="{ex['exercise_image']}" style="max-width:150px; max-height:130px;"></td>
                </tr>
                """

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

    elif is_daily:
        st.markdown("## <span style='color: white;'>Daily Recommendation</span>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px solid white; margin-top: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)

        st.markdown(f"**Focus:** {data['day_focus'].title()}")

        table_rows_html = ""
        for ex in data["exercises"]:
            table_rows_html += f"""
            <tr>
                <td>{ex['exercise_name'].title()}</td>
                <td>{ex['body_part'].title()}</td>
                <td>{', '.join(eq.title() for eq in ex['equipment'])}</td>
                <td>{', '.join(m.title() for m in ex['primary_muscle'])}</td>
                <td>{', '.join(m.title() for m in ex['secondary_muscle'])}</td>
                <td style='text-align:center;'><img src="{ex['exercise_image']}" style="max-width:150px; max-height:130px;"></td>
            </tr>
            """

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
        st.error("Unknown response format received from server.")
