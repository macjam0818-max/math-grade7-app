"""
curriculum.py - 中学1年生数学のカリキュラム定義・ページマッピング・問題生成ロジック
"""
import random
import re

# ==========================================
# 数式クレンジング関数（TeX記法・ドルマーク完全除去）
# ==========================================
def clean_math_text(text: str) -> str:
    """
    数式の TeX 記法（$ や $$、\\frac、\\timesなど）を中学生向けの分かりやすいプレーンテキストに変換・除去
    """
    if not text:
        return ""
    s = str(text)

    # 1. 分数 \\frac{a}{b} -> (a/b)
    s = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'(\1/\2)', s)

    # 2. \\text{...} -> ...
    s = re.sub(r'\\text\{([^{}]+)\}', r'\1', s)

    # 3. 数学記号の置換
    s = s.replace(r'\times', '×').replace(r'\div', '÷')
    s = s.replace(r'\pm', '±').replace(r'\mp', '∓')
    s = s.replace(r'\pi', 'π')
    s = s.replace(r'\cdot', '・')
    s = s.replace(r'\leq', '≦').replace(r'\geq', '≧')
    s = s.replace(r'\le', '≦').replace(r'\ge', '≧')
    s = s.replace(r'\neq', '≠')
    s = s.replace(r'\Rightarrow', '→').replace(r'\to', '→')

    # 4. LaTeX括弧の除去 \( ... \) や \[ ... \]
    s = s.replace(r'\(', '').replace(r'\)', '').replace(r'\[', '').replace(r'\]', '')

    # 5. ドルマーク（$$ や $）を完全に除去
    s = s.replace('$$', '').replace('$', '')

    # 6. 残った不要なバックスラッシュ記号の除去
    s = re.sub(r'\\([a-zA-Z]+)', r'\1', s)
    s = s.replace('\\', '')

    # 7. 余計な連続空白の正規化（改行は保持）
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in s.split('\n')]
    return '\n'.join(lines).strip()


# 中1数学 単元マスタ
CHAPTERS = [
    {
        "id": "ch1",
        "name": "第1章 正負の数",
        "page_range": (10, 57),
        "topics": [
            {"id": "ch1_1", "name": "正の数・負の数・絶対値", "page_range": (10, 23)},
            {"id": "ch1_2", "name": "正負の加法と減法", "page_range": (24, 38)},
            {"id": "ch1_3", "name": "正負の乗法と除法・四則混合", "page_range": (39, 50)},
            {"id": "ch1_4", "name": "正負の数の利用（平均・基準）", "page_range": (51, 57)},
        ]
    },
    {
        "id": "ch2",
        "name": "第2章 文字と式",
        "page_range": (58, 87),
        "topics": [
            {"id": "ch2_1", "name": "文字式の表し方・式の値", "page_range": (58, 70)},
            {"id": "ch2_2", "name": "1次式の加法・減法・乗除", "page_range": (71, 80)},
            {"id": "ch2_3", "name": "関係を表す式（等式・不等式）", "page_range": (81, 87)},
        ]
    },
    {
        "id": "ch3",
        "name": "第3章 1次方程式",
        "page_range": (88, 121),
        "topics": [
            {"id": "ch3_1", "name": "等式の性質と方程式の基本解き方", "page_range": (88, 98)},
            {"id": "ch3_2", "name": "かっこ・小数・分数を含む方程式・比例式", "page_range": (99, 107)},
            {"id": "ch3_3", "name": "方程式の利用（代金・過不足・速さの文章題）", "page_range": (108, 121)},
        ]
    },
    {
        "id": "ch4",
        "name": "第4章 比例と反比例",
        "page_range": (122, 157),
        "topics": [
            {"id": "ch4_1", "name": "関数と変数・変域・比例の式", "page_range": (122, 137)},
            {"id": "ch4_2", "name": "座標と比例・反比例のグラフ", "page_range": (138, 149)},
            {"id": "ch4_3", "name": "比例・反比例の利用（水そう・歯車など）", "page_range": (150, 157)},
        ]
    },
    {
        "id": "ch5",
        "name": "第5章 平面図形",
        "page_range": (158, 187),
        "topics": [
            {"id": "ch5_1", "name": "直線と角・基本作図（垂直二等分線・角の二等分線・垂線）", "page_range": (158, 170)},
            {"id": "ch5_2", "name": "円とおうぎ形（弧の長さと面積）", "page_range": (171, 187)},
        ]
    },
    {
        "id": "ch6",
        "name": "第6章 空間図形",
        "page_range": (188, 223),
        "topics": [
            {"id": "ch6_1", "name": "立体と位置関係（ねじれの位置）・展開図", "page_range": (188, 205)},
            {"id": "ch6_2", "name": "立体の表面積と体積・球", "page_range": (206, 223)},
        ]
    },
    {
        "id": "ch7",
        "name": "第7章 データの活用",
        "page_range": (224, 250),
        "topics": [
            {"id": "ch7_1", "name": "度数分布表・ヒストグラム・代表値（平均・中央・最頻値）", "page_range": (224, 250)},
        ]
    }
]

