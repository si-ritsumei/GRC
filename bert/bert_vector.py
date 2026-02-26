#要件文の類似度をはかるやつ

from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import pprint
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util
# モデル読み込み
model = SentenceTransformer('intfloat/e5-large')

"""要件文のベクトル化"""
from log.get_information import GetAvailableMashupData
mashup_data = './data/filtered_mashup_data.json'
mashup_data_getter = GetAvailableMashupData(mashup_data)
available_mashup = mashup_data_getter.get_mashup_details()
descriptions = {key: value['description'] for key, value in available_mashup.items()}
pprint.pprint(descriptions)

# BERTベクトル生成（E5系列なら prefix "passage:" を忘れずに）
desc_texts = [f"passage: {desc.strip()}" for desc in descriptions.values()]
embeddings = model.encode(desc_texts)

# 保存（key順を保持しておく）
keys = list(descriptions.keys())
np.savez("description_embeddings.npz", embeddings=embeddings, keys=keys)

"""要件文の類似度テスト"""
# # モデル読み込み
# device = "cuda" if torch.cuda.is_available() else "cpu"

# # ベクトル読み込み
# data = np.load("description_embeddings.npz", allow_pickle=True)
# embeddings = torch.tensor(data['embeddings']).to(device)
# keys = data['keys']

# # クエリのエンコード
# query = "query: Requirements: Show historical biblical sites accurately on a map."
# query_vec = model.encode(query, convert_to_tensor=True).to(device)

# # 類似度計算
# similarities = util.cos_sim(query_vec, embeddings)

# # 上位表示
# top_k = 3
# top_indices = similarities[0].topk(top_k).indices
# for i in top_indices:
#     print(f"{keys[i]} → 類似度: {similarities[0][i].item():.4f}")

