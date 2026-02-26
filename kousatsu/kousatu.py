import json

# JSONファイルのパス
file_path = "output/gpt/few_cot_infer/f1_instance_scores.json"

# JSON読み込み
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# (key, api_final_f1) のリストを作成
# api_final_f1 が int の 0 の場合のみ除外
scores = []
for key, value in data.items():
    score = value.get("api_final_f1")
    if score == 0 and isinstance(score, int):
        continue  # null相当なので除外
    scores.append((key, score))

# api_final_f1 でソート（降順）
scores_sorted = sorted(scores, key=lambda x: x[1], reverse=True)

# 上位10件・下位10件
top_10 = scores_sorted[:20]
bottom_10 = scores_sorted[-10:]

print("Top 10 (api_final_f1):")
for key, _ in top_10:
    print(key)

print("\nBottom 10 (api_final_f1):")
for key, _ in bottom_10:
    print(key)