def parse_page_range(input_text: str):
    """
    ユーザーの入力（例: 'p.42〜43', 'p42-45', '42', '42-43'）から開始ページと終了ページを抽出
    """
    if not input_text:
        return None, None
    numbers = [int(n) for n in re.findall(r'\d+', input_text)]
    if not numbers:
        return None, None
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    return min(numbers[0], numbers[1]), max(numbers[0], numbers[1])

def detect_topics_from_pages(start_p: int, end_p: int):
    """
    ページ番号から該当する中1数学の単元・トピックをリストで返す
    """
    matched_topics = []
    for ch in CHAPTERS:
        for topic in ch["topics"]:
            t_start, t_end = topic["page_range"]
            # 範囲重複チェック
            if not (end_p < t_start or start_p > t_end):
                matched_topics.append({
                    "chapter_name": ch["name"],
                    "topic_id": topic["id"],
                    "topic_name": topic["name"]
                })
    
    # 範囲外（または該当なし）ならデフォルトで第1章〜第3章から補完
    if not matched_topics:
        matched_topics.append({
            "chapter_name": "第1章 正負の数",
            "topic_id": "ch1_3",
            "topic_name": "正負の乗法と除法・四則混合"
        })
    return matched_topics

def find_topic_by_keyword(unit_text: str) -> dict:
    """
    教科書画像やAIから解析された単元キーワード（例: '比例', '変域', '一次方程式', '空間図形' など）
    から最も合致する単元情報を返す
    """
    if not unit_text:
        return {
            "chapter_name": "第4章 比例と反比例",
            "topic_id": "ch4_1",
            "topic_name": "関数と変数・変域・比例の式"
        }

    t = str(unit_text).lower()

    # 1. 比例・反比例・変域・座標
    if any(k in t for k in ["比例", "反比例", "変域", "座標", "関数", "変数", "グラフ"]):
        if "反比例" in t:
            return {"chapter_name": "第4章 比例と反比例", "topic_id": "ch4_2", "topic_name": "反比例の式とグラフ"}
        elif "変域" in t or "変数" in t:
            return {"chapter_name": "第4章 比例と反比例", "topic_id": "ch4_1", "topic_name": "関数と変数・変域・比例の式"}
        elif "利用" in t or "水そう" in t or "歯車" in t:
            return {"chapter_name": "第4章 比例と反比例", "topic_id": "ch4_3", "topic_name": "比例・反比例の利用"}
        else:
            return {"chapter_name": "第4章 比例と反比例", "topic_id": "ch4_1", "topic_name": "関数と変数・変域・比例の式"}

    # 2. 1次方程式
    if any(k in t for k in ["方程式", "移項", "等式の性質", "一次方程式"]):
        if "文章題" in t or "利用" in t or "代金" in t:
            return {"chapter_name": "第3章 1次方程式", "topic_id": "ch3_3", "topic_name": "方程式の利用（代金・過不足・速さ）"}
        else:
            return {"chapter_name": "第3章 1次方程式", "topic_id": "ch3_1", "topic_name": "等式の性質と方程式の基本解き方"}

    # 3. 文字と式
    if any(k in t for k in ["文字", "代入", "式の値", "項", "係数"]):
        return {"chapter_name": "第2章 文字と式", "topic_id": "ch2_1", "topic_name": "文字式の表し方・式の値"}

    # 4. 平面図形
    if any(k in t for k in ["作図", "円", "おうぎ形", "弧", "垂線", "二等分線", "平面図形"]):
        return {"chapter_name": "第5章 平面図形", "topic_id": "ch5_2", "topic_name": "円とおうぎ形（弧の長さと面積）"}

    # 5. 空間図形
    if any(k in t for k in ["立体", "体積", "表面積", "ねじれ", "展開図", "空間図形", "角柱", "円柱"]):
        return {"chapter_name": "第6章 空間図形", "topic_id": "ch6_2", "topic_name": "立体の表面積と体積・球"}

    # 6. データの活用
    if any(k in t for k in ["データ", "度数", "ヒストグラム", "平均値", "中央値", "最頻値"]):
        return {"chapter_name": "第7章 データの活用", "topic_id": "ch7_1", "topic_name": "度数分布表・ヒストグラム・代表値"}

    # 7. 正負の数
    if any(k in t for k in ["正負", "負の数", "正の数", "絶対値", "加法", "減法", "乗法", "除法", "四則"]):
        return {"chapter_name": "第1章 正負の数", "topic_id": "ch1_3", "topic_name": "正負の乗法と除法・四則混合"}

    # デフォルト
    return {
        "chapter_name": "第4章 比例と反比例",
        "topic_id": "ch4_1",
        "topic_name": "関数と変数・変域・比例の式"
    }

