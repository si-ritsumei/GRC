import json

json_path = "/home/matsumoto/llm_search2/output/gpt/few_cot_infer/f1_instance_scores.json"

with open(json_path, "r") as f:
    data = json.load(f)



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
    if scores.get("category_f1") == 1.0
    and scores.get("api_final_f1") == 1.0
]
category_0 = [
    service_name
    for service_name, scores in data.items()
    if scores.get("category_f1") == 0
    and isinstance(scores.get("category_f1"), int)
]

api_enum_0_with_category_ok = [
    service_name
    for service_name, scores in data.items()
    if scores.get("api_final_f1") != 1.0
    and scores.get("category_f1") not in (0, 0.0)
    and scores.get("api_intermediate_f1") == 0.0
]

api_0_with_category_ok = [
    service_name
    for service_name, scores in data.items()
    # カテゴリは推薦できている（0, 0.0 以外）
    if scores.get("category_f1") not in (0, 0.0)
    # API列挙は推薦できなかった
    and scores.get("api_intermediate_f1") not in (0, 0.0)
    and scores.get("api_final_f1") == 0
    and isinstance(scores.get("api_final_f1"), int)
]

# 失敗事例のみを対象にする
failed_instances = {
    service_name: scores
    for service_name, scores in data.items()
    if scores.get("api_final_f1") != 1.0
}


print("正しいカテゴリを提示できた推論数:", len(success_only_category))
print("最終的に正しい API を提示できた推論数:", len(success_instances))
print("正しいカテゴリ and 正しいAPiを提示できた推論数:", len(success_category_and_api))

print(len(category_0))
# print("categoryが0", category_0)
print(len(api_enum_0_with_category_ok))
print(len(api_0_with_category_ok))

def is_zero(x):
    return x == 0.0  # JSON上は0も0.0もここに吸収される前提

# # 除外したい集合（成功 + 0系）
# exclude = {
#     service_name
#     for service_name, scores in data.items()
#     if scores.get("api_final_f1") == 1.0
#     or is_zero(scores.get("category_f1"))
#     or is_zero(scores.get("api_intermediate_f1"))
#     or is_zero(scores.get("api_final_f1"))
# }

# 除外したい集合（成功 + 0系）
exclude = {
    service_name
    for service_name, scores in data.items()
    if is_zero(scores.get("category_f1"))
    or is_zero(scores.get("api_intermediate_f1"))
    or is_zero(scores.get("api_final_f1"))
}

# “純粋にどこでミスったか”を見る対象
pure_targets = {
    service_name: scores
    for service_name, scores in data.items()
    if service_name not in exclude
}

print("除外（成功 + 0系）:", len(exclude))
# print("純粋失敗分析の対象:", pure_targets)


import json
import re
from collections import defaultdict

import json
import re

mashup_path = "data/filtered_mashup_data.json"
output_path = "/home/matsumoto/llm_search2/output/gpt/few_cot_infer/responses_formatted.json"

with open(mashup_path, "r") as f:
    mashup_data = json.load(f)

with open(output_path, "r") as f:
    output_data = json.load(f)

# -----------------------------
# responses_formatted のパース（Step2/3/4のリスト取り出し）
# -----------------------------
LIST_RE = re.compile(r"\[([^\]]*)\]")

def parse_list_after_label(text: str, label: str):
    idx = text.find(label)
    if idx == -1:
        return []
    m = LIST_RE.search(text, idx)
    if not m:
        return []
    inner = m.group(1).strip()
    if not inner:
        return []

    # 'a','b' or "a","b"
    items = re.findall(r"'([^']*)'|\"([^\"]*)\"", inner)
    if items:
        out = []
        for a, b in items:
            v = (a or b).strip()
            if v:
                out.append(v)
        return out

    # fallback: comma separated
    parts = [p.strip() for p in inner.split(",")]
    return [p for p in parts if p]

def strip_suffix(service_key: str) -> str:
    # "slidemypics-1" -> "slidemypics"
    return re.sub(r"-\d+$", "", service_key)

# output_data を service_name -> (step2, step3, step4) に整形
pred_steps = {}
for k, text in output_data.items():
    service = strip_suffix(k)

    step2 = parse_list_after_label(text, "Recommend categories from 2.:")
    step3 = parse_list_after_label(text, "Recommend All matched APIs in 3.:")
    step4 = parse_list_after_label(text, "Final recommended APIs:")

    pred_steps[service] = (step2, step3, step4)

# -----------------------------
# pure_targets を基準に統合
# 出力形式:
# { service: [[gt_categories],[gt_apis],[step2],[step3],[step4]], ... }
# -----------------------------
merged = {}
missing_in_mashup = []
missing_in_output = []

for service in pure_targets.keys():
    # 正解側
    if service not in mashup_data:
        missing_in_mashup.append(service)
        continue

    arr = mashup_data[service]
    # 念のため構造チェック
    if not isinstance(arr, list) or len(arr) < 4:
        missing_in_mashup.append(service)
        continue

    gt_categories = arr[2] if isinstance(arr[2], list) else []
    gt_apis = arr[3] if isinstance(arr[3], list) else []

    # 予測側（step2/3/4）
    if service not in pred_steps:
        missing_in_output.append(service)
        continue

    step2, step3, step4 = pred_steps[service]

    merged[service] = [gt_categories, gt_apis, step2, step3, step4]

