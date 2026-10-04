def assign_importance_score(msg):
    content = msg["content"].lower()
    score = 0

    if len(content) > 200:
        score += 2

    if any(word in content for word in ["emocje", "cierpienie", "tragedia", "walka", "misja", "cel"]):
        score += 3

    if any(word in content for word in ["decyzja", "odpowiedzialność", "zaufanie", "prawda", "przysięga"]):
        score += 2

    if "opowieść" in content or "historia" in content:
        score += 1

    return score