def normalize_math_answer(ans_str: str) -> str:
    """
    生徒の入力した答えの文字列を正規化（全角半角、空白除去、x=3等のフォーマット対応）
    """
    if ans_str is None:
        return ""
    s = clean_math_text(str(ans_str).strip())
    # 全角数字・記号を半角に変換
    zenkaku = "０１２３４５６７８９＋－×÷＝／（）ｘＸｙＹａＡ"
    hankaku = "0123456789+-*/=//()xxya"
    table = str.maketrans(zenkaku, hankaku)
    s = s.translate(table)
    # スペース削除
    s = re.sub(r'\s+', '', s)
    # 小文字化
    s = s.lower()
    # 「度」や「cm」「cm2」「cm3」「人」「円」「個」「個数」などの単位を末尾から削除
    s = re.sub(r'(度|°|cm2|cm3|cm|m|km|円|個|人|本|枚|倍|π|pi)$', '', s)
    return s

def check_answer_match(user_ans: str, correct_ans: str, acceptable_variants=None) -> bool:
    """
    ユーザーの回答が正解と一致するか判定（同値判定・柔軟な表記揺れ対応）
    """
    u = normalize_math_answer(user_ans)
    c = normalize_math_answer(correct_ans)
    
    if u == c:
        return True
    
    # 'x=4' と '4' の一致判定
    for prefix in ["x=", "y=", "a="]:
        if u.startswith(prefix) and u[2:] == c:
            return True
        if c.startswith(prefix) and u == c[2:]:
            return True
        
    # 表記揺れの許容リストがある場合
    if acceptable_variants:
        for v in acceptable_variants:
            v_norm = normalize_math_answer(str(v))
            if u == v_norm:
                return True
            for prefix in ["x=", "y=", "a="]:
                if u.startswith(prefix) and u[2:] == v_norm:
                    return True
                if v_norm.startswith(prefix) and u == v_norm[2:]:
                    return True
                
    return False

