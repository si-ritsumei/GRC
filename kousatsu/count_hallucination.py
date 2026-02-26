#これはファイルからスコアを計算する

import json
from ollama import Client
import os
import re
import ast
from ollama import Client
"""""""①評価したいllmモデル選択"""""""""
# input_model = "deepseek"
# input_model = "llama"
input_model = "gpt"
"""""""②整形したいプロンプト選択"""""""""
# prompt_method_name = "few_shot_cot"
# prompt_method_name = "few_shot_cot_with_inference_process"
prompt_method_name = "few_shot"
# prompt_method_name = "few_shot_ablation"
# prompt_method_name ="plan_and_solve"
# prompt_method_name = "zero_shot_cot"
# prompt_method_name = "zero_shot_cot_with_inference_process"
# prompt_method_name ="zero_shot"
########################################################################

import pprint
from get_information import GetAvailableAPIData
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
def evaluate_responses(formatted_path, mashup_csv_path, prompt_method_name, expected_bracket_counts, available_categories, available_apis_name):
    with open(formatted_path, 'r', encoding='utf-8') as f:
        formatted_data = json.load(f)


    mashup_df = pd.read_csv(mashup_csv_path)
    mashup_data = {}
    for _, row in mashup_df.iterrows():
        mashup_data[row['mashup_name']] = {
            'apis': set(row['api_name'].strip("[]").replace("'", "").split(", ")),
            'api_categories': set(row['api_category'].strip("[]").replace("'", "").split(", "))
        }

    # === 利用可能カテゴリ一覧の構築（正規化済み） ===
    available_categories = set()
    for cats in mashup_df['api_category']:
        cleaned = cats.strip("[]").replace("'", "").split(", ")
        available_categories.update(x.lower().replace(" ", "-") for x in cleaned if x)

    expected_count = expected_bracket_counts.get(prompt_method_name, 0)

    # ハルシネーションカウント用
    hallucinated_categories = []
    hallucinated_mashup_count = 0
    hallucinated_apis = []
    hallucinated_api_mashup_count = 0
    # 🔢 合計数のカウント
    total_pred_categories = 0
    total_pred_apis = 0
    counted_mashups = 0
    total_gold_categories = 0
    total_gold_apis = 0

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

        gold = mashup_data[normalized_name]
        true_categories = {x.lower().replace(" ", "-") for x in gold['api_categories']}
        true_apis = {x.lower().replace(" ", "-") for x in gold['apis']}
        total_gold_categories += len(true_categories)
        total_gold_apis += len(true_apis)

        if expected_count == 3:
            pred_categories = set(parsed_lists[0])
            pred_apis_intermediate = set(parsed_lists[1])
            pred_apis_final = set(parsed_lists[2])
        else:
            pred_categories = set(parsed_lists[0])
            pred_apis_intermediate = set(parsed_lists[1])
            pred_apis_final = set(parsed_lists[1])

        pred_categories = {x.lower().replace(" ", "-") for x in pred_categories if isinstance(x, str)}
        pred_apis_intermediate = {x.lower().replace(" ", "-") for x in pred_apis_intermediate if isinstance(x, str)}
        pred_apis_final = {x.lower().replace(" ", "-") for x in pred_apis_final if isinstance(x, str)}

        # 🔍 ハルシネーションカテゴリ検出
        hallucinated = pred_categories - available_categories
        if hallucinated:
            hallucinated_mashup_count += 1
            hallucinated_categories.extend(hallucinated)
            # print(f"\n⚠️ ハルシネーションカテゴリ検出: {mashup_name}")
            # print(f"  予測カテゴリ: {pred_categories}")
            # print(f"  存在しないカテゴリ: {hallucinated}")

        # ✳️ 出力確認
        # print("\n🔹 pred_categories:", pred_categories)
        # print("🔹 pred_apis_intermediate:", pred_apis_intermediate)
        # print("🔹 pred_apis_final:", pred_apis_final)
        

        api_hallucinated = pred_apis_final - available_apis_name
        counted_mashups += 1  # 正常に処理できた mashup 数
        total_pred_categories += len(pred_categories)
        total_pred_apis += len(pred_apis_final)
        if api_hallucinated:
            hallucinated_api_mashup_count += 1
            hallucinated_apis.extend(api_hallucinated)
            # print(f"\n⚠️ ハルシネーションAPI検出: {mashup_name}")
            # print(f"  予測API: {pred_apis_final}")
            # print(f"  存在しないAPI: {api_hallucinated}")



    # 結果出力
    print("\n=== ハルシネーションカテゴリ検出結果 ===")
    print(f"不正カテゴリを含んだ mashup 数: {hallucinated_mashup_count} 件")
    print(f"ハルシネーションカテゴリの総数（重複込み）: {len(hallucinated_categories)} 件")
    print("\n=== ハルシネーションAPI検出結果 ===")
    print(f"不正APIを含んだ mashup 数: {hallucinated_api_mashup_count} 件")
    print(f"ハルシネーションAPIの総数（重複込み）: {len(hallucinated_apis)} 件")
     # 🎯 出力結果の追加
    print("\n=== 合計出力数と平均 ===")
    print(f"対象 mashup 数: {counted_mashups}")
    print(f"pred_categories の合計数: {total_pred_categories}")
    print(f"pred_apis の合計数: {total_pred_apis}")
    print(f"pred_categories の平均数: {total_pred_categories / counted_mashups:.2f}")
    print(f"pred_apis の平均数: {total_pred_apis / counted_mashups:.2f}")
    # 正解カテゴリ/API
    # print(f"✅ gold_categories 合計: {total_gold_categories} / 平均: {total_gold_categories / counted_mashups:.2f}")
    # print(f"✅ gold_apis 合計: {total_gold_apis} / 平均: {total_gold_apis / counted_mashups:.2f}")





if __name__ == "__main__":
    print("整形ファイル:", output_path)

    evaluate_responses(
        formatted_path=output_path,
        mashup_csv_path="./data/filterd_mashup_data.csv",
        prompt_method_name=prompt_method_name,
        expected_bracket_counts=expected_bracket_counts,
        available_categories={x.lower().replace(" ", "-") for x in available_categories},
        available_apis_name={x.lower().replace(" ", "-") for x in available_apis_name}  # ★ここをsetに変換
    )