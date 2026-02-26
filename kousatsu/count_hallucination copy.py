#これはファイルからスコアを計算する

import json
from ollama import Client
import os
import re
import ast
from ollama import Client
from collections import Counter
"""""""①評価したいllmモデル選択"""""""""
# input_model = "deepseek"
# input_model = "llama"
input_model = "gpt"
"""""""②整形したいプロンプト選択"""""""""
# prompt_method_name = "few_shot_cot"
prompt_method_name = "few_shot_cot_with_inference_process"
# prompt_method_name = "few_shot"
# prompt_method_name = "few_shot_ablation"
#prompt_method_name ="plan_and_solve"
# prompt_method_name = "zero_shot_cot"
# prompt_method_name = "zero_shot_cot_with_inference_process"
# prompt_method_name ="zero_shot"
########################################################################

import pprint
from log.get_information import GetAvailableAPIData
api_data = './data/filtered_api_data.json'
api_data_getter = GetAvailableAPIData(api_data)
# API情報を取得
available_apis, available_apis_name = api_data_getter.get_available_apis()
# カテゴリ一覧取得
available_categories = api_data_getter.get_available_categories()

# メソッド名 → ファイル名のマッピング
filename_map = {
    "zero_shot":"zero_shot",
    "zero_shot_cot": "zero_cot",
    "zero_shot_cot_with_inference_process": "zero_cot_infer",
    "few_shot":"few_shot",
    "few_shot_ablation":"few_shot_ablation",
    "few_shot_cot": "few_cot",
    "few_shot_cot_with_inference_process": "few_cot_infer",
    "plan_and_solve":"plan_and_solve"
    # 必要に応じて他も追加可能
}

# 各プロンプト手法に対して期待される [] の数を指定
expected_bracket_counts = {
    "few_shot_cot": 3,
    "few_shot_cot_with_inference_process": 3,
    "few_shot": 2,
    "few_shot_ablation": 3,
    "plan_and_solve": 3,
    "zero_shot_cot_with_inference_process": 3,
    "zero_shot_cot": 2,
    "zero_shot": 2
}

def extract_model_name(model_str):
    if "deepseek" in model_str.lower():
        return "deepseek"
    elif "llama" in model_str.lower():
        return "llama"
    elif "gemma" in model_str.lower():
        return "gemma"
    elif "gpt" in model_str.lower():
        return "gpt"
    else:
        return "other"

input_model_name = extract_model_name(input_model)
short_name = filename_map.get(prompt_method_name, prompt_method_name)
input_path = f"./output/{input_model_name}/{short_name}/responses.json"
output_path = f"./output/{input_model_name}/{short_name}/responses_formatted.json"


# ========== 整形チェック ==========
def is_properly_formatted(response_text: str, prompt_method_name: str) -> bool:
    expected_count = expected_bracket_counts.get(prompt_method_name, 0)
    lists_in_brackets = re.findall(r"\[.*?\]", response_text)

    if len(lists_in_brackets) < expected_count:
        return False
    if any(item.strip() == "[]" for item in lists_in_brackets):
        return False
    return True

import pandas as pd