# ==========================================
# 難易度別 中1数学問題生成ジェネレータ
# ==========================================
def generate_math_problem(topic_id: str, level: int = 1, force_type: str = None) -> dict:
    """
    単元IDとレベル（1〜5）、問題タイプ（'calc' or 'word'）に応じてアダプティブな問題を動的生成
    すべての出力は clean_math_text によりドルマーク・TeX記法が完全除去されたプレーンテキストになります。
    """
    if force_type in ["calc", "word"]:
        q_type = force_type
    else:
        if level <= 2:
            q_type = "calc" if random.random() < 0.75 else "word"
        else:
            q_type = "word" if random.random() < 0.6 else "calc"

    # 単元ごとの問題生成ディスパッチ
    if topic_id.startswith("ch1"):
        prob = _gen_ch1_problem(topic_id, level, q_type)
    elif topic_id.startswith("ch2"):
        prob = _gen_ch2_problem(topic_id, level, q_type)
    elif topic_id.startswith("ch3"):
        prob = _gen_ch3_problem(topic_id, level, q_type)
    elif topic_id.startswith("ch4"):
        prob = _gen_ch4_problem(topic_id, level, q_type)
    elif topic_id.startswith("ch5"):
        prob = _gen_ch5_problem(topic_id, level, q_type)
    elif topic_id.startswith("ch6"):
        prob = _gen_ch6_problem(topic_id, level, q_type)
    elif topic_id.startswith("ch7"):
        prob = _gen_ch7_problem(topic_id, level, q_type)
    else:
        prob = _gen_ch4_problem("ch4_1", level, q_type)

    # 最終クレンジング（絶対に$や$$が残らないように二重チェック）
    prob["question"] = clean_math_text(prob.get("question", ""))
    prob["answer"] = clean_math_text(prob.get("answer", ""))
    prob["explanation"] = clean_math_text(prob.get("explanation", ""))
    prob["topic_id"] = topic_id
    if "acceptable" in prob and prob["acceptable"]:
        prob["acceptable"] = [clean_math_text(x) for x in prob["acceptable"]]
    return prob

def _gen_ch1_problem(topic_id: str, level: int, q_type: str) -> dict:
    """正負の数の問題生成"""
    if q_type == "calc":
        if level == 1:
            a = random.choice([-8, -7, -6, -5, -4, -3, 3, 4, 5, 6, 7])
            b = random.choice([-9, -8, -6, -4, -3, 2, 5, 8])
            ans = a + b
            op_str = f"+ ({b})" if b < 0 else f"+ {b}"
            q_text = f"次の計算をしなさい。\n({a}) {op_str}"
            expl = f"【考え方】\n・同符号または異符号の足し算です。\n・({a}) + ({b}) = {ans} となります。"
            return {
                "type": "calc", "level": level, "topic_name": "正負の数（加法・減法）",
                "question": q_text, "answer": str(ans), "acceptable": [str(ans)], "explanation": expl
            }
        elif level == 2:
            a = random.choice([-9, -7, -5, -3, 4, 6, 8])
            b = random.choice([-8, -6, -4, -2, 3, 5, 7])
            ans = a - b
            q_text = f"次の計算をしなさい。\n({a}) - ({b})"
            expl = f"【考え方】\n・引き算は「引く数の符号を変えて足す」のが基本です。\n・({a}) - ({b}) = ({a}) + ({-b}) = {ans} となります。"
            return {
                "type": "calc", "level": level, "topic_name": "正負の数（減法）",
                "question": q_text, "answer": str(ans), "acceptable": [str(ans)], "explanation": expl
            }
        elif level == 3:
            a = random.choice([-6, -5, -4, -3, 3, 4, 5])
            b = random.choice([-7, -6, -4, -2, 2, 4, 6])
            ans = a * b
            q_text = f"次の計算をしなさい。\n({a}) × ({b})"
            expl = f"【考え方】\n・負の数の個数を数えます。\n・負の符号が2個（偶数）なら「+」、1個（奇数）なら「-」です。\n・答えは {ans} になります。"
            return {
                "type": "calc", "level": level, "topic_name": "正負の数（乗法・除法）",
                "question": q_text, "answer": str(ans), "acceptable": [str(ans)], "explanation": expl
            }
        elif level == 4:
            base = random.choice([-3, -2, 2, 3])
            c = random.choice([-12, -8, 8, 12, 16])
            ans = (base ** 2) + c
            q_text = f"次の計算をしなさい。\n({base})^2 + ({c})"
            expl = f"【考え方】\n・まず累乗を先に計算します: ({base})^2 = {base**2}\n・次に足し算を行います: {base**2} + ({c}) = {ans} です。"
            return {
                "type": "calc", "level": level, "topic_name": "正負の数（累乗と四則混合）",
                "question": q_text, "answer": str(ans), "acceptable": [str(ans)], "explanation": expl
            }
        else:
            q_text = f"次の計算をしなさい。\n(-4)^2 - 3 × (5 - 8)"
            ans = 25
            expl = f"【考え方（難関ステップ）】\n1. かっこの中を計算: 5 - 8 = -3\n2. 累乗を計算: (-4)^2 = 16\n3. かけ算を計算: 3 × (-3) = -9\n4. 引き算を実行: 16 - (-9) = 16 + 9 = 25 です！"
            return {
                "type": "calc", "level": level, "topic_name": "正負の数（難関四則混合）",
                "question": q_text, "answer": str(ans), "acceptable": [str(ans)], "explanation": expl
            }
    else:
        diff = random.choice([3, 4, 5, 6])
        ans = 25 + diff
        q_text = f"【文章題：ノートに解き方を書いて写真で提出してみよう！】\nある地点の今朝の気温は -3℃ でした。昼には今朝より {diff}℃ 高くなりました。昼の気温は何℃ですか？（単位なしの数値またはノートの写真で回答してください）"
        expl = f"【解き方とステップ】\n・求める昼の気温は、今朝の気温 -3℃ に上がった分 +{diff}℃ を足します。\n・式: (-3) + {diff} = {ans - 25}\n・答え: {ans - 25} (℃)"
        return {
            "type": "word", "level": level, "topic_name": "正負の数（気温の文章題）",
            "question": q_text, "answer": str(ans - 25), "acceptable": [str(ans - 25), f"{ans - 25}度", f"{ans - 25}℃"],
            "explanation": expl
        }

