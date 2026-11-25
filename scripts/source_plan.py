"""Offline V6 knowledge routing; never treats a source plan as evidence."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "references/knowledge/source_registry.json"
DOMAINS = {
    "industry": "交易结构、供需瓶颈、竞争与利润迁移",
    "company": "财务质量、合同、资本配置、估值及治理",
    "product": "用户任务、支付、替代、单位经济与留存",
    "policy": "原文、生效、适用对象、执行与成本承担",
    "market": "定价机制、流动性、成本、风险及历史基准",
    "expectation": "事前共识、价格隐含条件、兑现与失效",
}
DEFAULT_TAGS = {
    "industry": {"industry", "technology", "business"},
    "company": {"valuation", "accounting", "management", "business"},
    "product": {"product", "business", "industry"},
    "policy": {"policy", "macro"},
    "market": {"market", "risk", "quant"},
    "expectation": {"expectation", "valuation", "event"},
}
MODULES = {
    "expectations-moat": {"valuation", "expectation"},
    "management-capital-quality": {"management", "accounting"},
    "global-money-credit": {"macro", "bank"},
    "risk-market-microstructure": {"market", "risk"},
    "industry-constraints": {"industry", "technology", "energy"},
    "empirical-research": {"quant", "event"},
    "business-model-platforms": {"product", "business"},
    "country-policy-legal": {"policy"},
    "crypto-onchain-deep": {"crypto"},
}
COMPANION_TAGS = {
    "crypto": {"market", "risk", "quant", "macro", "policy"},
    "bank": {"macro", "accounting", "risk"},
    "energy": {"industry", "market", "policy"},
    "technology": {"industry", "product", "business"},
    "event": {"market", "expectation", "quant"},
}
ROLES = {"primary", "method", "lead", "tool"}
STATUSES = {"excerpt", "caption_excerpt", "index", "unavailable"}

def load_registry(path=REGISTRY):
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if data.get("schema") != 1:
        raise ValueError("Unsupported source registry schema")
    seen = set()
    entries = data["entries"]
    for e in entries:
        key = e["id"]
        if key in seen:
            raise ValueError(f"duplicate source ID: {key}")
        seen.add(key)
        if e["role"] not in ROLES or e["review_status"] not in STATUSES:
            raise ValueError(f"invalid role/status: {key}")
        u = urlsplit(e["url"])
        if u.scheme != "https" or not u.netloc:
            raise ValueError(f"invalid source URL: {key}")
        if not e["tags"] or not e["lesson"] or not e["limits"]:
            raise ValueError(f"incomplete source card: {key}")
    return entries

def build_plan(routes, focus=(), entries=None):
    routes = list(dict.fromkeys(routes))
    if not routes or any(r not in DOMAINS for r in routes):
        raise ValueError("routes must be one or more of: " + ", ".join(DOMAINS))
    valid_tags = set().union(*MODULES.values())
    focus = set(focus)
    if focus - valid_tags:
        raise ValueError("unknown focus: " + ", ".join(sorted(focus - valid_tags)))
    tags = set().union(*(DEFAULT_TAGS[r] for r in routes), focus)
    for t in list(tags):
        tags |= COMPANION_TAGS.get(t, set())
    if entries is None:
        entries = load_registry()
    relevant = [e for e in entries if set(e["tags"]) & tags]
    buckets = {}
    for role in sorted(ROLES):
        candidates = [e for e in relevant if e["role"] == role and e["review_status"] != "unavailable"]
        candidates.sort(key=lambda e: (-len(set(e["tags"]) & tags), e["review_status"] == "index", e["id"]))
        buckets[role] = candidates
    manuals = [f"references/playbooks/{r}.md" for r in routes]
    manuals += ["references/cross-domain.md", "references/metric-intelligence.md",
                "references/knowledge/field-intelligence.md", "references/knowledge/advanced-index.md"]
    manuals += [f"references/specialists/advanced/{name}.md" for name, keys in MODULES.items() if keys & tags]
    for m in manuals:
        if not (ROOT / m).is_file():
            raise FileNotFoundError(m)
    return {
        "release": "V6", "gate_schema": 5, "kind": "research_plan_not_evidence",
        "routes": routes, "focus": sorted(tags), "manuals": manuals,
        "six_domain_questions": DOMAINS,
        "source_candidates": buckets,
        "unavailable_sources": [e for e in relevant if e["review_status"] == "unavailable"],
        "instructions": [
            "按任务查当期公司/监管/交易所等原件；本表非实时数据、不能替代G1证据。",
            "X、视频、博客和信件按具体主张回溯原始数据；未读内容不冒充已读。",
            "工具先查许可证、版本与测试，不自动下载或执行。",
            "六域均要评估，主入口不等于排除其他域；八关验收仍必须使用 research_gate.py。",
        ],
    }

def split(value):
    return [x.strip().lower() for x in value.split(",") if x.strip()]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--routes", required=True, help="comma-separated primary research routes")
    p.add_argument("--focus", default="", help="comma-separated specialist topic tags")
    p.add_argument("--output", help="optional NEW plan file under research/")
    args = p.parse_args()
    plan = build_plan(split(args.routes), split(args.focus))
    out = json.dumps(plan, ensure_ascii=False, indent=2)
    if args.output:
        target = (ROOT / args.output).resolve()
        research = (ROOT / "research").resolve()
        if not target.is_relative_to(research) or target.suffix != ".json":
            p.error("--output must be a new JSON file under research/")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as f:
            f.write(out + "\n")
    else:
        print(out)

if __name__ == "__main__":
    main()
