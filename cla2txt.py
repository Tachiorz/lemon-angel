import sys
import binascii
import struct

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
	return u'PRINT "{}"'.format(s)

def op_05_jmp(f):
	offset = struct.unpack('H', f.read(2))[0]
	label = "LAB_{:04X}".format(offset)
	labels[offset] = label
	return "JMP {}".format(label)

def op_06_exec_cla(f):
	s = read_ascii(f)
	return 'OP06_EXEC_CLA "{}"'.format(s)

def op_07(f):
	x = ord(f.read(1))
	s = read_ascii(f)
	return u'OP07 {:02X}, "{}"'.format(x, s)

def op_0c(f):
	data = f.read(5)
	cnt = data[4]
	data += f.read(4*cnt)
	return "OP0C {}".format(data.hex())

def op_0f(f):
	s = read_ascii(f)
	return u'OP0F "{}"'.format(s)

def op_12_jz(f):
	x1 = ord(f.read(1))
	x2 = ord(f.read(1))
	offset = struct.unpack('H', f.read(2))[0]
	label = "LAB_{:04X}".format(offset)
	labels[offset] = label
	return "OP12_JZ {:02X}, {:02X}, {}".format(x1, x2, label)

def op_13_jnz(f):
	raise

def op_15_jnz(f):
	x = ord(f.read(1))
	offset = struct.unpack('H', f.read(2))[0]
	label = "LAB_{:04X}".format(offset)
	labels[offset] = label
	return "OP15_JNZ {:02X}, {}".format(x, label)

def op_1b(f):
	return u'OP1B {:02X}, "{}"'.format(ord(f.read(1)), read_string(f))

def op_20(f):
	s = read_ascii(f)
	return u'OP20 "{}"'.format(s)

def op_21(f):
	s = read_ascii(f)
	return u'OP21 "{}"'.format(s)

def op_23_call(f):
	global labels
	offset = struct.unpack('H', f.read(2))[0]
	label = "LAB_{:04X}".format(offset)
	labels[offset] = label
	return "CALL " + label

def op_24_ret(f):
	return "RET"

def op_26(f):
	x = ord(f.read(1))
	data = b''
	while True:
		d = f.read(1)
		if d == b'\x00': break
		data += d
		if d != b'\xff': continue
		data += f.read(4)
	return u'OP26 {:02X}, "{}"'.format(x, decode_string(data))

def op_2c(f):
	data = f.read(2)
	while True:
		c = f.read(1)
		data += c
		if c == b'\x00': break
		data += f.read(1)
	return "OP2C {}".format(data.hex())

def op_33(f):
	raise

def op_3d(f):
	x = ord(f.read(1))
	s = read_ascii(f)
	return u'OP3D {:02X}, "{}"'.format(x, s)

def op_3f(f):
	raise

def op_43_jle(f):
	raise

def op_44_jge(f):
	raise

def op_4d_jmp(f):
	raise

def op_56(f):
	s = read_ascii(f)
	return u'OP56 "{}"'.format(s)

def op_57(f):
	s = read_ascii(f)
	return u'OP57 "{}"'.format(s)

def op_63(f):
	data = f.read(3)
	while True:
		c = f.read(1)
		data += c
		if c == b'\x00': break
		data += f.read(1)
	return u'OP63 {}'.format(data.hex())

def op_6b(f):
	data = f.read(9)
	x = data[8]
	# check it
	return "OP6B {}".format(data.hex())

def op_72(f):
	raise

def op_73(f):
	raise

def op_78(f):
	raise

def op_82_jmp(f):
	raise

def op_85(f):
	data = f.read(3)
	cnt = data[2]
	for _ in range(cnt):
		data += f.read(1)
		chunk_len = data[-1]
		chunk_len*=4
		data += f.read(chunk_len)
	return "OP85 {}".format(data.hex())

def op_8c_jz(f):
	x = ord(f.read(1))
	offset = struct.unpack('H', f.read(2))[0]
	label = "LAB_{:04X}".format(offset)
	labels[offset] = label
	return "OP8C_JZ {:02X}, {}".format(x, label)

def op_8d(f):
	raise

