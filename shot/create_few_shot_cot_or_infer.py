#事例を作成する
######################以下選択必須#####################################

#事例を呼び出し
import pandas as pd
import pprint
import json
import os
from dotenv import load_dotenv
#open_ai_apiキーを取得

"""""""①APIデータ"""""""""
# 複合サービスに利用されているAPI情報のみ抽出(メイン)
api_data = './data/filtered_api_data.json'
"""""""①mashupデータ"""""""""
#複合サービスの内、完全データand api数が2以上
mashup_data = './data/filtered_mashup_data.json'
"""""""③llmモデル選択"""""""""
# model = "deepseek-r1:70b"
# model = "llama3.3:latest"
# model = "gpt-4.1-mini"
# model = "deepseek-r1:32b"
# model = "llama3.2:1b"
model = "gpt-oss:120b"
"""""""⑤使用GPU指定"""""""""
# os.environ["CUDA_VISIBLE_DEVICES"] = "1"
"""""""⑥評価サービスの選定"""""""""
#特定の以降サービスのみ評価時(サービス名を指定)
# start_key='similags'
#全てのサービスを評価時
start_key= None
"""""""⑦要件文ごとの評価回数・llm呼び出し上限"""""""""
#要件文ごとの評価回数
iterations = 1
#llm呼び出し上限
max_calls = 2000
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
    from prompt.prompt_correct_shot_openai import make_few_openai as MashupServicefew
else:
    from prompt.prompt_correct_shot_open_llm import make_few_open_llm as MashupServicefew

########################################################################

#JsonファイルにGPTの出力結果を保存
def save_to_json(data, mashup_name):
    """
    JSONファイルに番号付きでデータを追加保存し、値内の改行をそのまま反映する。
    :param data: 保存するデータ（文字列）
    :param prompt_method_name: 保存先ファイル名（変数として渡される）
    :param mashup_name: キーとして使用する名前
    """


    # メソッド名 → ファイル名のマッピング
    # モデル名を短縮名に変換
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
    #モデル名を変換
    model_name = extract_model_name(model)
    
    # ファイル名の生成
    filename = f"./output/{model_name}/few_shot_11_03.json"
    print(filename)

    try:
        # ファイルが存在する場合、既存の内容を読み取る
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                try:
                    existing_data = json.load(file)  # JSONを辞書に読み込む
                except json.JSONDecodeError:
                    # JSONが壊れている場合は初期化
                    existing_data = {}
        else:
            # ファイルが存在しない場合は空の辞書を作成
            existing_data = {}

        # 同じ mashup_name のキーがいくつあるかカウント
        existing_keys = [key for key in existing_data.keys() if key.startswith(mashup_name)]
        next_key_number = len(existing_keys) + 1
        new_key = f"{mashup_name}-{next_key_number}"

        # 新しいデータを追加
        existing_data[new_key] = data

        # JSON形式でファイルに書き込む
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)

        print(f"データが保存されました: {filename} (キー: {new_key})")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

"""""""②llmの実行"""""""""
call_count = 0  # LLM呼び出し回数（全体で1回だけ定義）
stop_flag = False
#一つずつサービスを実行する
for mashup_name, details in available_mashup.items():
    #事例に使用したサービスをスキップ
    #現在のmash upサービス情報取得
    correct_categories = details.get('api_categories', [])
    correct_apis = details.get('apis', [])
    description = details.get('description', "")

    #推薦システムの初期設定
    recommendation_system = MashupServicefew(available_categories, available_apis, description,correct_categories, correct_apis)
    print("-" * 30)
    print("評価中のサービス:",mashup_name)
    print("正解カテゴリ",correct_categories)
    print("正解API名",correct_apis)

    # iteration数だけ評価
    for i in range(iterations):  
        if call_count >= max_calls:
            print(f"呼び出し回数が {max_calls} に達しました。処理を終了します。")
            stop_flag = True
            break
        # LLM呼び出し回数カウント
        call_count += 1
        print(f"Iteration {i+1}, Total call: {call_count}")
        response = recommendation_system.choice_prompt("make_few", model)

        print(response)
        save_to_json(response, mashup_name)

    if stop_flag:
        break