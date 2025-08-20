import requests
import csv
import time

def fetch_problems(limit=50):
    url = "https://leetcode.com/graphql"
    query = """
    query problemsetQuestionList($categorySlug: String, $skip: Int, $limit: Int, $filters: QuestionListFilterInput) {
      problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        skip: $skip
        limit: $limit
        filters: $filters
      ) {
        total: totalNum
        questions: data {
          frontendQuestionId: questionFrontendId
          title
          titleSlug
          difficulty
        }
      }
    }
    """

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    all_problems = []
    skip = 0

    while True:
        variables = {"categorySlug": "", "skip": skip, "limit": limit, "filters": {}}
        resp = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        data = resp.json()

        if "errors" in data:
            print("❌ GraphQL Error:", data["errors"])
            break

        payload = data.get("data", {}).get("problemsetQuestionList")
        if not payload:
            break

        questions = payload.get("questions", [])
        if not questions:
            break

        for q in questions:
            all_problems.append({
                "id": int(q["frontendQuestionId"]),
                "title": q["title"],
                "url": f"https://leetcode.com/problems/{q['titleSlug']}/",
                "difficulty": q["difficulty"]
            })

        skip += limit
        print(f"Fetched {len(all_problems)} / {payload.get('total', '?')} problems so far...")
        time.sleep(0.5)

    return all_problems

def save_to_csv(problems, filename="leetcode_problems.csv"):
    problems.sort(key=lambda x: x["id"])
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "url", "difficulty"])
        writer.writeheader()
        for row in problems:
            writer.writerow(row)

if __name__ == "__main__":
    probs = fetch_problems(limit=50)
    save_to_csv(probs)
    print(f"Done! Saved {len(probs)} problems.")
