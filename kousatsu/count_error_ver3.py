import json
import re

# =========
# Paths
# =========
json_path = "/home/matsumoto/llm_search2/output/gpt/few_cot_infer/f1_instance_scores.json"
mashup_path = "data/filtered_mashup_data.json"
output_path = "/home/matsumoto/llm_search2/output/gpt/few_cot_infer/responses_formatted.json"

# =========
# Load
# =========
with open(json_path, "r") as f:
    data = json.load(f)

with open(mashup_path, "r") as f:
    mashup_data = json.load(f)

with open(output_path, "r") as f:
    output_data = json.load(f)

# =========
# Utilities
# =========
def is_zero(x):
    # JSON上は 0 と 0.0 の区別ができない前提で 0.0 として扱う
    return x == 0.0

def normalize_token(x: str) -> str:
    return (x or "").strip().lower()

def to_set(xs):
    return {normalize_token(x) for x in (xs or []) if normalize_token(x)}

def strip_suffix(service_key: str) -> str:
    # "slidemypics-1" -> "slidemypics"
    return re.sub(r"-\d+$", "", service_key)

LIST_RE = re.compile(r"\[([^\]]*)\]")

def parse_list_after_label(text: str, label: str):
    """
    label の後に出てくる最初の [ ... ] を取り出して list[str] にする。
    例: "Recommend categories from 2.: ['photos', 'social']" などに対応
    """
    idx = text.find(label)
    if idx == -1:
        return []
    m = LIST_RE.search(text, idx)
    if not m:
        return []
    inner = m.group(1).strip()
    if not inner:
        return []

    # クォート付き要素（'a' や "a"）を優先で抽出
    items = re.findall(r"'([^']*)'|\"([^\"]*)\"", inner)
    if items:
        out = []
        for a, b in items:
            v = (a or b).strip()
            if v:
                out.append(v)
        return out

    # クォートがない場合はカンマ区切りで分解
    parts = [p.strip() for p in inner.split(",")]
    return [p for p in parts if p]

def categories_correct(gt_cats, pred_cats) -> bool:
    """
    カテゴリ正解の定義：
      gtカテゴリが predカテゴリに全て含まれていればOK（subset）
    ※ 完全一致にしたいなら `return g == p` に変更
    """
    g = to_set(gt_cats)
    p = to_set(pred_cats)
    if not g:
        return False
    return g.issubset(p)

def final_correct(gt_apis, pred_final) -> bool:
    """
    最終API正解の定義：
      gt API が pred final に全て含まれていればOK（subset）
    ※ 完全一致にしたいなら `return g == p` に変更
    """
    g = to_set(gt_apis)
    p = to_set(pred_final)
    if not g:
        return False
    return g.issubset(p)

def enum_contains_any_gt(gt_apis, pred_enum) -> bool:
    """
    「含まれていればOK」の判定（Step4ミス用）
      列挙APIに gt API が 1つでも含まれていれば True
    """
    g = to_set(gt_apis)
    e = to_set(pred_enum)
    return len(g & e) > 0

# =========
# 1) Quick counts from F1-only json (optional / for context)
# =========
success_instances = [
    service_name
    for service_name, scores in data.items()
    if scores.get("api_final_f1") == 1.0
]
success_only_category = [
    service_name
    for service_name, scores in data.items()
    if scores.get("category_f1") == 1.0
]
success_category_and_api = [
    service_name
    for service_name, scores in data.items()
    if scores.get("category_f1") == 1.0 and scores.get("api_final_f1") == 1.0
]

print("正しいカテゴリを提示できた推論数:", len(success_only_category))
print("最終的に正しい API を提示できた推論数:", len(success_instances))
print("正しいカテゴリ and 正しいAPiを提示できた推論数:", len(success_category_and_api))

# =========
# 2) Build exclude set (成功 + 0系) and pure_targets from f1 json
# =========
exclude = {
    service_name
    for service_name, scores in data.items()
    if scores.get("api_final_f1") == 1.0
    or is_zero(scores.get("category_f1"))
    or is_zero(scores.get("api_intermediate_f1"))
    or is_zero(scores.get("api_final_f1"))
}

