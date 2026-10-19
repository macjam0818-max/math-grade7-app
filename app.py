"""
app.py - 中学1年生向け数学学習補助Webアプリ『マスマスター1』
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os
import random

# 自作モジュールのインポート
from styles import CUSTOM_CSS
from curriculum import (
    CHAPTERS,
    parse_page_range,
    detect_topics_from_pages,
    check_answer_match,
    generate_math_problem
)
from ai_engine import MathAIEngine
from storage import (
    load_history,
    add_record,
    calculate_statistics,
    clear_history
)

# ページ基本設定
st.set_page_config(
    page_title="マスマスター1 🌿 中学1年生 数学AIラーニング",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSSの適用
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# セッション状態の初期化
if "current_view" not in st.session_state:
    st.session_state.current_view = "home"  # home, daily_prep, test_prep, quiz, parent
if "active_mode" not in st.session_state:
    st.session_state.active_mode = "日々の授業復習"
if "current_page_range" not in st.session_state:
    st.session_state.current_page_range = "p.42〜43"
if "current_topics" not in st.session_state:
    st.session_state.current_topics = []
if "current_level" not in st.session_state:
    st.session_state.current_level = 1
if "combo_streak" not in st.session_state:
    st.session_state.combo_streak = 0
if "current_problem" not in st.session_state:
    st.session_state.current_problem = None
if "problem_answered" not in st.session_state:
    st.session_state.problem_answered = False
if "last_eval_result" not in st.session_state:
    st.session_state.last_eval_result = None
if "textbook_summary" not in st.session_state:
    st.session_state.textbook_summary = None
if "gemini_api_key" not in st.session_state:
    secret_key = ""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            secret_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "") or secret_key

# AIエンジンの初期化
ai_engine = MathAIEngine(api_key=st.session_state.gemini_api_key)

# ==========================================
# サイドバーナビゲーション & 設定
# ==========================================
with st.sidebar:
    st.markdown("### 🌿 マスマスター1 メニュー")
    
    # モード切り替えボタン群
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🏠 ホーム", use_container_width=True):
            st.session_state.current_view = "home"
            st.rerun()
    with col_nav2:
        if st.button("👨‍👩‍👦 保護者モード", use_container_width=True):
            st.session_state.current_view = "parent"
            st.rerun()
            
    st.markdown("---")
    st.markdown("#### 📖 学習モード選択")
    if st.button("① 日々の授業復習", use_container_width=True):
        st.session_state.current_view = "daily_prep"
        st.rerun()
        
    if st.button("② テスト前総復習", use_container_width=True):
        st.session_state.current_view = "test_prep"
        st.rerun()

    st.markdown("---")
    st.markdown("#### ⚙️ AI・教科書設定")
    
    # Gemini APIキー設定
    api_key_input = st.text_input(
        "Gemini APIキー（任意）",
        value=st.session_state.gemini_api_key,
        type="password",
        help="Google AI Studioで取得したAPIキーを入力すると、教科書やノート写真の高度なマルチモーダル解析が有効になります。未入力でも内蔵AIエンジンで100%動きます！"
    )
    if api_key_input != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = api_key_input
        st.rerun()

    if ai_engine.is_gemini_active():
        st.success("✨ Gemini AI連携中（写真認識・高度添削が有効）")
    else:
        st.info("💡 内蔵スマートAIエンジン稼働中（APIキーなしでも全機能快適に動きます）")

    # 教科書出版社
    textbook_publisher = st.selectbox(
        "使用している教科書",
        ["東京書籍（新しい数学1）", "啓林館（未来へひろがる数学1）", "数研出版（中学校数学1）", "学校図書（中学校数学1）"]
    )
    
    # 連続学習記録
    hist = load_history()
    stats = calculate_statistics(hist)
    st.markdown("---")
    st.markdown("#### 🏆 あなたの学習ステータス")
    st.markdown(f"**累計クリア問題数:** {stats['total_questions']} 問")
    st.markdown(f"**平均正答率:** {stats['accuracy_rate']}%")
    st.markdown(f"**現在の最高到達レベル:** Lv.{stats['current_max_level']}")

# ==========================================
# ヘッダー共通バナー
# ==========================================
header_html = f"""
<div class="app-header">
    <div class="app-title-group">
        <h1>📐 マスマスター1 <span style="font-size: 1.1rem; font-weight: 500; opacity: 0.9;">中1数学AIラーニング</span></h1>
        <p>1問ずつ解いてステップアップ！日々の授業復習から定期テスト対策まで完全サポート</p>
    </div>
    <div>
        <span class="header-badge">🔥 連勝中: {st.session_state.combo_streak} 問連続</span>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)


