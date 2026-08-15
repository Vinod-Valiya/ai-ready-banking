# AI-Ready Banking: White Paper Series

Short, practical papers on putting AI inside a regulated bank: the data, the delivery, and the rules.

Published for free on GitHub Pages. No paywalls, no gated content.

## Series

| No. | Title | Status |
|-----|-------|--------|
| 01 | Core Pillars of AI-Ready Banking | Published |

## Structure

```
index.html                  landing page
white-papers/
  core-pillars-of-ai-ready-banking.html   print-ready source of paper 01
  core-pillars-of-ai-ready-banking.pdf    paper 01 as PDF
```

## How the PDF is generated

The HTML file is print-styled (A4, cover page, page numbers). To rebuild the PDF locally, free tools only:

```
chrome --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=white-papers/core-pillars-of-ai-ready-banking.pdf \
  file:///path/to/white-papers/core-pillars-of-ai-ready-banking.html
```

## Site

The site is served from the `main` branch by GitHub Pages at:

https://vinod-valiya.github.io/ai-ready-banking/