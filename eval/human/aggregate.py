#!/usr/bin/env python3
"""여러 사람의 평가 결과(JSON)를 합쳐 익명으로 집계한다.

  python eval/human/aggregate.py <JSON이 든 폴더> [--out summary.json]

- 평가자 이름은 출력하지 않고 R01, R02…로 바꾼다(파일 순서 기준).
- 이름·코멘트 원문은 요약 JSON에 넣지 않는다(코멘트는 개수만).
- 불완전한 제출(승자나 별점이 비어 있는 행)은 따로 표시하고 집계에서 뺀다.
"""
import argparse, json, random, statistics as st
from pathlib import Path

CRIT = ["new", "do", "read", "fit"]
LABEL = {"new": "새로움", "do": "실행 가능성", "read": "이해하기 쉬움", "fit": "내 문제에 맞음"}


def load(folder: Path):
    people = []
    for f in sorted(folder.glob("*.json")):
        rows = json.loads(f.read_text(encoding="utf-8"))
        people.append(rows)
    return people


def complete(r):
    if r.get("winner") not in ("A", "B", "tie"):
        return False
    return all(str(r.get(f"{k}_{c}", "")).strip() != "" for k in "AB" for c in CRIT)


def per_person(rows):
    """한 사람의 문제별 (승자, 항목별 스킬-기준선 차이)"""
    out = []
    for r in rows:
        if not complete(r):
            continue
        sk = {c: int(r[f"{'A' if r['A_is']=='skill' else 'B'}_{c}"]) for c in CRIT}
        ba = {c: int(r[f"{'A' if r['A_is']=='base' else 'B'}_{c}"]) for c in CRIT}
        out.append({"id": r["id"], "domain": r.get("domain", ""), "winner_is": r["winner_is"],
                    "picked_slot": r["winner"], "skill": sk, "base": ba,
                    "has_comment": bool(str(r.get("comment", "")).strip())})
    return out


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def boot_ci(vals, n=5000, seed=1):
    rng = random.Random(seed)
    ms = sorted(mean([rng.choice(vals) for _ in vals]) for _ in range(n))
    return ms[int(n * 0.025)], ms[int(n * 0.975)]


def sign_flip_p(vals, n=20000, seed=2):
    """사람별 평균 차이가 0인지 보는 부호 뒤집기 검정(양측)"""
    rng = random.Random(seed)
    obs = abs(mean(vals))
    hit = sum(abs(mean([v if rng.random() < .5 else -v for v in vals])) >= obs - 1e-12 for _ in range(n))
    return hit / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    people = load(Path(a.folder))
    P = []
    dropped = 0
    for i, rows in enumerate(people, 1):
        cl = per_person(rows)
        dropped += len(rows) - len(cl)
        P.append((f"R{i:02d}", cl))

    n_people = len(P)
    all_rows = [(rid, x) for rid, cl in P for x in cl]
    wins = {"skill": 0, "base": 0, "tie": 0}
    for _, x in all_rows:
        wins[x["winner_is"]] += 1
    slot = {"A": 0, "B": 0, "tie": 0}
    for _, x in all_rows:
        slot[x["picked_slot"]] += 1

    print(f"평가자 {n_people}명 / 판단 {len(all_rows)}건 (불완전 {dropped}건 제외)")
    print(f"승패: 스킬 {wins['skill']} · 스킬 없음 {wins['base']} · 비슷함 {wins['tie']}"
          f"  → 스킬 승률(비김 제외) {wins['skill']/max(1,wins['skill']+wins['base']):.0%}")
    print(f"위치 편향 점검: A 선택 {slot['A']} · B 선택 {slot['B']} · 비슷함 {slot['tie']}")

    # 사람별 다수결
    pw = {"skill": 0, "base": 0, "tie": 0}
    for rid, cl in P:
        s = sum(1 for x in cl if x["winner_is"] == "skill"); b = sum(1 for x in cl if x["winner_is"] == "base")
        pw["skill" if s > b else "base" if b > s else "tie"] += 1
    print(f"사람별 다수결: 스킬 {pw['skill']}명 · 스킬 없음 {pw['base']}명 · 동률 {pw['tie']}명")

    print("\n[문제별]")
    probs = sorted({x["id"] for _, x in all_rows})
    summary = {"raters": n_people, "judgments": len(all_rows), "wins": wins, "slot_picks": slot,
               "rater_majority": pw, "by_problem": {}, "criteria": {}}
    for pid in probs:
        xs = [x for _, x in all_rows if x["id"] == pid]
        w = {"skill": 0, "base": 0, "tie": 0}
        for x in xs:
            w[x["winner_is"]] += 1
        d = {c: mean([x["skill"][c] - x["base"][c] for x in xs]) for c in CRIT}
        summary["by_problem"][pid] = {"domain": xs[0]["domain"], "n": len(xs), "wins": w, "mean_diff": d}
        print(f"  {pid} {xs[0]['domain']:<8} n={len(xs):>2}  스킬 {w['skill']:>2} / 없음 {w['base']:>2} / 비슷 {w['tie']:>2}   "
              + " ".join(f"{LABEL[c]}{d[c]:+.2f}" for c in CRIT))

    print("\n[항목별 평균 (1~5)]  차이 = 스킬 − 스킬 없음, 사람 단위 95% 신뢰구간·부호 뒤집기 p")
    for c in CRIT:
        sk = [x["skill"][c] for _, x in all_rows]; ba = [x["base"][c] for _, x in all_rows]
        diffs = []
        for rid, cl in P:
            if cl:
                diffs.append(mean([x["skill"][c] - x["base"][c] for x in cl]))
        lo, hi = boot_ci(diffs)
        p = sign_flip_p(diffs)
        summary["criteria"][c] = {"skill": mean(sk), "base": mean(ba), "diff": mean(diffs), "ci95": [lo, hi], "p": p}
        print(f"  {LABEL[c]:<8} 스킬 {mean(sk):.2f} · 없음 {mean(ba):.2f} · 차이 {mean(diffs):+.2f}  [{lo:+.2f}, {hi:+.2f}]  p={p:.3f}")

    tot_s = [mean([mean(list(x["skill"].values())) for x in cl]) for _, cl in P if cl]
    tot_b = [mean([mean(list(x["base"].values())) for x in cl]) for _, cl in P if cl]
    dd = [s - b for s, b in zip(tot_s, tot_b)]
    lo, hi = boot_ci(dd)
    print(f"\n[4항목 평균] 스킬 {mean(tot_s):.2f} · 없음 {mean(tot_b):.2f} · 차이 {mean(dd):+.2f} [{lo:+.2f}, {hi:+.2f}] p={sign_flip_p(dd):.3f}")
    summary["overall"] = {"skill": mean(tot_s), "base": mean(tot_b), "diff": mean(dd), "ci95": [lo, hi]}
    print(f"코멘트를 남긴 판단: {sum(1 for _, x in all_rows if x['has_comment'])}건 (원문은 요약에 넣지 않음)")

    if a.out:
        Path(a.out).write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n요약 저장: {a.out}")


if __name__ == "__main__":
    main()
