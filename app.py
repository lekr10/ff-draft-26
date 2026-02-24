import streamlit as st
import json, os

# ══════════════════════════════════════════════════════════════
#  ✏️  EDIT THESE BEFORE YOU SEND THE LINK!
# ══════════════════════════════════════════════════════════════
DRAFT_YEAR = 2026
CITIES = [
    "Vancouver",
    "Park City",
    "Charleston beach house",
    "Miami",
]
# ══════════════════════════════════════════════════════════════

DATA_FILE = "votes.json"
LS_KEY = f"ff_draft_voter_{DRAFT_YEAR}"

# ─────────────────────────────────────────────
#  Data store — shared across ALL user sessions
# ─────────────────────────────────────────────
@st.cache_resource
def get_store():
    """Single shared object for all sessions (in-memory + file backup)."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                d = json.load(f)
            d.setdefault("round", 1)
            d.setdefault("round1_locked", False)
            d.setdefault("round1_votes", {})
            d.setdefault("finalist_cities", [])
            d.setdefault("round2_votes", {})
            d.setdefault("round2_locked", False)
            return d
        except Exception:
            pass
    return dict(round=1, round1_locked=False, round1_votes={},
                finalist_cities=[], round2_votes={}, round2_locked=False)


def persist(d):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(d, f, indent=2)
    except Exception:
        pass


def r1_tally(d):
    counts = {c: 0 for c in CITIES}
    by_city = {c: [] for c in CITIES}
    for name, picks in d["round1_votes"].items():
        for c in picks:
            if c in counts:
                counts[c] += 1
                by_city[c].append(name)
    return counts, by_city


def r2_tally(d):
    fc = d.get("finalist_cities", [])
    counts = {c: 0 for c in fc}
    by_city = {c: [] for c in fc}
    for name, pick in d["round2_votes"].items():
        if pick in counts:
            counts[pick] += 1
            by_city[pick].append(name)
    return counts, by_city


def top2(d):
    counts, _ = r1_tally(d)
    return [c for c, _ in sorted(counts.items(), key=lambda x: -x[1])[:2]]


# ─────────────────────────────────────────────
#  Page config + CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title=f"🏈 FF Draft Vote {DRAFT_YEAR}",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #0d3b1e 0%, #1a5c32 55%, #0d3b1e 100%);
    min-height: 100vh;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #0a2e17; }

.main-title {
    font-size: clamp(2rem, 6vw, 3.8rem);
    font-weight: 900;
    text-align: center;
    color: #FFD700;
    text-shadow: 0 4px 14px rgba(0,0,0,.7);
    letter-spacing: 3px;
    margin-bottom: 2px;
    line-height: 1.1;
}
.subtitle {
    text-align: center;
    color: rgba(255,255,255,.6);
    font-size: 1.05rem;
    margin-bottom: 1.2rem;
}
.round-badge {
    display: inline-block;
    background: #FFD700;
    color: #0d3b1e;
    border-radius: 30px;
    padding: 7px 24px;
    font-weight: 900;
    font-size: 1rem;
    letter-spacing: 1px;
    box-shadow: 0 4px 14px rgba(255,215,0,.4);
}
.lb-card {
    background: rgba(0,0,0,.3);
    border: 1px solid rgba(255,215,0,.2);
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.lb-card-winner {
    border: 2px solid #FFD700 !important;
    box-shadow: 0 0 24px rgba(255,215,0,.35);
}
.vote-num {
    font-size: 2.2rem;
    font-weight: 900;
    color: #FFD700;
    line-height: 1;
}
.pbar-bg {
    background: rgba(255,255,255,.1);
    border-radius: 8px;
    height: 14px;
    margin: 8px 0;
    overflow: hidden;
}
.pbar-fill {
    background: linear-gradient(90deg, #FFD700, #FFA500);
    height: 100%;
    border-radius: 8px;
    transition: width .6s ease;
}
.name-chip {
    display: inline-block;
    background: rgba(255,215,0,.18);
    color: #FFD700;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: .8rem;
    margin: 2px 3px;
}
.voter-id {
    color: rgba(255,255,255,.65);
    font-size: .95rem;
    margin-bottom: .3rem;
}
.winner-box {
    background: linear-gradient(135deg, #FFD700, #FFA500);
    border-radius: 20px;
    padding: 32px 20px;
    text-align: center;
    color: #0d3b1e;
    font-size: clamp(1.4rem, 4vw, 2.4rem);
    font-weight: 900;
    letter-spacing: 2px;
    box-shadow: 0 0 50px rgba(255,215,0,.6);
    animation: glow 2s infinite;
}
@keyframes glow {
    0%,100% { box-shadow: 0 0 30px rgba(255,215,0,.5); }
    50%      { box-shadow: 0 0 70px rgba(255,215,0,.95); }
}
div[data-testid="stMarkdownContainer"] p { color: rgba(255,255,255,.85); }
h1,h2,h3,h4,h5 { color: #FFD700 !important; }

/* Inputs */
.stTextInput > label { color: #FFD700 !important; font-weight: 700; }
.stTextInput input {
    background: rgba(255,255,255,.08) !important;
    border: 1.5px solid rgba(255,215,0,.4) !important;
    border-radius: 30px !important;
    color: white !important;
    padding: 10px 20px !important;
}
.stTextInput input::placeholder { color: rgba(255,255,255,.35) !important; }
.stTextInput input:focus { border-color: #FFD700 !important; box-shadow: 0 0 0 3px rgba(255,215,0,.2) !important; }

/* Checkboxes */
.stCheckbox label p { color: white !important; font-size: 1.05rem !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #FFD700, #FFA500) !important;
    color: #0d3b1e !important;
    font-weight: 800 !important;
    border-radius: 30px !important;
    border: none !important;
    font-size: 1rem !important;
    letter-spacing: .5px !important;
    transition: all .25s !important;
}
.stButton > button:hover {
    transform: scale(1.04) !important;
    box-shadow: 0 6px 22px rgba(255,215,0,.45) !important;
}
.end-btn .stButton > button {
    background: linear-gradient(90deg, #c0392b, #e74c3c) !important;
    color: white !important;
}
.end-btn .stButton > button:hover {
    box-shadow: 0 6px 22px rgba(231,76,60,.5) !important;
}

/* Expanders */
div[data-testid="stExpander"] {
    border: 1px solid rgba(231,76,60,.4) !important;
    border-radius: 12px !important;
    background: rgba(0,0,0,.2) !important;
}

/* Alerts */
.stSuccess, .stInfo, .stWarning, .stError { border-radius: 12px !important; }

/* Divider */
hr { border-color: rgba(255,215,0,.2) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Auto-refresh every 20 s so everyone sees
#  live vote updates without manual refresh
# ─────────────────────────────────────────────
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=20_000, key="autorefresh")
except ImportError:
    pass

# ─────────────────────────────────────────────
#  Identity — localStorage so the browser
#  remembers who you are across visits
# ─────────────────────────────────────────────
try:
    from streamlit_js_eval import streamlit_js_eval
    JS_AVAILABLE = True
except ImportError:
    JS_AVAILABLE = False

if "voter_name" not in st.session_state:
    st.session_state.voter_name = None
if "ls_checked" not in st.session_state:
    st.session_state.ls_checked = False

if JS_AVAILABLE and not st.session_state.ls_checked:
    saved = streamlit_js_eval(
        js_expressions=f"localStorage.getItem('{LS_KEY}')",
        key="ls_read",
    )
    if saved and saved not in ("null", "None", "undefined", ""):
        st.session_state.voter_name = saved
    st.session_state.ls_checked = True


def save_identity(name: str):
    st.session_state.voter_name = name
    if JS_AVAILABLE:
        safe = name.replace("'", "\\'").replace('"', '\\"')
        streamlit_js_eval(
            js_expressions=f"localStorage.setItem('{LS_KEY}', '{safe}')",
            key="ls_write",
        )


def clear_identity():
    st.session_state.voter_name = None
    st.session_state.ls_checked = False
    if JS_AVAILABLE:
        streamlit_js_eval(
            js_expressions=f"localStorage.removeItem('{LS_KEY}')",
            key="ls_clear",
        )


# ─────────────────────────────────────────────
#  Header
# ─────────────────────────────────────────────
st.markdown(
    f'<div class="main-title">🏈 FF DRAFT VOTE {DRAFT_YEAR} 🏈</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">13 years strong — where are we going next?</div>',
    unsafe_allow_html=True,
)

d = get_store()  # shared mutable state

# ─────────────────────────────────────────────
#  Step 1: Name Entry
# ─────────────────────────────────────────────
if st.session_state.voter_name is None:
    st.markdown("---")
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("### 👋 Who are you?")
        st.markdown(
            "Enter your name to cast your votes. "
            "Your browser will remember you next time!"
        )
        name_in = st.text_input(
            "Your name",
            placeholder="e.g. Spencer",
            key="name_input",
            label_visibility="hidden",
        )
        if st.button("🏈 Let's Vote!", use_container_width=True, key="enter_btn"):
            clean = name_in.strip()
            if clean:
                save_identity(clean)
                st.rerun()
            else:
                st.error("🚫 Type your name first, champ!")
    st.stop()

voter = st.session_state.voter_name

# Identity bar
ic1, ic2 = st.columns([7, 1])
with ic1:
    st.markdown(
        f'<div class="voter-id">👤 Voting as: '
        f'<strong style="color:#FFD700">{voter}</strong></div>',
        unsafe_allow_html=True,
    )
with ic2:
    if st.button("Not me →", key="switch_id", use_container_width=True):
        clear_identity()
        st.rerun()

# ═══════════════════════════════════════════════════════════════
#  ROUND 1
# ═══════════════════════════════════════════════════════════════
if d["round"] == 1:
    r1_counts, r1_voters = r1_tally(d)
    total_r1 = sum(r1_counts.values())
    max_r1 = max(r1_counts.values()) if total_r1 else 1

    st.markdown(
        '<div style="text-align:center;margin:1.2rem 0">'
        '<span class="round-badge">🗳️  ROUND 1 — PICK YOUR TOP 2 CITIES</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Voting form ──────────────────────────────────────────────
    if not d["round1_locked"]:
        already_voted = voter in d["round1_votes"]

        if already_voted:
            my_picks = d["round1_votes"][voter]
            st.success(
                f"✅ Your votes are locked in!  \n"
                f"You picked **{my_picks[0]}** & **{my_picks[1]}**.  \n"
                "Sit tight while the rest of the crew votes... 🍺"
            )
        else:
            st.markdown("**Pick exactly 2 destinations — choose wisely:**")
            selected = []
            cc1, cc2 = st.columns(2)
            for i, city in enumerate(CITIES):
                col = cc1 if i % 2 == 0 else cc2
                with col:
                    if st.checkbox(city, key=f"r1_chk_{i}"):
                        selected.append(city)

            n = len(selected)
            st.markdown("")  # spacer
            if n == 0:
                st.info("☝️ Select 2 cities to continue")
            elif n == 1:
                st.info(f"☝️ Select 1 more city")
            elif n == 2:
                if st.button(
                    f"🗳️  Submit: {selected[0]}  +  {selected[1]}",
                    use_container_width=True,
                    key="r1_submit",
                ):
                    d["round1_votes"][voter] = selected
                    persist(d)
                    st.success("🎉 Votes locked in — let's gooo!")
                    st.rerun()
            else:
                st.warning(f"⚠️ You picked {n} cities. Max is 2 — uncheck one!")

    else:
        st.info("🔒 Round 1 voting is **closed**. Results below!")

    # ── Live Leaderboard ─────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Live Leaderboard")

    sorted_cities = sorted(r1_counts.items(), key=lambda x: -x[1])
    medals = ["🥇", "🥈", "🥉", "4️⃣"]
    for i, (city, cnt) in enumerate(sorted_cities):
        pct = int(cnt / max_r1 * 100) if total_r1 else 0
        names = r1_voters[city]
        is_finalist = d["round1_locked"] and city in d.get("finalist_cities", [])
        card_cls = "lb-card lb-card-winner" if is_finalist else "lb-card"
        finalist_tag = (
            ' &nbsp;<span style="background:#FFD700;color:#0d3b1e;'
            'border-radius:10px;padding:2px 10px;font-size:.75rem;font-weight:900">'
            "FINALIST ⚡</span>"
            if is_finalist
            else ""
        )
        chips = (
            "".join(f'<span class="name-chip">{n}</span>' for n in names)
            if names
            else '<span style="color:rgba(255,255,255,.35);font-size:.85rem">No votes yet</span>'
        )
        st.markdown(
            f"""<div class="{card_cls}">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
    <span style="color:white;font-size:1.15rem;font-weight:700">{medals[i]} {city}{finalist_tag}</span>
    <span class="vote-num">{cnt}</span>
  </div>
  <div class="pbar-bg"><div class="pbar-fill" style="width:{pct}%"></div></div>
  <div style="margin-top:6px">{chips}</div>
