import io
import csv
import time
import streamlit as st
from db import init_db, login_user, register_user, save_prediction, get_user_history
from styles import load_css

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OcuVisionAI",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
st.markdown(load_css(), unsafe_allow_html=True)

# ─── SESSION DEFAULTS ────────────────────────────────────────────────────────
for key, val in {
    "logged_in": False,
    "user_id": None,
    "user_name": None,
    "active_page": "Dashboard",
    "analysis_result": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ─── CONSTANTS & HELPERS ─────────────────────────────────────────────────────
SEVERITY_ORDER = ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]


def logout():
    st.session_state.clear()
    st.rerun()


def severity_badge(prediction: str) -> str:
    colors = {
        "No DR":            ("#22c55e", "✅"),
        "Mild":             ("#f59e0b", "⚠️"),
        "Moderate":         ("#f97316", "🔶"),
        "Severe":           ("#ef4444", "🔴"),
        "Proliferative DR": ("#dc2626", "🚨"),
    }
    color, icon = colors.get(prediction, ("#94a3b8", "❓"))
    return (
        f'<span style="background:{color};color:white;padding:3px 10px;'
        f'border-radius:20px;font-size:0.8rem;font-weight:600;">{icon} {prediction}</span>'
    )


def history_to_csv(history: list) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "File", "Prediction", "Confidence (%)"])
    for row in history:
        date = row["created_at"].strftime("%Y-%m-%d %H:%M") if row.get("created_at") else ""
        writer.writerow([
            row.get("id", ""),
            date,
            row.get("image_path", ""),
            row.get("prediction", ""),
            f"{row.get('confidence') or 0:.1f}",
        ])
    return output.getvalue().encode("utf-8")


