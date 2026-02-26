#メイン処理
#⚠️ promptがopen_llmとgptで異なる。要確認!!
######################以下選択必須#####################################
#事例を呼び出し
import pandas as pd
import pprint
import json
import os
from dotenv import load_dotenv
#open_ai_apiキーを取得
load_dotenv()
# 旧SDKを使う場合に備え、環境変数から取得
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

"""""""①APIデータ"""""""""
# 複合サービスに利用されているAPI情報のみ抽出(メイン)
api_data = './data/filtered_api_data.json'
# 全てのAPI情報を取得(メイン)
# api_data = './data/api_data_new.json'
"""""""①mashupデータ"""""""""
#複合サービスの内、完全データand api数が2以上
mashup_data = './data/filtered_mashup_data.json'
#複合サービスの内、完全データ and api数が1も含む
"#未実装#(フィルタしていない為)"
"""""""③llmモデル選択"""""""""
model = "deepseek-r1:70b"
# model = "llama3.3:latest"
# model = "gpt-4.1-mini"
# model = "deepseek-r1:32b"
# model = "gpt-oss:120b"
"""""""④プロンプト選択"""""""""
# prompt_method_name = "few_shot_cot"
prompt_method_name = "few_shot_cot_with_inference_process"
# prompt_method_name = "few_shot"
# prompt_method_name = "few_shot_ablation"
# prompt_method_name ="plan_and_solve"
# prompt_method_name ="zero_shot"
# prompt_method_name = "zero_shot_cot"
# prompt_method_name = "zero_shot_cot_with_inference_process"
"""""""⑤Shot類似度選択"""""""""
similar_services_json = "./bert/random_similar_services.json"
# similar_services_json = "./bert/top6_similar_services.json"
# similar_services_json = "./bert/low6_similar_services.json"
# similar_services_json = "./bert/top3_low3_similar_services.json"
"""""""⑤使用GPU指定"""""""""
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
"""""""⑥評価サービスの選定"""""""""
#特定の以降サービスのみ評価時(サービス名を指定)
# start_key='scoopmap.net'
#全てのサービスを評価時
start_key= None
"""""""⑦要件文ごとの評価回数・llm呼び出し上限"""""""""
#要件文ごとの評価回数
iterations = 1
#llm呼び出し上限
max_calls = 2000

#####################################################################
####################################################################
"""""""①データ抽出"""""""""
######APIデータ抽出#########
import pprint
from log.get_information import GetAvailableAPIData
api_data_getter = GetAvailableAPIData(api_data)
# API情報を取得
available_apis, available_apis_name = api_data_getter.get_available_apis()
# カテゴリ一覧取得
available_categories = api_data_getter.get_available_categories()


def filter_mashup(data, start_key=None):
    if start_key is None:
        return data  # 全体を返す

    keys = list(data.keys())
    if start_key in keys:
        start_index = keys.index(start_key)
        filtered_keys = keys[start_index:]
        return {k: data[k] for k in filtered_keys}
    else:
        return {}  # 指定キーが見つからなかった場合は空辞書

######mashupデータ抽出#########
from log.get_information import GetAvailableMashupData
# JSONファイルパスを渡してインスタンス作成
mashup_data_getter = GetAvailableMashupData(mashup_data)
# 複合サービスの詳細情報を取得
available_mashup = mashup_data_getter.get_mashup_details()

available_mashup = filter_mashup(available_mashup, start_key)
########################################################################
"""""""②プロンプト呼び出し"""""""""
# モデル名から使用クラスを判定してインポート
if "gpt-4.1" in model.lower():
    from prompt.prompt_openai import MashupServiceRecommendation_openai as MashupServiceRecommendation
else:
    from prompt.prompt_open_llm import MashupServiceRecommendation_open_llm as MashupServiceRecommendation

########################################################################
"""""""③Jsonへの保存設定"""""""""
#JsonファイルにGPTの出力結果を保存
def save_to_json(data, prompt_method_name, mashup_name, similar_services_json):
    """
    JSONファイルに番号付きでデータを追加保存する。
    similar_services_json の種類（random/top6/low6/top3_low3）に応じて保存先ファイル名を分ける。
    """

    # メソッド名 → フォルダ名のマッピング
    filename_map = {
        "zero_shot": "zero_shot",
        "zero_shot_cot": "zero_cot",
        "zero_shot_cot_with_inference_process": "zero_cot_infer",
        "few_shot": "few_shot",
        "few_shot_ablation": "few_shot_ablation",
        "few_shot_cot": "few_cot",
        "few_shot_cot_with_inference_process": "few_cot_infer",
        "plan_and_solve": "plan_and_solve"
    }

    # モデル名を短縮名に変換
    def extract_model_name(model_str):
        s = model_str.lower()
        if "deepseek" in s:
            return "deepseek"
        elif "llama" in s:
            return "llama"
        elif "gemma" in s:
            return "gemma"
        elif "gpt-4.1" in s:
            return "gpt"
        elif "gpt-oss" in s:
            return "gpt_oss"
        else:
            return "other"

    model_name = extract_model_name(model)
    short_name = filename_map.get(prompt_method_name, prompt_method_name)

    # ===== ここが追加：similar_services_json から suffix を決める =====
    sim_file = os.path.basename(similar_services_json).lower()

    if "top6" in sim_file:
        out_json_name = "top6_responses.json"
    elif "low6" in sim_file:
        out_json_name = "low6_responses.json"
    elif "top3_low3" in sim_file or "high3_low3" in sim_file:
        out_json_name = "top3_low3_responses.json"
    else:
        # random など（従来通り）
        out_json_name = "responses.json"

    # 保存先ディレクトリとファイル名
    out_dir = f"./output/{model_name}/{short_name}"
    filename = f"{out_dir}/{out_json_name}"

    try:
        # ディレクトリがなければ作る
        os.makedirs(out_dir, exist_ok=True)

        # 既存読み込み
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        # 番号付きキー作成
        existing_keys = [k for k in existing_data.keys() if k.startswith(mashup_name)]
        next_key_number = len(existing_keys) + 1
        new_key = f"{mashup_name}-{next_key_number}"

        existing_data[new_key] = data

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)

        print(f"データが保存されました: {filename} (キー: {new_key})")

    except Exception as e:
        print(f"エラーが発生しました: {e}")