def _gen_ch2_problem(topic_id: str, level: int, q_type: str) -> dict:
    """文字と式の問題生成"""
    if q_type == "calc":
        if level <= 2:
            c1 = random.randint(2, 6)
            c2 = random.randint(2, 5)
            ans_c = c1 + c2
            q_text = f"次の式を簡単にしなさい。\n{c1}x + {c2}x"
            ans_str = f"{ans_c}x"
            expl = f"【考え方】\n・文字の部分が同じ項（同類項）は係数をまとめます。\n・({c1} + {c2})x = {ans_c}x です。"
            return {
                "type": "calc", "level": level, "topic_name": "文字と式（同類項の計算）",
                "question": q_text, "answer": ans_str, "acceptable": [ans_str, f"{ans_c}*x"], "explanation": expl
            }
        elif level == 3:
            a = random.choice([2, 3, 4])
            b = random.choice([-5, -4, -3, 3, 4])
            x_val = random.choice([-3, -2, 2, 3])
            ans = a * x_val + b
            q_text = f"x = {x_val} のとき、次の式の値を求めなさい。\n{a}x + ({b})"
            expl = f"【考え方】\n・x の場所に ({x_val}) を代入して計算します。\n・{a} × ({x_val}) + ({b}) = {a*x_val} + ({b}) = {ans} です。"
            return {
                "type": "calc", "level": level, "topic_name": "文字と式（式の値）",
                "question": q_text, "answer": str(ans), "acceptable": [str(ans)], "explanation": expl
            }
        else:
            q_text = f"次の計算をしなさい。\n3(2x - 4) - 2(x - 5)"
            ans_str = "4x-2"
            expl = f"【考え方】\n1. 分配法則でかっこを外す: 6x - 12 - 2x + 10\n2. 同類項をまとめる: (6-2)x + (-12+10) = 4x - 2 です。"
            return {
                "type": "calc", "level": level, "topic_name": "文字と式（かっこのある1次式）",
                "question": q_text, "answer": ans_str, "acceptable": [ans_str, "4x - 2", "-2+4x"], "explanation": expl
            }
    else:
        cost = random.choice([80, 100, 120])
        q_text = f"【文章題：ノートに立式を書いて写真で提出してみよう！】\n1個 {cost} 円のりんごを x 個買って 1000 円を出したときのおつりを、文字を使った式で表しなさい。"
        ans_str = f"1000-{cost}x"
        expl = f"【解き方とステップ】\n・りんご全体の代金は {cost} × x = {cost}x 円。\n・出したお金 1000 円から代金を引くので、式は 1000 - {cost}x （円）となります。"
        return {
            "type": "word", "level": level, "topic_name": "文字と式（代金とおつりの立式）",
            "question": q_text, "answer": ans_str, "acceptable": [ans_str, f"1000 - {cost}x", f"-{cost}x+1000"],
            "explanation": expl
        }