</div>""",
            unsafe_allow_html=True,
        )

    who_voted_r1 = list(d["round1_votes"].keys())
    st.markdown(
        f'<p style="text-align:center;color:rgba(255,255,255,.4);margin-top:8px">'
        f"🏈 {len(who_voted_r1)} of your crew have voted</p>",
        unsafe_allow_html=True,
    )

    # ── Admin: End Round 1 ───────────────────────────────────────
    if not d["round1_locked"]:
        st.markdown("---")
        with st.expander("🔒  End of Round 1 Voting  (Admin Only)"):
            st.warning(
                "**This will lock all Round 1 votes and kick off the Championship Round.**  \n"
                "Only click when everyone has voted!"
            )
            _, btn_col, _ = st.columns([1, 2, 1])
            with btn_col:
                st.markdown('<div class="end-btn">', unsafe_allow_html=True)
                if st.button(
                    "🔒  Lock Round 1 & Start Championship",
                    use_container_width=True,
                    key="end_r1",
                ):
                    finalists = top2(d)
                    d["round1_locked"] = True
                    d["finalist_cities"] = finalists
                    d["round"] = 2
                    persist(d)
                    st.success(
                        f"✅ Round 1 locked!  \n"
                        f"Finalists: **{finalists[0]}** vs **{finalists[1]}**"
                    )
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # Hard reset (in case you want to start over during testing)
        with st.expander("🗑️  Reset All Votes  (Admin Only — Destructive!)"):
            st.error("This will permanently wipe ALL votes and start from scratch.")
            if st.button("💥 Yes, Reset Everything", key="reset_all"):
                d.clear()
                d.update(
                    dict(
                        round=1,
                        round1_locked=False,
                        round1_votes={},
                        finalist_cities=[],
                        round2_votes={},
                        round2_locked=False,
                    )
                )
                persist(d)
                st.rerun()

# ═══════════════════════════════════════════════════════════════
#  ROUND 2 — CHAMPIONSHIP
# ═══════════════════════════════════════════════════════════════
elif d["round"] == 2:
    finalists = d.get("finalist_cities", [])
    r2_counts, r2_voters = r2_tally(d)
    total_r2 = sum(r2_counts.values())
    max_r2 = max(r2_counts.values()) if total_r2 else 1

    # ── Winner screen ────────────────────────────────────────────
    if d.get("round2_locked"):
        if r2_counts:
            winner = max(r2_counts.items(), key=lambda x: x[1])[0]
            runner = [c for c in finalists if c != winner]
            runner = runner[0] if runner else None

            st.markdown(
                f'<div class="winner-box">'
                f"🏆 WE'RE GOING TO<br>"
                f'<span style="font-size:1.3em">{winner.upper()}</span><br>'
                f"🏈"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.balloons()

            st.markdown("---")
            st.markdown("### 🏆 Championship Results")
            total_r2_final = sum(r2_counts.values()) or 1
            for city in sorted(finalists, key=lambda c: -r2_counts.get(c, 0)):
                cnt = r2_counts.get(city, 0)
                names = r2_voters.get(city, [])
                pct = int(cnt / total_r2_final * 100)
                is_winner = city == winner
                card_cls = "lb-card lb-card-winner" if is_winner else "lb-card"
                icon = "🏆" if is_winner else "🥈"
                chips = "".join(
                    f'<span class="name-chip">{n}</span>' for n in names
                )
                st.markdown(
                    f"""<div class="{card_cls}">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
    <span style="color:white;font-size:1.2rem;font-weight:700">{icon} {city}</span>
    <span class="vote-num">{cnt} <span style="font-size:.9rem;color:rgba(255,255,255,.5)">({pct}%)</span></span>
  </div>
  <div class="pbar-bg"><div class="pbar-fill" style="width:{pct}%"></div></div>
  <div style="margin-top:6px">{chips}</div>