# 保存
save_path = "/home/matsumoto/llm_search2/output/gpt/few_cot_infer/pure_targets_merged.json"
with open(save_path, "w") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print("保存しました:", save_path)
print("merged件数:", len(merged))
print("pure_targets件数:", len(pure_targets))
print("mashup_dataに無かった件数:", len(missing_in_mashup))
print("responses_formattedに無かった件数:", len(missing_in_output))

import json

merged_path = "/home/matsumoto/llm_search2/output/gpt/few_cot_infer/pure_targets_merged.json"
with open(merged_path, "r") as f:
    merged = json.load(f)

def norm_set(xs):
    return {str(x).strip().lower() for x in xs if str(x).strip()}

success = []
step4_miss = []
step3_miss = []
step2or1_miss = []
bad_format = []
empty_gt = []

for service, items in merged.items():
    if not isinstance(items, list) or len(items) != 5:
        bad_format.append(service)
        continue

    gt_cats, gt_apis, s2_cats, s3_apis, s4_apis = items

    GT_C = norm_set(gt_cats)
    GT_A = norm_set(gt_apis)
    S2_C = norm_set(s2_cats)
    S3_A = norm_set(s3_apis)
    S4_A = norm_set(s4_apis)

    if not GT_C or not GT_A:
        empty_gt.append(service)
        continue

    # あなたの定義（厳密）
    cat_ok = GT_C.issubset(S2_C)
    enum_ok = GT_A.issubset(S3_A)     # 正解APIがすべて列挙に存在（余計はOK）
    final_ok = (S4_A == GT_A)         # 最終提示は完全一致のみ成功（余計も不足も失敗）

    if final_ok:
        success.append(service)
        continue

    # ここからは「最終提示が間違っていた」ケースのみ
    if enum_ok:
        step4_miss.append(service)          # 最終が間違い & 列挙には全部ある
    elif cat_ok:
        step3_miss.append(service)          # 列挙に全部ない & カテゴリは正しい
    else:
        step2or1_miss.append(service)       # カテゴリがズレ（=Step2/1）

print("成功（最終完全一致）:", len(success))
print("Step4ミス（最終提示APIのミス）:", len(step4_miss))
print("Step3ミス（API列挙のミス）:", len(step3_miss))
print("Step2/1ミス（カテゴリ or コア機能）:", len(step2or1_miss))

# print("bad_format:", len(bad_format))
# print("empty_gt:", len(empty_gt))

# print("チェック 合計:",
#       len(success)+len(step4_miss)+len(step3_miss)+len(step2or1_miss)+len(bad_format)+len(empty_gt),
#       "/ merged:", len(merged))

print("########################################################")
####################################################################
import json

merged_path = "/home/matsumoto/llm_search2/output/gpt/few_cot_infer/pure_targets_merged.json"
with open(merged_path, "r") as f:
    merged = json.load(f)

def norm_set(xs):
    return {str(x).strip().lower() for x in xs if str(x).strip()}

success = []
step4_miss = []
step3_miss = []
step2or1_miss = []
bad_format = []
empty_gt = []

for service, items in merged.items():
    if not isinstance(items, list) or len(items) != 5:
        bad_format.append(service)
        continue

    gt_cats, gt_apis, s2_cats, s3_apis, s4_apis = items

    GT_C = norm_set(gt_cats)
    GT_A = norm_set(gt_apis)
    S2_C = norm_set(s2_cats)
    S3_A = norm_set(s3_apis)
    S4_A = norm_set(s4_apis)

    if not GT_C or not GT_A:
        empty_gt.append(service)
        continue

    # Step2: 余計なカテゴリもNGにする（完全一致）
    cat_ok = (S2_C == GT_C)

    # Step3: 正解APIがすべて列挙に存在（余計はOK）
    enum_ok = GT_A.issubset(S3_A)

    # Step4: 最終提示は完全一致のみ成功（余計も不足も失敗）
    final_ok = (S4_A == GT_A)

    if final_ok:
        success.append(service)
        continue

    # ここからは「最終提示が間違っていた」ケースのみ
    if enum_ok:
        step4_miss.append(service)          # 最終が間違い & 列挙には全部ある
    elif cat_ok:
        step3_miss.append(service)          # 列挙に全部ない & カテゴリは正しい（完全一致）
    else:
        step2or1_miss.append(service)       # カテゴリがズレ（=Step2/1）

print("成功（最終完全一致）:", len(success))
print("Step4ミス（最終提示APIのミス）:", len(step4_miss))
print("Step3ミス（API列挙のミス）:", len(step3_miss))
print("Step2/1ミス（カテゴリ or コア機能）:", len(step2or1_miss))
print("bad_format:", len(bad_format))
print("empty_gt:", len(empty_gt))