def _gen_ch3_problem(topic_id: str, level: int, q_type: str) -> dict:
    """1次方程式の問題生成"""
    if q_type == "calc":
        if level <= 2:
            ans_val = random.choice([-5, -4, -3, -2, 2, 3, 4, 5, 6])
            a = random.choice([2, 3, 4, 5])
            b = a * ans_val
            q_text = f"次の方程式を解きなさい。\n{a}x = {b}"
            expl = f"【考え方】\n・両辺を x の係数 {a} で割ります。\n・x = {b} / {a} = {ans_val} となります。"
            return {
                "type": "calc", "level": level, "topic_name": "1次方程式（基本形）",
                "question": q_text, "answer": str(ans_val), "acceptable": [str(ans_val), f"x={ans_val}"], "explanation": expl
            }
        elif level == 3:
            ans_val = random.choice([-4, -3, -2, 2, 3, 4, 5])
            a = random.choice([2, 3, 4, 5])
            b = random.choice([-7, -5, -3, 3, 5, 7])
            c = a * ans_val + b
            op_b = f"+ {b}" if b > 0 else f"- {abs(b)}"
            q_text = f"次の方程式を解きなさい。\n{a}x {op_b} = {c}"
            expl = f"【考え方】\n1. 定数項を右辺に移項します: {a}x = {c} - ({b}) = {a * ans_val}\n2. 両辺を {a} で割ります: x = {ans_val} です。"
            return {
                "type": "calc", "level": level, "topic_name": "1次方程式（移項）",
                "question": q_text, "answer": str(ans_val), "acceptable": [str(ans_val), f"x={ans_val}"], "explanation": expl
            }
        elif level == 4:
            ans_val = random.choice([3, 4, 5, 6])
            k = 2
            m = 2 * ans_val - 6
            q_text = f"次の方程式を解きなさい。\n3(x - {k}) = x + {m}"
            expl = f"【考え方】\n1. かっこを外す: 3x - 6 = x + {m}\n2. 移項して整理: 3x - x = {m} + 6 → 2x = {2 * ans_val}\n3. 答え: x = {ans_val} です！"
            return {
                "type": "calc", "level": level, "topic_name": "1次方程式（かっこを含む方程式）",
                "question": q_text, "answer": str(ans_val), "acceptable": [str(ans_val), f"x={ans_val}"], "explanation": expl
            }
        else:
            q_text = f"次の方程式を解きなさい。\n(x - 1) / 2 = (2x + 3) / 5"
            ans_val = 11
            expl = f"【解法ステップ】\n1. 分母の最小公倍数 10 を両辺にかける（分母を払う）：\n   5(x - 1) = 2(2x + 3)\n2. かっこを展開する：\n   5x - 5 = 4x + 6\n3. 移項して整理する：\n   5x - 4x = 6 + 5 → x = 11 です！"
            return {
                "type": "calc", "level": level, "topic_name": "1次方程式（分数・難関）",
                "question": q_text, "answer": str(ans_val), "acceptable": [str(ans_val), f"x={ans_val}"], "explanation": expl
            }
    else:
        apples = random.choice([3, 4, 5])
        apple_price = 120
        box = 150
        total = apples * apple_price + box
        q_text = f"【文章題：ノートに解き方のプロセスを書いて写真で提出してみよう！】\n1個 {apple_price} 円のりんごを何個かと、1箱 {box} 円の箱を買ったら、代金の合計が {total} 円になりました。りんごは何個買いましたか？（りんごの個数を x として立式したノートの写真、または答えの数値を入力してください）"
        ans_val = apples
        expl = f"【解き方とステップ】\n1. りんごの個数を x 個とする。\n2. 方程式を立てる: {apple_price}x + {box} = {total}\n3. 移項して解く: {apple_price}x = {total - box} → x = {ans_val}\n・答え: {ans_val} 個"
        return {
            "type": "word", "level": level, "topic_name": "1次方程式（代金の文章題）",
            "question": q_text, "answer": str(ans_val), "acceptable": [str(ans_val), f"{ans_val}個", f"x={ans_val}"],
            "explanation": expl
        }