# ==========================================
# 画面 1: ホーム画面
# ==========================================
if st.session_state.current_view == "home":
    st.markdown("### 🎯 今日は何を勉強する？ モードを選んでスタートしよう！")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="mode-card">
            <div>
                <span class="mode-badge">✏️ 日常学習</span>
                <div class="mode-title">① 日々の授業復習モード</div>
                <div class="mode-desc">
                    今日学校でやった教科書の「ページ数」を入力、または教科書ページの「写真」を撮るだけ！<br>
                    AIがその日の範囲から計算問題と文章問題を1問ずつピックアップして出題します。
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("① 授業復習を始める 🚀", key="btn_start_daily", use_container_width=True):
            st.session_state.current_view = "daily_prep"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="mode-card">
            <div>
                <span class="mode-badge">📝 定期テスト対策</span>
                <div class="mode-title">② テスト前総復習モード</div>
                <div class="mode-desc">
                    定期テストの試験範囲（例: p.10〜p.50 や指定単元）を入力！<br>
                    範囲全体の重要エッセンスを凝縮し、解けば解くほど難易度が自動で上がる総まとめ特訓に挑めます。
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("② テスト総復習を始める 🔥", key="btn_start_test", use_container_width=True):
            st.session_state.current_view = "test_prep"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    # クイック保護者リンク
    with st.container():
        st.markdown("""
        <div class="green-card" style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="card-title">👨‍👩‍👦 保護者の方へ：学習の進捗とつまずきアドバイス</div>
                <p style="margin: 0; color: #4A5568; font-size: 0.95rem;">
                    勉強した日、取り組んだ単元、平均正答率、到達レベル、そして家庭で役立つAIのアドバイスを確認できます。
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("保護者用ダッシュボードを見る 📊", key="btn_home_parent", use_container_width=True):
            st.session_state.current_view = "parent"
            st.rerun()


# ==========================================
# 画面 2: ① 日々の授業復習モード（準備画面）
# ==========================================
elif st.session_state.current_view == "daily_prep":
    st.markdown("### ✏️ ① 日々の授業復習モード")
    st.caption("今日の授業で習った教科書のページ番号、または教科書の写真をアップロードしてください。")

    col_input, col_info = st.columns([1.1, 0.9])
    
    with col_input:
        st.markdown('<div class="green-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📖 1. 授業のページ数を入力</div>', unsafe_allow_html=True)
        page_input = st.text_input(
            "教科書のページ番号",
            value=st.session_state.current_page_range,
            placeholder="例: p.42〜43、p42-45、または 42"
        )
        st.session_state.current_page_range = page_input
        
        # ページ解析
        sp, ep = parse_page_range(page_input)
        detected = detect_topics_from_pages(sp or 42, ep or 43)
        st.session_state.current_topics = detected
        
        st.markdown("<hr style='margin: 1.2rem 0;'>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">📷 2. その日の教科書ページ写真（任意）</div>', unsafe_allow_html=True)
        st.caption("教科書の写真をつけると、AIがそのページに載っている公式や例題に完全マッチした問題を作成します！")
        
        upload_tab1, upload_tab2 = st.tabs(["📁 画像ファイルを添付", "📸 カメラで今すぐ撮影"])
        uploaded_image = None
        with upload_tab1:
            file_up = st.file_uploader("教科書画像をアップロード", type=["jpg", "jpeg", "png", "webp"], key="tb_file")
            if file_up:
                uploaded_image = Image.open(file_up)
        with upload_tab2:
            camera_up = st.camera_input("教科書を撮影", key="tb_camera")
            if camera_up:
                uploaded_image = Image.open(camera_up)
                
        if uploaded_image:
            st.image(uploaded_image, caption="アップロードされた教科書ページ", width=300)
            with st.spinner("AIが教科書の内容をスキャン中..."):
                summary_data = ai_engine.analyze_textbook_image(uploaded_image, page_input)
                st.session_state.textbook_summary = summary_data
            st.success("✅ AIスキャン完了！この範囲の計算問題と文章題を作成しました。")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown('<div class="green-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🎯 該当する中1数学の単元</div>', unsafe_allow_html=True)
        
        if detected:
            for d in detected:
                st.markdown(f"**【{d['chapter_name']}】**")
                st.markdown(f"- 🌿 **{d['topic_name']}**")
        else:
            st.info("ページ番号を入力すると、自動で単元を判別します。")

        if st.session_state.textbook_summary:
            st.markdown("---")
            st.markdown("💡 **AI教科書スキャンのポイント:**")
            st.write(st.session_state.textbook_summary.get("summary", "ポイントを抽出しました"))

        st.markdown("---")
        st.markdown("#### ⚡ 出題スタイル")
        st.markdown("- **1問ずつテンポよく** 進みます。")
        st.markdown("- **計算問題**：テキスト入力でサクサク解答！")
        st.markdown("- **文章問題**：ノートに書いた立式や解き方を**写真でアップロード**して提出！")
        st.markdown("- 正解するほど**自動で難易度レベルアップ**！")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 この範囲の復習をスタートする！", type="primary", use_container_width=True):
            st.session_state.active_mode = "日々の授業復習"
            st.session_state.current_level = 1
            st.session_state.combo_streak = 0
            # 最初の問題を作成
            first_topic = detected[0]["topic_id"] if detected else "ch1_3"
            st.session_state.current_problem = generate_math_problem(first_topic, level=1, force_type="calc")
            st.session_state.problem_answered = False
            st.session_state.last_eval_result = None
            st.session_state.current_view = "quiz"
            st.rerun()
            
        if st.button("← ホームに戻る", use_container_width=True):
            st.session_state.current_view = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 画面 3: ② テスト前総復習モード（準備画面）
# ==========================================
elif st.session_state.current_view == "test_prep":
    st.markdown("### 📝 ② 定期テスト前総復習モード")
    st.caption("テスト範囲のページ、またはテストに出る単元を選んでください。範囲全体の総まとめ問題を出題します！")

    col_test1, col_test2 = st.columns([1, 1])
    
    with col_test1:
        st.markdown('<div class="green-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📌 テスト範囲の指定方法</div>', unsafe_allow_html=True)
        
        test_method = st.radio("指定方法を選択", ["ページ数で指定（例: p.10〜50）", "単元名の一覧からまとめて選択"])
        
        selected_topics_for_test = []
        test_page_range_str = "全範囲"
        
        if test_method == "ページ数で指定（例: p.10〜50）":
            test_page_input = st.text_input("テスト範囲のページ", value="p.10〜p.50")
            test_page_range_str = test_page_input
            sp, ep = parse_page_range(test_page_input)
            selected_topics_for_test = detect_topics_from_pages(sp or 10, ep or 50)
            st.markdown(f"**自動検出された単元数:** {len(selected_topics_for_test)} 単元")
        else:
            st.markdown("**復習したい単元にチェックを入れてください:**")
            ch_options = [ch["name"] for ch in CHAPTERS]
            chosen_chs = st.multiselect("対象章", ch_options, default=ch_options[:3])
            test_page_range_str = "、".join(chosen_chs) if chosen_chs else "選択単元"
            
            for ch in CHAPTERS:
                if ch["name"] in chosen_chs:
                    for t in ch["topics"]:
                        selected_topics_for_test.append({
                            "chapter_name": ch["name"],
                            "topic_id": t["id"],
                            "topic_name": t["name"]
                        })
        st.markdown('</div>', unsafe_allow_html=True)

    with col_test2:
        st.markdown('<div class="green-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🔥 テスト対策特訓の特長</div>', unsafe_allow_html=True)
        st.markdown("""
        - **基本から応用・入試レベルまで網羅**: レベル1の基本問題から始まり、全問正解を重ねるごとに配点・難易度が上昇！
        - **計算と文章題のバランス出題**: 方程式の利用や文章題も出題され、ノートに途中式を書いて写真提出することで部分点・思考力を鍛えます。
        - **エンドレス挑戦**: 納得がいくまで何問でも継続可能！自信がつくまでとことん鍛えられます。
        """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔥 テスト総復習特訓をスタート！", type="primary", use_container_width=True):
            st.session_state.active_mode = "テスト前総復習"
            st.session_state.current_page_range = test_page_range_str
            st.session_state.current_topics = selected_topics_for_test or [{"topic_id": "ch1_3", "chapter_name": "第1章 正負の数", "topic_name": "総合問題"}]
            st.session_state.current_level = 1
            st.session_state.combo_streak = 0
            
            # 最初の問題
            t_id = st.session_state.current_topics[0]["topic_id"]
            st.session_state.current_problem = generate_math_problem(t_id, level=1)
            st.session_state.problem_answered = False
            st.session_state.last_eval_result = None
            st.session_state.current_view = "quiz"
            st.rerun()

        if st.button("← ホームに戻る", key="btn_test_back", use_container_width=True):
            st.session_state.current_view = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 画面 4: 1問ずつ進む「アダプティブ（適応型）出題」
# ==========================================
elif st.session_state.current_view == "quiz":
    prob = st.session_state.current_problem
    if not prob:
        st.warning("問題が見つかりませんでした。もう一度設定してください。")
        if st.button("ホームに戻る"):
            st.session_state.current_view = "home"
            st.rerun()
        st.stop()

    level = prob.get("level", st.session_state.current_level)
    q_type = prob.get("type", "calc")
    topic_title = prob.get("topic_name", "中1数学")
    
    # レベルバーとステータス
    level_names = {
        1: "レベル 1: 基礎確認（1ステップ基本）",
        2: "レベル 2: 標準計算（基本の組み合わせ）",
        3: "レベル 3: 応用（小数・分数・初級文章題）",
        4: "レベル 4: 発展（四則混合・複雑な方程式・文章題）",
        5: "レベル 5: 難関突破（入試・思考力問題）"
    }
    level_label = level_names.get(level, f"レベル {level}: マスター挑戦")
    progress_val = min(100, level * 20)

    # 上部ステータスバー
    col_stat1, col_stat2 = st.columns([3, 1])
    with col_stat1:
        st.markdown(f"**現在の難易度:** `{level_label}`")
        st.markdown(f"""
        <div class="level-meter-container">
            <div class="level-meter-bar" style="width: {progress_val}%;"></div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f"<div style='text-align: right; font-weight: 800; font-size: 1.1rem; color: #2F855A;'>🔥 {st.session_state.combo_streak} 連勝中</div>", unsafe_allow_html=True)
        st.caption(f"モード: {st.session_state.active_mode}")

    # 問題表示ボックス
    type_badge = "🔢 計算問題" if q_type == "calc" else "📝 文章問題（ノート写真提出対応）"
    st.markdown(f"""
    <div class="question-box">
        <span class="question-level-badge">Lv.{level}</span>
        <span class="question-type-badge">{type_badge}</span>
        <span style="color: #718096; font-size: 0.88rem; margin-left: 0.5rem;">【{topic_title}】</span>
        <div class="question-text">{prob.get('question')}</div>
    </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------
    # 解答入力エリア（計算問題 vs 文章問題）
    # ------------------------------------------
    if not st.session_state.problem_answered:
        col_ans_main, col_ans_side = st.columns([1.1, 0.9])
        
        with col_ans_main:
            st.markdown('<div class="green-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">✍️ あなたの解答</div>', unsafe_allow_html=True)
            
            user_text_input = ""
            uploaded_note = None
            
            if q_type == "calc":
                user_text_input = st.text_input(
                    "答えを入力してください（例: -3, 4x, x=5 など）:",
                    key=f"calc_ans_input_{prob.get('question')[:10]}"
                )
            else:
                st.markdown("##### 📸 ノートに解いた途中式や図を写真で提出しよう！")
                st.caption("先生やAIが、あなたの考え方のプロセス（立式や途中式）を見てアドバイスします。")
                
                note_tab1, note_tab2 = st.tabs(["📁 ノートの写真をアップロード", "📸 カメラでノートを撮影"])
                with note_tab1:
                    f_note = st.file_uploader("ノート画像をアップロード", type=["jpg", "png", "jpeg", "webp"], key="note_file")
                    if f_note:
                        uploaded_note = Image.open(f_note)
                with note_tab2:
                    c_note = st.camera_input("ノートを直接撮影", key="note_cam")
                    if c_note:
                        uploaded_note = Image.open(c_note)

                if uploaded_note:
                    st.image(uploaded_note, caption="提出されたノート答案", width=320)
                
                user_text_input = st.text_input(
                    "（任意）立式メモや最終的な答えの数値:",
                    placeholder="例: x=4個、式は 120x+150=630 など",
                    key=f"word_ans_input_{prob.get('question')[:10]}"
                )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎯 回答を送信する！", type="primary", use_container_width=True):
                # 採点実行
                is_correct = False
                score = 0
                ai_feedback = ""
                recognized_ans = user_text_input
                
                if q_type == "calc":
                    if not user_text_input.strip():
                        st.error("答えを入力してください！")
                        st.stop()
                    is_correct = check_answer_match(user_text_input, prob.get("answer"), prob.get("acceptable"))
                    score = 100 if is_correct else 0
                    ai_feedback = "正解です！正確に計算できました。" if is_correct else "惜しい！符号や計算順序を確認してみましょう。"
                else:
                    # 文章題の場合
                    if uploaded_note:
                        with st.spinner("AIがノートの解き方・立式プロセスを丁寧に添削中..."):
                            eval_res = ai_engine.evaluate_notebook_answer(uploaded_note, prob, user_text_input)
                            is_correct = eval_res.get("is_correct", True) in [True, "partial"]
                            score = eval_res.get("score", 90)
                            ai_feedback = f"{eval_res.get('thought_process_eval', '')} {eval_res.get('advice', '')}"
                            recognized_ans = eval_res.get("recognized_answer", user_text_input)
                    else:
                        if not user_text_input.strip():
                            st.error("ノートの写真をアップロードするか、答えを入力してください！")
                            st.stop()
                        is_correct = check_answer_match(user_text_input, prob.get("answer"), prob.get("acceptable"))
                        score = 100 if is_correct else 0
                        ai_feedback = "文章題の立式・計算がしっかりできています！" if is_correct else "文章題の条件をもう一度整理してみましょう。"

                # 履歴に記録
                add_record(
                    mode=st.session_state.active_mode,
                    page_range=st.session_state.current_page_range,
                    topic_name=topic_title,
                    problem_type=q_type,
                    level=level,
                    is_correct=is_correct,
                    score=score,
                    user_answer=recognized_ans,
                    correct_answer=prob.get("answer"),
                    note_image_attached=(uploaded_note is not None),
                    ai_feedback=ai_feedback
                )

                # セッション更新
                st.session_state.problem_answered = True
                st.session_state.last_eval_result = {
                    "is_correct": is_correct,
                    "score": score,
                    "feedback": ai_feedback,
                    "user_answer": recognized_ans
                }
                
                if is_correct:
                    st.session_state.combo_streak += 1
                    # 正解なら難易度を自動アップ！（最大レベル5）
                    st.session_state.current_level = min(5, st.session_state.current_level + 1)
                else:
                    st.session_state.combo_streak = 0
                    # 間違えた場合は同じレベルで再挑戦か、レベルを1つ下げる
                    st.session_state.current_level = max(1, st.session_state.current_level - 1)

                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_ans_side:
            st.markdown('<div class="green-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">💡 ヒント・考え方</div>', unsafe_allow_html=True)
            st.markdown("""
            - 符号ミス（$+$ と $-$）に気をつけましょう！
            - かっこを外すときは、分配法則を忘れずに。
            - 文章問題は「何を $x$ にするか」を最初に決めるのがコツです。
            """)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("中断してホームに戻る", use_container_width=True):
                st.session_state.current_view = "home"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ------------------------------------------
    # 回答後の解説・フィードバック画面
    # ------------------------------------------
    else:
        eval_data = st.session_state.last_eval_result
        is_correct = eval_data.get("is_correct")
        
        if is_correct:
            st.balloons()
            st.markdown(f"""
            <div class="result-correct">
                <span>🎉 大正解！ Excellent! （得点: {eval_data.get('score')}点）</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-incorrect">
                <span>💪 おしい！ 次につながるステップです！（正解: {prob.get('answer')}）</span>
            </div>
            """, unsafe_allow_html=True)

        col_exp1, col_exp2 = st.columns([1.2, 0.8])
        
        with col_exp1:
            st.markdown(f"""
            <div class="explanation-box">
                <div class="explanation-title">📖 詳しい解説とステップ</div>
                <div>{prob.get('explanation')}</div>
                <hr style="margin: 1rem 0;">
                <div style="font-weight: 700; color: #2B6CB0; margin-bottom: 0.3rem;">🤖 AI先生からの思考プロセスフィードバック:</div>
                <div style="color: #2D3748; font-size: 0.95rem;">{eval_data.get('feedback')}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_exp2:
            st.markdown('<div class="green-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🚀 次のレベルへ挑戦！</div>', unsafe_allow_html=True)
            
            if is_correct:
                next_lvl = st.session_state.current_level
                st.markdown(f"🌟 正解につき難易度UP！ **次の問題は Lv.{next_lvl}** です！")
            else:
                st.markdown(f"🔄 復習完了！ 次は基礎を固める **Lv.{st.session_state.current_level}** の問題に挑戦しましょう！")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("👉 次の問題へ進む！（エンドレス挑戦）", type="primary", use_container_width=True):
                # 次の問題を生成
                target_topic = prob.get("topic_id", "ch1_3")
                if st.session_state.current_topics:
                    target_topic = random.choice(st.session_state.current_topics)["topic_id"]
                
                # 計算問題と文章題をバランスよく出題
                next_type = "word" if prob.get("type") == "calc" else "calc"
                st.session_state.current_problem = generate_math_problem(
                    topic_id=target_topic,
                    level=st.session_state.current_level,
                    force_type=next_type
                )
                st.session_state.problem_answered = False
                st.session_state.last_eval_result = None
                st.rerun()

            if st.button("🏁 今日の学習を終了する", use_container_width=True):
                st.session_state.current_view = "home"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)


