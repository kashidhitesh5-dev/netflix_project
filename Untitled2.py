import base64
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


ROOT = Path(__file__).parent
REQUIRED_COLUMNS = {
	"Watch_Date",
	"Region",
	"Monthly_Revenue",
	"Subscription_Plan",
	"Rating",
	"Category",
}


st.set_page_config(
	page_title="Netflix | Audience Intelligence",
	page_icon="logo.png",
	layout="wide",
	initial_sidebar_state="expanded",
)


def image_as_css(path: Path) -> str:
	if not path.exists():
		return ""
	encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
	extension = path.suffix.lstrip(".") or "png"
	return f"url('data:image/{extension};base64,{encoded}')"


def demo_data() -> pd.DataFrame:
	return pd.DataFrame(
		{
			"Watch_Date": pd.date_range("2025-01-01", periods=12, freq="MS"),
			"Region": ["North America", "Europe", "Asia Pacific", "Latin America"] * 3,
			"Monthly_Revenue": [18_400, 14_700, 11_250, 8_900, 21_300, 16_100, 13_850, 9_700, 24_100, 18_600, 15_200, 10_850],
			"Subscription_Plan": ["Premium", "Standard", "Basic", "Premium"] * 3,
			"Rating": [4.8, 4.3, 3.9, 4.5, 4.9, 4.4, 4.1, 4.6, 4.7, 4.2, 4.0, 4.4],
			"Category": ["Drama", "Comedy", "Documentary", "Action"] * 3,
		}
	)


def load_data(uploaded_file=None) -> tuple[pd.DataFrame, bool]:
	source = uploaded_file if uploaded_file is not None else ROOT / "Netflix.csv"
	try:
		frame = pd.read_csv(source)
		if not REQUIRED_COLUMNS.issubset(frame.columns):
			return demo_data(), True
		frame = frame.drop_duplicates().copy()
		frame["Watch_Date"] = pd.to_datetime(frame["Watch_Date"], errors="coerce")
		frame["Monthly_Revenue"] = pd.to_numeric(frame["Monthly_Revenue"], errors="coerce").fillna(0)
		frame["Rating"] = pd.to_numeric(frame["Rating"], errors="coerce").fillna(0)
		return frame.dropna(subset=["Watch_Date"]), False
	except (FileNotFoundError, pd.errors.ParserError, OSError):
		return demo_data(), True


st.markdown(
	f"""
	<style>
	@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=DM+Sans:wght@400;500;700&display=swap');
	:root {{ --red: #e50914; --ink: #090909; --muted: #a6a6a6; --line: rgba(255,255,255,.12); }}
	.stApp {{ background: #090909 {image_as_css(ROOT / 'background.avif')} center / cover fixed; color: #f5f5f5; font-family: 'DM Sans', sans-serif; }}
	.stApp::before {{ content: ''; position: fixed; inset: 0; z-index: -1; background: linear-gradient(90deg, rgba(4,4,4,.98) 0%, rgba(4,4,4,.88) 45%, rgba(4,4,4,.72) 100%); }}
	[data-testid='stSidebar'] {{ background: rgba(7,7,7,.92); border-right: 1px solid var(--line); }}
	.block-container {{ max-width: 1440px; padding: 2rem 3.5rem 4rem; animation: rise .7s ease-out both; }}
	@keyframes rise {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: translateY(0); }} }}
	@keyframes pulse {{ 0%, 100% {{ box-shadow: 0 0 0 0 rgba(229,9,20,.35); }} 50% {{ box-shadow: 0 0 0 10px rgba(229,9,20,0); }} }}
	h1, h2, h3 {{ font-family: 'Barlow Condensed', sans-serif !important; letter-spacing: .02em; }}
	h1 {{ font-size: clamp(2.5rem, 5vw, 5.4rem) !important; line-height: .9 !important; text-transform: uppercase; margin: .5rem 0 0 !important; }}
	.eyebrow {{ color: var(--red); font-size: .72rem; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; }}
	.subtitle {{ color: var(--muted); margin: .65rem 0 1.8rem; }}
	.metric {{ background: rgba(15,15,15,.82); border: 1px solid var(--line); border-top: 3px solid var(--red); padding: 1rem 1.2rem; min-height: 104px; animation: rise .7s .12s ease-out both; }}
	.metric-label {{ color: var(--muted); font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; }}
	.metric-value {{ font-family: 'Barlow Condensed'; font-size: 2.25rem; font-weight: 700; }}
	.section {{ border-top: 1px solid var(--line); margin-top: 2.4rem; padding-top: 1.25rem; }}
	.section-title {{ font-family: 'Barlow Condensed'; font-size: 1.5rem; text-transform: uppercase; letter-spacing: .08em; }}
	.brand {{ display: flex; align-items: center; gap: .7rem; margin-bottom: 2rem; }}
	.brand img {{ width: 95px; }}
	.stButton > button, .stDownloadButton > button {{ border: 1px solid var(--red); border-radius: 0; background: transparent; color: white; }}
	.stButton > button:hover {{ background: var(--red); color: white; border-color: var(--red); }}
	.stRadio label, .stFileUploader label {{ color: #ddd !important; }}
	div[data-testid='stFileUploader'] {{ border: 1px dashed var(--line); padding: .5rem; }}
	</style>
	""",
	unsafe_allow_html=True,
)


