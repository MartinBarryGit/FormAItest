import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import streamlit as st
from config import pkg_path, root

SCENE_FILE = pkg_path / "manim_algs.py"


def render_maze(seed, quality, disable_caching):
	"""Render the Labyrinth scene and return the generated video as bytes."""
	render_dir = Path(tempfile.mkdtemp(prefix="maze-manim-"))
	output_name = f"maze-seed-{seed}"
	command = [
		sys.executable,
		"-m",
		"manim",
		f"-{quality}",
		str(SCENE_FILE),
		"Labyrinth",
		"--media_dir",
		str(render_dir),
		"-o",
		output_name,
	]
	environment = os.environ.copy()
	environment["MANIM_SCENARIO_SEED"] = str(seed)
	if disable_caching:
		command.append("--disable_caching")

	try:
		completed = subprocess.run(
			command,
			cwd=root,
			env=environment,
			capture_output=True,
			text=True,
			check=False,
		)
		if completed.returncode != 0:
			details = completed.stderr.strip() or completed.stdout.strip()
			raise RuntimeError(details or "Manim exited without an error message.")

		videos = sorted(render_dir.rglob(f"{output_name}.mp4"))
		if not videos:
			raise RuntimeError("Manim completed, but no MP4 video was created.")
		return videos[0].read_bytes()
	finally:
		shutil.rmtree(render_dir, ignore_errors=True)


def main():
	st.set_page_config(page_title="Maze algorithms", layout="wide")
	st.title("Maze algorithm visualisation")
	st.write("Compare Trémaux, Dijkstra, and A* searching the same generated maze.")

	with st.form("maze_options"):
		columns = st.columns(3)
		seed = columns[0].number_input("Scenario seed", min_value=0, value=1, step=1)
		quality = columns[1].selectbox(
			"Render quality",
			options=["ql", "qm", "qh"],
			format_func={"ql": "Low (fast)", "qm": "Medium", "qh": "High"}.get,
		)
		disable_caching = columns[2].checkbox("Disable Manim cache", value=True)
		render = st.form_submit_button("Render maze", type="primary")

	if render:
		with st.spinner("Rendering the maze with Manim..."):
			try:
				video = render_maze(seed, quality, disable_caching)
			except (OSError, RuntimeError) as error:
				st.error(f"Could not render the maze: {error}")
			else:
				st.session_state["maze_video"] = video
				st.session_state["maze_seed"] = seed

	if "maze_video" in st.session_state:
		st.video(st.session_state["maze_video"])
		st.caption(f"Scenario seed: {st.session_state['maze_seed']}")
	else:
		st.info("Choose the render options and click Render maze to create the video.")


if __name__ == "__main__":
	main()