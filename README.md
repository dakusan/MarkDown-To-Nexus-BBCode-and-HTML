# [Visual Studio] Markdown to Nexus Mods BBCode and HTML

Convert a **restricted, “works-for-me” subset** of Markdown + a few HTML tags into:

- **Nexus Mods BBCode** via `MdToNexusBBCode.py`
- **Standalone HTML** via `MdToHtml.sh` (uses `pandoc`)

> [!IMPORTANT]
> This project is intentionally narrow: it only implements the conversions needed for the author’s workflow.
>
> See [Supported Conversions](#user-content-supported-conversions) and [Limitations / Gotchas](#user-content-limitations--gotchas) before assuming it’s a general Markdown converter.
>
> If anyone needs support for more markdowns added, let me know.

1. [Repo Layout](#user-content-repo-layout)
1. [Quick Start](#user-content-quick-start)
1. [Supported Conversions](#user-content-supported-conversions)
1. [Rendering Suggestions/Notes](#user-content-rendering-suggestionsnotes)
1. [Limitations / Gotchas](#user-content-limitations--gotchas)
1. [Examples](#user-content-examples)
1. [Internal Conversion Rules (Separate file)](./InternalConversionRules.md)

## Repo Layout

- `MdToNexusBBCode.py` — Markdown/HTML → [Nexus](https://www.nexusmods.com) BBCode
- `MdToHtml.sh` — Markdown → HTML using `pandoc`, with some pre and post processing
- `RecommendedCSS.css` — CSS to make HTML output look closer to Nexus
- `Examples/SilkDev.AboutMe.*` — example input/output files

## Quick Start

### BBCode conversion

**Requirements**: Python **3.x** (tested via `python3`)

```bash
cat IN_FILE.md | python3 MdToNexusBBCode.py > OUT_FILE.bbcode
```

### HTML conversion

**Requirements**: `pandoc` available on PATH (Uses: `pandoc -f gfm+raw_html+strikeout -t html`)

```bash
cat IN_FILE.md | ./MdToHtml.sh "PAGE_TITLE" > OUT_FILE.html
```

## Supported Conversions

### HTML input handling (BBCode path)

Unless specified below, HTML elements are left alone.

- **Removed**
  - `<div class=Delete>...</div>` blocks
- **Alignment**
  - `<center>...</center>`
  - `<p align=center>...</p>`
  - `<p align=right>...</p>`
- **Font styles**
  - `<font size=...>...</font>` → `[size=...]...[/size]`
  - `<font color=...>...</font>` → `[color=...]...[/color]`
  - `<details><summary>Spoiler</summary>...</details>` → `[spoiler]...[/spoiler]`
  - `<strong>`/`<b>`, `<em>`/`<i>`, `<ins>`/`<u>`, `<del>`/`<s>`
- **Other**
  - `<hr>` (special-cased; see [Horizontal Lines](#user-content-horizontal-lines))
  - `<a href="...">text</a>`
  - `<br>`
  - `<img src="..." align="...">`
  - `<meta/>` — See [Forcing Markdown Rendering After HTML](#user-content-forcing-markdown-rendering-after-html)

### Markdown input handling (BBCode path)
- Nested lists (unordered: `* - +`, ordered: `1.`)
- Horizontal rules: ` ---`, `---`, ` ***`, `***` (See [Horizontal Lines](#user-content-horizontal-lines))
- Multiline quotes: consecutive `> ...` → single `[quote]...[/quote]`
- Images: `![alt](url)`
- Links: `[text](url)`
- Emphasis: `***`, `**`, `__`, `*`, `_`, `~~`


## Rendering Suggestions/Notes

### Recommended CSS (HTML output)
To make HTML (in both Visual Studio and HTML output) resemble Nexus Mods, embed the contents of `RecommendedCSS.css` near the top of your Markdown file. Comments can be removed.

Because GitHub renders `<style>` blocks as plain text inside Markdown, the workflow relies on a wrapper that is hidden on GitHub and stripped during BBCode conversion.

### Delete blocks
To hide content on GitHub **and** remove it during BBCode conversion, wrap it as:

```html
<div class=Delete>
  <details><summary></summary>
      <!-- <style>CSS</style> or other HTML -->
  </details>
</div>
```

Notes:
- Entire `<div class=Delete>` regions are removed during BBCode conversion.
- Do not nest other `<div>` blocks inside a Delete block.

#### Top-of-file Delete block
It is recommended to use the following HTML block for the [css section](#user-content-recommended-css-html-output) at the top. The comments in the [css file](./RecommendedCSS.css) explain this too.

```html
<div class=Delete>NOTE: HTML rendered via /Compile/MdToHtml.sh with pandoc and .md is viewable in Microsoft Visual Studio. This will not look correct on Github.<details><summary></summary><style>
	CSS_CONTENTS
</style></details></div>
```

### Alignment
`<center>` / `<right>` content should be kept to a single logical line. Multiline alignment can render inconsistently.

Newline font/height sizes in visual studio are sometimes improperly influenced by the following line. In this case you may want to add extra `<br class=Hide>` after the newline to match vertical spacing in other renderers.

To best horizontally align text in Nexus Mods I recommend combining normal sized spaces and a few extra spaces between `<font size=1>··</font>` for finer control.
<br>To facilitate this, the BBcode conversion will automatically replace all instances of 2 spaces with a space and an NBSP character.
<br>For horizontal aligning in the MarkDown/HTML, you can add css padding styles to an HTML element.

### Horizontal lines
`---` immediately following an HTML line in both Visual Studio and Github render a 1px high vertical line.
Nexus `<hr>` elements also have large margins. This project standardizes rules by mapping them to line images for BBCode.

| Tag    | Visual Studio/GitHub | BBCode                                                                                                             | HTML               | Best for                                                                    |
|--------|----------------------|--------------------------------------------------------------------------------------------------------------------|--------------------|--------------------------------------------------                           |
| `---`  | 1px border-bottom    | <code>\n[img=top][Line425.png](https://static.castledragmire.com/silksong/Line425.png)[/img]</code>                | `<hr class=small>` | Left aligned text to underline                                              |
| ` ---` | 1px border-bottom    | <code>[center][img=top][Line425.png](https://static.castledragmire.com/silksong/Line425.png)[/img][/center]</code> | `<hr class=small>` | Center aligned text to underline                                            |
| `***`  | `<hr>`               | <code>\n[img=top][Line1018.png](https://static.castledragmire.com/silksong/Line1018.png)[/img]</code>              | `<hr>`             | Full width line for [Nexus Mods](https://www.nexusmods.com) Mod description |
| ` ***` | `<hr>`               | <code>\n[img=top][Line1230.png](https://static.castledragmire.com/silksong/Line1230.png)[/img]</code>              | `<hr>`             | Full width line for [Nexus Mods](https://www.nexusmods.com) Mod articles    |

`Line###.png` are 3px height white lines with width matching their filename. They are located at `https://static.castledragmire.com/silksong/`. Their values work well on Nexus Mods (which squishes images that are too long) as partial and full line `<hr>`s.

### Forcing Markdown Rendering After HTML
I have found that adding a `<meta/>` tag between HTML and markdown can help force markdown to render. Soft newlines (not `<br>`s) after these meta tags are also removed.

## Limitations / Gotchas
- Not a general Markdown parser; edge cases exist.
- Ordered lists always emit `[list=1]` regardless of source numbering.
- Mixed ordered/unordered lists at the same nesting level are normalized.
- Delete blocks must not contain nested `<div>` elements.

### Security / trust assumptions
- Input Markdown/HTML is assumed to be **trusted**.
- BBCode conversion is not a general-purpose HTML sanitizer.
- HTML conversion enables `raw_html` in pandoc; raw HTML is preserved verbatim.

Do not use this toolchain on untrusted user content without a separate sanitization step.

## Examples

- `SilkDev.AboutMe.md` — input Markdown
- `SilkDev.AboutMe.bbcode` — BBCode output
- `SilkDev.AboutMe.html` — HTML output