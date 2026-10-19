"""
styles.py - ライトグリーン（黄緑色）を基調とした中学生向けUIスタイル定義
"""

CUSTOM_CSS = """
<style>
/* フォント設定と基本リセット */
@import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;500;700;800;900&family=Nunito:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'M PLUS Rounded 1c', 'Nunito', 'Segoe UI', sans-serif;
    color: #2D3748;
}

/* メインコンテナの余白調整 */
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1000px;
}

/* ヘッダー・アプリバー */
.app-header {
    background: linear-gradient(135deg, #48BB78 0%, #38A169 50%, #2F855A 100%);
    color: white;
    padding: 1.6rem 2rem;
    border-radius: 18px;
    box-shadow: 0 10px 25px -5px rgba(72, 187, 120, 0.35);
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.app-title-group h1 {
    color: #FFFFFF !important;
    font-size: 1.85rem;
    font-weight: 800;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.12);
    letter-spacing: -0.02em;
}

.app-title-group p {
    color: #E6FFFA !important;
    font-size: 0.95rem;
    margin-top: 0.3rem;
    margin-bottom: 0;
    font-weight: 500;
}

.header-badge {
    background: rgba(255, 255, 255, 0.22);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.35);
    padding: 0.45rem 1rem;
    border-radius: 9999px;
    font-size: 0.88rem;
    font-weight: 700;
    color: #FFFFFF;
}

/* カード共通スタイル */
.green-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 1.5rem;
    border: 1.5px solid #E2E8F0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
    margin-bottom: 1.5rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.green-card:hover {
    box-shadow: 0 8px 25px rgba(72, 187, 120, 0.12);
    border-color: #9AE6B4;
}

.card-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #276749;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* モード選択カード（ホーム画面用） */
.mode-card {
    background: #FFFFFF;
    border-radius: 18px;
    padding: 1.6rem;
    border: 2px solid #E2E8F0;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
    cursor: pointer;
    transition: all 0.25s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.mode-card:hover {
    border-color: #48BB78;
    transform: translateY(-4px);
    box-shadow: 0 12px 28px rgba(72, 187, 120, 0.2);
}

.mode-badge {
    display: inline-block;
    background: #F0FFF4;
    color: #2F855A;
    font-weight: 700;
    padding: 0.3rem 0.8rem;
    border-radius: 8px;
    font-size: 0.85rem;
    border: 1px solid #C6F6D5;
    margin-bottom: 0.8rem;
}

.mode-title {
    font-size: 1.3rem;
    font-weight: 800;
    color: #22543D;
    margin-bottom: 0.5rem;
}

.mode-desc {
    font-size: 0.92rem;
    color: #4A5568;
    line-height: 1.55;
    margin-bottom: 1.2rem;
}

/* 問題ボックス（ライトグリーンアクセント） */
.question-box {
    background: linear-gradient(180deg, #F0FFF4 0%, #FFFFFF 100%);
    border: 2px solid #9AE6B4;
    border-radius: 16px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 12px rgba(72, 187, 120, 0.08);
}

.question-level-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #38A169;
    color: white;
    padding: 0.35rem 0.9rem;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 800;
    letter-spacing: 0.03em;
    margin-bottom: 1rem;
}

.question-type-badge {
    display: inline-block;
    background: #EDF2F7;
    color: #4A5568;
    padding: 0.35rem 0.8rem;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-left: 0.5rem;
    margin-bottom: 1rem;
}

.question-text {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1A202C;
    line-height: 1.65;
    margin-bottom: 1rem;
}

/* 解説ボックス */
.explanation-box {
    background: #FFFFFF;
    border-left: 5px solid #48BB78;
    border-radius: 8px 14px 14px 8px;
    padding: 1.2rem 1.5rem;
    margin-top: 1rem;
    box-shadow: 0 3px 10px rgba(0,0,0,0.04);
}

.explanation-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #276749;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* 成績・正解/不正解ハイライト */
.result-correct {
    background: #F0FFF4;
    border: 2px solid #48BB78;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: #22543D;
    font-weight: 800;
    font-size: 1.15rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
}

.result-incorrect {
    background: #FFF5F5;
    border: 2px solid #F56565;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: #9B2C2C;
    font-weight: 800;
    font-size: 1.15rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1rem;
}

/* ステータスバー・レベル表示 */
.level-meter-container {
    background: #EDF2F7;
    border-radius: 10px;
    height: 12px;
    overflow: hidden;
    margin: 0.6rem 0 1rem 0;
}

.level-meter-bar {
    background: linear-gradient(90deg, #68D391 0%, #38A169 100%);
    height: 100%;
    border-radius: 10px;
    transition: width 0.4s ease;
}

/* ボタンのスタイル統一（黄緑テーマ） */
.stButton > button {
    background: linear-gradient(135deg, #48BB78 0%, #38A169 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 12px rgba(72, 187, 120, 0.3) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(72, 187, 120, 0.45) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* 保護者ダッシュボードカード */
.metric-box {
    background: #F0FFF4;
    border: 1.5px solid #C6F6D5;
    border-radius: 14px;
    padding: 1.1rem;
    text-align: center;
}

.metric-number {
    font-size: 2rem;
    font-weight: 900;
    color: #22543D;
    line-height: 1.1;
}

.metric-label {
    font-size: 0.85rem;
    color: #4A5568;
    font-weight: 600;
    margin-top: 0.3rem;
}

/* アドバイスカード */
.advice-card {
    background: linear-gradient(135deg, #EBF8FF 0%, #F0FFF4 100%);
    border: 1.5px solid #BEE3F8;
    border-radius: 14px;
    padding: 1.3rem;
    margin-top: 1rem;
}

.advice-title {
    font-weight: 800;
    color: #2B6CB0;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ツールチップ・注記 */
.hint-text {
    font-size: 0.88rem;
    color: #718096;
    margin-top: 0.3rem;
}
</style>
"""