# ===== 評価実行関数 =====
def evaluate_responses_with_hallucination_analysis(
    formatted_path,
    mashup_csv_path,
    prompt_method_name,
    expected_bracket_counts,
    available_categories,
    available_apis_name,
):
    with open(formatted_path, 'r', encoding='utf-8') as f:
        formatted_data = json.load(f)

    mashup_df = pd.read_csv(mashup_csv_path)
    mashup_data = {}
    for _, row in mashup_df.iterrows():
        mashup_data[row['mashup_name']] = {
            'apis': set(row['api_name'].strip("[]").replace("'", "").split(", ")),
            'api_categories': set(row['api_category'].strip("[]").replace("'", "").split(", "))
        }

    # === 利用可能カテゴリ一覧（データセット由来）===
    # ここは「mashup_dfに登場するカテゴリの集合」として扱う（既存コードと同じ意図）
    dataset_categories = set()
    for cats in mashup_df['api_category']:
        cleaned = cats.strip("[]").replace("'", "").split(", ")
        dataset_categories.update(x.lower().replace(" ", "-") for x in cleaned if x)

    expected_count = expected_bracket_counts.get(prompt_method_name, 0)

    # ====== 従来の「要件文単位で1件」カウント ======
    hallucinated_categories_all = []
    hallucinated_mashup_count = 0
    hallucinated_apis_all = []
    hallucinated_api_mashup_count = 0

    # ====== 追加：要件文ごとの詳細ログ ======
    # ここで「総崩れか／局所か」を分析する
    per_item = []  # 各要件文(=mashup)の分析結果を格納

    counted_mashups = 0
    total_pred_categories = 0
    total_pred_apis = 0

    for mashup_name, response_text in formatted_data.items():
        normalized_name = mashup_name.rsplit("-", 1)[0]
        if normalized_name not in mashup_data:
            continue

        lists = re.findall(r"\[.*?\]", response_text)
        parsed_lists = []
        valid = True
        for lst in lists:
            if "..." in lst:
                valid = False
                break
            try:
                parsed = ast.literal_eval(lst)
                if not isinstance(parsed, list):
                    raise ValueError("Not a list")
                parsed_lists.append(parsed)
            except Exception:
                valid = False
                break

        if not valid or len(parsed_lists) < expected_count:
            continue

        # goldは必要なら使えるが、今回の追加分析では必須ではない
        # gold = mashup_data[normalized_name]

        if expected_count == 3:
            pred_categories = set(parsed_lists[0])
            pred_apis_final = set(parsed_lists[2])
        else:
            pred_categories = set(parsed_lists[0])
            pred_apis_final = set(parsed_lists[1])

        # 正規化
        pred_categories = {x.lower().replace(" ", "-") for x in pred_categories if isinstance(x, str)}
        pred_apis_final = {x.lower().replace(" ", "-") for x in pred_apis_final if isinstance(x, str)}

        # ====== ハルシネーション検出 ======
        # カテゴリ：データセットに存在しないカテゴリ（現行コードと同じ思想）
        hallucinated_cats = pred_categories - dataset_categories

        # API：利用可能API一覧に存在しないAPI
        hallucinated_apis = pred_apis_final - available_apis_name

        # ====== 従来カウント（要件文ごとに1件） ======
        if hallucinated_cats:
            hallucinated_mashup_count += 1
            hallucinated_categories_all.extend(hallucinated_cats)

        if hallucinated_apis:
            hallucinated_api_mashup_count += 1
            hallucinated_apis_all.extend(hallucinated_apis)

        # ====== 追加ログ ======
        per_item.append({
            "mashup_name": mashup_name,
            "normalized_name": normalized_name,
            "pred_category_count": len(pred_categories),
            "pred_api_count": len(pred_apis_final),
            "cat_hallu_flag": 1 if len(hallucinated_cats) > 0 else 0,
            "api_hallu_flag": 1 if len(hallucinated_apis) > 0 else 0,
            "cat_hallu_count": len(hallucinated_cats),
            "api_hallu_count": len(hallucinated_apis),
            "cat_hallu_list": sorted(list(hallucinated_cats)),
            "api_hallu_list": sorted(list(hallucinated_apis)),
        })

        counted_mashups += 1
        total_pred_categories += len(pred_categories)
        total_pred_apis += len(pred_apis_final)

    # =============================
    # 1) 従来の結果（あなたの表5用）
    # =============================
    print("\n=== ハルシネーションカテゴリ検出結果 ===")
    print(f"不正カテゴリを含んだ mashup 数: {hallucinated_mashup_count} 件")
    print(f"ハルシネーションカテゴリの総数（重複込み）: {len(hallucinated_categories_all)} 件")

    print("\n=== ハルシネーションAPI検出結果 ===")
    print(f"不正APIを含んだ mashup 数: {hallucinated_api_mashup_count} 件")
    print(f"ハルシネーションAPIの総数（重複込み）: {len(hallucinated_apis_all)} 件")

    print("\n=== 合計出力数と平均 ===")
    print(f"対象 mashup 数: {counted_mashups}")
    if counted_mashups > 0:
        print(f"pred_categories の平均数: {total_pred_categories / counted_mashups:.2f}")
        print(f"pred_apis の平均数: {total_pred_apis / counted_mashups:.2f}")

    # =============================
    # 2) 追加分析A：カテゴリとAPIの同時発生（総崩れ？）
    # =============================
    df = pd.DataFrame(per_item)
    if len(df) == 0:
        print("\n[WARN] 有効な出力が0件です（整形やパースに失敗している可能性）")
        return

    both = int(((df["cat_hallu_flag"] == 1) & (df["api_hallu_flag"] == 1)).sum())
    cat_only = int(((df["cat_hallu_flag"] == 1) & (df["api_hallu_flag"] == 0)).sum())
    api_only = int(((df["cat_hallu_flag"] == 0) & (df["api_hallu_flag"] == 1)).sum())
    none = int(((df["cat_hallu_flag"] == 0) & (df["api_hallu_flag"] == 0)).sum())

    print("\n=== 追加分析A：カテゴリ×API 同時発生（要件文単位） ===")
    print(f"カテゴリのみ: {cat_only}")
    print(f"APIのみ     : {api_only}")
    print(f"両方        : {both}")
    print(f"なし        : {none}")

    # 条件付き確率（「カテゴリが起きたらAPIも？」など）
    cat_hallu_total = int((df["cat_hallu_flag"] == 1).sum())
    api_hallu_total = int((df["api_hallu_flag"] == 1).sum())
    print("\n=== ハルシネーションAPI（中身のみ） ===")

    for _, row in df.iterrows():
        if row["api_hallu_flag"] == 1:
            for api in row["api_hallu_list"]:
                print(api)
    exit()
    print("\n--- 条件付き割合 ---")
    if cat_hallu_total > 0:
        print(f"P(APIハルシネーション | カテゴリハルシネーション) = {both / cat_hallu_total:.3f} ({both}/{cat_hallu_total})")
    else:
        print("カテゴリハルシネーションが0件のため条件付き確率は計算できません。")

    if api_hallu_total > 0:
        print(f"P(カテゴリハルシネーション | APIハルシネーション) = {both / api_hallu_total:.3f} ({both}/{api_hallu_total})")
    else:
        print("APIハルシネーションが0件のため条件付き確率は計算できません。")

    # =============================
    # 3) 追加分析B：1要件文あたりの“個数”分布（多数起きる？）
    # =============================
    print("\n=== 追加分析B：1要件文あたりのハルシネーション個数 ===")

    # カテゴリの個数分布
    cat_count_dist = Counter(df["cat_hallu_count"].tolist())
    api_count_dist = Counter(df["api_hallu_count"].tolist())

    def print_dist(title, dist: Counter, max_k=10):
        print(f"\n[{title}]")
        # 0,1,2,...の順に表示（ただし上限max_k、残りはまとめる）
        keys = sorted(dist.keys())
        shown = [k for k in keys if k <= max_k]
        for k in shown:
            print(f"  {k}個: {dist[k]}")
        # max_kより大きいものはまとめ
        tail = sum(v for k, v in dist.items() if k > max_k)
        if tail > 0:
            print(f"  >{max_k}個: {tail}")

    print_dist("カテゴリハルシネーション個数分布", cat_count_dist, max_k=10)
    print_dist("APIハルシネーション個数分布", api_count_dist, max_k=10)

    # 「ハルシネーションが起きた要件文」に限定した平均個数
    cat_positive = df[df["cat_hallu_count"] > 0]
    api_positive = df[df["api_hallu_count"] > 0]

    print("\n--- ハルシネーション発生要件文に限定した平均個数 ---")
    if len(cat_positive) > 0:
        print(f"カテゴリ: 平均 {cat_positive['cat_hallu_count'].mean():.2f} 個/要件文 (発生要件文数={len(cat_positive)})")
    else:
        print("カテゴリ: 発生要件文が0件")

    if len(api_positive) > 0:
        print(f"API     : 平均 {api_positive['api_hallu_count'].mean():.2f} 個/要件文 (発生要件文数={len(api_positive)})")
    else:
        print("API     : 発生要件文が0件")

    # =============================
    # 4) 任意：詳細ログをCSV出力（後で論文用に確認しやすい）
    # =============================
    out_csv = formatted_path.replace(".json", "_hallucination_detail.csv")
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print(f"\n[Saved] 要件文ごとの詳細ログCSV: {out_csv}")


if __name__ == "__main__":
    # ここはあなたの既存コードの変数を流用してOK
    # output_path / prompt_method_name / expected_bracket_counts / available_categories / available_apis_name など
    evaluate_responses_with_hallucination_analysis(
        formatted_path=output_path,
        mashup_csv_path="./data/filterd_mashup_data.csv",
        prompt_method_name=prompt_method_name,
        expected_bracket_counts=expected_bracket_counts,
        available_categories={x.lower().replace(" ", "-") for x in available_categories},
        available_apis_name={x.lower().replace(" ", "-") for x in available_apis_name},
    )