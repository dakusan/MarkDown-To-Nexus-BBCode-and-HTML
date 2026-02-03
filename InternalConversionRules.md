# Internal BBCode Conversion Rules
These are the rules to convert the markdown to bbcode.
* Rule explanations are in the format: `Regular_Expression_Search` → `Regular_Expression_Replace`
	* Regular expressions may not match exactly how things are done during the conversion, but are equivalent. For example:
		* In-tag whitespace is often ignored
		* CAPGRP represents a capture group, which is generally `(.*)` but may actually be `([^>]+)` or other gobbling rules. Capture groups are used in replacements from left to right as `$1`, `$2`, etc.
		* HTML tag contents allows newlines
## The following rules are in order of processing:
1. **Change Windows newlines to Unix style**: `\r?\n` → `\n`
1. **Remove** `<div class=Delete>...</div>` **blocks** (Note: Do not put other `<div>`s inside)
1. **Convert nested lists**
	* List items must start at the very beginning of the line with no whitespace in front
	* List type support:
		* Must match the following format, followed by a space
		* Unordered
			* Single character: `*` `-` `+` 
			* Characters can be used interchangably on the same list
		* Ordered
			* Number followed by a period `\d+\.`
			* The actual number is ignored. List is always incrementally sequentially starting at 1
	* Unordered vs Ordered cannot mix on same level
	* Indention amounts for nested list levels must be the exact same for a list level. Each additional level must be 2-4 spaces or a tab.
	* Conversion notes: `[list]` will start at the beginning of the previous line. `[/list]` will start on its own line
1. **Centered short horizontal rule**: `^ ---$` → `[center][img=top]https://images.castledragmire.com/silksong/Line425.png[/img][/center]`
	* Centered 425*3px white line
	* See [Horizontal Lines](./README.md#user-content-horizontal-lines)
1. **Short horizontal rule**: `^---$` → `\n[img=top]https://images.castledragmire.com/silksong/Line425.png[/img]`
	* Same as above rule but not centered
1. **Full-width horizontal rule**: `^***$|<hr>` → `\n[img=top]https://images.castledragmire.com/silksong/Line1018.png[/img]`
	* 1018*3px white line
	* See [Horizontal Lines](./README.md#user-content-horizontal-lines)
1. **Blockquotes**: 
	* Collapse consecutive lines starting with `> ?` into one `[quote]$1[/quote]`, with each collapsed line on its own line
1. **Single newline instances collapse into a single line with a space separator**: `(?<!\n)\n(?!\n)` → ` `
	* If there is a tag before the newline, the space is omitted
1. **2+ newlines together become a single newline**: `\n{2,}` - > `\n`
1. **Center align tags**: `<center>CAPGRP</center>|<p.*?align=center>CAPGRP</p>` → `[center]$1\n[/center]`
	* Both `<center></center>` and `<p align=center></p>` supported
	* `[/center]` and `[/right]` always starts on a newline
	* [HTML conversion](#user-content-html-conversion) removes `<p></p>` tags for any paragraph with a `<center>` or `<right>` in it
1. **Right align tag**: `<p.*?align=right>CAPGRP</p>` → `[right]$1\n[/right]`
	* Same as above rule but right aligned instead of centered
1. **Hyperlink**: `<a.*?href="CAPGRP">CAPGRP</a>` → `[url=$1]$2[/url]`
1. **Font size/color**:
	* `<font.*?size="?CAPGRP"?>CAPGRP</font>` → `[size=$1]$2[/size]`
	* `<font.*?color="?CAPGRP"?>CAPGRP</font>` → `[color=$1]$2[/color]`
1. **Spoiler**: `<details><summary>Spoiler</summary>CAPGRP</details>` → `[spoiler]$1[/spoiler]`
1. **Font emphasis HTML tags: Underline/Italics/Bold/Strikethrough**:
	|Name          | HTML Tag         | BB Code Tag |
	|--------------|------------------|-------------|
	| Bold         | **strong**, **b**| **b**       |
	| Italics      | **em**, **i**    | **i**       |
	| Underline    | **ins**, **u**   | **u**       |
	| Strikethrough| **del**, **s**   | **s**       |
1. **Remove spaces before line break**: ` +<br>` → `<br>`
	These line breaks are not collapsed
1. **Images**:
	* `<img src="CAPGRP" align="CAPGRP">` → `[img=$2]$1[/img]`
		* HTML attributes can be in any order. `src` is required. If `align` is left out, the bbcode tag will just be `[img]`
	* `!\[CAPGRP]\(CAPGRP\)` → `[img=$2]$1[/img]`
1. **Markdown Link**: `\[CAPGRP]\(CAPGRP\)` → `[url=$2]$1[/url]`
1. **Font emphasis markdown tags: Underline/Italics/Bold/Strikethrough**:
	|Name          | MD Tag             | BB Code Tag |
	|--------------|--------------------|-------------|
	| Bold+Italics | **\*\*\***         | **[b][i]**  |
	| Bold         | **\*\***, **\_\_** | **[b]**     |
	| Italics      | **\***, **\_**     | **[i]**     |
	| Strikethrough| **\~\~**           | **[s]**     |
1. <ins>Extra rules for render matching</ins>
	1. **Remove a newline after block level elements**: `(\[/(?:list|center|right|spoiler|quote)\])\n` → `\1`
	1. **For double spaces, every other space becomes NBSP**: `  ` → ` \u00A0`
	1. **Unescape emphasis markdown tags**: `\\([*_])` → `$1`
	1. **Add newline back between list and first item**: `\[/list]\[\*]` → `[/list]\n[*]"`
	1. **Remove empty meta tags and following soft newlines**: `<meta/>\n*` → <code></code>
		* See [Forcing Markdown Rendering After HTML](./README.md#user-content-forcing-markdown-rendering-after-html)
	1. **Change `<br>` to newline**: `<br>` → `\n`
	1. **Strip spaces from beginning of file**
	1. **Other raw HTML is kept as-is**

# Internal HTML Conversion Rules
`MdToHtml.sh` process (in order):
* The 1 passed parameter is used as the HTML title inside `<title>...</title>`
* `#___markdown-content___`’s in css rules are changed to `body` (`body body` collapsed)
* `^ ?---` is changed to `<hr class=small>` (See [Horizontal Lines](./README.md#user-content-horizontal-lines))
* `pandoc -f gfm+raw_html+strikeout -t html` is ran
* The following is added around the contents
	* `pandoc` also has a `--standalone` flag that can be used instead, but I didn’t like its css rules.
```html
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>$TITLE</title>
<style>
body ul, body p { margin-top:0; }
html body ul, html body ol { margin-bottom:15px; padding-left:1.7em; }
html body ul ul, html body ul ol, html body ol ul, html body ol ol { margin-bottom:0; }
body hr { margin-top:0; background-color:#d8dee4; border-color:#d8dee4; }
hr.small { height:1px; border:0; margin:0 0 1em 0; }
body br.Hide { display:initial; }
</style>
<body>
...
</body>
</html>
```
* `<p></p>` tags for any paragraph with a `<center>` or `<right>` in it are removed