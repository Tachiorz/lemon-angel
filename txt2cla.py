import struct
from ops import ops

labels = {}  # {offset: "label"}
fixes = {}  # {"label": [offsets]}


with open('STARTUP.TXT') as f:
	lines = f.readlines()
	cla = b''
	for linenumber in range(len(lines)):
		line = lines[linenumber]
		line = line.strip('\r\n')
		if len(line) == 0: continue
		if line[-1] == ':':  # parse label
			labels[len(cla)] = line.strip(':')
		if line[:2] == 'OP':  # parse generic op
			op = ord(bytes.fromhex(line[2:4]))
			print(op, line)
		elif line == 'PRINT': op == 0x02
		elif line == 'JMP': op == 0x05
		elif line == 'CALL': op == 0x23
		elif line == 'RET': op == 0x24
		else:
			raise Exception(f'Syntax error at line {linenumber+1}')
		if op not in ops:
			raise Exception(f"unknown op {op:02X}")
		cla += struct.pack('B', op)
		if callable(ops[op]):
			line = ops[op](f)
		else:
			data = bytes.fromhex(line.split(' ')[1])
			cla += data
