"""Evidence-chain figure (v2): dashed arrows for every comparison with p_Holm >= 0.05.

Same drawing as analysis.security_final.paper_assets.fig_chain, but reads the values from
generated/numbers.tex (the frozen numbers) and draws non-significant steps dashed, as the caption states.
Usage: python fig_chain_v2.py PAPER_DIR
"""
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

paper = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
nums = dict(re.findall(r"\\numdef\{([^}]+)\}\{([^}]*)\}", (paper / "generated/numbers.tex").read_text()))
CHAIN = ["A", "Apre", "Apost", "ApostG", "D"]
TESTS = {"A→Apre": "AApre", "Apre→Apost": "ApreApost", "Apost→ApostG": "ApostApostG", "Apost→D": "ApostD"}


def f(key):
    return float(nums[key].replace(",", ""))


plt.rcParams["font.family"] = "DejaVu Sans"
fig, ax = plt.subplots(figsize=(3.4, 2.3))
for x, c in enumerate(CHAIN):
    s, u = int(f(f"ch.{c}.total.s")), int(f(f"ch.{c}.total.u"))
    lo, hi = f(f"ch.{c}.total.lo"), f(f"ch.{c}.total.hi")
    if u:
        ax.bar(x, lo, color="#4c72b0", width=0.6)
        ax.bar(x, hi - lo, bottom=lo, color="#4c72b0", alpha=0.35, width=0.6, hatch="///")
        label = f"{s}(+{u})"
    else:
        mid = 100 * s / f(f"ch.{c}.total.n")
        ax.bar(x, mid, color="#4c72b0", width=0.6)
        ax.errorbar(x, mid, yerr=[[mid - lo], [hi - mid]], color="black", capsize=2, lw=0.8)
        label = f"{s}"
    ax.text(x, hi + 1.5, label, ha="center", va="bottom", fontsize=7)
for i, comp in enumerate(("A→Apre", "Apre→Apost", "Apost→ApostG")):
    left, right = CHAIN.index(comp.split("→")[0]), CHAIN.index(comp.split("→")[1])
    y = 62 + 6 * (i % 2)
    ph = float(nums[f"ch.test.all.{TESTS[comp]}.ph"])
    ax.annotate("", xy=(right, y), xytext=(left, y),
                arrowprops=dict(arrowstyle="->", lw=0.7, ls="-" if ph < 0.05 else "--"))
    ax.text((left + right) / 2, y + 0.8, "$p_{\\rm Holm}$=" + nums[f"ch.test.all.{TESTS[comp]}.ph"],
            ha="center", va="bottom", fontsize=6)
ax.annotate("", xy=(4, 48), xytext=(2, 48), arrowprops=dict(arrowstyle="->", lw=0.7, ls="--"))
ax.text(3, 48.8, "$p_{\\rm Holm}$=" + nums["ch.test.all.ApostD.ph"], ha="center", va="bottom", fontsize=6)
ax.set_xticks(range(len(CHAIN)), CHAIN, fontsize=8)
ax.set_ylabel("Attack success (%)", fontsize=8)
ax.set_ylim(0, 75)
ax.tick_params(axis="y", labelsize=7)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(paper / "figures/fig_chain_v2.pdf", metadata={"CreationDate": None, "ModDate": None})
fig.savefig(paper / "figures/fig_chain_v2.png", dpi=300)
print("saved figures/fig_chain_v2.{pdf,png}")
