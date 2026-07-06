import streamlit as st
import time
import random

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Last Board Meeting",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Colour constants ────────────────────────────────────────────────────────
NAVY   = "#1A3C5C"
TEAL   = "#028090"
GOLD   = "#E67E22"
RED    = "#C0392B"
GREEN  = "#1E8449"
CREAM  = "#FEF9E7"
LIGHT  = "#EAF4FB"
DARK   = "#1C1C2E"
WHITE  = "#FFFFFF"

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: #101820;
    color: #e0e8f0;
}}

.stApp {{ background-color: #101820; }}

/* Hide streamlit chrome */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 1.5rem 2rem; max-width: 1200px; }}

/* Cards */
.card {{
    background: linear-gradient(135deg, #1a2a3a 0%, #1e3048 100%);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    border: 1px solid #2a4060;
}}
.card-gold  {{ border-left: 4px solid {GOLD}; }}
.card-teal  {{ border-left: 4px solid {TEAL}; }}
.card-red   {{ border-left: 4px solid {RED}; }}
.card-green {{ border-left: 4px solid {GREEN}; }}
.card-navy  {{ border-left: 4px solid #4a7aaa; }}

/* Role badge */
.role-badge {{
    display: inline-block;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}}

/* Big metric */
.big-metric {{
    text-align: center;
    padding: 1.2rem;
    border-radius: 10px;
    background: #1a2a3a;
    border: 1px solid #2a4060;
}}
.big-metric .value {{ font-size: 2.2rem; font-weight: 800; }}
.big-metric .label {{ font-size: 0.8rem; color: #8aabcc; text-transform: uppercase; letter-spacing: 0.08em; }}

/* Timer */
.timer-box {{
    background: linear-gradient(135deg, #1a2a3a, #0d1a27);
    border: 2px solid {GOLD};
    border-radius: 12px;
    text-align: center;
    padding: 1rem;
    font-size: 2.8rem;
    font-weight: 800;
    color: {GOLD};
    letter-spacing: 0.05em;
}}

/* Alert boxes */
.alert-red {{
    background: rgba(192,57,43,0.15);
    border: 1px solid rgba(192,57,43,0.5);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: #f1948a;
}}
.alert-green {{
    background: rgba(30,132,73,0.15);
    border: 1px solid rgba(30,132,73,0.5);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: #7dcea0;
}}
.alert-gold {{
    background: rgba(227,126,34,0.15);
    border: 1px solid rgba(227,126,34,0.5);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    color: #f0b27a;
}}

/* Voting bar */
.vote-bar-container {{
    background: #1a2a3a;
    border-radius: 6px;
    height: 28px;
    overflow: hidden;
    margin: 0.3rem 0;
}}
.vote-bar {{
    height: 100%;
    border-radius: 6px;
    display: flex;
    align-items: center;
    padding-left: 8px;
    font-size: 0.78rem;
    font-weight: 600;
    transition: width 0.5s ease;
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    background: #1a2a3a;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    color: #8aabcc;
    font-weight: 600;
    font-size: 0.85rem;
}}
.stTabs [aria-selected="true"] {{
    background: {TEAL} !important;
    color: white !important;
}}

/* Divider */
.section-divider {{
    border: none;
    border-top: 1px solid #2a4060;
    margin: 1.5rem 0;
}}

/* Headline */
.headline {{
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 0.3rem;
}}
.subline {{
    font-size: 1rem;
    color: #8aabcc;
    font-weight: 400;
}}
</style>
""", unsafe_allow_html=True)

# ── Session state init ──────────────────────────────────────────────────────
def ss(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

ss("phase", "lobby")          # lobby → briefing → investigation → boardroom → verdict → reveal → debrief
ss("selected_role", None)
ss("team_name", "")
ss("cards_unlocked", [])
ss("timer_start", None)
ss("timer_duration", 0)
ss("votes", {"A": 0, "B": 0, "C": 0})
ss("my_vote", None)
ss("icr_attempts", 0)
ss("icr_solved", False)
ss("suspect_rankings", {})
ss("questions_asked", set())
ss("analyst_findings", [])
ss("chat_log", [])
ss("company_revealed", False)

# ── Data ───────────────────────────────────────────────────────────────────
ROLES = {
    "CEO": {
        "icon": "👔",
        "color": GOLD,
        "badge_bg": "#7d5a0a",
        "tagline": "You built this company from zero.",
        "hidden_objective": "Keep the company alive at any cost. Do not let anyone blame the strategy.",
        "secret_info": "You borrowed Rs.2,600 Crore in Year 2 to fund the marketing blitz and fleet expansion. The Board approved it. You believed the brand would grow fast enough to service the debt.",
        "opening_statement": "We have built something extraordinary. The brand is the strongest it has ever been. Customers love us. This is a temporary liquidity crisis. We need 18 more months.",
    },
    "CFO": {
        "icon": "📊",
        "color": TEAL,
        "badge_bg": "#01545c",
        "tagline": "You have been warning them for 18 months.",
        "hidden_objective": "Make the record show you raised the alarm. Present the honest financial case.",
        "secret_info": "The ICR fell to 1.13× in Year 2. You wrote a memo. The Board noted it and took no action. You wrote another memo in Year 3 when ICR hit 0.47×. Same response.",
        "opening_statement": "I have two memos on record. Both were ignored. The Interest Coverage Ratio has been below 1.0× for six quarters. We cannot service our debt from operations. This is not a liquidity crisis. This is insolvency.",
    },
    "CHRO": {
        "icon": "👥",
        "color": "#9B59B6",
        "badge_bg": "#5b2d7a",
        "tagline": "You hired 1,200 people. They may have no jobs in 90 days.",
        "hidden_objective": "Protect as many jobs as possible. But figure out what you missed.",
        "secret_info": "When you submitted the 1,200-person hiring plan, the ICR was 0.47×. You did not know what an ICR was. The plan was approved. The CFO attached a note: 'Subject to Q2 EBITDA improvement.' Q2 EBITDA missed the target. The hires joined anyway.",
        "opening_statement": "14,000 people come to work every day trusting that this company is viable. I submitted the hiring plan in good faith. It was approved. If there were financial constraints that should have stopped it, I needed to know that before I hired 1,200 families into this situation.",
    },
    "CMO": {
        "icon": "📣",
        "color": "#E74C3C",
        "badge_bg": "#7b1a12",
        "tagline": "The brand has never been stronger. The company is dying.",
        "hidden_objective": "Prove the marketing investment was not the problem. Or was it?",
        "secret_info": "Your marketing ROI model shows Rs.4.2 in revenue for every Rs.1 of marketing spend. What the model does not show: the Rs.320 Crore was funded by debt. The incremental EBITDA generated by that revenue was Rs.28 Crore. The interest cost of the Rs.320 Crore debt was Rs.38 Crore per year. The marketing campaign lost money on a debt-adjusted basis.",
        "opening_statement": "Our brand awareness is 94%. Our NPS is 67. We are the most recognised brand in our category. That asset took three years and Rs.320 Crore to build. You do not destroy that in a restructuring. The brand IS the value.",
    },
    "Operations Head": {
        "icon": "⚙️",
        "color": "#27AE60",
        "badge_bg": "#145a32",
        "tagline": "You had an Rs.80 Crore saving plan. Nobody listened.",
        "hidden_objective": "Present the Rs.80 Crore plan. Argue operations was never the problem.",
        "secret_info": "31% of churned customers cited 'product quality declined' as the reason they left. Operations requested Rs.80 Crore for supply chain and product investment in Year 3. The CMO's marketing budget got that Rs.80 Crore instead. The product deteriorated. Customers left. Then marketing spent more to acquire new ones.",
        "opening_statement": "I have been saying for two years: fix the product before fixing the brand. 31% of our churned customers left because the product quality fell. We spent Rs.320 Crore on marketing and Rs.0 on the operations investment that could have stopped the churn.",
    },
    "Lead Banker": {
        "icon": "🏦",
        "color": "#3498DB",
        "badge_bg": "#1a4a6e",
        "tagline": "You are owed Rs.2,400 Crore. You could have called the loan. You did not.",
        "hidden_objective": "Protect the bank's money. A restructuring at Rs.1,800 Crore is better than liquidation at Rs.900 Crore.",
        "secret_info": "The covenant was ICR > 1.5×. It was breached in Year 2 (ICR 1.13×). You waived the breach because the CEO promised a turnaround. ICR fell to 0.47× in Year 3. You waived again. You are now two waivers deep and the company is insolvent. Your credit committee is asking why.",
        "opening_statement": "We believe in this company's fundamentals. We have supported two covenant waivers. We are not here to liquidate — we are here to restructure. But the restructuring must be real. We cannot waive a third time.",
    },
    "Activist Investor": {
        "icon": "📈",
        "color": "#F39C12",
        "badge_bg": "#7d5200",
        "tagline": "You paid Rs.180 per share. Current price: Rs.23.",
        "hidden_objective": "Find who is responsible. But also — is this company worth saving?",
        "secret_info": "You bought your 8% stake after the Year 2 annual report. The ICR was already 1.13× and falling. You saw it. You bought anyway because you believed in the turnaround story. You were wrong. The question is whether you were reckless or simply unlucky.",
        "opening_statement": "I have lost Rs.157 per share on this investment. I am not here to assign blame — I am here to recover value. The question before this Board is simple: is there more value in saving this company or selling its parts? Let us answer that question with numbers, not emotions.",
    },
    "Junior Analyst": {
        "icon": "🔍",
        "color": "#95A5A6",
        "badge_bg": "#2c3e50",
        "tagline": "Find the exact moment this became inevitable.",
        "hidden_objective": "Present your finding clearly and honestly, even if it implicates someone powerful.",
        "secret_info": "The three decision points: (1) Year 2 Month 3: debt jumped from Rs.600 Cr to Rs.2,100 Cr to fund expansion. ICR fell from 2.9× to 1.13×. This was the point of no return if EBITDA did not grow 40%. (2) Year 2 Month 9: CFO memo. Board inaction. The last chance to course-correct without restructuring. (3) Year 3 Month 2: CHRO submitted 1,200-hire plan with ICR at 0.47×. CFO approved. This locked in Rs.96 Crore of additional fixed costs when the company was already insolvent.",
        "opening_statement": "I have identified three decision points where a different choice would have changed the outcome. I would like to present them — with the specific numbers — when the Board is ready.",
    },
}

CARDS = {
    "card1": {
        "title": "📊 The Brand Story",
        "color": "card-gold",
        "content": """
**Brand Tracking Scores — Year 3:**
- Aided awareness: **94%** (up from 61% in Year 1)
- Net Promoter Score: **67** (industry average: 42)
- Top-of-mind recall: **38%** (up from 12%)
- Customer satisfaction: **4.2/5**

**Marketing spend Year 3: Rs.320 Crore** (11.4% of revenue)

> *CMO's Board presentation (Year 3, Q2): "Every rupee of marketing spend is generating Rs.4.2 in revenue. We are building an asset that will last 20 years."*
        """
    },
    "card2": {
        "title": "📉 The Financial Timeline",
        "color": "card-teal",
        "content": """
| Year | Revenue | EBITDA | Debt | Interest | **ICR** |
|------|---------|--------|------|----------|---------|
| Year 1 | Rs.800 Cr | Rs.140 Cr | Rs.600 Cr | Rs.48 Cr | **2.9×** ✅ |
| Year 2 | Rs.1,400 Cr | Rs.190 Cr | Rs.2,100 Cr | Rs.168 Cr | **1.13×** ⚠️ |
| Year 3 | Rs.2,200 Cr | Rs.180 Cr | Rs.4,800 Cr | Rs.384 Cr | **0.47×** 🔴 |

**Marketing spend Year 3: Rs.320 Crore**
**Interest expense Year 3: Rs.384 Crore**

> *One of these two numbers could have saved the company. Which one?*
        """
    },
    "card3": {
        "title": "📝 The Memo Nobody Acted On",
        "color": "card-red",
        "content": """
**CFO Memo to Board — Year 2, Month 9:**

*"Our interest expense has grown from Rs.48 Crore to Rs.168 Crore in 24 months. At current debt levels, EBITDA must grow by at least 40% next year for ICR to remain above 1.5×. I recommend we halt discretionary spend and begin a debt repayment programme immediately."*

**Board response:** *Noted. No action recorded.*

**Discretionary spend reviewed:** Rs.0 Crore cut.

**Six months later — CFO Second Memo, Year 3 Month 3:**
*"ICR is now 0.47×. We cannot cover interest from operations. This is a covenant breach. I am formally requesting the Board authorise a restructuring advisor."*

**Board response:** *CEO presented revised revenue projections. Board voted to allow 2 more quarters.*
        """
    },
    "card4": {
        "title": "💰 The Marketing vs Debt Debate",
        "color": "card-navy",
        "content": """
**CMO's position:**
Rs.320 Crore generates Rs.1,344 Crore in attributed revenue (Rs.4.2× ROI).
Brand equity is a 20-year asset. You cannot measure it in one year.

**CFO's counter:**
Rs.320 Crore used for debt repayment saves Rs.38 Crore/year in interest.
PV of interest saving at 12% discount: **Rs.38 Cr / 0.12 = Rs.317 Crore** (perpetuity).

Rs.320 Cr debt repayment ≈ Rs.317 Cr NPV of interest saved.

> *"Brand equity cannot service debt."* — CFO

**The question the Board never asked:**
What is the incremental EBITDA from the Rs.320 Crore of marketing-generated revenue?
*(Answer on the hidden side of this card — unlock during Investigation)*
        """
    },
    "card5": {
        "title": "👥 The HR Decision",
        "color": "card-red",
        "content": """
**Year 3, Month 2 — HR Head submits annual hiring plan:**
- New hires: **1,200 employees**
- Average CTC: Rs.8 lakh
- Total incremental payroll: **Rs.96 Crore**
- ICR at time of submission: **0.47×**

**CFO's approval note:**
*"Approved subject to EBITDA improvement in Q2."*

**Q2 EBITDA result:** Rs.38 Crore (vs Rs.60 Crore plan — **37% miss**)

**Status of 1,200 hires:** All joined. No review triggered.

**8 months later:** Salary delays begin.
**12 months later:** Operations suspended.

> *The HR Head did not know what ICR meant.*
> *The CFO approved a plan with conditions that were never enforced.*
> *Which failure was more consequential?*
        """
    },
    "card6": {
        "title": "📋 The Customer Evidence",
        "color": "card-green",
        "content": """
**Exit survey — 2,400 churned customers, Year 3:**

| Reason for leaving | % |
|--------------------|---|
| Found a cheaper alternative | 42% |
| Product quality declined | **31%** |
| Still love the brand, can't afford premium | 19% |
| Other | 8% |

**Operations Head's Rs.80 Crore investment proposal (Year 3):**
- Supply chain quality improvement
- Product consistency programme
- Customer experience upgrade

**Board decision:** Budget allocated to marketing instead.

**CMO's interpretation of exit data:** *"We need more marketing to reinforce premium positioning and justify the price."*

**Operations Head's interpretation:** *"We need to fix the product. 31% are leaving because the product is broken, not the brand."*
        """
    },
    "card7": {
        "title": "🗳️ The Three Options",
        "color": "card-gold",
        "content": """
**Option A — Restructuring:**
Cut marketing to Rs.80 Crore. Reduce headcount by 3,000.
Use savings to service debt. 18-month runway to profitability.
*Preserves 11,000 jobs. Requires painful cuts. Brand takes a hit.*

**Option B — Sell the Brand:**
Competitor has offered Rs.1,400 Crore for brand + customer list.
Covers 58% of debt. Rs.1,000 Crore still owed to banks.
*All 14,000 jobs lost. Partial debt recovery. Clean exit.*

**Option C — Emergency Equity Raise:**
Strategic investor offers Rs.1,200 Crore for 51% stake.
Founder loses control. Activist investor diluted by 40%.
*Company survives. Ownership changes. Existing shareholders take heavy loss.*
        """
    },
    "card8": {
        "title": "🔍 The Analyst's Task",
        "color": "card-navy",
        "content": """
**Your mission: Find the three decision points.**

The exact moment. The exact number. The exact person who had the authority to change the outcome.

**Clue 1:** Look at Year 1 vs Year 2. Debt tripled. EBITDA grew 36%. What does the ICR change tell you about sustainability?

**Clue 2:** The CFO memo in Year 2 Month 9. What would have happened to the Year 3 ICR if the Board had acted?

**Clue 3:** The 1,200-hire plan in Year 3 Month 2. ICR was 0.47×. The plan added Rs.96 Crore in fixed costs. What did the ICR become after the hires joined?

**Hidden calculation (solve this):**
If marketing had been cut from Rs.320 Crore to Rs.80 Crore in Year 3, and the Rs.240 Crore was used to repay debt:
- New debt: Rs.4,800 - Rs.240 = Rs.4,560 Crore
- New interest (at 8%): Rs.365 Crore
- New ICR: Rs.180 Crore / Rs.365 Crore = ?
- *Would this have saved the company?*
        """
    },
}

OPTIONS = {
    "A": {"label": "Option A — Restructure", "desc": "Cut marketing, reduce 3,000 jobs, service debt", "color": GOLD},
    "B": {"label": "Option B — Sell the Brand", "desc": "Rs.1,400 Cr sale, all 14,000 jobs lost", "color": RED},
    "C": {"label": "Option C — Equity Raise", "desc": "51% stake for Rs.1,200 Cr, founder loses control", "color": TEAL},
}

QUESTIONS = [
    {"from": "CMO", "to": "CFO", "q": "You say marketing spend should have been cut. But our brand metrics were the best in company history. What is the financial value of brand equity — and how exactly do you measure it?"},
    {"from": "CFO", "to": "CMO", "q": "In Year 3, our interest expense was Rs.384 Crore and our marketing spend was Rs.320 Crore. We could not pay our interest from operations. Should that comparison have changed anything?"},
    {"from": "CHRO", "to": "CFO", "q": "The ICR was 0.47× when I submitted the hiring plan. Why was it approved?"},
    {"from": "CFO", "to": "CHRO", "q": "The ICR was 0.47× when you submitted the hiring plan. Why did you not check it before submitting?"},
    {"from": "Activist Investor", "to": "CEO", "q": "At the Year 2 AGM you said the company was on track. The ICR was already 1.13×. Was that statement accurate?"},
    {"from": "Operations Head", "to": "CMO", "q": "31% of our churned customers left because product quality declined. You got the Rs.80 Crore I needed for product investment. If that had gone to operations instead of marketing, would those customers still be with us?"},
    {"from": "Lead Banker", "to": "CEO", "q": "We gave you two covenant waivers. Both times you promised a turnaround. What specifically did you believe was going to change — and when did you know it was not going to?"},
    {"from": "Junior Analyst", "to": "All", "q": "I have found the three decision points where a different choice would have changed the outcome. The Board is collectively responsible for two of them. Do you want to hear the specific numbers?"},
]

SUSPECTS = ["CEO", "CFO", "CHRO", "CMO", "Board (collective)", "External forces (fuel/market)"]

# ── Helper functions ────────────────────────────────────────────────────────
def phase_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <div class="headline">{icon} {title}</div>
        {"<div class='subline'>" + subtitle + "</div>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)

def role_pill(role, size="normal"):
    r = ROLES[role]
    fs = "0.75rem" if size == "normal" else "0.9rem"
    st.markdown(f"""
    <span class="role-badge" style="background:{r['badge_bg']};color:{r['color']};font-size:{fs};">
        {r['icon']} {role}
    </span>
    """, unsafe_allow_html=True)

def metric_box(value, label, color=TEAL, danger=False):
    col = RED if danger else color
    return f"""
    <div class="big-metric">
        <div class="value" style="color:{col};">{value}</div>
        <div class="label">{label}</div>
    </div>
    """

def card_html(title, content, card_class="card-teal"):
    st.markdown(f'<div class="card {card_class}">', unsafe_allow_html=True)
    st.markdown(f"**{title}**")
    st.markdown(content)
    st.markdown('</div>', unsafe_allow_html=True)

def icr_color(icr):
    if icr >= 2.0: return GREEN, "✅ SAFE"
    if icr >= 1.5: return GOLD, "⚠️ WATCH"
    if icr >= 1.0: return "#E67E22", "🔶 DANGER"
    return RED, "🔴 CRITICAL"

# ── PHASE: LOBBY ───────────────────────────────────────────────────────────
if st.session_state.phase == "lobby":

    st.markdown(f"""
    <div style="text-align:center; padding: 3rem 1rem 2rem 1rem;">
        <div style="font-size:4rem; margin-bottom:0.5rem;">🏢</div>
        <div style="font-size:2.8rem; font-weight:800; color:{GOLD}; line-height:1.2;">
            The Last Board Meeting
        </div>
        <div style="font-size:1.1rem; color:#8aabcc; margin-top:0.8rem; max-width:600px; margin-left:auto; margin-right:auto;">
            A company is in crisis. The Board has called an emergency meeting.<br>
            Every function is in the room. Nobody agrees on what went wrong.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
        <div class="card card-gold">
            <div style="font-size:0.8rem; color:{GOLD}; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.5rem;">
                📋 MISSION BRIEFING
            </div>
            <div style="font-size:0.95rem; line-height:1.7; color:#c8ddef;">
                A fictional Indian company is 90 days from collapse.<br><br>
                You will be assigned a <strong style="color:{GOLD};">role</strong> — CEO, CFO, CHRO, CMO, Operations, Banker, Investor, or Analyst.<br><br>
                You will investigate the financial evidence, run a Board meeting, vote on a rescue plan, and discover what <em>really</em> killed the company.<br><br>
                <strong style="color:white;">The number that explains everything: 0.47</strong><br>
                <span style="color:#8aabcc; font-size:0.85rem;">Figure out what it is. Figure out what it means.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        team = st.text_input("🏷️ Enter your team / company name", placeholder="e.g. Team Alpha, Board Room 3...")
        role = st.selectbox("🎭 Select your role", ["— choose —"] + list(ROLES.keys()))

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("⚡ Enter the Boardroom", use_container_width=True, type="primary"):
            if role == "— choose —":
                st.error("Please select a role to continue.")
            else:
                st.session_state.selected_role = role
                st.session_state.team_name = team if team else "Anonymous Team"
                st.session_state.phase = "briefing"
                st.rerun()

        st.markdown(f"""
        <div style="text-align:center; margin-top:1.5rem;">
            <div style="display:flex; justify-content:center; gap:1rem; flex-wrap:wrap;">
                {''.join([f'<span style="font-size:0.8rem; color:#4a7aaa;">{r["icon"]} {name}</span>' for name, r in ROLES.items()])}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── PHASE: BRIEFING ────────────────────────────────────────────────────────
elif st.session_state.phase == "briefing":
    role = st.session_state.selected_role
    r = ROLES[role]

    phase_header("🎭", "Your Role Briefing", f"Team: {st.session_state.team_name}")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div style="text-align:center; padding:2rem; background:linear-gradient(135deg, {r['badge_bg']}, #1a2a3a);
             border-radius:16px; border:2px solid {r['color']};">
            <div style="font-size:4rem;">{r['icon']}</div>
            <div style="font-size:1.5rem; font-weight:800; color:{r['color']}; margin-top:0.5rem;">{role}</div>
            <div style="font-size:0.85rem; color:#8aabcc; margin-top:0.3rem; font-style:italic;">{r['tagline']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card card-gold">
            <div style="font-size:0.75rem; color:{GOLD}; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;">Hidden Objective</div>
            <div style="margin-top:0.4rem; color:#f0d090; font-weight:500;">{r['hidden_objective']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card card-teal">
            <div style="font-size:0.75rem; color:{TEAL}; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;">What You Know (That Others Don't)</div>
            <div style="margin-top:0.4rem; color:#a0d4dc; line-height:1.6;">{r['secret_info']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card card-navy">
            <div style="font-size:0.75rem; color:#7aabdd; font-weight:700; text-transform:uppercase; letter-spacing:0.1em;">Your Opening Statement</div>
            <div style="margin-top:0.4rem; color:#c8ddef; font-style:italic;">"{r['opening_statement']}"</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class="alert-gold">
            <strong>⏱️ Game Flow</strong><br>
            Phase 1: Investigation (20 min) — unlock evidence cards<br>
            Phase 2: Board Meeting (25 min) — ask questions, debate<br>
            Phase 3: Vote on the rescue plan<br>
            Phase 4: Reveal — find out what really happened
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class="alert-gold">
            <strong>🎯 Remember</strong><br>
            Stay in character during the Board meeting.<br>
            The number 0.47 — figure out what it is.<br>
            Everyone is partially right. Everyone is partially responsible.<br>
            The best outcome uses finance to support humanity.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔍 Begin Investigation →", use_container_width=True, type="primary"):
        st.session_state.phase = "investigation"
        st.session_state.timer_start = time.time()
        st.session_state.timer_duration = 20 * 60
        st.rerun()

# ── PHASE: INVESTIGATION ───────────────────────────────────────────────────
elif st.session_state.phase == "investigation":
    role = st.session_state.selected_role

    # Timer
    elapsed = time.time() - st.session_state.timer_start
    remaining = max(0, st.session_state.timer_duration - elapsed)
    mins = int(remaining // 60)
    secs = int(remaining % 60)

    col_t, col_role, col_btn = st.columns([1, 3, 1])
    with col_t:
        color = RED if mins < 5 else GOLD
        st.markdown(f"""
        <div class="timer-box" style="border-color:{color}; color:{color}; font-size:2rem; padding:0.6rem;">
            {mins:02d}:{secs:02d}
        </div>
        """, unsafe_allow_html=True)
    with col_role:
        phase_header("🔍", "Investigation Phase", "Unlock evidence cards. Find what the company is hiding.")
    with col_btn:
        if st.button("→ Board Meeting", type="primary"):
            st.session_state.phase = "boardroom"
            st.session_state.timer_start = time.time()
            st.session_state.timer_duration = 25 * 60
            st.rerun()

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # ICR Calculator — always visible
    st.markdown(f"""
    <div class="card card-teal">
        <div style="font-size:0.8rem; color:{TEAL}; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.8rem;">
            🧮 Interest Coverage Ratio Calculator — The Number That Explains Everything
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        ebitda = st.number_input("EBITDA (Rs. Crore)", value=180.0, step=10.0)
    with c2:
        interest = st.number_input("Interest Expense (Rs. Crore)", value=384.0, step=10.0)
    with c3:
        if interest > 0:
            icr = ebitda / interest
            col, status = icr_color(icr)
            st.markdown(f"""
            <div style="margin-top:1.8rem;">
                {metric_box(f"{icr:.2f}×", f"ICR  —  {status}", col, icr < 1.5)}
            </div>
            """, unsafe_allow_html=True)

    if interest > 0 and ebitda > 0:
        icr = ebitda / interest
        if icr < 1.0:
            st.markdown(f'<div class="alert-red" style="margin-top:0.5rem;">🔴 ICR below 1.0× — the company cannot pay its interest from operations. Every rupee of interest must be funded by selling assets or borrowing more. This is the definition of insolvency.</div>', unsafe_allow_html=True)
        elif icr < 1.5:
            st.markdown(f'<div class="alert-gold" style="margin-top:0.5rem;">⚠️ ICR below 1.5× — most bank covenants require ICR ≥ 1.5×. This company is likely in technical covenant breach.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-green" style="margin-top:0.5rem;">✅ ICR above 1.5× — company can service its debt from operations. Financial position is manageable.</div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Evidence cards
    st.markdown(f"### 📁 Evidence Cards — Click to unlock")
    st.markdown(f"<div style='color:#8aabcc; font-size:0.85rem; margin-bottom:1rem;'>Each card reveals a piece of the story. The full picture only emerges when all cards are open.</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    card_items = list(CARDS.items())

    for idx, (card_key, card_data) in enumerate(card_items):
        col = col1 if idx % 2 == 0 else col2
        with col:
            is_unlocked = card_key in st.session_state.cards_unlocked
            if is_unlocked:
                with st.expander(f"✅ {card_data['title']}", expanded=True):
                    st.markdown(card_data['content'])
                    if card_key == "card4" and is_unlocked:
                        st.markdown("---")
                        st.markdown("**🔓 Hidden calculation (unlocked):**")
                        st.markdown("""
                        Incremental EBITDA from Rs.320 Cr marketing-generated revenue:
                        - Marketing-attributed revenue: Rs.1,344 Crore
                        - Company-wide EBITDA margin: 8.2% (180/2,200)
                        - Incremental EBITDA = Rs.1,344 Cr × 8.2% = **Rs.110 Crore**
                        - Interest cost of Rs.320 Cr debt (at 8%): **Rs.25.6 Crore/year**
                        - Incremental EBITDA >> Interest cost → marketing did generate real value
                        - **BUT**: the debt itself was the problem, not just this year's interest
                        - The Rs.320 Cr added to a debt pile that was already destroying the company
                        """)
            else:
                if st.button(f"🔒 Unlock: {card_data['title']}", key=f"unlock_{card_key}", use_container_width=True):
                    st.session_state.cards_unlocked.append(card_key)
                    st.rerun()

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Suspect ranking
    st.markdown("### ⚖️ Preliminary Suspect Ranking")
    st.markdown("<div style='color:#8aabcc; font-size:0.85rem; margin-bottom:1rem;'>Rank from most to least responsible for the company's collapse. You can update this in the Board Meeting.</div>", unsafe_allow_html=True)

    for i, suspect in enumerate(SUSPECTS):
        rank = st.selectbox(f"Rank for {suspect}", ["-"] + ["1st", "2nd", "3rd", "4th", "5th", "6th"],
                          key=f"rank_{suspect}", index=0)
        st.session_state.suspect_rankings[suspect] = rank

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏛️ Enter the Board Meeting →", use_container_width=True, type="primary"):
        st.session_state.phase = "boardroom"
        st.session_state.timer_start = time.time()
        st.session_state.timer_duration = 25 * 60
        st.rerun()

# ── PHASE: BOARDROOM ───────────────────────────────────────────────────────
elif st.session_state.phase == "boardroom":
    role = st.session_state.selected_role
    r = ROLES[role]

    elapsed = time.time() - st.session_state.timer_start
    remaining = max(0, st.session_state.timer_duration - elapsed)
    mins = int(remaining // 60)
    secs = int(remaining % 60)

    col_t, col_h, col_b = st.columns([1, 3, 1])
    with col_t:
        color = RED if mins < 5 else GOLD
        st.markdown(f'<div class="timer-box" style="border-color:{color};color:{color};font-size:2rem;padding:0.6rem;">{mins:02d}:{secs:02d}</div>', unsafe_allow_html=True)
    with col_h:
        phase_header("🏛️", "Emergency Board Meeting", "Every role must speak. Every accusation must be answered with numbers.")
    with col_b:
        if st.button("→ Vote Now", type="primary"):
            st.session_state.phase = "verdict"
            st.rerun()

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Financial Dashboard", "❓ Mandatory Questions", "💬 Board Discussion", "🎯 My Position"])

    with tab1:
        st.markdown("#### Company Financial Position at Collapse")
        c1, c2, c3, c4 = st.columns(4)
        metrics = [
            ("Rs.2,200 Cr", "Revenue (Year 3)", TEAL, False),
            ("Rs.180 Cr", "EBITDA (Year 3)", TEAL, False),
            ("Rs.4,800 Cr", "Total Debt", RED, True),
            ("0.47×", "Interest Coverage Ratio", RED, True),
        ]
        for col, (val, lab, col_c, danger) in zip([c1,c2,c3,c4], metrics):
            with col:
                st.markdown(metric_box(val, lab, col_c, danger), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(metric_box("Rs.320 Cr", "Marketing Spend Year 3", GOLD, False), unsafe_allow_html=True)
        with c2:
            st.markdown(metric_box("Rs.384 Cr", "Interest Expense Year 3", RED, True), unsafe_allow_html=True)
        with c3:
            st.markdown(metric_box("14,000", "Employees at Risk", "#9B59B6", False), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ICR Timeline — When Did It Become Irreversible?")
        years = ["Year 1", "Year 2", "Year 3"]
        icrs  = [2.9, 1.13, 0.47]

        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_hline(y=1.5, line_dash="dash", line_color=GOLD,
                      annotation_text="Covenant threshold (1.5×)", annotation_position="right")
        fig.add_hline(y=1.0, line_dash="dot", line_color=RED,
                      annotation_text="Cannot cover interest (1.0×)", annotation_position="right")
        fig.add_trace(go.Scatter(
            x=years, y=icrs,
            mode="lines+markers+text",
            text=[f"{v}×" for v in icrs],
            textposition="top center",
            line=dict(color=TEAL, width=3),
            marker=dict(size=12,
                       color=[GREEN, GOLD, RED],
                       line=dict(color=WHITE, width=2)),
            textfont=dict(color=WHITE, size=13)
        ))
        fig.add_vrect(x0="Year 2", x1="Year 3", fillcolor=RED, opacity=0.08,
                      annotation_text="Board ignored CFO memo here", annotation_position="top left")
        fig.update_layout(
            paper_bgcolor="#0f1923", plot_bgcolor="#1a2a3a",
            font=dict(color="#c8ddef", family="Inter"),
            xaxis=dict(gridcolor="#2a4060"),
            yaxis=dict(gridcolor="#2a4060", title="ICR (×)"),
            height=320, margin=dict(l=20,r=20,t=20,b=20),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("#### Mandatory Cross-Examination Questions")
        st.markdown(f"<div style='color:#8aabcc; font-size:0.85rem; margin-bottom:1rem;'>These questions MUST be asked and answered before the vote. Mark each as asked when your group has addressed it.</div>", unsafe_allow_html=True)

        for i, q in enumerate(QUESTIONS):
            is_asked = i in st.session_state.questions_asked
            col_q, col_chk = st.columns([8,1])
            with col_q:
                from_color = ROLES[q['from']]['color'] if q['from'] in ROLES else TEAL
                to_color = ROLES[q['to']]['color'] if q['to'] in ROLES else GOLD
                st.markdown(f"""
                <div class="card {'card-green' if is_asked else 'card-navy'}" style="opacity:{'0.6' if is_asked else '1'};">
                    <span style="color:{from_color}; font-weight:700; font-size:0.8rem;">
                        {ROLES[q['from']]['icon'] if q['from'] in ROLES else '❓'} {q['from']}
                    </span>
                    <span style="color:#8aabcc; font-size:0.8rem;"> asks </span>
                    <span style="color:{to_color}; font-weight:700; font-size:0.8rem;">
                        {ROLES[q['to']]['icon'] if q['to'] in ROLES else '🎯'} {q['to']}:
                    </span>
                    <div style="margin-top:0.4rem; color:#c8ddef; font-style:italic; line-height:1.5;">
                        "{q['q']}"
                    </div>
                    {'<div style="color:#7dcea0; font-size:0.75rem; margin-top:0.3rem;">✅ Asked & Answered</div>' if is_asked else ''}
                </div>
                """, unsafe_allow_html=True)
            with col_chk:
                if not is_asked:
                    if st.button("✓", key=f"q_{i}", help="Mark as asked"):
                        st.session_state.questions_asked.add(i)
                        st.rerun()

        progress = len(st.session_state.questions_asked) / len(QUESTIONS)
        st.progress(progress, text=f"{len(st.session_state.questions_asked)}/{len(QUESTIONS)} questions addressed")

    with tab3:
        st.markdown("#### Board Room Discussion Log")
        with st.form("chat_form", clear_on_submit=True):
            msg = st.text_area("Your statement (speak in character)", height=80,
                             placeholder=f"As {role}: make your argument, challenge a colleague, present evidence...")
            submitted = st.form_submit_button("📢 Speak", use_container_width=True)
            if submitted and msg:
                st.session_state.chat_log.append({
                    "role": role,
                    "icon": r['icon'],
                    "color": r['color'],
                    "msg": msg,
                    "time": time.strftime("%H:%M")
                })

        for entry in reversed(st.session_state.chat_log[-10:]):
            st.markdown(f"""
            <div class="card" style="border-left:3px solid {entry['color']}; padding:0.8rem 1rem; margin-bottom:0.5rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
                    <span style="color:{entry['color']}; font-weight:700; font-size:0.85rem;">
                        {entry['icon']} {entry['role']}
                    </span>
                    <span style="color:#4a6a8a; font-size:0.75rem;">{entry['time']}</span>
                </div>
                <div style="color:#c8ddef; line-height:1.5; font-style:italic;">"{entry['msg']}"</div>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("#### My Position & Arguments")
        role_pill(role, "large")
        st.markdown(f"**Hidden objective:** {r['hidden_objective']}")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("**Your key arguments (use these in the discussion):**")
        st.markdown(f"""
        <div class="card card-teal">
            <div style="color:#a0d4dc; font-size:0.9rem; line-height:1.8;">
                {r['secret_info']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Suspected decision points (your view):**")
        for suspect in SUSPECTS:
            rank = st.session_state.suspect_rankings.get(suspect, "-")
            if rank != "-":
                st.markdown(f"- **{suspect}:** {rank}")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Investigation", use_container_width=True):
            st.session_state.phase = "investigation"
            st.rerun()
    with col2:
        if st.button("🗳️ Proceed to Vote →", use_container_width=True, type="primary"):
            st.session_state.phase = "verdict"
            st.rerun()

# ── PHASE: VERDICT ─────────────────────────────────────────────────────────
elif st.session_state.phase == "verdict":

    phase_header("🗳️", "Cast Your Vote", "The Board must decide. 90 days remain.")

    role = st.session_state.selected_role

    col1, col2, col3 = st.columns(3)
    for col, (opt_key, opt) in zip([col1,col2,col3], OPTIONS.items()):
        with col:
            is_selected = st.session_state.my_vote == opt_key
            border = f"3px solid {opt['color']}" if is_selected else f"1px solid #2a4060"
            bg = f"rgba({','.join(str(int(opt['color'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},0.15)" if is_selected else "#1a2a3a"

            st.markdown(f"""
            <div style="background:{bg}; border:{border}; border-radius:12px; padding:1.2rem; text-align:center; margin-bottom:0.5rem;">
                <div style="font-size:1.5rem; margin-bottom:0.4rem;">
                    {'✅' if is_selected else ('🔵' if opt_key=='A' else ('🔴' if opt_key=='B' else '🟢'))}
                </div>
                <div style="color:{opt['color']}; font-weight:700; font-size:0.9rem;">{opt['label']}</div>
                <div style="color:#8aabcc; font-size:0.8rem; margin-top:0.3rem;">{opt['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Vote {opt_key}", key=f"vote_{opt_key}", use_container_width=True,
                        type="primary" if is_selected else "secondary"):
                if st.session_state.my_vote:
                    st.session_state.votes[st.session_state.my_vote] -= 1
                st.session_state.my_vote = opt_key
                st.session_state.votes[opt_key] += 1
                st.rerun()

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Justification
    st.markdown("#### Your Justification (required)")
    justification = st.text_area(
        "Why did you vote this way? Use at least one financial metric in your answer.",
        height=120,
        placeholder="e.g. I voted for Option A because the ICR of 0.47× shows... The NPV of restructuring vs liquidation..."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Simulated class votes
    st.markdown("#### 📊 Live Vote Count (simulated class)")

    sim_votes = {
        "A": st.session_state.votes["A"] + random.randint(8, 14),
        "B": st.session_state.votes["B"] + random.randint(2, 5),
        "C": st.session_state.votes["C"] + random.randint(5, 9),
    }
    total = sum(sim_votes.values())

    for opt_key, opt in OPTIONS.items():
        pct = int(sim_votes[opt_key] / total * 100) if total > 0 else 0
        col_v, col_p = st.columns([4,1])
        with col_v:
            st.markdown(f"""
            <div style="margin-bottom:0.3rem;">
                <span style="color:{opt['color']}; font-weight:600; font-size:0.85rem;">{opt['label']}</span>
            </div>
            <div class="vote-bar-container">
                <div class="vote-bar" style="width:{pct}%; background:linear-gradient(90deg,{opt['color']}88,{opt['color']});">
                    {sim_votes[opt_key]} votes
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_p:
            st.markdown(f"<div style='text-align:right; color:{opt['color']}; font-weight:700; margin-top:1rem;'>{pct}%</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.my_vote:
        if st.button("🔍 Reveal What Really Happened →", use_container_width=True, type="primary"):
            st.session_state.phase = "reveal"
            st.rerun()
    else:
        st.markdown('<div class="alert-gold">You must cast your vote before proceeding to the reveal.</div>', unsafe_allow_html=True)

# ── PHASE: REVEAL ──────────────────────────────────────────────────────────
elif st.session_state.phase == "reveal":

    phase_header("💥", "The Reveal", "What really happened — and what the numbers said all along.")

    # Dramatic reveal
    st.markdown(f"""
    <div style="text-align:center; padding:2rem; background:linear-gradient(135deg,#1a0a0a,#2a1010);
         border-radius:16px; border:2px solid {RED}; margin-bottom:2rem;">
        <div style="font-size:3rem; margin-bottom:0.5rem;">✈️</div>
        <div style="font-size:2rem; font-weight:800; color:{RED};">KINGFISHER AIRLINES</div>
        <div style="font-size:1.1rem; color:#f1948a; margin-top:0.5rem;">Founded 2005. Ceased operations 2012. 20,000 employees. Rs.9,000 Crore in unpaid debt.</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📅 The Real Timeline", "🔍 Three Decision Points", "📊 Marketing vs Finance", "💡 The HR Lesson"])

    with tab1:
        events = [
            ("2005", "Launch", "Kingfisher launches as India's first luxury airline. ICR: healthy.", GREEN, "✅"),
            ("2007", "Expansion", "Fleet doubles. Debt triples to Rs.2,100 Cr. ICR: 1.13×. First warning.", GOLD, "⚠️"),
            ("2008", "Deccan Air", "Acquires Air Deccan for Rs.550 Crore. Debt: Rs.4,800 Cr. ICR: 0.47×.", RED, "🔴"),
            ("2009", "CFO Memo", "CFO warns Board. Board takes no action. Marketing spend continues.", RED, "📝"),
            ("2010", "Hiring", "HR submits 1,200-hire plan. ICR: 0.47×. Plan approved.", RED, "👥"),
            ("2011", "Salary Delays", "Salaries delayed 45 days. Pilots call in sick. Flights cancelled.", RED, "💸"),
            ("2012", "Collapse", "Operations suspended. 20,000 jobs gone. Rs.9,000 Cr owed.", RED, "💀"),
        ]
        for year, event, desc, color, icon in events:
            st.markdown(f"""
            <div style="display:flex; gap:1rem; margin-bottom:0.8rem; align-items:flex-start;">
                <div style="min-width:50px; text-align:center; color:{color}; font-weight:700;">{year}</div>
                <div style="width:24px; text-align:center;">{icon}</div>
                <div>
                    <div style="color:{color}; font-weight:600;">{event}</div>
                    <div style="color:#8aabcc; font-size:0.85rem;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("#### The Three Moments This Could Have Been Stopped")
        points = [
            ("Decision Point 1", "Year 2 — The Deccan Acquisition", GOLD,
             "Debt jumped from Rs.600 Cr to Rs.2,100 Cr overnight. ICR fell from 2.9× to 1.13×. This was survivable ONLY if EBITDA grew 40% the following year. It grew 0%. After this moment, the company needed perfect execution with zero margin for error.",
             "Who had the power to stop it: The Board. The lenders who provided the acquisition financing. Both chose to believe the growth story."),
            ("Decision Point 2", "Year 2 Month 9 — The Ignored CFO Memo", RED,
             "The CFO wrote the clearest possible warning: 'EBITDA must grow 40% or ICR will breach 1.5×.' The Board noted the memo. Nobody cut the marketing budget. Nobody halted the fleet expansion. This was the last moment to course-correct without a formal restructuring.",
             "Who had the power to stop it: The Board Chairman. The CEO. Either could have insisted on a response to the memo."),
            ("Decision Point 3", "Year 3 Month 2 — The Hiring Plan", "#9B59B6",
             "ICR: 0.47×. The company literally could not cover its interest from operations. The HR Head submitted a plan to hire 1,200 people at Rs.96 Crore incremental cost. The CFO approved it with a condition that was never enforced. 1,200 families joined a company that was already technically insolvent.",
             "Who had the power to stop it: The CFO (who approved despite the condition being missed). The HR Head (who did not check the balance sheet)."),
        ]
        for title, context, color, analysis, responsibility in points:
            st.markdown(f"""
            <div class="card" style="border-left:4px solid {color}; margin-bottom:1rem;">
                <div style="color:{color}; font-weight:700; font-size:1rem;">{title}</div>
                <div style="color:#c8ddef; font-weight:600; margin:0.3rem 0;">{context}</div>
                <div style="color:#8aabcc; font-size:0.9rem; line-height:1.6;">{analysis}</div>
                <div style="color:{color}; font-size:0.85rem; margin-top:0.5rem; font-style:italic;">→ {responsibility}</div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("#### The Marketing vs Finance Debate — Resolved")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="card card-red">
                <div style="color:{RED}; font-weight:700;">CMO's Claim</div>
                <div style="color:#f1948a; margin-top:0.5rem;">Rs.4.2 in revenue for every Rs.1 of marketing spend</div>
                <div style="color:#8aabcc; font-size:0.85rem; margin-top:0.5rem;">
                    Measurement: Revenue attribution model<br>
                    Horizon: Current year<br>
                    Debt impact: Not considered
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="card card-teal">
                <div style="color:{TEAL}; font-weight:700;">CFO's Claim</div>
                <div style="color:#a0d4dc; margin-top:0.5rem;">Rs.320 Cr in debt repayment saves Rs.317 Cr NPV in perpetuity</div>
                <div style="color:#8aabcc; font-size:0.85rem; margin-top:0.5rem;">
                    Measurement: NPV at 12% discount rate<br>
                    Horizon: Long-term<br>
                    Debt impact: Directly considered
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="alert-gold" style="margin-top:1rem;">
            <strong>The actual answer:</strong> Both were partially right — and both were missing the other's framework.
            The CMO was measuring the RIGHT thing for a different question (does marketing generate revenue?).
            The CFO was measuring the RIGHT thing for the actual question (can the company survive?).
            <br><br>
            The company needed someone who could hold BOTH questions simultaneously.
            Marketing ROI measured in revenue is not the same as marketing ROI measured against the cost of capital.
            A campaign that generates Rs.4.20 per rupee spent looks brilliant on a marketing dashboard.
            But if the incremental EBITDA does not cover the interest cost of the debt used to fund it — the campaign destroyed value.
            <br><br>
            <strong>This is what this course teaches you to see.</strong>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown("#### The HR Head's Lesson — The One That Changes Everything")

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#2a1a3e); border:2px solid #9B59B6;
             border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
            <div style="font-size:1rem; color:#c09adc; line-height:1.8;">
                Kingfisher's HR Head submitted a 1,200-person hiring plan when the company's ICR was <strong style="color:{RED};">0.47×</strong>.<br><br>
                She did nothing wrong by ordinary HR standards. She followed process. The plan was justified by business need. It was approved.<br><br>
                She was missing <strong style="color:#c09adc;">one skill</strong>: reading the balance sheet before submitting a budget.<br><br>
                If she had read it, she would have seen the 0.47×. She would have known the company could not service its debt.
                She would never have submitted that plan. She might have given 1,200 families a warning — or an honest conversation about risk — before they joined.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card card-teal">
            <div style="font-size:1rem; font-weight:700; color:{TEAL}; margin-bottom:0.5rem;">
                What "reading the balance sheet" actually means for HR:
            </div>
            <div style="color:#a0d4dc; line-height:2; font-size:0.95rem;">
                1. Find Net Debt and EBITDA → compute Debt/EBITDA (>4× = high risk)<br>
                2. Find Interest Expense → compute ICR = EBITDA/Interest (<1.5× = covenant danger)<br>
                3. Compute EBITDA Buffer = Current EBITDA − (1.5 × Interest) → this is your hiring headroom<br>
                4. Maximum safe payroll addition = Buffer × 0.85<br>
                5. If Buffer is negative → do not submit a hiring plan. Submit a cost reduction plan instead.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center; padding:1.5rem; background:#0f1923; border-radius:12px; margin-top:1rem;">
            <div style="font-size:1.3rem; font-weight:800; color:{GOLD}; line-height:1.4;">
                That five-step check takes 10 minutes.<br>
                It would have changed everything for 1,200 people.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📖 Faculty Debrief & Discussion Guide →", use_container_width=True, type="primary"):
        st.session_state.phase = "debrief"
        st.rerun()

# ── PHASE: DEBRIEF ─────────────────────────────────────────────────────────
elif st.session_state.phase == "debrief":

    phase_header("📖", "Faculty Debrief Guide", "Discussion questions, answer keys, and course connections.")

    tab1, tab2, tab3, tab4 = st.tabs(["🔑 Key Questions", "💰 ICR Calculator", "📚 Course Preview", "🔄 Play Again"])

    with tab1:
        questions = [
            ("Which suspect did your group rank as most responsible — and which financial number best supports that ranking?",
             GOLD,
             "The CFO has the strongest financial case for partial responsibility — two memos, both ignored. But the Board bears institutional responsibility. The most important insight: the CFO did EVERYTHING right by financial standards and was still ignored. This raises the question: what does it take to get financial analysis acted on? Answer: you need to present it in the language of consequences, not ratios. 'ICR is 1.13×' gets noted. 'If EBITDA does not grow 40% this year, our bank can demand immediate repayment of Rs.2,100 Crore' gets urgent attention."),
            ("The CMO's marketing ROI was Rs.4.2 per rupee. The CFO said this destroyed value. Who was right?",
             TEAL,
             "Both were measuring correctly — for different questions. The CMO's Rs.4.2× ROI measures revenue generated per rupee of marketing spend. This is the right metric for a marketing decision. The CFO's NPV analysis measures whether the debt-funded marketing spend creates or destroys enterprise value. This is the right metric for a capital allocation decision. The company needed a framework that combined both — and nobody had built it. The key calculation: incremental EBITDA from marketing-generated revenue (Rs.110 Cr) vs annual interest cost of the marketing debt (Rs.25.6 Cr). Marketing did generate value. But the total debt load was already unsustainable before the marketing spend — the marketing spend accelerated the problem rather than creating it."),
            ("At what exact moment did this company's failure become mathematically inevitable?",
             "#9B59B6",
             "Year 2, Month 3 — when debt jumped from Rs.600 Cr to Rs.2,100 Cr and EBITDA grew only 36%. From this moment, the company needed 40% EBITDA growth to maintain covenant compliance. Anything less and failure was a question of when, not if. The subsequent marketing spend, hiring plan, and Board inaction were all symptoms of the original sin: taking on Rs.2,100 Crore of debt without a credible path to the EBITDA growth required to service it."),
            ("The HR Head did not know what ICR meant. Is this acceptable for a senior executive?",
             RED,
             "This is the most important conversation of Day 1. The answer most students give: 'No, every senior executive should understand basic financial metrics.' The more nuanced answer: 'The HR Head's job description did not include financial analysis. The CFO approved the plan. The system failed, not just the individual.' But the most honest answer: 'In a company where the ICR is 0.47×, every senior executive who submits a budget that increases fixed costs is making a financial decision — whether they know it or not. Not knowing the ICR does not exempt you from the consequences of the decision it implies.' This is the argument for this course."),
        ]

        for q, color, answer in questions:
            with st.expander(f"❓ {q}"):
                st.markdown(f"""
                <div class="card card-teal">
                    <div style="font-size:0.75rem; color:{color}; font-weight:700; text-transform:uppercase; margin-bottom:0.5rem;">
                        FACULTY ANSWER KEY
                    </div>
                    <div style="color:#a0d4dc; line-height:1.7; font-size:0.9rem;">{answer}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.markdown("#### 🧮 ICR Explorer — Try Any Scenario")
        st.markdown("Use this to run live calculations during the debrief discussion.")

        col1, col2 = st.columns(2)
        with col1:
            ebitda_d = st.slider("EBITDA (Rs. Crore)", 0, 1000, 180, 10)
            interest_d = st.slider("Interest Expense (Rs. Crore)", 0, 1000, 384, 10)
        with col2:
            mkt_cut = st.slider("Marketing cut (Rs. Crore)", 0, 320, 240, 10)
            new_ebitda = ebitda_d + (mkt_cut * 0.08)
            new_interest = max(1, interest_d - (mkt_cut * 0.08))
            new_icr = new_ebitda / new_interest if new_interest > 0 else 0
            orig_icr = ebitda_d / interest_d if interest_d > 0 else 0

            col_orig, stat_orig = icr_color(orig_icr)
            col_new, stat_new = icr_color(new_icr)

            st.markdown(f"""
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.8rem; margin-top:1rem;">
                {metric_box(f"{orig_icr:.2f}×", f"Current ICR — {stat_orig}", col_orig, orig_icr < 1.5)}
                {metric_box(f"{new_icr:.2f}×", f"After Cut — {stat_new}", col_new, new_icr < 1.5)}
            </div>
            """, unsafe_allow_html=True)

        if mkt_cut > 0:
            st.markdown(f"""
            <div class="alert-gold" style="margin-top:1rem;">
                Cutting Rs.{mkt_cut} Crore of marketing and using it to repay debt:
                reduces interest by Rs.{mkt_cut*0.08:.1f} Crore/year and adds
                Rs.{mkt_cut*0.08:.1f} Crore of EBITDA (freed from marketing expense).
                ICR moves from {orig_icr:.2f}× to {new_icr:.2f}×.
                {'This would have saved the company from covenant breach.' if new_icr >= 1.5 and orig_icr < 1.5 else
                 'Still below covenant threshold — more cuts needed.' if new_icr < 1.5 else
                 'Already above threshold — company was viable before marketing decision.'}
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("#### What This Game Connects to in the Course")
        connections = [
            ("Module 1: FSA", "Reading ICR and Debt/EBITDA from annual reports. The 10-minute balance sheet check.", TEAL),
            ("Module 2: TVM", "NPV of debt repayment vs marketing spend. The Rs.317 Crore perpetuity calculation.", GOLD),
            ("Module 3: Capital Budgeting", "PI ranking: marketing project PI vs debt repayment PI. Which creates more value?", "#9B59B6"),
            ("Module 6: WACC", "The company's WACC was higher than its ROIC. It was destroying value every quarter.", GREEN),
            ("Module 7: Capital Structure", "Degree of Operating Leverage. High fixed costs + high debt = catastrophic DOL.", "#E67E22"),
            ("Module 10: Forecasting", "Scenario planning: what if EBITDA misses by 20%? The company had no Plan B.", "#3498DB"),
            ("Module 11: Debt", "Covenant breach mechanics. ICR, DSCR, restricted payment clauses. Hiring headroom formula.", RED),
        ]
        for mod, connection, color in connections:
            st.markdown(f"""
            <div style="display:flex; gap:0.8rem; margin-bottom:0.6rem; align-items:flex-start;">
                <span style="color:{color}; font-weight:700; min-width:180px; font-size:0.85rem;">{mod}</span>
                <span style="color:#8aabcc; font-size:0.85rem; line-height:1.5;">{connection}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center; padding:1.5rem; background:linear-gradient(135deg,#0d1a27,#1a2a3a);
             border-radius:16px; border:1px solid {TEAL};">
            <div style="font-size:1.1rem; font-weight:700; color:{GOLD}; line-height:1.6;">
                "The number 0.47 was in the annual report three years before the collapse.<br>
                Nobody read it.<br>
                This course teaches you to read it."
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown("#### Play Again with a Different Role")
        st.markdown("<div style='color:#8aabcc; margin-bottom:1rem;'>Different roles reveal different parts of the story. The CFO experience is very different from the CMO experience.</div>", unsafe_allow_html=True)

        for role_name, role_data in ROLES.items():
            col_r, col_b = st.columns([3,1])
            with col_r:
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:0.8rem;">
                    <span style="font-size:1.4rem;">{role_data['icon']}</span>
                    <div>
                        <div style="color:{role_data['color']}; font-weight:700;">{role_name}</div>
                        <div style="color:#8aabcc; font-size:0.8rem;">{role_data['tagline']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                if st.button("Play →", key=f"replay_{role_name}"):
                    st.session_state.selected_role = role_name
                    st.session_state.phase = "briefing"
                    st.session_state.cards_unlocked = []
                    st.session_state.my_vote = None
                    st.session_state.questions_asked = set()
                    st.session_state.chat_log = []
                    st.session_state.suspect_rankings = {}
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏠 Back to Start", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

