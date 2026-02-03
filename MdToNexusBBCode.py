#!/usr/bin/env python3
#Convert [Visual Studio] markdown to NexusMods BBCode
import sys
from typing import List
from Convert import convert

def main(argv: List[str]) -> int:
	sys.stdout.write(convert(sys.stdin.read()))
	return 0

if __name__ == "__main__":
	raise SystemExit(main(sys.argv))