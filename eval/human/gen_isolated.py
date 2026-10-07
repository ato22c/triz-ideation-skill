#!/usr/bin/env python3
"""사람 평가용 A/B 답안을 '격리 실행'으로 만든다 (세션 지침·CLAUDE.md·메모리가 섞이지 않게).

  python eval/human/gen_isolated.py H1 H2 D2 [--model claude-fable-5-1]

각 문제(eval/problems.json의 id)마다 같은 모델·같은 최소 지시로 두 번 실행한다.
  baseline: 최소 지시만
  skill   : 최소 지시 + skills/triz-ideation/SKILL.md + reference/*.md 전문(도구를 못 쓰므로 본문에 붙인다)
결과는 eval/human/pairs/<id>/{problem.txt, baseline.md, skill.md}에 저장된다.
저장소 밖의 빈 임시 폴더에서 실행한다.
"""
import argparse, json, subprocess, sys, tempfile, concurrent.futures as cf
from pathlib import Path

HERE = Path(__file__).parent
EVAL = HERE.parent
SKILL = EVAL.parent / "skills" / "triz-ideation"
BASE_SYS = "너는 사용자의 질문에 한국어로 답하는 도우미야. 사용자에게 되물을 수 없으니 필요한 가정은 답변에 적고 바로 답해줘."


def skill_system(skill_dir: Path = SKILL) -> str:
    parts = [BASE_SYS, "\n\n아래 '스킬 문서'의 절차를 빠짐없이 따라 답해줘. 도구를 쓸 수 없으므로 문서가 링크한 참고 파일은 모두 아래에 붙어 있다.\n"]
    for rel in ["SKILL.md", "reference/principles.md", "reference/tools.md"]:
        txt = (skill_dir / rel).read_text(encoding="utf-8").replace("\r\n", "\n")
        parts.append(f"\n\n===== 스킬 문서: {rel} =====\n{txt}")
    return "".join(parts)


def run(sysprompt: str, problem: str, model: str, tmp: Path, tag: str) -> str:
    sp = tmp / f"sys_{tag}.txt"
    sp.write_text(sysprompt, encoding="utf-8")
    cmd = ["claude", "-p", problem, "--model", model, "--output-format", "json",
           "--setting-sources", "", "--system-prompt-file", str(sp),
           "--disable-slash-commands", "--tools", "", "--no-session-persistence"]
    r = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, encoding="utf-8", timeout=900, stdin=subprocess.DEVNULL)
    if r.returncode != 0:
        raise RuntimeError(f"{tag} failed (code {r.returncode}): stderr={r.stderr[:300]!r} stdout={r.stdout[:300]!r}")
    out = json.loads(r.stdout)
    if out.get("is_error"):
        raise RuntimeError(f"{tag} error: {out.get('result')}")
    return out["result"].strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--model", default="claude-fable-5-1")
    ap.add_argument("--out-dir", default=None, help="지정하면 pairs/ 대신 <out-dir>/<id>_<arm>.md 로 저장(기존 결과를 덮어쓰지 않음)")
    ap.add_argument("--skill-dir", default=None, help="스킬 폴더(기본: skills/triz-ideation). 옛 버전과 비교할 때 지정")
    ap.add_argument("--arms", nargs="+", default=["baseline", "skill"], choices=["baseline", "skill"], help="다시 만들 쪽만 고를 수 있다")
    a = ap.parse_args()
    problems = {p["id"]: p for p in json.loads((EVAL / "problems.json").read_text(encoding="utf-8"))}
    tmp = Path(tempfile.mkdtemp(prefix="triz_iso_"))
    jobs = []
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for pid in a.ids:
            text = problems[pid]["text"]
            for arm, sysp in (("baseline", BASE_SYS), ("skill", skill_system(Path(a.skill_dir) if a.skill_dir else SKILL))):
                if arm not in a.arms:
                    continue
                jobs.append((pid, arm, ex.submit(run, sysp, text, a.model, tmp, f"{pid}_{arm}")))
        for pid, arm, fut in jobs:
            res = fut.result()
            if a.out_dir:
                od = Path(a.out_dir)
                od.mkdir(parents=True, exist_ok=True)
                (od / f"{pid}_{arm}.md").write_text(res, encoding="utf-8")
            else:
                d = HERE / "pairs" / pid
                d.mkdir(parents=True, exist_ok=True)
                (d / "problem.txt").write_text(problems[pid]["text"], encoding="utf-8")
                (d / f"{arm}.md").write_text(res, encoding="utf-8")
            print(f"{pid} {arm}: {len(res)}자", flush=True)


if __name__ == "__main__":
    sys.exit(main())
