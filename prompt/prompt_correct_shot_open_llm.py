#プロンプト一覧
#zero_shot(推論プロセス)
#few_shot_cot(事例)
#zero_shot_cot_with_inference_process(推論プロセス)
#few_shot_cot_with_inference_process(事例+推論プロセス)

from ollama import Client
class make_few_open_llm:
    def __init__(self,  available_categories, available_apis, service_requirements,correct_categories,correct_apis):
        self.available_categories = available_categories
        self.available_apis = available_apis
        self.service_requirements = service_requirements
        self.correct_categories = correct_categories
        self.correct_apis = correct_apis
        self.client = Client(
            host='http://localhost:11434',
            headers={'Content-Type': 'application/json'}
        )
    
    
    def make_few(self):
        messages = [
            # 1. system ロールでAIの推論手順と目的を明確に
            {
                "role": "system",
                "content": (
                    "This is a system for creating reasoning examples that propose appropriate APIs based on the requirements of a mashup service, following the given reasoning process.\n"
                    "Follow this reasoning process:\n"
                    "1. Infer the core functionalities of the mashup service based on the given Requirements.\n"
                    "2. Identify and propose multiple highly relevant API categories from the Available categories.\n"
                    "3. Match APIs from the proposed categories and identify relevant ones based on their descriptions.\n"
                    "4. Select and recommend the best-suited APIs with reasons.\n"

                    "Rules for output correctness:\n"
                    "- Global:\n"
                    "  • Use only items that appear in the provided 'Available categories' and 'Available APIs'.\n"
                    "  • Do NOT invent, infer, or hallucinate new names. Case and spelling must exactly match.\n"
                    "  • Use the exact name string from 'Available APIs'; do NOT add words like 'API', 'service', or 'endpoint' unless they are explicitly part of the name.\n"
                    "  • If something (e.g., Google Plus) is not in Available APIs, you must NOT output it.\n"
                    "- Step 2 (Identify Relevant API Categories): output **only the Correct categories**.\n"
                    "- Step 3 (Match APIs): output **all Correct APIs**, and you may include a few plausible-but-incorrect APIs, but they **must be strictly selected from the Available APIs** and belong to Step-2 categories.\n"
                    "- Step 4 (Select the Most Suitable APIs): output **only the Correct APIs**.\n"
                    "- At the end, in the Conclusion, restate the Correct categories and Correct APIs exactly as provided.\n"
                )
            },

            # 2. ユーザー入力を user ロールとして明確に分ける
            {
                "role": "user",
                "content": (
                    f"Available categories: {', '.join(self.available_categories)}\n"
                    f"Available APIs: {self.available_apis}\n"
                    f"Requirements: {self.service_requirements}\n\n"
                    f"Correct categories: {self.correct_categories}\n"
                    f"Correct APIs: {self.correct_apis}\n"

                    "Please provide the following:\n"
                        "1. **Identify Core Features**:\n"
                        "   - Feature_name: reason\n"
                        "   - Feature_name: reason\n"
                        "   ...\n\n"
                        "2. **Identify Relevant API Categories**:\n"
                        "   - Category_name: reason\n"
                        "   - Category_name: reason\n"
                        "   ...\n\n"
                        "3. **Match APIs from Relevant Categories**:\n"
                        "   - **Category APIs**:\n"
                        "       - API_name: reason\n"
                        "       - API_name: reaspn\n"
                        "       ...\n\n"
                        "   - **Category APIs**:\n"
                        "       - API_name: reason\n"
                        "       - API_name: reason\n"
                        "       ...\n\n"
                        "4. **Select the Most Suitable APIs**:\n"
                        "   - API_name: reason\n"
                        "   - API_name: reason\n"
                        "   ...\n\n"
                        "### Conclusion:\n"
                        "   - Recommend categories from 2.:['Category_name', 'Category_name', ...]\n"
                        "   - Recommend All matched APIs in 3.:['API_name', 'API_name', ...]\n"
                        "   - Final recommended APIs: ['API_name', 'API_name', ...]"
                )
            }
        ]

        return messages
    
    
    #回答を作成するプロンプト
    def choice_prompt(self, prompt_method_name, model):
        prompt_method = getattr(self, prompt_method_name, None)
        if not prompt_method:
            raise ValueError(f"Method {prompt_method_name} not found")

        messages = prompt_method()
        # === 毎回プロンプトの「完成形（全体）」を表示 ===
        # print("\n===== [COMPLETE PROMPT TO LLM] =====")
        # for msg in messages:
        #     print(f"Role: {msg['role']}")
        #     print(msg['content'])
        #     print("------------------------------------")
        
        try:
            response = self.client.chat(model=model, messages=messages,options={
                "temperature": 0
            })
            return response.message.content
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return None
    