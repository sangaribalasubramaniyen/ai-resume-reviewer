import re

def analyze_resume_text(text):
      """Rule-based resume reviewer. Returns a score (0-100), good points, and improvements."""
      lower = text.lower()          # lowercase copy so our checks are case-insensitive
      words = text.split()          # split into words to count length
      word_count = len(words)

      score = 0
      good = []
      improve = []

      # --- 1. Email (10 pts) ---
      if re.search(r"[^\s@]+@[^\s@]+\.[^\s@]+", text):
          score += 10
          good.append("Email address found")
      else:
          improve.append("Add an email address so recruiters can contact you")

      # --- 2. Phone number (10 pts) ---
      # Looks for 10+ digits, allowing spaces, +, - between them
      if re.search(r"(\+?\d[\d\s-]{8,}\d)", text):
          score += 10
          good.append("Phone number found")
      else:
          improve.append("Add a phone number")

      # --- 3. LinkedIn (10 pts) ---
      if "linkedin" in lower:
          score += 10
          good.append("LinkedIn profile included")
      else:
          improve.append("Add your LinkedIn profile link")

      # --- 4. Length (15 pts) ---
      if 300 <= word_count <= 800:
          score += 15
          good.append(f"Good length ({word_count} words)")
      elif word_count < 300:
          improve.append(f"Resume is short ({word_count} words) — add more detail")
      else:
          improve.append(f"Resume is long ({word_count} words) — try to trim it")

      # --- 5. Important sections (10 pts each) ---
      sections = ["experience", "education", "skills", "projects"]
      for section in sections:
          if section in lower:
              score += 10
              good.append(f"Has a {section.capitalize()} section")
          else:
              improve.append(f"Add a {section.capitalize()} section")

      # --- 6. Measurable achievements (10 pts) ---
      # Numbers or % signs suggest quantified impact, e.g. "improved speed by 40%"
      if re.search(r"\d+%|\d+\+|\b\d{2,}\b", text):
          score += 10
          good.append("Includes measurable achievements (numbers)")
      else:
          improve.append('Add numbers to show impact (e.g. "reduced load time by 30%")')

      # --- 7. Action verbs (5 pts) ---
      action_verbs = ["built", "led", "designed", "developed", "managed",
                      "created", "improved", "implemented", "launched"]
      found_verbs = [v for v in action_verbs if v in lower]
      if len(found_verbs) >= 3:
          score += 5
          good.append("Strong action verbs used")
      else:
          improve.append('Start bullet points with action verbs like "Built", "Led", "Designed"')

      return {
          "score": score,
          "good": good,
          "improve": improve,
      }


if __name__ == "__main__":
      sample = "SANGARI B. Email: test@gmail.com. LinkedIn. Skills: Python. Education: BE. Built APIs improved speed by 40%."
      print(analyze_resume_text(sample))