</div>""",
                    unsafe_allow_html=True,
                )

            # Show Round 1 for the record
            st.markdown("---")
            st.markdown("### Round 1 Results (for the record 📜)")
            r1_counts_f, r1_voters_f = r1_tally(d)
            sorted_r1 = sorted(r1_counts_f.items(), key=lambda x: -x[1])
            max_r1_f = max(r1_counts_f.values()) if r1_counts_f else 1
            medals_f = ["🥇", "🥈", "🥉", "4️⃣"]
            for i, (city, cnt) in enumerate(sorted_r1):
                pct = int(cnt / max_r1_f * 100) if sum(r1_counts_f.values()) else 0
                names = r1_voters_f[city]
                chips = (
                    "".join(f'<span class="name-chip">{n}</span>' for n in names)
                    or '<span style="color:rgba(255,255,255,.35)">No votes</span>'
                )
                st.markdown(
                    f"""<div class="lb-card">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px">
    <span style="color:white;font-size:1.05rem">{medals_f[i]} {city}</span>
    <span class="vote-num" style="font-size:1.6rem">{cnt}</span>
  </div>
  <div class="pbar-bg"><div class="pbar-fill" style="width:{pct}%"></div></div>
  <div style="margin-top:6px">{chips}</div>
</div>""",
                    unsafe_allow_html=True,
                )

        else:
            st.info("No championship votes cast yet.")

    # ── Active Round 2 voting ────────────────────────────────────
    else:
        st.markdown(
            '<div style="text-align:center;margin:1.2rem 0">'
            '<span class="round-badge">🏆  CHAMPIONSHIP ROUND — ONE VOTE, ONE DESTINY</span>'
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="text-align:center;color:rgba(255,255,255,.6);margin-bottom:1.5rem">'
            "Round 1 is over. Two cities remain. You get ONE vote.</p>",
            unsafe_allow_html=True,
        )

        already_voted_r2 = voter in d["round2_votes"]

        if already_voted_r2:
            my_r2 = d["round2_votes"][voter]
            st.success(
                f"✅ You voted for **{my_r2}** in the Championship!  \n"
                "Watch the scoreboard below for live results! 👇"
            )
        else:
            st.markdown("**Cast your championship vote:**")
            cc1, cc2 = st.columns(2)
            r2_choice = None
            for i, city in enumerate(finalists):
                col = cc1 if i == 0 else cc2
                cnt = r2_counts.get(city, 0)
                names = r2_voters.get(city, [])
                chips = " ".join(
                    f'<span class="name-chip">{n}</span>' for n in names
                ) or '<span style="color:rgba(255,255,255,.35)">No votes yet</span>'
                pct = int(cnt / max_r2 * 100) if total_r2 else 0
                with col:
                    st.markdown(
                        f"""<div class="lb-card" style="text-align:center;margin-bottom:10px">
  <div style="font-size:1.35rem;font-weight:800;color:white;margin-bottom:10px">{city}</div>
  <div class="pbar-bg"><div class="pbar-fill" style="width:{pct}%"></div></div>
  <div style="margin:8px 0">{chips}</div>
  <div class="vote-num">{cnt}</div>
