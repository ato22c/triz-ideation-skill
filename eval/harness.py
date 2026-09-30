#!/usr/bin/env python3
"""블라인드 채점 보조 스크립트.

  python eval/harness.py blind  <run> [split]   # runs/baseline + runs/<run> → runs/<run>/blind/ (무작위 1/2 배정)
  python eval/harness.py score  <run> [split]   # runs/<run>/judge.json + key.json → 조건별 점수표
"""
import json, random, shutil, sys
from pathlib import Path

ROOT = Path(__file__).parent
PROBLEMS = json.loads((ROOT / "problems.json").read_text(encoding="utf-8"))
AXES = ["A", "B", "C", "D", "E", "F"]


def ids(split):
    return [p["id"] for p in PROBLEMS if split in (None, "all", p["split"])]


def blind(run, split):
    run_dir = ROOT / "runs" / run
    out = run_dir / "blind"
    out.mkdir(exist_ok=True)
    key = {}
    rng = random.Random(f"{run}-{split}")
    for pid in ids(split):
        base = ROOT / "runs" / "baseline" / f"{pid}.md"
        cand = run_dir / f"{pid}.md"
        if not (base.exists() and cand.exists()):
            print(f"skip {pid}: missing file")
            continue
        order = ["baseline", "skill"]
        rng.shuffle(order)
        key[pid] = {"1": order[0], "2": order[1]}
        for slot, cond in zip(("1", "2"), order):
            shutil.copyfile(base if cond == "baseline" else cand, out / f"{pid}_{slot}.md")
    (run_dir / "key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"blind ready: {out}  ({len(key)} problems)")


def score(run, split):
    run_dir = ROOT / "runs" / run
    judge = json.loads((run_dir / "judge.json").read_text(encoding="utf-8"))
    key = json.loads((run_dir / "key.json").read_text(encoding="utf-8"))
    tot = {"baseline": [], "skill": []}
    axes = {c: {a: [] for a in AXES} for c in tot}
    print(f"{'문제':<4} {'baseline':>8} {'skill':>8}   (better)")
    for pid in ids(split):
        if pid not in judge or pid not in key:
            continue
        row = {}
        for slot, cond in key[pid].items():
            s = judge[pid][slot]
            row[cond] = sum(s[a] for a in AXES)
            for a in AXES:
                axes[cond][a].append(s[a])
        for c in tot:
            tot[c].append(row[c])
        better = key[pid].get(judge[pid].get("better"), "tie")
        print(f"{pid:<4} {row['baseline']:>8} {row['skill']:>8}   ({better})")
    avg = lambda xs: round(sum(xs) / len(xs), 1) if xs else 0
    print(f"평균  {avg(tot['baseline']):>8} {avg(tot['skill']):>8}")
    print("축별 평균  " + "  ".join(f"{a}:{avg(axes['baseline'][a])}/{avg(axes['skill'][a])}" for a in AXES) + "  (baseline/skill)")


if __name__ == "__main__":
    cmd, run = sys.argv[1], sys.argv[2]
    split = sys.argv[3] if len(sys.argv) > 3 else "dev"
    {"blind": blind, "score": score}[cmd](run, split)
