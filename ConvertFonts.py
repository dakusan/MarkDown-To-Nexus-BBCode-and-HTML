import re
from dataclasses import dataclass
from Helper import parse_attrs, tag_replace

@dataclass
class FontProperties:
	def copy(self):
		return FontProperties(**self.__dict__)
	color		: str|None	= None
	size		: int|None	= None
	bold		: bool		= False
	italics		: bool		= False
	underline	: bool		= False
	strike		: bool		= False
	dummy		: bool		= False

def apply_font_css(fp: FontProperties, prop: str, val: str) -> None:
	v=val.strip().lower()
	match prop.strip().lower():
		case "color"		: fp.color		=val.strip()
		case "font-size"	: fp.size		=int(v) if v.isdigit() else None
		case "font-weight"	: fp.bold		=(v in ("bold", "bolder")) or (v.isdigit() and int(v)>=700)
		case "font-style"	: fp.italics	=v in ("italic", "oblique")
		case "text-decoration" | "text-decoration-line":
			 				  fp.underline	|= "underline" in v
			 				  fp.strike		|= "line-through" in v

def get_font_styles(html: str) -> dict[str, FontProperties]:
	GetClassRe=re.compile(r"\.(\w+)\s*\{\s*(.*?)\s*\}", re.DOTALL)
	GetPropsRe=re.compile(r"([a-zA-Z][\w-]*)\s*:\s*(.*?)\s*(?:;|$)")
	out: dict[str, FontProperties]={}

	for style_body in re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE|re.DOTALL).findall(html):
		for m in GetClassRe.finditer(style_body):
			class_name, css_props=m.group(1), m.group(2)
			fp=out.setdefault(class_name, FontProperties())
			for pm in GetPropsRe.finditer(css_props):
				apply_font_css(fp, pm.group(1), pm.group(2))

	return out

def convert_fonts(s: str, fonts: dict[str, FontProperties]) -> str:
	old_string=""
	while old_string!=s:
		old_string=s
		s=tag_replace(
			s, "font", "-", r"([^>]*)",
			lambda m: get_font_str(m, fonts),
			r"(?:(?!<font\b).)*?"
		)
	return s

def get_font_str(match: re.Match, fonts: dict[str, FontProperties]) -> str:
	attrs=parse_attrs(match.group(1))
	basefp=fonts.get(attrs.get("class"))
	fp=basefp.copy() if basefp is not None else FontProperties()
	for attr, val in attrs.items():
		match attr.strip():
			case "color": fp.color=val
			case "size": fp.size=int(val) if val.isdigit() else fp.size

	prefix : list[str]=[]
	postfix: list[str]=[]
	def add_tag(tag: str, tagVal: str=""):
		prefix.append(f"[{tag}{tagVal}]")
		postfix.append(f"[/{tag}]")

	if(fp.color is not None): add_tag("color", f"={fp.color}")
	if(fp.size  is not None): add_tag("size", f"={fp.size}")
	if(fp.bold)				: add_tag("b")
	if(fp.italics)			: add_tag("i")
	if(fp.underline)		: add_tag("u")
	if(fp.strike)			: add_tag("s")

	return "".join(prefix)+match.group(2)+"".join(reversed(postfix))