def _gen_ch4_problem(topic_id: str, level: int, q_type: str) -> dict:
    """比例と反比例・変域の問題生成"""
    if level == 1:
        # 変域または比例の基本式
        a = random.choice([2, 3, 4, 5, -2, -3])
        x_val = random.choice([2, 3, 4])
        y_val = a * x_val
        q_text = f"y は x に比例し、x = {x_val} のとき y = {y_val} です。このとき比例定数 a を求めなさい。"
        expl = f"【考え方】\n・比例の式は y = ax です。\n・x = {x_val}, y = {y_val} を代入すると、{y_val} = a × {x_val} となります。\n・両辺を {x_val} で割ると、a = {a} です。"
        return {
            "type": "calc", "level": level, "topic_name": "比例と反比例（比例の式と比例定数）",
            "question": q_text, "answer": str(a), "acceptable": [str(a), f"a={a}"], "explanation": expl
        }
    elif level == 2:
        # 変域の問題
        a = random.choice([2, 3, 4])
        # y = ax で、x の変域が 1 <= x <= 4 のときの y の最大値
        max_x = 4
        max_y = a * max_x
        q_text = f"関数 y = {a}x について、x の変域が 1 ≦ x ≦ {max_x} のとき、y の最大値を求めなさい。"
        expl = f"【考え方】\n・比例 y = {a}x は x が増えると y も増えます。\n・x が最大のとき y も最大になるので、x = {max_x} を代入します。\n・y = {a} × {max_x} = {max_y} となります。"
        return {
            "type": "calc", "level": level, "topic_name": "比例と反比例（変域）",
            "question": q_text, "answer": str(max_y), "acceptable": [str(max_y), f"y={max_y}"], "explanation": expl
        }
    elif level == 3:
        # 比例の式を求める
        a = random.choice([2, 3, 5, -3, -4])
        x_in = 3
        y_in = a * x_in
        ans_expr = f"y={a}x"
        q_text = f"y は x に比例し、x = {x_in} のとき y = {y_in} です。y を x の式で表しなさい。"
        expl = f"【考え方】\n・比例の基本式は y = ax です。\n・代入して {y_in} = {x_in}a より a = {a}\n・したがって式は y = {a}x となります。"
        return {
            "type": "calc", "level": level, "topic_name": "比例と反比例（比例の式）",
            "question": q_text, "answer": ans_expr, "acceptable": [ans_expr, f"y = {a}x", f"{a}x"], "explanation": expl
        }
    elif level == 4:
        # 反比例の式と値
        a_inv = 24
        x1 = 4
        y1 = 6
        x2 = 8
        ans2 = 3
        q_text = f"【文章題：ノートにグラフや解き方を書いて写真提出してみよう！】\ny は x に反比例し、x = {x1} のとき y = {y1} です。x = {x2} のときの y の値を求めなさい。"
        expl = f"【考え方】\n1. 反比例の式は y = a/x （または xy = a）\n2. 比例定数 a = {x1} × {y1} = {a_inv}\n3. x = {x2} を代入すると: y = {a_inv} / {x2} = {ans2} です。"
        return {
            "type": "word", "level": level, "topic_name": "比例と反比例（反比例の式と値）",
            "question": q_text, "answer": str(ans2), "acceptable": [str(ans2), f"y={ans2}"], "explanation": expl
        }
    else: # level 5
        # 比例・反比例の文章題・歯車や水そう
        # 歯数 20 の歯車Aが毎秒 6 回転するとき、歯数 x の歯車Bは毎秒 y 回転する。
        # 歯数 30 の歯車Bの毎秒の回転数
        ans_rot = 4
        q_text = f"【文章題：ノートに立式・思考プロセスを書いて提出しよう！】\n歯数が 20 の歯車Aが毎秒 6 回転しています。これとかみ合っている歯数 30 の歯車Bは、毎秒何回転しますか？（単位なしの数値またはノートの写真で回答してください）"
        expl = f"【解き方とステップ】\n1. 2つの歯車がかみ合うとき、（歯数）×（回転数）は常に一定になります（反比例の関係）。\n2. 一定の値: 20 × 6 = 120\n3. 歯車Bの回転数を y とすると: 30 × y = 120 → y = 4 (回転) です！"
        return {
            "type": "word", "level": level, "topic_name": "比例と反比例（歯車の反比例文章題）",
            "question": q_text, "answer": str(ans_rot), "acceptable": [str(ans_rot), f"{ans_rot}回転", f"y={ans_rot}"], "explanation": expl
        }