def high_risk_banner(history: list):
    if not history:
        return
    latest_pred = history[0].get("prediction", "")
    if latest_pred in ("Severe", "Proliferative DR"):
        st.markdown(f"""
        <div style="background:#fef2f2;border:2px solid #dc2626;border-radius:10px;
                    padding:0.9rem 1.2rem;margin-bottom:1.2rem;display:flex;
                    align-items:center;gap:0.8rem;">
            <span style="font-size:1.5rem;">🚨</span>
            <div>
                <strong style="color:#dc2626;">High-Risk Result Detected</strong><br>
                <span style="font-size:0.88rem;color:#7f1d1d;">
                    Your most recent scan was classified as <strong>{latest_pred}</strong>.
                    Please seek immediate ophthalmology consultation.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  AUTH PAGE
# ═══════════════════════════════════════════════════════════════════════════
def page_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:2rem 0 1rem;">
            <h1 style="font-size:2.2rem;margin-bottom:0;">👁️ OcuVisionAI</h1>
            <p style="color:#64748b;margin-top:0.3rem;">Detect Early. Save Vision.</p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Create Account"])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            email = st.text_input("Email address", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pw", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", use_container_width=True, type="primary"):
                if not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    user = login_user(email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["id"]
                        st.session_state.user_name = user["name"]
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Incorrect email or password.")

        with tab_signup:
            st.markdown("<br>", unsafe_allow_html=True)
            name = st.text_input("Full name", key="reg_name", placeholder="Dr. Priya Sharma")
            reg_email = st.text_input("Email address", key="reg_email", placeholder="you@example.com")
            reg_pw = st.text_input("Password", type="password", key="reg_pw", placeholder="Min. 6 characters")
            reg_pw2 = st.text_input("Confirm password", type="password", key="reg_pw2", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True, type="primary"):
                if not name or not reg_email or not reg_pw:
                    st.error("All fields are required.")
                elif reg_pw != reg_pw2:
                    st.error("Passwords do not match.")
                elif len(reg_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    if register_user(name, reg_email, reg_pw):
                        st.success("Account created! Please sign in.")
                    else:
                        st.error("An account with this email already exists.")


# ═══════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1rem 0 0.5rem;">
            <h2 style="margin:0;">👁️ OcuVisionAI</h2>
            <p style="font-size:0.8rem;opacity:0.75;margin:0.2rem 0 1rem;">Retinal Screening System</p>
            <div style="background:rgba(255,255,255,0.1);border-radius:8px;
                        padding:0.6rem 0.8rem;margin-bottom:1rem;">
                <strong>👤 {st.session_state.user_name}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pages = {
            "📊 Dashboard": "Dashboard",
            "🔬 New Scan":  "New Scan",
            "📜 History":   "History",
        }
        for label, page in pages.items():
            active = st.session_state.active_page == page
            if st.button(
                label,
                use_container_width=True,
                type="primary" if active else "secondary",
                key=f"nav_{page}",
            ):
                st.session_state.active_page = page
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
def page_dashboard():
    import pandas as pd
    from collections import Counter

    st.markdown(f"## 👋 Welcome back, {st.session_state.user_name}")
    st.caption("Here's your retinal screening summary")

    history = get_user_history(st.session_state.user_id)

    # ── High-risk banner ──
    high_risk_banner(history)

    # ── Metrics (no avg confidence) ──
    total = len(history)
    last_scan = history[0]["created_at"] if history else None
    if last_scan:
        if hasattr(last_scan, 'strftime'):
            last_scan_str = last_scan.strftime("%b %d, %Y")
        else:
            try:
                last_scan_str = str(last_scan).replace("-", "/")[0:10]
            except:
                last_scan_str = str(last_scan)
    last_pred = history[0].get("prediction", "—") if history else "—"

    c1, c2, c3 = st.columns(3)
    c1.metric("🔬 Total Scans", total)
    c2.metric("📅 Last Scan", last_scan_str)
    c3.metric("🏷️ Last Diagnosis", last_pred)

    st.markdown("---")

    col_a, col_b = st.columns([2, 1])

    with col_a:
        # ── Confidence over time chart ──
        if history:
            st.markdown("### 📈 Confidence Over Time")
            chart_rows = [
                {"Scan": f"#{i+1} {r.get('image_path','')[:10]}", "Confidence (%)": round(r.get("confidence") or 0, 1)}
                for i, r in enumerate(reversed(history))
            ]
            df_chart = pd.DataFrame(chart_rows).set_index("Scan")
            st.line_chart(df_chart, use_container_width=True)

        # ── Recent scans ──
        st.markdown("### 📋 Recent Scans")
        if not history:
            st.info("No scans yet. Start a new scan to see results here.")
        else:
            for row in history[:5]:
                conf = row.get("confidence") or 0
                pred = row.get("prediction", "Unknown")
                date = row["created_at"].strftime("%b %d, %Y %H:%M") if row.get("created_at") else "—"
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;align-items:center;
                            padding:0.7rem 1rem;border-radius:8px;margin-bottom:0.5rem;
                            background:#f8fafc;border:1px solid #e2e8f0;">
                    <div>
                        <strong>{date}</strong><br>
                        <span style="font-size:0.8rem;color:#64748b;">{row.get('image_path','—')}</span>
                    </div>
                    <div style="text-align:right;">
                        {severity_badge(pred)}<br>
                        <span style="font-size:0.8rem;color:#64748b;">Conf: {conf:.1f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_b:
        # ── Diagnosis breakdown bar chart ──
        if history:
            st.markdown("### 🏷️ Diagnosis Breakdown")
            counts = Counter(r.get("prediction", "Unknown") for r in history)
            # Order by severity
            ordered = {k: counts.get(k, 0) for k in SEVERITY_ORDER if k in counts}
            df_bar = pd.DataFrame({"Count": list(ordered.values())}, index=list(ordered.keys()))
            st.bar_chart(df_bar, use_container_width=True)

        st.markdown("### ⚡ Quick Start")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔬 Start New Scan", use_container_width=True, type="primary"):
            st.session_state.active_page = "New Scan"
            st.rerun()
        if st.button("📜 View Full History", use_container_width=True):
            st.session_state.active_page = "History"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#eff6ff;border-left:4px solid #3b82f6;
                    padding:0.8rem;border-radius:6px;font-size:0.85rem;">
            <strong>ℹ️ How it works</strong><br>
            Upload a retinal fundus image. Our AI classifies diabetic retinopathy severity in seconds.
        </div>
        """, unsafe_allow_html=True)


