# Intersection Strategies: Production Landing Page

**Entity:** Intersection Strategies LLC
**Author:** James Bonaguro, Founder
**Repository Purpose:** Internal source code and deployment management for the primary consulting landing page.

## 🏗 Architecture & Tech Stack

This repository relies on a zero-dependency, static architecture optimized for speed, security, and absolute control. 

* **Structure:** Single-page application (`index.html`).
* **Styling:** Embedded CSS. 
    * *Typography:* Cormorant Garamond (Headings/Accents), DM Sans (Body text).
    * *Color Palette:* Strict dark mode variables (`--bg`, `--surface`, `--gold`, etc.) defined in the `:root`.
* **Interactivity:** Vanilla JavaScript utilizing the `IntersectionObserver` API for lightweight scroll animations (`.fade-up` class). No external libraries or heavy frameworks.
* **Hosting:** GitHub Pages.

## 🔄 Deployment Protocol

Updates to the live site are handled via standard git commits to the primary branch.

1. Modify `index.html` locally.
2. Commit changes: `git commit -m "update: [description of change]"`
3. Push to `main`: `git push origin main`
4. *GitHub Pages will automatically rebuild and deploy the live site within 1-2 minutes.*

## 📝 Maintenance & Update Guide (SOP)

As the client portfolio evolves, use this structure to swap out case studies while maintaining the grid integrity and animation sequence.

### 1. Adding/Updating a Case Study
Locate the relevant `<div class="category-header fade-up">` and insert/modify the `work-row` block below it. Maintain this exact HTML structure to preserve the CSS grid logic:

```html
<div class="work-row fade-up">
  <div class="work-industry">Industry<br>Specific Niche</div>
  <div class="work-body">
    <h3>Headline of the exact solution</h3>
    <p>Brief description of the operational bottleneck solved and the system built.</p>
  </div>
  <div class="work-stats">
    <div class="stat">
      <div class="stat-n">X<sup>%</sup></div>
      <div class="stat-d">hard metric description</div>


2. Updating the Primary Contact Link
The primary Call to Action currently uses a mailto: link. When a dedicated scheduling tool is implemented, update the href attribute in the bottom contact block:

Find:
<a href="mailto:james@intersectionstrategies.com" class="email-link">Book 15 Minutes Here →</a>

Replace with:
<a href="https://calendly.com/your-custom-link" class="email-link">Book 15 Minutes Here →</a>

🔒 Internal Notes
The scroll animation is triggered by the .fade-up class. If adding a completely new section (outside of .work-row), simply attach the fade-up class to the parent container to hook it into the global IntersectionObserver.


***

This gives you a permanent, structural reference for maintaining the site's architecture. 

Would you like me to draft a private `CLIENT_INTAKE.md` file to keep in this repos
    </div>
  </div>
</div>