def op_8e(f):
	data = b''
	while True:
		d = f.read(1)
		data += d
		if d == b'\x00': break
		data += f.read(3)
	return "OP8E {}".format(data.hex())


def op_8f(f):
	raise

def op_90(f):
	raise

def op_95(f):
	raise

def op_99(f):
	data = f.read(2)
	cnt = data[1]
	data += f.read(4*cnt)
	return "OP99 {}".format(data.hex())

def op_9b(f):
	data = f.read(4)
	return "OP9B {}".format(data.hex())


ops = {
0x01: 4,
0x02: op_02_print,
0x03: 4,
0x04: 2,
0x05: op_05_jmp,
0x06: op_06_exec_cla,
0x07: op_07,
0x08: 1,
0x09: 2,
0x0A: 1,
0x0B: 0,
0x0C: op_0c,
0x0D: 2,
0x0E: 0,
0x0F: op_0f,
0x10: 0,
0x11: 1,
0x12: op_12_jz,
0x13: op_13_jnz,
0x14: 1,
0x15: op_15_jnz,
0x16: 2,
0x17: 2,
0x18: 0,
0x19: 2,
0x1A: 0,
0x1B: op_1b,
0x1C: 2,
0x1D: 2,
0x1E: 5,
0x1F: 11,
0x20: op_20,
0x21: op_21,
0x22: 2,
0x23: op_23_call,
0x24: op_24_ret,
0x25: 0,
0x26: op_26,
0x27: 2,
0x28: 1,
0x29: 1,
0x2A: 4,
0x2B: 3,
0x2C: op_2c,
0x2D: 0,
0x2E: 0,
0x2F: 0,
0x30: 0,
0x31: 6,
0x32: 0,
0x33: op_33,
0x34: 0,
0x35: 2,
0x36: 0,
0x37: 2,
0x38: 1,
0x39: 0,
0x3A: 6,
0x3B: 0,
0x3C: 1, # game reset?
0x3D: op_3d,
0x3E: 1,
0x3F: op_3f, # save load?
0x40: 2,
0x41: 0,
0x42: 0,
0x43: op_43_jle,
0x44: op_44_jge,
0x45: 2,
0x46: 1,
0x47: 0,
0x48: 2,
0x49: 0,
0x4A: 1,
0x4B: 2,
0x4C: 0,
0x4D: op_4d_jmp,
0x4E: 1,
0x4F: 0,
0x50: 4,    # calls 2A
0x51: 1,
0x52: 2,
0x53: 2,
0x54: 1,
0x55: 0,
0x56: op_56,
0x57: op_57,  # confirm
0x58: 1,
0x59: 0,
0x5A: 0,
0x5B: 1,
0x5C: 8,
0x5D: 0,
0x5E: 0,
0x5F: 14,
0x60: 0,
0x61: 7,
0x62: 8,
0x63: op_63,
0x64: 1,
0x65: 2,
0x66: 0,
0x67: 15,
0x68: 0,
0x69: 0,
0x6A: 1,
0x6B: op_6b,
0x6C: 1,
0x6D: 1,
0x6E: 1,
0x6F: 1,
0x70: 1,
0x71: 1,
0x72: op_72,
0x73: op_73, #weird
0x74: 2,
0x75: 2,
0x76: 1,
0x77: 1,
0x78: 0, #weird
0x79: 0x40,  #confirm
0x7A: 2,
0x7B: 1,    #weird
0x7C: 1,
0x7D: 1,
0x7E: 0,
0x7F: 0,
0x80: 2,
0x81: 2,
0x82: op_82_jmp,
0x83: 1,
0x84: 0,
0x85: op_85,
0x86: 1,
0x87: 8,
0x88: 18,
0x89: 4,
0x8A: 6,
0x8B: 4,
0x8C: op_8c_jz,
0x8D: op_8d,
0x8E: op_8e,
0x8F: op_8f,
0x90: op_90,
0x91: 2,
0x92: 1,
0x93: 0,
0x94: 0,
0x95: op_95,
0x96: 9,
0x97: 3,
0x98: 5,
0x99: op_99,
0x9A: 1,
0x9B: op_9b,  #hard
}

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
				raise Exception("unknown op {:02X}".format(op))
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

