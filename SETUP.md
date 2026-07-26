# Setup

Everything here belongs in the special repository named after your account:
**`priyaprabhudgp/priyaprabhudgp`**. GitHub renders that repo's `README.md`
at the top of your profile page.

That repo already exists, but currently holds the default *"Introduction to
GitHub"* tutorial content — which is what visitors see right now. Replacing
it is the whole job.

---

## 1. Publish

```bash
cd ~/Downloads/priyaprabhudgp-profile
git init -b main
git remote add origin https://github.com/priyaprabhudgp/priyaprabhudgp.git
git add .
git commit -m "New profile README: emerald marble theme"
git push --force origin main
```

`--force` is deliberate — it overwrites the tutorial content. If you want to
keep that history, `git pull --rebase origin main` first and resolve instead.

---

## 2. Fill in the two placeholders

In `README.md`, under **Elsewhere**, replace:

| Placeholder | Replace with |
|---|---|
| `mailto:you@example.com` | your real email |
| `https://www.linkedin.com/in/your-handle` | your real LinkedIn URL |

If you'd rather not publish contact details at all, delete those two `<a>`
blocks — the GitHub link below them stands fine on its own.

### Also still open

| Where | What |
|---|---|
| **Selected Work** → mobile-walker | `airesx2/mobile-walker` is **private** — a logged-out visitor gets a 404. Make it public, or delete the link and keep the description text. |
| **Contributed To** → Sentinel | Needs a one-line description. `1exii/sentinel` has none on GitHub and I didn't want to invent one. |

Link check, run 2026-07-26:

| Repo | Status |
|---|---|
| `1exii/accessibility-extension` | public ✓ — you're on the contributor list |
| `airesx2/curing-with-care-WEBAPP` | public ✓ — you're on the contributor list |
| `1exii/bisvhacks` | public ✓ — you're on the contributor list |
| `1exii/sentinel` | public ✓ — but GitHub's contributor list shows only `1exii` and `waterfall83`. Harmless if your commits were under a different email, worth a look if not. |
| `airesx2/mobile-walker` | **404 / private** |

---

## 3. Turn on the contribution snake

`.github/workflows/snake.yml` renders your contribution grid as an animated
snake in the emerald/gold palette, and commits it to an `output` branch. The
README reads it from there, so it never depends on a third-party server.

1. Push (step 1 above).
2. Go to **Actions** → *Generate contribution snake* → **Run workflow**.
3. If Actions prompts you to enable workflows on the repo, accept.

It re-runs daily at 06:00 UTC. Until the first run finishes, that one image
in the README will show as broken — this is expected.

---

## 4. About the stats cards

Two of the widgets that every profile-README guide recommends are **currently
offline**, not by your doing:

| Service | Status (checked 2026-07-26) |
|---|---|
| `github-readme-stats.vercel.app` | `503 DEPLOYMENT_PAUSED` |
| `github-profile-trophy.vercel.app` | `402 DEPLOYMENT_DISABLED` |

So the trophy case was dropped, and the two stats cards point at a community
mirror (`github-readme-stats-sigma-five.vercel.app`) that works today. A
mirror is somebody else's server and could vanish too.

**The durable fix — host your own copy (~5 minutes, free):**

1. Fork <https://github.com/anuraghazra/github-readme-stats>.
2. Create a [GitHub personal access token](https://github.com/settings/tokens)
   with **no scopes at all** (public data only).
3. Go to <https://vercel.com/new>, import your fork, and add an environment
   variable `PAT_1` set to that token.
4. Deploy. You'll get a URL like `https://your-stats.vercel.app`.
5. In `README.md`, swap `github-readme-stats-sigma-five.vercel.app` for your
   own hostname. All the colour parameters carry over unchanged.

These services stay up: `shields.io`, `readme-typing-svg.demolab.com`,
`streak-stats.demolab.com`, `github-readme-activity-graph.vercel.app`,
`komarev.com`, and `capsule-render.vercel.app`.

> One quirk worth knowing: adding `disable_animations=true` to the stats card
> makes that mirror return a **completely blank card**. Leave animations on.

---

## 4b. Two cards held back on purpose

The streak card and the activity graph are *not* in the README. They work
fine — they just don't flatter the account today:

- Current streak **0**, longest streak **3 days** (Feb 28 – Mar 2, 2025)
- No public contributions since **9 June 2026**, so the graph is a flat line

Once you've got a stretch of steady commits, paste either of these back into
the **By the Numbers** block. Both are already themed to match:

```html
<img height="170" src="https://streak-stats.demolab.com?user=priyaprabhudgp&border_radius=10&background=0B3D34&border=C9A227&stroke=C9A227&ring=E3C567&fire=E3C567&currStreakNum=EFEFEA&sideNums=CFE3DC&currStreakLabel=E3C567&sideLabels=CFE3DC&dates=8FB8AC" alt="Contribution streak" />

<img width="95%" src="https://github-readme-activity-graph.vercel.app/graph?username=priyaprabhudgp&bg_color=0B3D34&color=E3C567&line=C9A227&point=EFEFEA&title_color=E3C567&area=true&area_color=2E9B85&hide_border=true&radius=10" alt="Contribution activity graph" />
```

A note on the trophy case: `github-profile-trophy` is in every profile guide,
but its public instance now returns `402 DEPLOYMENT_DISABLED`, so there is
nothing to link to. Self-hosting it is possible but rarely worth it.

---

## 5. Regenerating the artwork

`assets/generate_marble.py` produced the banner, divider, and orb from
domain-warped fractal noise — no stock images, so they're yours to keep.

```bash
python3 -m venv venv && ./venv/bin/pip install numpy pillow
./venv/bin/python assets/generate_marble.py
```

Useful knobs, all near the top of the file:

- `INK_STOPS` — the emerald ramp. Change these hexes to re-theme everything.
- `GOLD_DARK` / `GOLD_MID` / `GOLD_LIGHT` — the veining.
- `SEED` — change it for a completely different slab of marble.
- `make_banner(name=..., tagline=...)` — the wordmark text.

If you re-theme, update the hex values in the README's badge and card URLs to
match.
