#Do the actual conversions
import re
from typing import List
from MdList import convert_lists

HR_FULL ="[img=top]https://images.castledragmire.com/silksong/Line1018.png[/img]"
HR_SHORT="[img=top]https://images.castledragmire.com/silksong/Line425.png[/img]"

def parse_attrs(attrs: str) -> dict:
	out={}
	for m in re.finditer(r"""(?is)\b([a-zA-Z_][-\w]*)\b\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""", attrs):
		val=m.group(2) or m.group(3) or m.group(4)
		out[m.group(1).lower()]=True if val is None else val
	return out

def image_tag_replace(m: re.Match) -> str:
	attrs=parse_attrs(m.group("attrs") or "")
	url=attrs.get("src")
	align=attrs.get("align")
	return (
		 	 "" if not isinstance(url, str) or not url
		else f"[img={align}]{url}[/img]" if isinstance(align, str) and align
		else f"[img]{url}[/img]"
	)

def convert(s: str) -> str:
	s=re.sub(r"\r\n?", "\n", s)																#Remove windows newlines
	s=re.sub(r"(?is)(?:\n|^)<div\b[^>]*class=['\"]?Delete[^>]*>.*?</div>(?:\n|$)", "", s)	#Remove <div class=Delete> blocks
	s=convert_lists(s)																		#Convert lists first

	#Replace elements that must start at the beginning of the line
	bol_marker_tail=r"(?P<tail>\[list(?:=1)?])?"
	def bol_markers(haystack: str, needle: str, make_repl):
		return re.sub(
			rf"(?m)(?:^|\n)[ \t]*{re.escape(needle)}[ \t]*{bol_marker_tail}[ \t]*(?:\n|$)",
			lambda m: make_repl(m) + (m.group("tail") or ""),
			haystack,
		)

	#HR markers
	s=bol_markers(s, " ---", lambda m: f"[center]{HR_SHORT}[/center]")
	s=bol_markers(s, "---" , lambda m: "\n\n" + HR_SHORT)
	s=bol_markers(s, "***" , lambda m: "\n\n" + HR_FULL )

	#Blockquotes (collapse consecutive > lines into one [quote]..[/quote] block)
	#Emit \n\n between quote blocks to survive the later newline-collapser.
	lines=s.split("\n")
	out: list[str]=[]
	i=0
	while i<len(lines):
		if not (m := re.match(r"^>\s?(.*)$", lines[i])):
			out.append(lines[i])
			i+=1
			continue
		q: list[str]=[m.group(1)]
		i+=1
		while i<len(lines):
			if not (m := re.match(r"^>\s?(.*)$", lines[i])):
				break
			q.append(m.group(1))
			i+=1
		out.append("[quote]" + "\n".join(q) + "[/quote]")
		out.append("\n")
	s="\n".join(out)

	#Fix newlines
	def protect_str  (haystack: str, needle: str, name: str): return haystack.replace(needle, f"\x00{name}\x00")
	def unprotect_str(haystack: str, needle: str, name: str): return haystack.replace(f"\x00{name}\x00", needle)
	s=re.sub(r"\n{3,}", "\n\n", s)		#Make sure there are never more than 2 adjacent newlines
	s=  protect_str(s, "\n\n", "DBLNL")	#Protect double newlines
	s=re.sub(r"([>\]])\n", r"\1", s)	#Remove single line following a tag
	s=s.replace("\n", " ")				#Change single line into a space
	s=unprotect_str(s, "\n"  , "DBLNL")	#Change what were double newlines into a single newline

	#Center/p align/a (TEXT can include newlines)
	def tag_replace(haystack: str, html_tag: str, bbcode_tag: str, per_attr_regex: str="", override_rep: str|None=None, override_text: str=".*?"):
		return re.sub(
			rf'(?is)<{html_tag}\b{per_attr_regex}[^>]*>({override_text})</{html_tag}\s*>',
			override_rep if override_rep is not None else rf"[{bbcode_tag}]\1[/{bbcode_tag}]",
			haystack
		)
	s=tag_replace(s, "center", "center");												#<center> -> [center]
	s=tag_replace(s, "p", "center",	r'[^>]*\balign\s*=\s*"?center"?');					#<p align=center> -> [center]
	s=tag_replace(s, "p", "right",	r'[^>]*\balign\s*=\s*"?right"?');					#<p align=right> -> [right]
	s=tag_replace(s, "a", "url",	r'[^>]*\bhref\s*=\s*"([^"]+)"', r"[url=\1]\2[/url]")#<a href="URL">TEXT</a> -> [url=URL]TEXT[/url]
	s=re.sub(r"\[/(center|right)]", r"\n[/\1]", s)										#Add newline before end center or right

	#Font -> color/size (with nesting)
	old_string=""
	while old_string!=s:
		old_string=s
		s=tag_replace(s, "font", "-",	r'[^>]*\b(color|size)\s*=\s*(?:"([^"]+)"|([#\w]+))', r"[\1=\2\3]\4[/\1]", r'(?:(?!<font\b).)*?');

	#Details spoiler
	s=re.sub(r"(?is)<details>\s*<summary>\s*Spoiler\s*</summary>(.*?)</details>", r"[spoiler]\1[/spoiler]", s)

	#Simple HTML tags
	for html_tag, bbcode_tag in {
		"strong":	"b",
		"em":		"i",
		"ins":		"u",
		"del":		"s",
		"b":		"b",
		"i":		"i",
		"u":		"u",
		"s":		"s",
	}.items():
		s=tag_replace(s, html_tag, bbcode_tag)

	#More advanced replacements
	BBTags=r'(?:\*|/?(?:list|center|right|spoiler|size|quote|color|img|url|b|i|s)\b)'
	for replace, search in {
		HR_FULL:			r"(?i)<hr[^/>]*/?>",							#<hr>
		"<br>":				r"(?i) *<br[^/>]*/?>",							#Remove spaces before <br>
		image_tag_replace:	r"(?is)<img\b(?P<attrs>[^>]*)>",				#<img ...> (attrs any order; supports src= or href=; align optional)
		r"[img]\1[/img]":	r"!\[[^\]]*]\(([^)]+)\)",						#Markdown image: ![Text](URL)
		r"[url=\2]\1[/url]":rf"\[((?!{BBTags})[^\]]+)]\(([^)]+)\)",			#Markdown link: [Text](URL)
	}.items():
		s=re.sub(search, replace, s);

	#Emphasis markdown tags
	s=  protect_str(s, "[*]", "LI");
	for markdown_tag, replace_with in {
		r"\*\*\*":	r"[b][i]\1[/i][/b]",
		r"\*\*":	r"[b]\1[/b]",
		r"__":		r"[b]\1[/b]",
		r"\*":		r"[i]\1[/i]",
		r"_":		r"[i]\1[/i]",
		r"~~":		r"[s]\1[/s]",
	}.items():
		s=re.sub(rf"(?s)(?<!\\){markdown_tag}([^\n]+?)(?<!\\){markdown_tag}", replace_with, s)
	s=unprotect_str(s, "[*]", "LI");

	#Finishing touch ups
	NBSP="\u00A0"
	s=re.sub(r"(?i)(\[/(?:list|center|right|spoiler|quote)\])\n", r"\1", s)							#Remove newline after block level elements
	while "  " in s: s=s.replace("  ", " "+NBSP)													#Two spaces -> space + NBSP
	s=re.sub(r"\\([*_])", r"\1", s)																	#\* and \_ -> * and _
	s=s.replace("[/list][*]", "[/list]\n[*]")														#Add newline back between list and first item
	s=re.sub(r"<meta/>\n*", "", s)																	#<meta/> removes all newlines after it
	s=s.replace("<br>", "\n");																		#Unprotect breaks
	s = s.lstrip(' ')																				#Strip spaces from the beginning of the file
	return s