import sys
import struct
from ops import ops

labels = {}  # {"label": offset}
fixes = {}  # {"label": [offsets]}
cla = b''


def get_args(line):
	return list(map(lambda l: l.strip(' '), line[line.find(' '):].split(',')))


def add_fix(label, offset):
	if label not in fixes:
		fixes[label] = []
	fixes[label].append(offset)


def convert_string(s):
	s = s.strip('"')
	data = s.encode('iso2022_jp_3')
	if data == b'': return b'\x00'
	data = data.replace(b'\x1b$B', b'')
	data = data.replace(b'\x1b(B', b'')
	data = data.replace(b'\x1b$(O', b'')
	if b'\x1b' in data: raise
	return data + b'\x00'


def convert_ascii(s):
	s = s.strip('"')
	return s.encode('ascii') + b'\x00'

def op_02_print(l):
	return convert_string(get_args(l)[0])
ops[0x02] = op_02_print


def op_05_jmp(l):
	label = get_args(l)[0]
	offset = len(cla)
	add_fix(label, offset)
	return b'\x00\x00'
ops[0x05] = op_05_jmp


def op_06_exec_cla(l):
	return convert_ascii(get_args(l)[0])
ops[0x06] = op_06_exec_cla


def op_07(l):
	args = get_args(l)
	return bytes.fromhex(args[0]) + convert_ascii(args[1])
ops[0x07] = op_07


def op_0c(l):
	return bytes.fromhex(get_args(l)[0])
ops[0x0c] = op_0c


def op_0f(l):
	return convert_ascii(get_args(l)[0])
ops[0x0f] = op_0f


def op_12_jz(l):
	args = get_args(l)
	offset = len(cla) + 2
	add_fix(args[2], offset)
	return bytes.fromhex(args[0]) + bytes.fromhex(args[1]) + b'\x00\x00'
ops[0x12] = op_12_jz


def op_15_jnz(l):
	args = get_args(l)
	offset = len(cla) + 1
	add_fix(args[1], offset)
	return bytes.fromhex(args[0]) + b'\x00\x00'
ops[0x15] = op_15_jnz


def op_1b(l):
	args = get_args(l)
	return bytes.fromhex(args[0]) + convert_string(args[1])
ops[0x1b] = op_1b


def op_20(l):
	return convert_ascii(get_args(l)[0])
ops[0x20] = op_20


def op_21(l):
	return convert_ascii(get_args(l)[0])
ops[0x21] = op_21


def op_23_call(l):
	label = get_args(l)[0]
	offset = len(cla)
	add_fix(label, offset)
	return b'\x00\x00'
ops[0x23] = op_23_call


def op_24_ret(l):
	return b''
ops[0x24] = op_24_ret


def op_26(l):
	args = get_args(l)
	return bytes.fromhex(args[0]) + convert_string(args[1])
ops[0x26] = op_26


def op_2c(l):
	return bytes.fromhex(get_args(l)[0])
ops[0x2c] = op_2c


def op_3d(l):
	args = get_args(l)
	return bytes.fromhex(args[0]) + convert_ascii(args[1])
ops[0x3d] = op_3d


def op_56(l):
	return convert_ascii(get_args(l)[0])
ops[0x56] = op_56


def op_57(l):
	return convert_ascii(get_args(l)[0])
ops[0x57] = op_57


def op_63(l):
	return bytes.fromhex(get_args(l)[0])
ops[0x63] = op_63


def op_6b(l):
	return bytes.fromhex(get_args(l)[0])
ops[0x6b] = op_6b


def op_85(l):
	return bytes.fromhex(get_args(l)[0])
ops[0x85] = op_85


def op_8c_jz(l):
	args = get_args(l)
	offset = len(cla) + 1
	add_fix(args[1], offset)
	return bytes.fromhex(args[0]) + b'\x00\x00'
ops[0x8c] = op_8c_jz


def op_8e(l):
	return bytes.fromhex(get_args(l)[0])
ops[0x8e] = op_8e


def op_99(l):
	return bytes.fromhex(get_args(l)[0])
ops[0x99] = op_99


def op_9b(l):
	return bytes.fromhex(get_args(l)[0])
ops[0x9b] = op_9b


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Missing argument')
		exit(1)
	with open(sys.argv[1]) as f:
		lines = f.readlines()
		for linenumber in range(len(lines)):
			line = lines[linenumber]
			line = line.strip('\r\n ')
			if len(line) == 0: continue
			if line[-1] == ':':  # parse label
				labels[line.strip(':')] = len(cla)
				continue
			if line[:2] == 'OP':  # parse generic op
				op = ord(bytes.fromhex(line[2:4]))
			elif line.startswith('PRINT '): op = 0x02
			elif line.startswith('JMP '): op = 0x05
			elif line.startswith('CALL '): op = 0x23
			elif line == 'RET': op = 0x24
			else:
				raise Exception(f'Syntax error at line {linenumber+1}')
			if op not in ops:
				raise Exception(f"unknown op {op:02X}")
			cla += struct.pack('B', op)
			if callable(ops[op]):
				data = ops[op](line)
			else:
				if len(line.split(' ')) > 1:
					data = bytes.fromhex(line.split(' ')[1])
				else:
					data = b''
			cla += data
	cla = bytearray(cla)
	for label, fixlist in fixes.items():
		if label not in labels:
			raise Exception
		for fix in fixlist:
			cla[fix:fix+2] = struct.pack('H', labels[label])
	with open(sys.argv[1][:-4] + '.CLA', 'wb') as f:
		f.write(cla)
