#プロンプト一覧
#zero_shot(推論プロセス)
#few_shot_cot(事例)
#zero_shot_cot_with_inference_process(推論プロセス)
#few_shot_cot_with_inference_process(事例+推論プロセス)

import openai
class MashupServiceRecommendation_openai:
    def __init__(self, few_shot_examples, available_categories, available_apis, service_requirements):
        self.few_shot_examples =few_shot_examples
        self.available_categories = available_categories
        self.available_apis = available_apis
        self.service_requirements = service_requirements
    
    def plan_and_solve(self):
        messages = [
            # 1. system ロールでAIの振る舞いを定義
            {
                "role": "system",
                "content": (
                    "You are an expert system for recommending APIs based on the requirements for a mashup service.\n"
                    
                )
            },

            # 2. ユーザー入力を user ロールとして分離
            {
                "role": "user",
                "content": (
                    f"Available categories: {', '.join(self.available_categories)}\n"
                    f"Available APIs: {self.available_apis}\n"
                    f"Requirements: {self.service_requirements}\n\n"
                    "Let's first understand the problem and devise a plan to solve the problem. Then, let's carry out the plan and solve the problem step by step."
                    "Output format:\n"
                    "###Reasoning###:\n"
                    "Detailed breakdown of the thought process\n\n"
                    "###answer###:\n"
                    "Recommend categories: ['Category_name', 'Category_name', ...]\n"
                    "Recommend All matched APIs: ['API_name', 'API_name', ...]"
                )
            }
        ]

        return messages

    def zero_shot(self):
        messages = [
            # 1. system ロールでAIの振る舞いを定義
            {
                "role": "system",
                "content": (
                    "You are an expert system for recommending APIs based on the requirements for a mashup service.\n"
                )
            },

            # 2. ユーザー入力を user ロールとして分離
            {
                "role": "user",
                "content": (
                    f"Available categories: {', '.join(self.available_categories)}\n"
                    f"Available APIs: {self.available_apis}\n"
                    f"Requirements: {self.service_requirements}\n\n"
                    "Output format:\n"
                    "###Reasoning###:\n"
                    "Detailed breakdown of the thought process\n\n"
                    "###answer###:\n"
                    "Recommend categories: ['Category_name', 'Category_name', ...]\n"
                    "Recommend All matched APIs: ['API_name', 'API_name', ...]"
                )
            }
        ]

        return messages

    def zero_shot_cot(self):
        messages = [
            # 1. system ロールでAIの振る舞いを定義
            {
                "role": "system",
                "content": (
                    "You are an expert system for recommending APIs based on the requirements for a mashup service.\n"
                )
            },

            # 2. ユーザー入力を user ロールとして分離
            {
                "role": "user",
                "content": (
                    f"Available categories: {', '.join(self.available_categories)}\n"
                    f"Available APIs: {self.available_apis}\n"
                    f"Requirements: {self.service_requirements}\n\n"
                    "Let's think step by step."
                    "Output format:\n"
                    "###Reasoning###:\n"
                    "Detailed breakdown of the thought process\n\n"
                    "**answer**:\n"
                    "Recommend categories: ['Category_name', 'Category_name', ...]\n"
                    "Recommend All matched APIs: ['API_name', 'API_name', ...]"
                )
            }
        ]

        return messages
    
    def few_shot(self):
        messages = [
            # 1. system ロールでAIの振る舞いを定義
            {
                "role": "system",
                "content": (
                    "You are an expert system for recommending APIs based on the requirements for a mashup service.\n"
                )
            }
        ]
        # 2. few-shot examples（user → assistant のペア）を追加
        messages.extend(self.few_shot_examples)

        # 3. タスク入力（userロール）を追加
        messages.append({
            "role": "user",
            "content": (
                f"Available categories: {', '.join(self.available_categories)}\n"
                f"Available APIs: {self.available_apis}\n"
                f"Requirements: {self.service_requirements}\n\n"
                "Output format:\n"
                "###Reasoning###:\n"
                "Detailed breakdown of the thought process\n\n"
                "###answer###:\n"
                "Recommend categories: ['Category_name', 'Category_name', ...]\n"
                "Recommend All matched APIs: ['API_name', 'API_name', ...]"
            )
        })
        return messages
    
    def few_shot_cot(self):
        messages = [
            # 1. system ロールでAIの振る舞いを定義
            {
                "role": "system",
                "content": (
                    "You are an expert system for recommending APIs based on the requirements for a mashup service.\n"
                )
            }
        ]
        # 2. few-shot examples（user → assistant のペア）を追加
        messages.extend(self.few_shot_examples)

        # 3. タスク入力（userロール）を追加
        messages.append({
            "role": "user",
            "content": (
                f"Available categories: {', '.join(self.available_categories)}\n"
                f"Available APIs: {self.available_apis}\n"
                f"Requirements: {self.service_requirements}\n\n"
                "Output format:\n"
                "###Reasoning###:\n"
                "Detailed breakdown of the thought process\n\n"
                "###answer###:\n"
                "Recommend categories: ['Category_name', 'Category_name', ...]\n"
                "Recommend All matched APIs: ['API_name', 'API_name', ...]"
            )
        })
        return messages
    
    def few_shot_ablation(self):
        messages = [
            # 1. system ロールでAIの振る舞いを定義
            {
                "role": "system",
                "content": (
                    "You are an expert system for recommending APIs based on the requirements for a mashup service.\n"
                )
            }
        ]
        # 2. few-shot examples（user → assistant のペア）を追加
        messages.extend(self.few_shot_examples)

        # 3. タスク入力（userロール）を追加
        messages.append({
            "role": "user",
            "content": (
                f"Available categories: {', '.join(self.available_categories)}\n"
                f"Available APIs: {self.available_apis}\n"
                f"Requirements: {self.service_requirements}\n\n"
                "Output format:\n"
                "###Reasoning###:\n"
                "Detailed breakdown of the thought process\n\n"
                "###answer###:\n"
                "Recommend categories: ['Category_name', 'Category_name', ...]\n"
                "Recommend All matched APIs: ['API_name', 'API_name', ...]"
            )
        })

        return messages
    def zero_shot_cot_with_inference_process(self):
        messages = [
            # 1. system ロールでAIの振る舞いを定義
            {
                "role": "system",
                "content": (
                    "You are an expert system for recommending APIs based on the requirements for a mashup service.\n"
                    "Follow the reasoning process below:\n"
                    "1. Infer the core functionalities of the mashup service from the given Requirements.\n"
                    "2. Select relevant categories from Available categories that correspond to the core functionalities inferred in Step1.\n"
                    "3. Select APIs from Available APIs within the categories selected in Step 2 whose descriptions align with the core functionalities inferred in Step 1.\n"
                    "4. Propose an optimal combination of APIs identified in Step 3 that covers the core functionalities inferred in Step1 with the minimum number of APIs.\n"
                )
            }
        ]
        # 2. few-shot examples（user → assistant のペア）を追加
        messages.extend(self.few_shot_examples)

        # 3. タスク入力（userロール）を追加
        messages.append({
            "role": "user",
            "content": (
                f"Available categories: {', '.join(self.available_categories)}\n"
                f"Available APIs: {self.available_apis}\n"
                f"Requirements: {self.service_requirements}\n\n"
                "Output format:\n"
                "###Reasoning###:\n"
                "Detailed breakdown of the thought process\n\n"
                "###answer###:\n"
                "Recommend categories: ['Category_name', 'Category_name', ...]\n"
                "Recommend All matched APIs: ['API_name', 'API_name', ...]"
            )
        })

        return messages
    

    
    def few_shot_cot_with_inference_process(self):
        messages = [
            # 1. systemメッセージ：推論プロセスと目的を定義
            {
                "role": "system",
                "content": (
                    "You are an expert system for recommending APIs based on the Rquirements for mashup service.\n"
                    "Follow the reasoning process below:\n"
                    "1. Infer the core functionalities of the mashup service from the given [Requirements].\n"
                    "2. From the given [Available Categories], select the categories that correspond to the core functionalities identified in Step 1.\n"
                    "3. For each category chosen in Step 2, select from the given [Available APIs] the APIs whose descriptions match the core functionalities identified in Step 1.\n"
                    "4. Propose an optimal combination of the APIs selected in Step 3 that covers all core functionalities identified in Step 1, using the minimum number of APIs.\n"
                )
            }
        ]

        # 2. few-shot examples（user → assistant のペア）を追加
        messages.extend(self.few_shot_examples)

        # 3. タスク入力（userロール）を追加
        messages.append({
            "role": "user",
            "content": (
                f"Available categories: {', '.join(self.available_categories)}\n"
                f"Available APIs: {self.available_apis}\n"
                f"Requirements: {self.service_requirements}\n\n"
                "Output format:\n"
                "###Reasoning###:\n"
                "1. Core Features:\n"
                "- Feature_name：reason\n"
                "...\n"
                "2. API Categories:\n"
                "- Category_name：reason\n"
                "...\n"
                "3. Candidate APIs per Category\n"
                "- Category_name：\n"
                "  - API_name:reason\n"
                "  ...\n"
                "...\n"
                "4. Final API Recommendation\n"
                "- API_name:reason\n"
                "...\n"

                "###answer###:\n"
                "Recommend categories: ['Category_name', 'Category_name', ...]\n"
                "Recommend All matched APIs: ['API_name', 'API_name', ...]"
            )
        })

        return messages


    
    #回答を作成するプロンプト
    def choice_prompt(self, prompt_method_name,model):
        prompt_method = getattr(self, prompt_method_name, None)
        messages = prompt_method()
        response = openai.ChatCompletion.create(
            model = model,
            messages=messages,
        )
        return response['choices'][0]['message']['content']
    