########################################################################
"""""""③事例の作成（修正版：mashupごとにfew-shot生成）"""""""""

from pathlib import Path

# ====== 事前に1回だけ：類似サービス一覧JSONを読む ======
with open(similar_services_json, "r", encoding="utf-8") as f:
    similar_map = json.load(f)

def get_shot_json_path(prompt_method_name):
    mapping = {
        "few_shot_cot": "./shot/shot_few_shot_cot.json",
        "few_shot_cot_with_inference_process": "./shot/shot_few_shot_infer.json",
        "few_shot": "./shot/shot_few_shot.json",
        "few_shot_ablation": "./shot/shot_few_shot_infer.json",
    }

    if prompt_method_name not in mapping:
        # zero-shot 系などは shot を使わない
        return None

    return mapping[prompt_method_name]


def load_shot_data(prompt_method_name):
    shot_json = get_shot_json_path(prompt_method_name)
    if shot_json is None:
        return {}

    with open(shot_json, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_shot_data_keys(shot_data):
    normalized = {}
    for key, value in shot_data.items():
        base_key = key.rsplit("-", 1)[0]
        if base_key not in normalized:
            normalized[base_key] = value
    return normalized


def build_few_shot_prompt_examples(matched_results: list) -> list:
    few_shot_examples = []
    for item in matched_results:
        desc = (item.get("description") or "").strip()
        llm  = (item.get("llm_output") or "").strip()
        if not desc or not llm:
            continue

        few_shot_examples.append({"role": "user", "content": f"Requirements: {desc}"})
        few_shot_examples.append({"role": "assistant", "content": llm})

    return few_shot_examples

def build_few_shot_examples_for_mashup(
    mashup_name: str,
    available_mashup: dict,
    similar_map: dict,
    normalized_llm: dict
) -> list:
    """
    similar_map は
      { "slidemypics": ["twxlate", ...], ... }
    の形式。
    mashup_name の類似サービスを取り出し、
    description と llm_output を集めて few_shot_examples を作る。
    """
    bert_shot = similar_map.get(mashup_name, [])
    if not bert_shot:
        return []

    matched_results = []
    for key in bert_shot:
        matched_results.append({
            "mashup_name": key,
            "description": available_mashup.get(key, {}).get("description", "[No description]"),
            "llm_output": normalized_llm.get(key, ""),
        })

    return build_few_shot_prompt_examples(matched_results)

# ====== shot_data を読み込み（few-shot系の時だけ有効） ======
shot_data = load_shot_data(prompt_method_name)
normalized_llm = normalize_shot_data_keys(shot_data)

########################################################################
"""""""③llmの実行"""""""""
call_count = 0  # LLM呼び出し回数（全体で1回だけ定義）
stop_flag = False

for mashup_name, details in available_mashup.items():
    #現在のmash upサービス情報取得
    true_categories = details.get('api_categories', [])
    true_apis = details.get('apis', [])
    description = details.get('description', "")

    # ★追加：mashup_nameごとにfew-shotを作る
    few_shot_examples = build_few_shot_examples_for_mashup(
        mashup_name=mashup_name,
        available_mashup=available_mashup,
        similar_map=similar_map,
        normalized_llm=normalized_llm,
    )
    # pprint.pprint(few_shot_examples)

    #推薦システムの初期設定
    recommendation_system = MashupServiceRecommendation(few_shot_examples, available_categories, available_apis, description)
    print("-" * 30)
    print("評価中のサービス:",mashup_name)

    # iteration数だけ評価
    for i in range(iterations):  
        if call_count >= max_calls:
            print(f"呼び出し回数が {max_calls} に達しました。処理を終了します。")
            stop_flag = True
            break
        # LLM呼び出し回数カウント
        call_count += 1
        print(f"Iteration {i+1}, Total call: {call_count}")
        response = recommendation_system.choice_prompt(prompt_method_name, model)
        
        print(response)
        save_to_json(response, prompt_method_name, mashup_name, similar_services_json)


    if stop_flag:
        break