</div>""",
                        unsafe_allow_html=True,
                    )
                    if st.button(
                        f"🗳️  Vote: {city}",
                        key=f"r2_btn_{i}",
                        use_container_width=True,
                    ):
                        r2_choice = city

            if r2_choice:
                d["round2_votes"][voter] = r2_choice
                persist(d)
                st.success(f"🎉 Championship vote locked in for **{r2_choice}**!")
                st.rerun()

        # Scoreboard — visible to everyone after voting
        if already_voted_r2:
            st.markdown("---")
            st.markdown("### 🏆 Championship Scoreboard")
            total_r2_now = sum(r2_counts.values()) or 1
            for city in finalists:
                cnt = r2_counts.get(city, 0)
                names = r2_voters.get(city, [])
                pct = int(cnt / total_r2_now * 100)
                chips = (
                    "".join(f'<span class="name-chip">{n}</span>' for n in names)
                    or '<span style="color:rgba(255,255,255,.35)">No votes yet</span>'
                )
                st.markdown(
                    f"""<div class="lb-card">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
    <span style="color:white;font-size:1.2rem;font-weight:700">🏆 {city}</span>
    <span class="vote-num">{cnt}</span>
  </div>
  <div class="pbar-bg"><div class="pbar-fill" style="width:{pct}%"></div></div>
  <div style="margin-top:6px">{chips}</div>
</div>""",
                    unsafe_allow_html=True,
                )

        who_voted_r2 = list(d["round2_votes"].keys())
        st.markdown(
            f'<p style="text-align:center;color:rgba(255,255,255,.4);margin-top:8px">'
            f"🏈 {len(who_voted_r2)} championship vote(s) cast</p>",
            unsafe_allow_html=True,
        )

        # ── Admin: Declare winner ──────────────────────────────
        st.markdown("---")
        with st.expander("🏆  Declare the Winner  (Admin Only)"):
            st.warning(
                "**This will lock Championship votes and reveal the winner!**  \n"
                "Make sure everyone has voted!"
            )
            _, btn_col, _ = st.columns([1, 2, 1])
            with btn_col:
                st.markdown('<div class="end-btn">', unsafe_allow_html=True)
                if st.button(
                    "🏆  Declare the Winner!",
                    use_container_width=True,
                    key="end_r2",
                ):
                    d["round2_locked"] = True
                    persist(d)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
