"""
storage.py - 学習履歴データのローカル永続化（JSON）および統計処理
"""
import os
import json
from datetime import datetime

HISTORY_FILE = "learning_history.json"

DEFAULT_DEMO_DATA = [
    {
        "id": "demo-1",
        "timestamp": "2026-10-14 17:30",
        "date": "2026-10-14",
        "mode": "日々の授業復習",
        "page_range": "p.24〜28",
        "topic_name": "正負の加法と減法",
        "problem_type": "calc",
        "level": 1,
        "is_correct": True,
        "score": 100,
        "user_answer": "-4",
        "correct_answer": "-4",
        "note_image_attached": False,
        "ai_feedback": "符号の判定が完璧です！"
    },
    {
        "id": "demo-2",
        "timestamp": "2026-10-14 17:35",
        "date": "2026-10-14",
        "mode": "日々の授業復習",
        "page_range": "p.24〜28",
        "topic_name": "正負の加法と減法",
        "problem_type": "calc",
        "level": 2,
        "is_correct": True,
        "score": 100,
        "user_answer": "12",
        "correct_answer": "12",
        "note_image_attached": False,
        "ai_feedback": "引き算を足し算に変換して確実に解けました！"
    },
    {
        "id": "demo-3",
        "timestamp": "2026-10-15 18:10",
        "date": "2026-10-15",
        "mode": "日々の授業復習",
        "page_range": "p.39〜45",
        "topic_name": "正負の乗法と除法・四則混合",
        "problem_type": "calc",
        "level": 2,
        "is_correct": False,
        "score": 0,
        "user_answer": "-18",
        "correct_answer": "18",
        "note_image_attached": False,
        "ai_feedback": "マイナス×マイナスの符号ルールを再確認しましょう。"
    },
    {
        "id": "demo-4",
        "timestamp": "2026-10-15 18:15",
        "date": "2026-10-15",
        "mode": "日々の授業復習",
        "page_range": "p.39〜45",
        "topic_name": "正負の乗法と除法・四則混合",
        "problem_type": "word",
        "level": 3,
        "is_correct": True,
        "score": 95,
        "user_answer": "6",
        "correct_answer": "6",
        "note_image_attached": True,
        "ai_feedback": "ノートに丁寧な立式が書かれており素晴らしいです！"
    }
]

def load_history() -> list:
    """学習履歴を読み込む（存在しない場合は初期デモデータを生成）"""
    if not os.path.exists(HISTORY_FILE):
        save_history(DEFAULT_DEMO_DATA)
        return DEFAULT_DEMO_DATA.copy()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error loading history: {e}")
        return []

def save_history(history: list):
    """学習履歴をJSONファイルに保存"""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

def add_record(
    mode: str,
    page_range: str,
    topic_name: str,
    problem_type: str,
    level: int,
    is_correct: bool,
    score: int,
    user_answer: str,
    correct_answer: str,
    note_image_attached: bool = False,
    ai_feedback: str = ""
):
    """新しい学習記録を1件追加して保存"""
    history = load_history()
    now = datetime.now()
    record = {
        "id": f"rec-{int(now.timestamp() * 1000)}",
        "timestamp": now.strftime("%Y-%m-%d %H:%M"),
        "date": now.strftime("%Y-%m-%d"),
        "mode": mode,
        "page_range": page_range or "未指定",
        "topic_name": topic_name,
        "problem_type": problem_type,
        "level": level,
        "is_correct": bool(is_correct),
        "score": score,
        "user_answer": str(user_answer),
        "correct_answer": str(correct_answer),
        "note_image_attached": note_image_attached,
        "ai_feedback": ai_feedback
    }
    history.append(record)
    save_history(history)
    return record

def calculate_statistics(history: list) -> dict:
    """学習履歴から保護者用ダッシュボード向けの各種集計指標を計算"""
    if not history:
        return {
            "total_questions": 0,
            "correct_count": 0,
            "accuracy_rate": 0,
            "current_max_level": 1,
            "study_days_count": 0,
            "unique_dates": [],
            "recent_pages": "まだありません",
            "topic_stats": {},
            "daily_stats": {}
        }
    
    total_q = len(history)
    correct_q = sum(1 for h in history if h.get("is_correct"))
    accuracy = round((correct_q / total_q) * 100, 1) if total_q > 0 else 0
    max_level = max(h.get("level", 1) for h in history)
    
    # 勉強した日
    dates = sorted(list(set(h.get("date") for h in history if h.get("date"))))
    
    # 最近勉強したページ範囲
    recent_pages = [h.get("page_range") for h in reversed(history) if h.get("page_range") and h.get("page_range") != "未指定"]
    recent_pages_str = "、".join(list(dict.fromkeys(recent_pages))[:3]) if recent_pages else "全範囲"
    
    # 単元別正答率
    topic_stats = {}
    for h in history:
        t = h.get("topic_name", "その他")
        if t not in topic_stats:
            topic_stats[t] = {"total": 0, "correct": 0}
        topic_stats[t]["total"] += 1
        if h.get("is_correct"):
            topic_stats[t]["correct"] += 1
            
    for t, val in topic_stats.items():
        val["rate"] = round((val["correct"] / val["total"]) * 100, 1) if val["total"] > 0 else 0

    # 日別の解答数
    daily_stats = {}
    for h in history:
        d = h.get("date", "不明")
        daily_stats[d] = daily_stats.get(d, 0) + 1

    return {
        "total_questions": total_q,
        "correct_count": correct_q,
        "accuracy_rate": accuracy,
        "current_max_level": max_level,
        "study_days_count": len(dates),
        "unique_dates": dates,
        "recent_pages": recent_pages_str,
        "topic_stats": topic_stats,
        "daily_stats": daily_stats
    }

def clear_history():
    """学習履歴のリセット"""
    save_history([])
