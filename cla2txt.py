import sys
import binascii
import struct
from ops import ops

listing = []
labels = {}


def decode_string(s):
	s = b'\033$(O' + s
	try:
		s = s.decode('iso2022_jp_3')
	except:
		print('ERROR ' + s.hex())
		raise
	return s


def read_string(f):
	s = b''
	while True:
		ch = f.read(1)
		if ch == b'\x00': break
		s += ch
	return decode_string(s)


def read_ascii(f):
	s = b''
	while True:
		ch = f.read(1)
		if ch == b'\x00': break
		s += ch
	return s.decode('ascii')


def op_02_print(f):
	s = read_string(f)
	return f'PRINT "{s}"'
ops[0x02] = op_02_print


def op_05_jmp(f):
	offset = struct.unpack('H', f.read(2))[0]
	label = f"LAB_{offset:04X}"
	labels[offset] = label
	return f"JMP {label}"
ops[0x05] = op_05_jmp


def op_06_exec_cla(f):
	s = read_ascii(f)
	return f'OP06_EXEC_CLA "{s}"'
ops[0x06] = op_06_exec_cla


def op_07(f):
	x = ord(f.read(1))
	s = read_ascii(f)
	return f'OP07 {x:02X}, "{s}"'
ops[0x07] = op_07


def op_0c(f):
	data = f.read(5)
	cnt = data[4]
	data += f.read(4*cnt)
	return f"OP0C {data.hex()}"
ops[0x0c] = op_0c


def op_0f(f):
	s = read_ascii(f)
	return f'OP0F "{s}"'
ops[0x0f] = op_0f


def op_12_jz(f):
	x1 = ord(f.read(1))
	x2 = ord(f.read(1))
	offset = struct.unpack('H', f.read(2))[0]
	label = f"LAB_{offset:04X}".format(offset)
	labels[offset] = label
	return f"OP12_JZ {x1:02X}, {x2:02X}, {label}"
ops[0x12] = op_12_jz


def op_15_jnz(f):
	x = ord(f.read(1))
	offset = struct.unpack('H', f.read(2))[0]
	label = f"LAB_{offset:04X}"
	labels[offset] = label
	return f"OP15_JNZ {x:02X}, {label}"
ops[0x15] = op_15_jnz


def op_1b(f):
	return f'OP1B {ord(f.read(1)):02X}, "{read_string(f)}"'
ops[0x1b] = op_1b


def op_20(f):
	s = read_ascii(f)
	return f'OP20 "{s}"'
ops[0x20] = op_20


def op_21(f):
	s = read_ascii(f)
	return f'OP21 "{s}"'
ops[0x21] = op_21


def op_23_call(f):
	offset = struct.unpack('H', f.read(2))[0]
	label = f"LAB_{offset:04X}"
	labels[offset] = label
	return "CALL " + label
ops[0x23] = op_23_call


def op_24_ret(f):
	return "RET"
ops[0x24] = op_24_ret


def op_26(f):
	x = ord(f.read(1))
	data = b''
	while True:
		d = f.read(1)
		if d == b'\x00': break
		data += d
		if d != b'\xff': continue
		data += f.read(4)
		raise
	return f'OP26 {x:02X}, "{decode_string(data)}"'
ops[0x26] = op_26


def op_2c(f):
	data = f.read(2)
	while True:
		c = f.read(1)
		data += c
		if c == b'\x00': break
		data += f.read(1)
	return f"OP2C {data.hex()}"
ops[0x2c] = op_2c


def op_3d(f):
	x = ord(f.read(1))
	s = read_ascii(f)
	return f'OP3D {x:02X}, "{s}"'
ops[0x3d] = op_3d


def op_56(f):
	s = read_ascii(f)
	return f'OP56 "{s}"'
ops[0x56] = op_56


def op_57(f):
	s = read_ascii(f)
	return f'OP57 "{s}"'
ops[0x57] = op_57


def op_63(f):
	data = f.read(3)
	while True:
		c = f.read(1)
		data += c
		if c == b'\x00': break
		data += f.read(1)
	return f'OP63 {data.hex()}'
ops[0x63] = op_63


def op_6b(f):
	data = f.read(9)
	x = data[8]
	# check it
	return f"OP6B {data.hex()}"
ops[0x6b] = op_6b


def op_85(f):
	data = f.read(3)
	cnt = data[2]
	for _ in range(cnt):
		data += f.read(1)
		chunk_len = data[-1]
		chunk_len*=4
		data += f.read(chunk_len)
	return f"OP85 {data.hex()}"
ops[0x85] = op_85


def op_8c_jz(f):
	x = ord(f.read(1))
	offset = struct.unpack('H', f.read(2))[0]
	label = f"LAB_{offset:04X}"
	labels[offset] = label
	return f"OP8C_JZ {x:02X}, {label}"
ops[0x8c] = op_8c_jz


def op_8e(f):
	data = b''
	while True:
		d = f.read(1)
		data += d
		if d == b'\x00': break
		data += f.read(3)
	return f"OP8E {data.hex()}"
ops[0x8e] = op_8e


def op_99(f):
	data = f.read(2)
	cnt = data[1]
	data += f.read(4*cnt)
	return f"OP99 {data.hex()}"
ops[0x99] = op_99


def op_9b(f):
	data = f.read(4)
	return f"OP9B {data.hex()}"
ops[0x9b] = op_9b


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Missing argument')
		exit(1)

	with open(sys.argv[1], 'rb') as f:
		while True:
			offset = f.tell()
			op = f.read(1)
			line = u''
			if len(op) == 0: break
			op = ord(op)
			if op not in ops:
				raise Exception(f"unknown op {op:02X}")
			if callable(ops[op]):
				line = ops[op](f)
			else:
				line = "OP{:02X} {}".format(op, f.read(ops[op]).hex())
			#print(u'{:06X} {}'.format(offset, line))
			listing.append([offset, line])

	for l in listing:
		if l[0] in labels:
			print(f"\n{labels[l[0]]}:")
		print(l[1])

