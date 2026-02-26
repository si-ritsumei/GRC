import json
import matplotlib.pyplot as plt

# -----------------------------
# 1. 要件文データ読み込み
# -----------------------------
mashup_path = "data/filtered_mashup_data.json"

with open(mashup_path, "r", encoding="utf-8") as f:
    mashup_data = json.load(f)

# 複合サービス -> 文章量
service_to_length = {}

for service_name, values in mashup_data.items():
    requirement_text = values[1]
    text_length = len(requirement_text.strip())
    service_to_length[service_name] = text_length


# -----------------------------
# 2. 精度データ読み込み
# -----------------------------
score_path = "output/gpt/few_cot_infer/f1_instance_scores.json"

with open(score_path, "r", encoding="utf-8") as f:
    score_data = json.load(f)


# -----------------------------
# 3. データ結合
# -----------------------------
lengths = []
category_f1_scores = []
api_final_f1_scores = []

for service_name, scores in score_data.items():
    if service_name not in service_to_length:
        continue

    lengths.append(service_to_length[service_name])
    category_f1_scores.append(scores["category_f1"])
    api_final_f1_scores.append(scores["api_final_f1"])

print(lengths)
print(category_f1_scores)
print(api_final_f1_scores)

# -----------------------------
# 4. 散布図（文章量 × 精度）
# -----------------------------
plt.figure()
plt.scatter(lengths, category_f1_scores)
plt.xlabel("Requirement Length (characters)")
plt.ylabel("Category F1")
plt.title("Requirement Length vs Category F1")
plt.show()

plt.figure()
plt.scatter(lengths, api_final_f1_scores)
plt.xlabel("Requirement Length (characters)")
plt.ylabel("API Final F1")
plt.title("Requirement Length vs API Final F1")
plt.show()


# -----------------------------
# 5. ヒストグラム（文章量ごとの精度分布）
# -----------------------------
plt.figure()
plt.hist(category_f1_scores, bins=10)
plt.xlabel("Category F1")
plt.ylabel("Frequency")
plt.title("Distribution of Category F1")
plt.show()

plt.figure()
plt.hist(api_final_f1_scores, bins=10)
plt.xlabel("API Final F1")
plt.ylabel("Frequency")
plt.title("Distribution of API Final F1")
plt.show()
