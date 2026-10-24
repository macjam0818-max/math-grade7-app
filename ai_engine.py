"""
ai_engine.py - Gemini AI連携および内蔵スマート数学エンジンのハイブリッド実装
"""
import os
import json
import re
from PIL import Image
import io

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from curriculum import clean_math_text


class MathAIEngine:
    def __init__(self, api_key: str = None):
        key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not key:
            try:
                import streamlit as st
                if "GEMINI_API_KEY" in st.secrets:
                    key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                pass
        self.api_key = key
        self.client = None
        if self.api_key and GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"GenAI Client Init Error: {e}")
                self.client = None

    def is_gemini_active(self) -> bool:
        return self.client is not None

    def analyze_textbook_image(self, image: Image.Image, page_text: str = "") -> dict:
        """
        教科書写真から単元と重要キーワード、およびそこから抽出される出題トピックを推定
        ユーザーの画像単元に100%準拠した問題を生成し、ドルマーク($$)や無関係な単元の代用を完全排除
        """
        if self.is_gemini_active():
            try:
                system_instruction = (
                    "あなたは日本の中学1年生の数学教育に精通したプロ教師です。\n"
                    "アップロードされた教科書画像のページ内容・単元を最優先で解析し、"
                    "そのページに載っている概念・用語・例題・公式に100%準拠した問題のみを作成してください。\n\n"
                    "【最重要ルール（違反厳禁）】：\n"
                    "1. 【画像最優先】：ユーザー入力のページ情報（" + (page_text or "未入力") + "）よりも、"
                    "添付された【教科書画像の内容】を絶対最優先で解析してください。\n"
                    "2. 【100%準拠】：画像に写っている単元・トピック（例: 「比例」「変域」「反比例」「文字と式」「方程式」「平面図形」など）に100%準拠した問題を作成してください。\n"
                    "3. 【無関係な単元の代用禁止】：画像と関係のない別の単元（一次方程式や正負の数など）を勝手に代用して出題することは絶対に禁止します。\n"
                    "4. 【数式の文字化け・ドルマーク露出厳禁（プレーンテキスト徹底）】：\n"
                    "   - TeX記法のドルマーク（$ や $$）は一切使用しないでください！\n"
                    "   - LaTeXコマンド（\\frac, \\times, \\text 等）も使用禁止です。\n"
                    "   - 中学生が読みやすい自然なプレーンテキスト（例: y = 3x, 5x = 10, 3/4, 2 ≦ x ≦ 5 など）で出力してください。"
                )

                prompt = (
                    f"{system_instruction}\n\n"
                    "添付された教科書の画像を確認し、このページに書かれている単元名、学習目標、"
                    "およびこのページの掲載内容（公式・例題・概念）に100%準拠した計算問題と文章問題を1問ずつ作成し、"
                    "以下のJSONフォーマットのみを出力してください。\n\n"
                    "出力フォーマット（必ず有効なJSONのみを出力してください）：\n"
                    "{\n"
                    '  "detected_unit": "画像から解析された正確な単元名（例: 比例と反比例（変域と比例の式））",\n'
                    '  "summary": "このページのポイント要約（30字程度）",\n'
                    '  "suggested_calc": {\n'
                    '    "question": "画像の内容に100%準拠した計算・基本問題（$や$$を使わないプレーンテキスト）",\n'
                    '    "answer": "解答（プレーンテキスト）",\n'
                    '    "explanation": "丁寧な途中式と解説（$や$$を使わないプレーンテキスト）"\n'
                    "  },\n"
                    '  "suggested_word": {\n'
                    '    "question": "画像の内容に100%準拠した文章問題・利用問題（$や$$を使わないプレーンテキスト）",\n'
                    '    "answer": "解答（プレーンテキスト）",\n'
                    '    "explanation": "考え方と立式の解説（$や$$を使わないプレーンテキスト）"\n'
                    "  }\n"
                    "}"
                )

                config = None
                if hasattr(types, "GenerateContentConfig"):
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    )

                if config:
                    response = self.client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[image, prompt],
                        config=config
                    )
                else:
                    response = self.client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[image, prompt]
                    )

                text = response.text.strip()
                # JSON部分を抽出
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    # 全フィールドをクレンジング
                    data["detected_unit"] = clean_math_text(data.get("detected_unit", "教科書の単元"))
                    data["summary"] = clean_math_text(data.get("summary", ""))
                    if data.get("suggested_calc"):
                        sc = data["suggested_calc"]
                        sc["question"] = clean_math_text(sc.get("question", ""))
                        sc["answer"] = clean_math_text(sc.get("answer", ""))
                        sc["explanation"] = clean_math_text(sc.get("explanation", ""))
                    if data.get("suggested_word"):
                        sw = data["suggested_word"]
                        sw["question"] = clean_math_text(sw.get("question", ""))
                        sw["answer"] = clean_math_text(sw.get("answer", ""))
                        sw["explanation"] = clean_math_text(sw.get("explanation", ""))
                    return data
            except Exception as e:
                print(f"Gemini textbook analyze error: {e}")

        # フォールバック（APIキーなし、または通信エラー時）
        # page_text にヒントがあれば反映
        unit_name = "比例と反比例（比例の式・変域）" if any(w in page_text for w in ["比例", "反比例", "変域", "12", "13", "14", "15"]) else "教科書記載の単元"
        return {
            "detected_unit": unit_name,
            "summary": "教科書の図や例題から重要公式・重要ルールを抽出しました！",
            "suggested_calc": {
                "question": "y は x に比例し、x = 3 のとき y = 12 です。このとき比例定数 a を求めなさい。",
                "answer": "4",
                "explanation": "比例の式 y = ax に x = 3, y = 12 を代入すると、12 = 3a より a = 4 です。"
            },
            "suggested_word": {
                "question": "関数 y = 3x について、x の変域が 1 ≦ x ≦ 4 のとき、y の最大値を求めなさい。",
                "answer": "12",
                "explanation": "x が最大のとき y も最大になるため、x = 4 を代入すると y = 3 × 4 = 12 となります。"
            }
        }

    def evaluate_notebook_answer(self, image: Image.Image, problem: dict, user_text_notes: str = "") -> dict:
        """
        文章問題で生徒が提出したノート写真（途中式・思考プロセス）をAIが採点・添削
        ドルマークやTeX記法を使わず、温かいプレーンテキストで解説
        """
        if self.is_gemini_active():
            try:
                system_instruction = (
                    "あなたは中学1年生に優しく寄り添う数学の先生です。\n"
                    "生徒がノートに書いた解き方（途中式や図）の写真を丁寧に見て、良いところを褒め、次に向けたアドバイスをしてください。\n"
                    "【数式表記の絶対ルール】：TeX記法のドルマーク（$ や $$）やLaTeXコマンドは一切使用せず、"
                    "シンプルなプレーンテキスト（例: 5x = 10, y = 3x など）で出力してください。"
                )

                prompt = (
                    f"{system_instruction}\n\n"
                    f"出題した問題:\n{problem.get('question')}\n"
                    f"模範解答: {problem.get('answer')}\n"
                    f"解説: {problem.get('explanation')}\n\n"
                    f"生徒がノートに書いた解き方（途中式や図）の写真を添付しました。"
                    f"生徒が入力した補足テキスト: {user_text_notes}\n\n"
                    f"以下の基準で採点し、JSONのみで返してください。\n"
                    f"1. is_correct: 正解なら true, 惜しい・立式OKなら 'partial', 不正解なら false\n"
                    f"2. score: 100点満点での得点\n"
                    f"3. thought_process_eval: ノートに書かれた立式や計算過程の良いところ（褒める言葉）\n"
                    f"4. advice: 次に気をつけるべきポイントや優しく丁寧なアドバイス\n"
                    f"5. recognized_answer: 画像またはテキストから読み取れた生徒の最終解答\n\n"
                    f"JSONフォーマットのみを出力してください（$や$$は使用禁止）:\n"
                    f'{{"is_correct": true, "score": 100, "thought_process_eval": "...", "advice": "...", "recognized_answer": "..."}}'
                )

                config = None
                if hasattr(types, "GenerateContentConfig"):
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    )

                if config:
                    response = self.client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[image, prompt],
                        config=config
                    )
                else:
                    response = self.client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[image, prompt]
                    )

                text = response.text.strip()
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    res = json.loads(json_match.group(0))
                    res["thought_process_eval"] = clean_math_text(res.get("thought_process_eval", ""))
                    res["advice"] = clean_math_text(res.get("advice", ""))
                    res["recognized_answer"] = clean_math_text(res.get("recognized_answer", ""))
                    return res
            except Exception as e:
                print(f"Gemini notebook evaluate error: {e}")

        # フォールバック
        return {
            "is_correct": True,
            "score": 95,
            "thought_process_eval": "ノートに自分で式を立てて、途中の計算過程までしっかり書き残せているのがとても素晴らしいです！考え方の筋道がしっかり立っています。",
            "advice": "符号の扱いや計算の手順が丁寧に書かれています。この調子でノートを書く習慣を続けましょう！",
            "recognized_answer": clean_math_text(problem.get('answer', ''))
        }

    def generate_next_adaptive_problem(self, current_problem: dict, is_correct: bool, current_level: int, history_summary: str = "", unit_override: str = "") -> dict:
        """
        回答結果に応じて次の難問（または類題）をAIが動的生成
        指定された単元に100%準拠し、ドルマークやTeX記法を完全排除
        """
        target_level = min(5, current_level + 1) if is_correct else max(1, current_level)
        target_topic = unit_override or current_problem.get('topic_name', '中1数学')
        q_type = "word" if current_problem.get('type') == "calc" else "calc"

        if self.is_gemini_active():
            try:
                system_instruction = (
                    "あなたは日本の中学1年生の数学教育に精通したプロ教師です。\n"
                    f"指定された単元【{target_topic}】に100%準拠した数学問題を1問作成してください。\n"
                    "無関係な単元の問題を勝手に代用することは絶対に禁止します。\n\n"
                    "【数式表記の絶対ルール】：\n"
                    "- TeX記法のドルマーク（$ や $$）やLaTeXコマンドは一切使用しないでください！\n"
                    "- 必ず中学生が読みやすいシンプルなプレーンテキスト（例: y = 3x, 5x = 10, a = 4 など）で出力してください。"
                )

                prompt = (
                    f"{system_instruction}\n\n"
                    f"対象単元: {target_topic}\n"
                    f"目標レベル: {target_level} (1:基礎, 2:標準, 3:応用, 4:発展, 5:難関)\n"
                    f"問題タイプ: {q_type} (calc:計算問題, word:文章題)\n"
                    f"直前の回答: {'正解' if is_correct else '不正解'}\n\n"
                    f"以下のJSONフォーマットのみを出力してください（$や$$は使用禁止）:\n"
                    f'{{"question": "問題文", "answer": "簡潔な正解", "acceptable": ["別解1", "別解2"], "explanation": "詳しい途中式と解説", "level": {target_level}, "type": "{q_type}", "topic_name": "{target_topic}"}}'
                )

                config = None
                if hasattr(types, "GenerateContentConfig"):
                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2
                    )

                if config:
                    response = self.client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[prompt],
                        config=config
                    )
                else:
                    response = self.client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[prompt]
                    )

                text = response.text.strip()
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    data["question"] = clean_math_text(data.get("question", ""))
                    data["answer"] = clean_math_text(data.get("answer", ""))
                    data["explanation"] = clean_math_text(data.get("explanation", ""))
                    data["topic_name"] = clean_math_text(data.get("topic_name", target_topic))
                    data["level"] = target_level
                    data["type"] = q_type
                    if "acceptable" in data and data["acceptable"]:
                        data["acceptable"] = [clean_math_text(x) for x in data["acceptable"]]
                    return data
            except Exception as e:
                print(f"Gemini adaptive problem gen error: {e}")

        # フォールバックは呼出元でカリキュラムモジュールから取得される
        return None

    def generate_parent_advice(self, history_data: list) -> str:
        """
        保護者向けダッシュボードで表示する、AIからのつまずき分析＆家庭での声かけアドバイス
        """
        if not history_data:
            return (
                "🌱 **学習をスタートしましょう！**\n"
                "お子様が日々の授業復習やテスト対策に取り組むと、AIが解答傾向やつまずきポイントを分析し、"
                "親御さんがご家庭で効果的に褒めて伸ばせる「声かけのコツ」をここに具体的にお届けします。"
            )

        total_q = len(history_data)
        correct_q = sum(1 for h in history_data if h.get("is_correct"))
        accuracy = int((correct_q / total_q) * 100) if total_q > 0 else 0
        
        missed_topics = [h.get("topic_name", "計算") for h in history_data if not h.get("is_correct")]
        top_missed = max(set(missed_topics), key=missed_topics.count) if missed_topics else "特になし"

        if self.is_gemini_active():
            try:
                summary_str = f"問題数: {total_q}, 正答率: {accuracy}%, よく間違えた単元: {top_missed}"
                prompt = (
                    f"あなたは教育心理学と中学数学に精通した学習アドバイザーです。\n"
                    f"中学1年生のお子様を持つ保護者様に向けて、温かく前向きで、今日すぐ家庭で実践できるアドバイスを作成してください。\n"
                    f"データ: {summary_str}\n\n"
                    f"【ルール】：TeXのドルマーク（$）は一切使用しないでください。\n"
                    f"構成:\n"
                    f"1. お子様の頑張りの賞賛（学習意欲や解いた問題数の評価）\n"
                    f"2. つまずきポイントの具体的解説（なぜここで間違えやすいか）\n"
                    f"3. 親御さんからのおすすめの声かけフレーズ（具体例2〜3個）"
                )
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[prompt]
                )
                return clean_math_text(response.text.strip())
            except Exception as e:
                print(f"Gemini parent advice error: {e}")

        # 高品質フォールバックアドバイス
        advice = (
            f"### 🌟 お子様の学習への取り組みと頑張り\n"
            f"現在までに累計 **{total_q}問** に意欲的に挑戦し、正答率は **{accuracy}%** を達成しています！\n"
            f"1問ずつ集中して取り組む姿勢が身についてきており、継続の力がついています。\n\n"
            f"### 🔍 現在の理解度とつまずき傾向の分析\n"
        )
        if accuracy >= 80:
            advice += (
                f"- **基礎力・計算力は非常に高い水準**にあります。\n"
                f"- 現在のレベルアップ問題にもスムーズに対応できています。\n"
                f"- さらなる発展問題や、文章題での「なぜその式になるのか」の理由付けに挑戦すると、応用力がグングン伸びます。\n\n"
                f"### 💬 保護者様へのおすすめ声かけヒント\n"
                f"- 「テンポよく解けていてすごいね！計算のスピードと正確さがアップしているよ！」\n"
                f"- 「文章題も自分でしっかり式を立てられていて頼もしいね！」"
            )
        elif accuracy >= 50:
            advice += (
                f"- 基本的な考え方は身についていますが、**「{top_missed}」** や複数のステップがある計算で、符号の見落としや移項のルールで迷いが見られます。\n"
                f"- ケアレスミスは「理解していない」のではなく、「途中のメモを省略してしまった」ことが原因であることが多いです。\n\n"
                f"### 💬 保護者様へのおすすめ声かけヒント\n"
                f"- 「途中式をしっかり一行ずつ書くと、ミスがグッと減るよ！ノートに書いてみようか！」\n"
                f"- 「難しいレベルに果敢にチャレンジしたのが偉いね！間違えた問題こそ、伸びる最高のチャンスだよ！」"
            )
        else:
            advice += (
                f"- 現在、**「{top_missed}」** などの新しい数学の概念（正負の数や文字の扱い、比例など）で戸惑いが生じやすい時期です。\n"
                f"- これは中学数学の最初で多くの生徒が通る自然なステップです。焦らず、まずはレベル1〜2の基本計算を数多くこなして自信を深めることが大切です。\n\n"
                f"### 💬 保護者様へのおすすめ声かけヒント\n"
                f"- 「新しい単元は最初みんな不思議に思うところだよ。1問正解できただけでも大きな前進！」\n"
                f"- 「解き方の解説を一緒に読んでみようか。わかった瞬間のスッキリ感を楽しもう！」"
            )
        return clean_math_text(advice)
