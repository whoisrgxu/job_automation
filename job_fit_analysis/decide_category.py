from typing import Literal, TypedDict

class FitScores(TypedDict):
    sde_fit: int
    cloud_support_fit: int
    sharepoint_support_fit: int
    application_support_fit: int

Category = Literal["sde", "cloud_support", "sharepoint_support", "application_support", "skip"]

def decide_category(scores: FitScores) -> Category:
    sde = scores["sde_fit"]
    cloud = scores["cloud_support_fit"]
    sp = scores["sharepoint_support_fit"]
    app = scores["application_support_fit"]

    # 1. 先按你的优先级+阈值
    if sde >= 82:
        return "sde"
    if cloud >= 75:
        return "cloud_support"
    if sp >= 70:
        return "sharepoint_support"
    if app >= 75:
        return "application_support"

    # 2. 都没达标 -> 看最高分
    best_cat = max(scores, key=scores.get)
    best_score = scores[best_cat]

    if best_score < 71:
        return "skip"

    mapping = {
        "sde_fit": "sde",
        "cloud_support_fit": "cloud_support",
        "sharepoint_support_fit": "sharepoint_support",
        "application_support_fit": "application_support",
    }
    return mapping[best_cat]
