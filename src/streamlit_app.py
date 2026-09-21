import streamlit as st
import glob
from pathlib import Path

from config import pages_path


APP_ROOT = Path(__file__).resolve().parents[1]
HEADER_IMAGE = APP_ROOT / "logos" / "—Pngtree—blue minimalistic smart technology background_1145450.jpg"
logo_image = APP_ROOT / "logos" / "FormIA-removebg-preview.png"

def render_branding():
	st.markdown(
		f"""
		<style>
			[data-testid="stAppViewContainer"] .main .block-container {{
				padding-top: 4.5rem;
			}}
			
			
			.formia-footer {{
				margin-top: 4rem;
				padding: 2rem 0 .5rem;
				border-top: 1px solid rgba(64, 217, 242, .35);
				color: #526174;
			}}
			.formia-footer-grid {{
				display: grid;
				grid-template-columns: 1.5fr 1fr 1fr 1fr;
				gap: 1.5rem;
			}}
			.formia-footer h3 {{
				margin: 0 0 .55rem;
				color: #14243f;
				font-size: 1rem;
			}}
			.formia-footer p {{
				margin: .25rem 0;
				font-size: .88rem;
				line-height: 1.5;
			}}
			.formia-footer a {{ color: #087f9b; text-decoration: none; }}
			.formia-footer-bottom {{
				margin-top: 1.5rem;
				padding-top: .8rem;
				border-top: 1px solid rgba(82, 97, 116, .2);
				font-size: .78rem;
			}}
			@media (max-width: 700px) {{
				[data-testid="stAppViewContainer"] .main .block-container {{
					padding-top: 4rem;
				}}
				.formia-footer-grid {{ grid-template-columns: 1fr 1fr; }}
			}}
		</style>
		""",
		unsafe_allow_html=True,
	)
def render_footer():
	st.markdown(
		"""
		<footer class="formia-footer">
			<div class="formia-footer-grid">
				<section>
					<h3>FormIA Workshops</h3>
					<p>A shared space for hands-on workshops and experimental learning.</p>
				</section>
				<section>
					<h3>Groups</h3>
					<p>Microscopy</p>
					<p>Algorithms</p>
					<p>Data and AI</p>
				</section>
				<section>
					<h3>Contact</h3>
					<p><a href="mailto:formia@ens-paris-saclay.fr">formia@ens-paris-saclay.fr</a></p>
					<p>Questions, ideas, and workshop feedback welcome.</p>
				</section>
				<section>
					<h3>Project</h3>
					<p>Collaborative teaching tools for the FormIA community.</p>
					<p><a href="https://github.com/" target="_blank">Project resources</a></p>
				</section>
			</div>
			<p class="formia-footer-bottom">FormIA Workshops · Built for exploration and shared learning</p>
		</footer>
		""",
		unsafe_allow_html=True,
	)


render_branding()
st.markdown(
    """
    <style>
    img[data-testid="stSidebarLogo"] {
            height: 4.5rem;}
	img[data-testid="stHeaderLogo"] {
                height: 4.5rem;
}

    </style>
    """,
    unsafe_allow_html=True,
)
home_page = st.Page(pages_path / "home.py", title="Home")

st.logo(logo_image, link ="http://localhost:8501", icon_image=logo_image)
pages = glob.glob(str(pages_path/ "**" / "*.py"))
topics = set([Path(page).relative_to(pages_path).parent.parts[0] for page in pages])

page_list = {topic: [st.Page(page, title=Path(page).stem.capitalize()) for page in pages if Path(page).relative_to(pages_path).parent.parts[0] == topic] for topic in topics}
## add a home page but not show it in the sidebar
all_pages = {"Home": [home_page], **page_list}
pg = st.navigation(all_pages, position="hidden")
with st.sidebar:
    for topic, p_list in page_list.items():
        with st.expander(f"**{topic}**"):
            for p in p_list:
                st.page_link(p, label=p.title)
pg.run()
render_footer()

