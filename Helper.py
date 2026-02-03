import re

parse_attr_regex=re.compile(r"""\b([a-zA-Z_][-\w]*)\b\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))""", re.IGNORECASE|re.DOTALL)
def parse_attrs(attrs: str) -> dict:
	out={}
	for m in re.finditer(parse_attr_regex, attrs):
		val=m.group(2) or m.group(3) or m.group(4)
		out[m.group(1).lower()]=True if val is None else val
	return out

#Replace in haystack: `<html_tag per_attr_regex>override_text</html_tag>` with `override_rep ?? [bbcode_tag]override_text[/bbcode_tag]`
def tag_replace(haystack: str, html_tag: str, bbcode_tag: str, per_attr_regex: str="", override_rep: str|None=None, override_text: str=".*?"):
	return re.sub(
		rf'(?is)<{html_tag}\b{per_attr_regex}[^>]*>({override_text})</{html_tag}\s*>',
		override_rep if override_rep is not None else rf"[{bbcode_tag}]\1[/{bbcode_tag}]",
		haystack
	)