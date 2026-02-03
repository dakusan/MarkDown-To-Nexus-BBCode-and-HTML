#Parse MD lists
import re

class ListSection:
	def __init__(self, indent: int, kind: str):
		self.indent=indent
		self.kind=kind #ul or ol

#Lists: Supports mixed bullet markers on same level; numeric vs non-numeric cannot mix on same level (we auto-close/open)
def convert_lists(md: str) -> str:
	"""
	Converts markdown lists into Nexus BBCode lists, obeying:
	  - Every item starts at BOL: [*]
	  - [list] starts at end of previous line of text
	  - [/list] on its own line
	"""
	lines=md.split("\n")
	out: list[str]=[]
	stack: list[ListSection]=[]

	def open_list(kind: str):
		tag="[list=1]\n\n" if kind=="ol" else "[list]\n\n"
		if out and out[-1]!="":
			out[-1] += tag
		else:
			out.append(tag)

	def close_list():
		stack.pop()
		out.append("\n[/list]")

	def close_to(indent: int):
		while stack and stack[-1].indent>indent:
			close_list()

	def close_all():
		while stack:
			close_list()

	def push_section(indent: int, kind: str):
		stack.append(ListSection(indent, kind))
		open_list(kind)

	bullet_re	=re.compile(r"^(?P<indent>[ \t]*)(?P<marker>[-*+])\s+(?P<text>.*)$")
	ol_re		=re.compile(r"^(?P<indent>[ \t]*)(?P<num>\d+)\.\s+(?P<text>.*)$")
	for line in lines:
		#Check if line is a list
		if (match_list := ol_re.match(line)):
			kind="ol"
		elif (match_list := bullet_re.match(line)):
			kind="ul"
		else:
			#On non-list, close any open lists before output
			close_all()
			out.append(line)
			continue

		#Determine current level changes
		text=match_list.group("text")
		indent=sum(4 if ch=="\t" else 1 for ch in match_list.group("indent")) #Tabs are treated as 4 spaces for nesting purposes
		if not stack or indent>stack[-1].indent: #First or nested list
			push_section(indent, kind)
		else: #Same level or outdent
			close_to(indent)
			if not stack or indent<stack[-1].indent: #First or same indent level now
				push_section(indent, kind)
			elif stack[-1].kind!=kind: #Same indent; if kind differs, close+open at same level
				close_list()
				push_section(indent, kind)

		#Output item
		out.append(f"\n[*]{text}")

	close_all()
	return "\n".join(out)