pure_targets = {
    service_name: scores
    for service_name, scores in data.items()
    if service_name not in exclude
}

print("除外（成功 + 0系）:", len(exclude))
print("純粋失敗分析の対象:", len(pure_targets))

# =========
# 3) Parse ground-truth (mashup_data)
#    mashup_data[service] = [
#        [tags?], desc, [gt_categories], [gt_apis], id
#    ]
# =========
gt_data = {}
for service, arr in mashup_data.items():
    if not isinstance(arr, list) or len(arr) < 4:
        continue
    gt_categories = arr[2] if isinstance(arr[2], list) else []
    gt_apis = arr[3] if isinstance(arr[3], list) else []
    gt_data[service] = {
        "gt_categories": gt_categories,
        "gt_apis": gt_apis,
    }

# =========
# 4) Parse predictions (responses_formatted)
#    output_data key is like "service-1" so we strip "-1"
# =========
pred_data = {}
for k, text in output_data.items():
    service = strip_suffix(k)

    cats = parse_list_after_label(text, "Recommend categories from 2.:")
    enum_apis = parse_list_after_label(text, "Recommend All matched APIs in 3.:")
    final_apis = parse_list_after_label(text, "Final recommended APIs:")

    pred_data[service] = {
        "pred_categories": cats,
        "pred_enum_apis": enum_apis,
        "pred_final_apis": final_apis,
        "raw": text,
    }

# =========
# 5) Pure failure stage classification using *contents*
#    (use pure_targets keys as the analysis population)
#
#    - Step4ミス: 最終が誤り AND 列挙に正解APIが含まれている
#    - Step3ミス: 列挙に正解が含まれない AND カテゴリが正しい
#    - Step2/1  : それ以外（カテゴリ誤り含む。コア機能と分離不能なのでまとめ）
# =========
final_miss = []               # Step4
enum_miss = []                # Step3
category_or_core_miss = []    # Step2/1
missing_or_unmatched = []     # gt/pred が揃わない・パース不足など

for service_name in pure_targets.keys():
    if service_name not in gt_data or service_name not in pred_data:
        missing_or_unmatched.append(service_name)
        continue

    gt_cats = gt_data[service_name]["gt_categories"]
    gt_apis = gt_data[service_name]["gt_apis"]

    p_cats = pred_data[service_name]["pred_categories"]
    p_enum = pred_data[service_name]["pred_enum_apis"]
    p_final = pred_data[service_name]["pred_final_apis"]

    cat_ok = categories_correct(gt_cats, p_cats)
    final_ok = final_correct(gt_apis, p_final)
    enum_has_gt = enum_contains_any_gt(gt_apis, p_enum)

    # pure_targets は最終成功を除外済みだが、念のため final_ok はチェックしておく
    if final_ok:
        # ここに入るなら pure_targets 条件と矛盾しているので確認用
        continue

    if enum_has_gt:
        final_miss.append(service_name)  # Step4ミス（含まれているのに選ばない/落とす）
    elif cat_ok:
        enum_miss.append(service_name)   # Step3ミス（カテゴリはOKだが列挙に正解がない）
    else:
        category_or_core_miss.append(service_name)  # Step2/1（カテゴリ or コア機能）

print("\n=== 純粋失敗（pure_targets）段階別分類 ===")
print("Step4ミス（最終提示APIのミス）:", len(final_miss))
print("Step3ミス（API列挙のミス）:", len(enum_miss))
print("Step2/1（カテゴリのミス and コア機能のミス）:", len(category_or_core_miss))
print("（参考）gt/pred不足など:", len(missing_or_unmatched))

print("\n--- Step2/1（カテゴリのミス and コア機能のミス）サービス名一覧 ---")
for name in sorted(category_or_core_miss):
    print("-", name)

print("\nチェック: 分類合計 =",
      len(final_miss) + len(enum_miss) + len(category_or_core_miss) + len(missing_or_unmatched),
      "/ pure_targets =", len(pure_targets))