#  PAGE: NEW SCAN
# ═══════════════════════════════════════════════════════════════════════════
def page_new_scan():
    st.markdown("## 🔬 New Retinal Scan")
    st.caption("Upload a fundus image for AI-powered diabetic retinopathy screening")

    col_upload, col_result = st.columns([1, 1], gap="large")

    with col_upload:
        st.markdown("### 📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Drag & drop or browse",
            type=["jpg", "jpeg", "png"],
            help="Supported formats: JPG, JPEG, PNG",
        )

        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded retinal scan", use_container_width=True)
            notes = st.text_area("Clinical notes (optional)", placeholder="Add any relevant notes for this scan...")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🧠 Analyse Image", type="primary", use_container_width=True):
                with st.spinner("AI is analysing your retinal scan..."):
                    # ── Plug your model inference here ──
                    # result = your_model.predict(uploaded_file)
                    # For now: placeholder
                    import time, random
                    time.sleep(1.5)
                    labels = ["No DR", "Mild", "Moderate", "Severe", "Proliferative DR"]
                    prediction = random.choice(labels)
                    confidence = round(random.uniform(72, 99), 1)
                    # ── Save to DB ──
                    save_prediction(
                        user_id=st.session_state.user_id,
                        image_path=uploaded_file.name,
                        prediction=prediction,
                        confidence=confidence,
                    )
                    st.session_state.analysis_result = {
                        "prediction": prediction,
                        "confidence": confidence,
                    }
                    st.rerun()

    with col_result:
        st.markdown("### 📊 Analysis Result")
        result = st.session_state.get("analysis_result")

        if not result:
            st.markdown("""
            <div style="border:2px dashed #cbd5e1;border-radius:12px;padding:3rem;text-align:center;color:#94a3b8;">
                <p style="font-size:2rem;">👁️</p>
                <p>Results will appear here after analysis</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            pred = result["prediction"]
            conf = result["confidence"]

            # Severity colour map
            severity_info = {
                "No DR":             ("#f0fdf4", "#16a34a", "No signs of diabetic retinopathy detected. Routine follow-up recommended."),
                "Mild":              ("#fffbeb", "#d97706", "Mild NPDR detected. Schedule follow-up within 12 months."),
                "Moderate":          ("#fff7ed", "#ea580c", "Moderate NPDR. Refer to ophthalmologist within 6 months."),
                "Severe":            ("#fef2f2", "#dc2626", "Severe NPDR. Urgent ophthalmology referral needed."),
                "Proliferative DR":  ("#fef2f2", "#991b1b", "Proliferative DR. Immediate specialist intervention required."),
            }
            bg, accent, advice = severity_info.get(pred, ("#f8fafc", "#475569", "Please consult a specialist."))

            st.markdown(f"""
            <div style="background:{bg};border:2px solid {accent};border-radius:12px;padding:1.5rem;">
                <h3 style="color:{accent};margin:0 0 0.3rem;">Diagnosis</h3>
                <p style="font-size:1.8rem;font-weight:700;color:{accent};margin:0;">{pred}</p>
                <hr style="border-color:{accent};opacity:0.2;margin:0.8rem 0;">
                <div style="display:flex;justify-content:space-between;">
                    <div>
                        <span style="font-size:0.8rem;color:#64748b;">CONFIDENCE</span><br>
                        <strong style="font-size:1.3rem;">{conf}%</strong>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:0.8rem;color:#64748b;">SEVERITY</span><br>
                        {severity_badge(pred)}
                    </div>
                </div>
                <hr style="border-color:{accent};opacity:0.2;margin:0.8rem 0;">
                <p style="font-size:0.88rem;color:#475569;margin:0;">💡 {advice}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Analyse Another", use_container_width=True):
                st.session_state.analysis_result = None
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE: HISTORY
# ═══════════════════════════════════════════════════════════════════════════
def page_history():
    st.markdown("## 📜 Scan History")
    st.caption("All your past retinal scans and AI diagnoses")

    history = get_user_history(st.session_state.user_id)

    # ── High-risk banner ──
    high_risk_banner(history)

    if not history:
        st.info("No scan history found. Run your first scan to get started.")
        if st.button("🔬 Start a Scan", type="primary"):
            st.session_state.active_page = "New Scan"
            st.rerun()
        return

    # ── Controls: search + filter + sort + export ──
    col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1.2, 1.2, 1])
    with col_f1:
        search = st.text_input("🔍 Search", placeholder="filename or diagnosis")
    with col_f2:
        filter_pred = st.selectbox(
            "Diagnosis",
            ["All", "No DR", "Mild", "Moderate", "Severe", "Proliferative DR"],
        )
    with col_f3:
        sort_by = st.selectbox(
            "Sort by",
            ["Date (newest)", "Date (oldest)", "Confidence ↑", "Confidence ↓", "Severity"],
        )
    with col_f4:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Export CSV",
            data=history_to_csv(history),
            file_name="ocuvision_history.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── Filter ──
    filtered = [
        r for r in history
        if (filter_pred == "All" or r.get("prediction") == filter_pred)
        and (
            not search
            or search.lower() in (r.get("image_path") or "").lower()
            or search.lower() in (r.get("prediction") or "").lower()
        )
    ]

    # ── Sort ──
    if sort_by == "Date (oldest)":
        filtered = list(reversed(filtered))
    elif sort_by == "Confidence ↑":
        filtered = sorted(filtered, key=lambda r: r.get("confidence") or 0)
    elif sort_by == "Confidence ↓":
        filtered = sorted(filtered, key=lambda r: r.get("confidence") or 0, reverse=True)
    elif sort_by == "Severity":
        filtered = sorted(
            filtered,
            key=lambda r: SEVERITY_ORDER.index(r["prediction"])
            if r.get("prediction") in SEVERITY_ORDER else 99,
            reverse=True,
        )

    st.markdown(f"**{len(filtered)} record(s)** found")
    st.markdown("---")

    for row in filtered:
        pred = row.get("prediction", "Unknown")
        conf = row.get("confidence") or 0
        raw_date = row.get("created_at")
        raw_date = row.get("created_at")
        if raw_date:
            if hasattr(raw_date, 'strftime'):
                date_display = raw_date.strftime("%B %d, %Y — %H:%M")
            else:
                try:
                    date_display = str(raw_date).replace("-", "/")[0:16]
                except:
                    date_display = str(raw_date)
        else:
            date_display = "—"
        fname = row.get("image_path", "—")

        with st.expander(f"🗓️ {date_display}  ·  {pred}  ·  {fname}", expanded=False):
            c1, c2 = st.columns(2)
            c1.markdown(f"**Diagnosis:** {severity_badge(pred)}", unsafe_allow_html=True)
            c1.markdown(f"**Confidence:** `{conf:.1f}%`")
            c2.markdown(f"**File:** `{fname}`")
            c2.markdown(f"**Date:** {date_display}")


# ═══════════════════════════════════════════════════════════════════════════
#  ROUTER
# ════════════════════════════════════
if not st.session_state.logged_in:
    page_login()
else:
    render_sidebar()
    page = st.session_state.active_page
    if page == "Dashboard":
        page_dashboard()
    elif page == "New Scan":
        page_new_scan()
    elif page == "History":
        page_history()