with st.sidebar:
	logo = ROOT / "logo.png"
	if logo.exists():
		st.image(str(logo), width=108)
	st.markdown("<div class='eyebrow'>Audience intelligence</div>", unsafe_allow_html=True)
	st.markdown("### Dashboard controls")
	uploaded = st.file_uploader("Upload Netflix CSV", type="csv")
	if uploaded:
		st.success("Dataset loaded")
	st.caption("Expected fields: Watch_Date, Region, Monthly_Revenue, Subscription_Plan, Rating, Category")

netflix, using_demo = load_data(uploaded)
netflix["Month"] = netflix["Watch_Date"].dt.strftime("%b")

st.markdown("<div class='eyebrow'>Netflix analytics / 2025</div>", unsafe_allow_html=True)
st.title("Audience, in focus.")
st.markdown(
	"<p class='subtitle'>A living snapshot of what people watch, where they watch it, and what keeps the lights on.</p>",
	unsafe_allow_html=True,
)
if using_demo:
	st.info("Showing demo data. Add Netflix.csv beside this file or upload your dataset from the sidebar.")

total_revenue = netflix["Monthly_Revenue"].sum()
avg_rating = netflix["Rating"].mean()

top_region = netflix.groupby("Region")["Monthly_Revenue"].sum().idxmax()
metrics = [("Total revenue", f"${total_revenue:,.0f}"), ("Titles tracked", f"{len(netflix):,}"), ("Avg. rating", f"{avg_rating:.1f} / 5"), ("Top market", top_region)]
metric_columns = st.columns(4)
for column, (label, value) in zip(metric_columns, metrics):
	column.markdown(f"<div class='metric'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>", unsafe_allow_html=True)

st.markdown("<div class='section'><span class='section-title'>Performance pulse</span></div>", unsafe_allow_html=True)
chart_one, chart_two = st.columns([1.35, 1])
plt.style.use("dark_background")

with chart_one:
	st.markdown("#### Revenue by region")
	region_revenue = netflix.groupby("Region")["Monthly_Revenue"].sum().sort_values()
	fig, ax = plt.subplots(figsize=(8, 4.1))
	fig.patch.set_alpha(0)
	ax.set_facecolor("#111111")
	ax.barh(region_revenue.index, region_revenue.values, color="#e50914")
	ax.tick_params(colors="#d0d0d0", labelsize=9)
	ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"${value / 1000:.0f}k"))
	ax.grid(axis="x", color="white", alpha=.1)
	ax.set_axisbelow(True)
	for spine in ax.spines.values(): spine.set_visible(False)
	st.pyplot(fig, use_container_width=True)
	plt.close(fig)

with chart_two:
	st.markdown("#### Plan mix")
	plan_counts = netflix.groupby("Subscription_Plan")["Rating"].mean().sort_values(ascending=False)
	fig, ax = plt.subplots(figsize=(6, 4.1))
	fig.patch.set_alpha(0)
	ax.set_facecolor("#111111")
	ax.pie(plan_counts.values, labels=plan_counts.index, startangle=90, colors=["#e50914", "#8b0a10", "#4a4a4a"], wedgeprops={"width": .38, "edgecolor": "#111111"}, textprops={"color": "#eeeeee", "fontsize": 9})
	st.pyplot(fig, use_container_width=True)
	plt.close(fig)

st.markdown("<div class='section'><span class='section-title'>Monthly momentum</span></div>", unsafe_allow_html=True)
monthly = netflix.groupby("Watch_Date", as_index=False)["Monthly_Revenue"].sum().sort_values("Watch_Date")
st.line_chart(monthly.set_index("Watch_Date"), color="#E50914", height=280)

st.markdown("<div class='section'><span class='section-title'>Latest records</span></div>", unsafe_allow_html=True)
st.dataframe(netflix.sort_values("Watch_Date", ascending=False).head(10), use_container_width=True, hide_index=True)




