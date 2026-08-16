# AI-Ready Banking: White Paper Series

Short, practical papers on putting AI inside a regulated bank: the data, the delivery, and the rules.

Published for free on GitHub Pages. No paywalls, no gated content.

## Series

| No. | Title | Status |
|-----|-------|--------|
| 01 | Core Pillars of AI-Ready Banking | Published |
| 02 | The Strategic Benefits of REST APIs in Open Banking | Published |
| 03 | Future of Banking: Open Banking | Published |

## Structure

```
index.html                            landing page
assets/
  site.css                            design system (tokens, type, components)
  fonts.css                           self-hosted Newsreader @font-face
  fonts/                              Newsreader variable TTFs + woff2 + static instances
white-papers/
  core-pillars-of-ai-ready-banking.html   print-ready source of paper 01
  core-pillars-of-ai-ready-banking.pdf    paper 01 as PDF
_build_pdf.py                       PDF typesetter (pure Python, no browser)
```

## How the PDF is generated

The HTML file is the single source of truth. `_build_pdf.py` parses it
(html.parser), typesets it with fpdf2, and embeds Newsreader static instances
made with fontTools (from the variable TTFs in `assets/fonts/`). Fully offline,
free, and browser-free:

```
pip install fpdf2 fonttools brotli
python _build_pdf.py
```

## Site

The site is served from the `main` branch by GitHub Pages at:

https://vinod-valiya.github.io/ai-ready-banking/