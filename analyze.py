import re

def analyze_resume_text(text):
      """Weighted rule-based resume reviewer. Returns score (0-100), good points, improvements."""
      lower = text.lower()
      words = text.split()
      word_count = len(words)

      score = 0
      good = []
      improve = []

      # --- Contact info (weight: 15 total) ---
      if re.search(r"[^\s@]+@[^\s@]+\.[^\s@]+", text):
          score += 5
          good.append("Email address found")
      else:
          improve.append("Add an email address")

      if re.search(r"(\+?\d[\d\s-]{8,}\d)", text):
          score += 5
          good.append("Phone number found")
      else:
          improve.append("Add a phone number")

      if "linkedin" in lower or "github" in lower:
          score += 5
          good.append("Online profile (LinkedIn/GitHub) included")
      else:
          improve.append("Add a LinkedIn or GitHub link")

      # --- Key sections, weighted (Experience & Skills matter most) ---
      section_weights = {"experience": 15, "education": 10, "skills": 15, "projects": 10}
      for section, weight in section_weights.items():
          if section in lower:
              score += weight
              good.append(f"Has a {section.capitalize()} section")
          else:
              improve.append(f"Add a {section.capitalize()} section (worth {weight} pts)")

      # --- Quantified achievements: reward DEPTH, not just presence (weight: 15) ---
      numbers = re.findall(r"\d+%|\d+\+|\b\d{2,}\b", text)
      if len(numbers) >= 5:
          score += 15
          good.append(f"Strong measurable impact ({len(numbers)} numbers/metrics)")
      elif len(numbers) >= 1:
          score += 7
          improve.append("Add more numbers to quantify impact (aim for 5+)")
      else:
          improve.append('Add measurable results (e.g. "cut load time by 30%")')

      # --- Action-verb variety (weight: 10) ---
      action_verbs = ["built", "led", "designed", "developed", "managed", "created",
                      "improved", "implemented", "launched", "optimized", "automated"]
      found = [v for v in action_verbs if v in lower]
      if len(found) >= 4:
          score += 10
          good.append(f"Good action-verb variety ({len(found)} used)")
      elif len(found) >= 1:
          score += 5
          improve.append("Use more varied action verbs (Built, Led, Optimized...)")
      else:
          improve.append('Start bullets with action verbs like "Built", "Led", "Designed"')

      # --- Length, graduated (weight: 5) ---
      if 350 <= word_count <= 700:
          score += 5
          good.append(f"Good length ({word_count} words)")
        
      if 350 <= word_count <= 700:
          score += 10
          good.append(f"Good length ({word_count} words)")

      # --- PENALTY: weak/filler phrases (negative points) ---
      weak_phrases = ["responsible for", "hardworking", "team player",
                      "duties included", "good communication", "go-getter"]
      found_weak = [p for p in weak_phrases if p in lower]
      if found_weak:
          score -= len(found_weak) * 3
          improve.append(f"Remove weak phrases: {', '.join(found_weak)} — use strong action verbs instead")

      # Keep score within 0-100
      score = max(0, min(100, score))

      return {
          "score": score,
          "good": good,
          "improve": improve,
      }