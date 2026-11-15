# Profile setup (one time)

1. Make sure this repo is **public** and named exactly like the account (`7YMERA`). GitHub then shows `README.md` on the profile.
2. **Settings, Actions, General, Workflow permissions:** choose **Read and write permissions**, then Save. Without this the daily job cannot commit the new card.
3. **Actions tab, Update skyline card, Run workflow.** The first run replaces the seeded card with exact numbers from GitHub. After that it refreshes itself every day at 00:20 Malaysia time.

## Edit things

- Text, projects, links: `README.md`.
- Toolkit chips: edit `GROUPS` in `scripts/make_toolkit.py`, run `python3 scripts/make_toolkit.py`, commit `toolkit-card.svg`.
- Landmarks and heights: `LANDMARKS` in `scripts/make_skyline.py`.
- Banner: `banner.svg` is plain SVG; edit the text lines.

The first `skyline-card.svg` was drawn from commit history on one machine, so its numbers are approximate until the first Action run.
