#!/usr/bin/env python3
#Convert [Visual Studio] markdown to NexusMods BBCode
import sys
from Convert import convert

def main(argv: list[str]) -> int:
	sys.stdout.write(convert(sys.stdin.read()))
	return 0

if __name__ == "__main__":
	raise SystemExit(main(sys.argv))