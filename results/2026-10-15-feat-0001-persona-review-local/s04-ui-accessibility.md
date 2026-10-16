# S4: Quick picks on the borrow form (local, headless)

- **Pinned:** feat/0001-persona-review (f6f14ff)
- **Model:** Claude Code default
- **Exit code:** 0
- **Seconds:** 40
- **Files written in the testbed:** none

Check against scenarios/s04-ui-accessibility/expect.md, skipping (CI) items.

---

<!-- review-personas -->
## 🧩 Persona review: 3.5/10 (advisory)

| Persona | Score | Summary |
|---|---|---|
| 🧑‍💻 App developer | 4 | The new quick picks are clickable divs that a keyboard can't reach, the input has lost its label, and errors are no longer announced to screen readers. |
| ☁️ AWS architect | – | Not relevant |
| 🗄️ DBA | – | Not relevant |
| 🎨 UI developer | 3 | The quick picks can't be reached by keyboard, and the input has lost its label, hint and alert semantics, so this is a significant accessibility regression. |
| 🔌 API contract | – | Not relevant |

**🧑‍💻 App developer**
- 🔴 `web/src/components/BorrowForm.tsx:36` Use &lt;button type="button" aria-pressed={d === days}&gt; instead of a clickable div so keyboard and screen-reader users can select quick picks.
- 🔴 `web/src/components/BorrowForm.tsx:45` Restore the &lt;label htmlFor&gt; and input id, plus the aria-describedby hint about the 60-day limit and late fees. A placeholder can't stand in for a…
- 🟠 `web/src/components/BorrowForm.tsx:53` Restore role="alert" on the error paragraph so errors are announced, and add tests for quick-pick selection and error rendering.

**🎨 UI developer**
- 🔴 `web/src/components/BorrowForm.tsx:36` Use &lt;button type="button" aria-pressed&gt; (or radio inputs) instead of a clickable div so the picks are focusable, keyboard-operable and announced.
- 🔴 `web/src/components/BorrowForm.tsx:45` Restore the &lt;label htmlFor="borrow-days"&gt;, the input id, the aria-describedby hint and role="alert" on the error. The placeholder is not a label.
- 🟠 `web/src/styles.css:78` Text color \#b0b7bf on \#f6f8fa fails WCAG AA contrast. Use var(--muted) or something darker, and add a focus-visible style.

<sub>Reviewed branch scenario/s04-ui-accessibility vs main, including uncommitted changes.</sub>

Want me to fix these accessibility findings in `BorrowForm.tsx` and `styles.css`?