def _gen_ch5_problem(topic_id: str, level: int, q_type: str) -> dict:
    """平面図形（円とおうぎ形・作図）"""
    r = random.choice([3, 4, 5, 6])
    ans_circ = 2 * r
    q_text = f"半径が {r} cm の円の円周の長さを求めなさい。（円周率は π を用い、例えば 6π の場合は「{ans_circ}pi」または「{ans_circ}π」と入力してください）"
    ans_str = f"{ans_circ}pi"
    expl = f"【公式と計算】\n・円周の長さの公式: l = 2πr\n・半径 r = {r} を代入: l = 2 × π × {r} = {ans_circ}π (cm) です。"
    return {
        "type": "calc", "level": level, "topic_name": "平面図形（円の円周）",
        "question": q_text, "answer": ans_str, "acceptable": [ans_str, f"{ans_circ}π", str(ans_circ)], "explanation": expl
    }

def _gen_ch6_problem(topic_id: str, level: int, q_type: str) -> dict:
    """空間図形（体積・表面積）"""
    s_base = random.choice([12, 15, 20])
    h = random.choice([4, 5, 6])
    ans_v = s_base * h
    q_text = f"底面積が {s_base} cm^2、高さが {h} cm の角柱の体積は何 cm^3 ですか？"
    expl = f"【公式と計算】\n・角柱の体積の公式: 体積 = 底面積 × 高さ\n・計算: {s_base} × {h} = {ans_v} (cm^3) です。"
    return {
        "type": "calc", "level": level, "topic_name": "空間図形（柱体の体積）",
        "question": q_text, "answer": str(ans_v), "acceptable": [str(ans_v), f"{ans_v}cm3"], "explanation": expl
    }

def _gen_ch7_problem(topic_id: str, level: int, q_type: str) -> dict:
    """データの活用（平均値・中央値・最頻値）"""
    ans_avg = 8
    q_text = f"5人の数学の小テストの点数が次の通りでした。\n点数: 4点, 6点, 8点, 10点, 12点\nこの5人の平均値を求めなさい。"
    expl = f"【計算方法】\n・合計: 4 + 6 + 8 + 10 + 12 = 40\n・平均: 40 / 5 = 8 (点) です。"
    return {
        "type": "calc", "level": level, "topic_name": "データの活用（平均値）",
        "question": q_text, "answer": str(ans_avg), "acceptable": [str(ans_avg), f"{ans_avg}点"], "explanation": expl
    }
