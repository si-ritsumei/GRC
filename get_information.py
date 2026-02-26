#api_data, mashupデータの抽出
import json

# ========================================================
# 共通処理を提供する基底クラス
# JSONファイルの読み込みとエラーハンドリングを担当
# ========================================================
class BaseJSONLoader:
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        self.data = None  # JSONデータを格納する共通変数

    def load_data(self):
        """
        JSONファイルを読み込んで self.data に格納
        エラー処理を含む
        """
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: ファイル「{self.json_file_path}」が見当たりません")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSONの読み込みエラー: {e}")
        except Exception as e:
            raise RuntimeError(f"読み込み中に予期せぬエラー: {e}")

# ========================================================
# APIデータ（単独API情報）を扱うクラス
# 名前・カテゴリ・説明の抽出と、カテゴリ一覧の取得を提供
# ========================================================
class GetAvailableAPIData(BaseJSONLoader):
    def __init__(self, json_file_path):
        """
        親クラスの初期化を呼び出す
        """
        super().__init__(json_file_path)

    def get_available_apis(self):
        """
        APIの情報を整形して文字列出力し、API名リストも返す
        :return:
            - available_apis: "[api name: ..., Category: ..., description: ...]" の文字列
            - available_apis_name_list: API名（キー）のリスト
        """
        if self.data is None:
            self.load_data()

        available_apis = "\n".join([
            f"[api name: {name}, Category: {info[0][0]}, description: {info[1]}]"
            for name, info in self.data.items()
        ])
        available_apis_name_list = list(self.data.keys())

        return available_apis, available_apis_name_list

    def get_available_categories(self):
        """
        各APIのカテゴリリストの最初の要素（メインカテゴリ）を集め、
        重複を排除してソートしたリストを返す
        """
        if self.data is None:
            self.load_data()

        category_set = {
            info[0][0]
            for info in self.data.values()
            if isinstance(info[0], list) and info[0]
        }

        self.available_categories = sorted(category_set)
        return self.available_categories


# ========================================================
# Mashupデータ（複合サービス）を扱うクラス
# 構成API名・カテゴリ・説明文を詳細辞書として返す
# ========================================================
class GetAvailableMashupData(BaseJSONLoader):
    def __init__(self, json_file_path):
        super().__init__(json_file_path)

    def get_mashup_details(self):
        """
        複合サービス名をキーに、構成API名・カテゴリ・説明を格納した辞書を返す
        :return: {mashup_name: {'apis': [...], 'api_categories': [...], 'description': ...}}
        """
        if self.data is None:
            self.load_data()

        mashup_data_details = {}
        for mashup_name, info in self.data.items():
            description = info[1] if len(info) > 1 else ""
            api_categories = info[2] if len(info) > 2 else []
            apis = info[3] if len(info) > 3 else []
            mashup_data_details[mashup_name] = {
                'apis': apis,
                'api_categories': api_categories,
                'description': description
            }

        return mashup_data_details

