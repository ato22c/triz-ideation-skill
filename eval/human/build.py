#!/usr/bin/env python3
"""사람용 A/B 블라인드 평가 페이지(index.html)를 만든다.

  python eval/human/build.py [--seed N]

기본 쌍: eval/problems.json 의 6문제 × (스킬 없음 = runs/baseline, 스킬 = runs/v7 또는 runs/v7h)
추가 쌍: eval/human/pairs/<id>/{problem.txt, baseline.md, skill.md} 를 넣으면 같이 들어간다.
A/B 배정은 문제마다 무작위이며(--seed로 고정), 정답표는 base64로 페이지에 들어 있어 평가를 끝낸 뒤에만 공개된다.
"""
import argparse, base64, json, random
from pathlib import Path

HERE = Path(__file__).parent
EVAL = HERE.parent
SKILL_RUNS = {"dev": "v7", "holdout": "v7h"}


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8").replace("\r\n", "\n").strip()


def default_pairs():
    out = []
    for p in json.loads((EVAL / "problems.json").read_text(encoding="utf-8")):
        run = SKILL_RUNS[p["split"]]
        out.append({
            "id": p["id"], "domain": p["domain"], "problem": p["text"],
            "base": read(EVAL / "runs" / "baseline" / f"{p['id']}.md"),
            "skill": read(EVAL / "runs" / run / f"{p['id']}.md"),
        })
    return out


def extra_pairs():
    out = []
    root = HERE / "pairs"
    if not root.exists():
        return out
    for d in sorted(x for x in root.iterdir() if x.is_dir()):
        need = [d / "problem.txt", d / "baseline.md", d / "skill.md"]
        if not all(f.exists() for f in need):
            print(f"skip {d.name}: problem.txt/baseline.md/skill.md 필요")
            continue
        out.append({"id": d.name, "domain": "직접 추가", "problem": read(need[0]),
                    "base": read(need[1]), "skill": read(need[2])})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    pairs = default_pairs() + extra_pairs()
    rng.shuffle(pairs)  # 문제 순서도 섞어 앞부분 학습효과를 줄인다
    data, key = [], {}
    for p in pairs:
        order = ["base", "skill"]
        rng.shuffle(order)
        key[p["id"]] = {"A": order[0], "B": order[1]}
        data.append({"id": p["id"], "domain": p["domain"], "problem": p["problem"],
                     "A": p[order[0]], "B": p[order[1]]})

    def js(obj):  # <script type=application/json> 안전화
        return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

    key_b64 = base64.b64encode(json.dumps(key).encode("utf-8")).decode("ascii")
    html = (HERE / "template.html").read_text(encoding="utf-8")
    html = html.replace("__MARKED__", (HERE / "marked.min.js").read_text(encoding="utf-8").replace("</script", "<\\/script"))
    html = html.replace("__DATA__", js(data)).replace("__KEY__", js(key_b64))
    out = HERE / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"built {out}  ({len(data)} problems, {out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