# ==========================================
# 画面 5: 保護者用ダッシュボード（進捗共有機能）
# ==========================================
elif st.session_state.current_view == "parent":
    st.markdown("### 👨‍👩‍👦 保護者用ダッシュボード（進捗共有）")
    st.caption("お子様の学習の継続状況、得意・苦手単元、到達レベル、そして家庭でできるAIのアドバイスを確認できます。")

    hist = load_history()
    stats = calculate_statistics(hist)

    # 4大メトリクスカード
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-number">📅 {stats['study_days_count']} <span style="font-size: 1rem;">日</span></div>
            <div class="metric-label">勉強した日数</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-number">📝 {stats['total_questions']} <span style="font-size: 1rem;">問</span></div>
            <div class="metric-label">累計クリア問題数</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-number">🎯 {stats['accuracy_rate']} <span style="font-size: 1rem;">%</span></div>
            <div class="metric-label">平均正答率</div>
        </div>
        """, unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-number">🏆 Lv.{stats['current_max_level']}</div>
            <div class="metric-label">最高到達難易度</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # AIからのつまずきアドバイス＆家庭での声かけヒント
    st.markdown('<div class="advice-card">', unsafe_allow_html=True)
    st.markdown('<div class="advice-title">🤖 AI学習アドバイザーからの分析＆家庭での声かけヒント</div>', unsafe_allow_html=True)
    with st.spinner("AIが最新の学習ログからアドバイスをまとめています..."):
        parent_advice_text = ai_engine.generate_parent_advice(hist)
    st.markdown(parent_advice_text)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # グラフエリア（Plotlyでライトグリーン調に描画）
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.markdown('<div class="green-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 単元別の正答率</div>', unsafe_allow_html=True)
        if stats["topic_stats"]:
            df_topics = pd.DataFrame([
                {"単元名": k, "正答率(%)": v["rate"], "挑戦数": v["total"]}
                for k, v in stats["topic_stats"].items()
            ])
            fig_topic = px.bar(
                df_topics,
                x="正答率(%)",
                y="単元名",
                orientation='h',
                color="正答率(%)",
                color_continuous_scale=["#FEB2B2", "#9AE6B4", "#38A169"],
                range_x=[0, 100],
                text="正答率(%)"
            )
            fig_topic.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=260,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_topic, use_container_width=True)
        else:
            st.info("まだ単元のデータがありません。")
        st.markdown('</div>', unsafe_allow_html=True)

    with g_col2:
        st.markdown('<div class="green-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 日別の学習問数推移</div>', unsafe_allow_html=True)
        if stats["daily_stats"]:
            df_daily = pd.DataFrame([
                {"日付": k, "解いた問題数": v}
                for k, v in stats["daily_stats"].items()
            ])
            fig_daily = px.line(
                df_daily,
                x="日付",
                y="解いた問題数",
                markers=True,
                line_shape="linear"
            )
            fig_daily.update_traces(line_color="#38A169", marker=dict(size=9, color="#2F855A"))
            fig_daily.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=260
            )
            st.plotly_chart(fig_daily, use_container_width=True)
        else:
            st.info("まだ日別のデータがありません。")
        st.markdown('</div>', unsafe_allow_html=True)

    # 詳細な履歴テーブル
    st.markdown('<div class="green-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📋 最近の学習履歴一覧</div>', unsafe_allow_html=True)
    st.caption(f"直近で勉強したページ範囲: {stats['recent_pages']}")
    
    if hist:
        records_display = []
        for h in reversed(hist):
            records_display.append({
                "勉強した日時": h.get("timestamp"),
                "モード": h.get("mode"),
                "ページ範囲": h.get("page_range"),
                "単元": h.get("topic_name"),
                "種別": "計算" if h.get("problem_type") == "calc" else "文章題",
                "難易度": f"Lv.{h.get('level')}",
                "正否": "⭕ 正解" if h.get("is_correct") else "❌ 不正解",
                "ノート添付": "あり 📷" if h.get("note_image_attached") else "なし",
                "AIアドバイス": h.get("ai_feedback")
            })
        st.dataframe(pd.DataFrame(records_display), use_container_width=True, height=260)
    else:
        st.info("学習履歴はありません。")

    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    col_p_btn1, col_p_btn2 = st.columns(2)
    with col_p_btn1:
        if st.button("🏠 ホーム画面に戻る", use_container_width=True):
            st.session_state.current_view = "home"
            st.rerun()
    with col_p_btn2:
        if st.button("🗑️ 学習履歴をリセットする", use_container_width=True):
            clear_history()
            st.success("学習履歴をリセットしました。")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
