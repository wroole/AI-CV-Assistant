from app.processing.resume_features import count_bullets
import re


def calculate_basic_score(text: str) -> dict:
    if not text or not text.strip():
        return {"total_score": 0, "details": {"reason": "Empty text"}}

    text_lower = text.lower()

    key_sections = ["experience", "education", "skills", "projects", "certifications"]
    sections_found = sum(1 for section in key_sections if section in text_lower)
    sections_score = min(sections_found * 20, 100)

    bullet_points = count_bullets(text)
    bullet_score = min(bullet_points * 2, 40)

    achievement_pattern = r"\d+%|\$\d+|\b\d+\s*(?:years?|months?|%|percent)\b"
    achievements = len(re.findall(achievement_pattern, text))
    achievement_score = min(achievements * 5, 30)

    raw_score = sections_score + bullet_score + achievement_score
    total_score = min(int(raw_score), 100)

    return {
        "total_score": total_score,
        "details": {
            "sections_score": sections_score,
            "bullet_score": bullet_score,
            "achievement_score": achievement_score,
            "sections_found": sections_found,
            "bullet_points_found": bullet_points,
            "achievements_found": achievements,
        },
    }
