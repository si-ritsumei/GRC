import json
import os

###################### 設定（ここだけ変えればOK） ######################
mashup_data = "./data/filtered_mashup_data.json"
out_json = "./shot/shot_few_shot.json"

# あなたのデータ構造に合わせる
CATEGORY_INDEX = 2   # ← これが ["social","video","photos","storage"] の位置
API_INDEX = 3        # ← これが ["flickr","youtube",...] の位置

LINE1_PREFIX = "Recommend categories: "
LINE2_PREFIX = "Final recommended APIs: "

SORT_LISTS = False
SKIP_IF_EMPTY = True
#######################################################################


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(obj, path):
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)


def main():
    data = load_json(mashup_data)

    if not isinstance(data, dict):
        raise ValueError("filtered_mashup_data.json は {mashup_name: [...]} の dict 形式を想定しています")

    shot = {}
    total = 0
    kept = 0

    for mashup_name, arr in data.items():
        total += 1

        # 値がリスト形式であることを想定
        if not isinstance(arr, list):
            continue

        # indexが存在するかチェック
        if len(arr) <= max(CATEGORY_INDEX, API_INDEX):
            continue

        cats = arr[CATEGORY_INDEX]
        apis = arr[API_INDEX]

        # 念のため list 以外も吸収
        if cats is None:
            cats = []
        if apis is None:
            apis = []
        if not isinstance(cats, list):
            cats = [cats]
        if not isinstance(apis, list):
            apis = [apis]

        if SORT_LISTS:
            cats = sorted(cats)
            apis = sorted(apis)

        if SKIP_IF_EMPTY and (len(cats) == 0 or len(apis) == 0):
            continue

        text = f"{LINE1_PREFIX}{cats}\n{LINE2_PREFIX}{apis}"
        shot[f"{mashup_name}-1"] = text
        kept += 1

    save_json(shot, out_json)
    print(f"input mashups: {total}")
    print(f"saved: {out_json} (count={kept})")


if __name__ == "__main__":
    main()
