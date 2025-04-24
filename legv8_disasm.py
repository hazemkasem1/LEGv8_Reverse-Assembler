#!/usr/bin/env python3
import sys

# -----------------------------------------------------------------------------
# 1) Fixed-shamt map (17 bits = 11-bit opcode + 6-bit shamt)
# -----------------------------------------------------------------------------
fixed_shamt_map = {
    # — Floating-point single precision —
    '00011110001' + '000010': 'FMULS',
    '00011110001' + '000110': 'FDIVS',
    '00011110001' + '001000': 'FCMPS',
    '00011110001' + '001010': 'FADDS',
    '00011110001' + '001110': 'FSUBS',
    # — Floating-point double precision —
    '00011110011' + '000010': 'FMULD',
    '00011110011' + '000110': 'FDIVD',
    '00011110011' + '001000': 'FCMPD',
    '00011110011' + '001010': 'FADDD',
    '00011110011' + '001110': 'FSUBD',
    # — Integer fixed-shamt ops —
    '10011010110' + '000010': 'SDIV',
    '10011010110' + '000011': 'UDIV',
    '10011011000' + '011111': 'MUL',
}

# -----------------------------------------------------------------------------
# 2) Remaining opcodes by primary bits: (mnemonic, format)
# -----------------------------------------------------------------------------
opcode_map = {
    # R-types (variable shamt) and special integer R types moved to fixed_shamt_map
    '10001010000': ('AND',  'R'),
    '10001011000': ('ADD',  'R'),
    '10011011010': ('SMULH','R'),
    '10011011110': ('UMULH','R'),
    '10101010000': ('ORR',  'R'),
    '10101011000': ('ADDS', 'R'),
    '10111100000': ('STURS','R'),
    '10111100010': ('LDURS','R'),
    '11001010000': ('EOR',  'R'),
    '11001011000': ('SUB',  'R'),
    '11010011010': ('LSR',  'R'),
    '11010011011': ('LSL',  'R'),
    '11010110000': ('BR',   'R'),
    '11101010000': ('ANDS', 'R'),
    '11101011000': ('SUBS', 'R'),
    '11111100000': ('STURD','R'),
    '11111100010': ('LDURD','R'),

    # I-types (10 bits)
    '1001000100':  ('ADDI',  'I'),
    '1001001000':  ('ANDI',  'I'),
    '1011000100':  ('ADDIS', 'I'),
    '1011001000':  ('ORRI',  'I'),
    '1101001000':  ('EORI',  'I'),
    '1111000100':  ('SUBIS', 'I'),
    '1111001000':  ('ANDIS', 'I'),

    # D-types (11 bits)
    '00111000000': ('STURB',  'D'),
    '00111000010': ('LDURB',  'D'),
    '01111000000': ('STURH',  'D'),
    '01111000010': ('LDURH',  'D'),
    '10111000000': ('STURW',  'D'),
    '10111000100': ('LDURSW','D'),
    '11001000000': ('STXR',   'D'),
    '11001000010': ('LDXR',   'D'),
    '11111000000': ('STUR',   'D'),
    '11111000010': ('LDUR',   'D'),

    # B-types (6 bits)
    '000101': ('B',  'B'),
    '100101': ('BL', 'B'),

    # CB-types (8 bits)
    '01010100': ('B.cond','CB'),
    '10110100': ('CBZ',   'CB'),
    '10110101': ('CBNZ',  'CB'),

    # IM-types (9 bits)
    '110100101': ('MOVZ', 'IM'),
    '111100101': ('MOVK', 'IM'),
}

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def bits(s, i, j):       return s[i:j]
def u(s):                 return int(s, 2)

# -----------------------------------------------------------------------------
# Decode R-type (and fixed-shamt) instructions
# -----------------------------------------------------------------------------
def decode_r(b: str) -> str | None:
    # fixed-shamt floating/integer
    k17 = b[:17]
    if k17 in fixed_shamt_map:
        m = fixed_shamt_map[k17]
        Rm, Rn, Rd = u(b[11:16]), u(b[22:27]), u(b[27:32])
        return f"{m} X{Rd}, X{Rn}, X{Rm}"

    # variable-shamt R-types
    op11 = b[:11]
    if op11 in opcode_map and opcode_map[op11][1] == 'R':
        m, _ = opcode_map[op11]
        Rm, sh, Rn, Rd = u(b[11:16]), u(b[16:22]), u(b[22:27]), u(b[27:32])
        suffix = f", LSL #{sh}" if sh else ""
        return f"{m} X{Rd}, X{Rn}, X{Rm}{suffix}"

    return None

# -----------------------------------------------------------------------------
# Decode D-type instructions
# -----------------------------------------------------------------------------
def decode_d(b: str) -> str | None:
    op11 = b[:11]
    if op11 in opcode_map and opcode_map[op11][1] == 'D':
        m, _ = opcode_map[op11]
        imm   = u(b[11:20])
        Rn    = u(b[22:27])  # CORE D-format: bits 9–5
        Rt    = u(b[27:32])
        return f"{m} X{Rt}, [X{Rn}, #{imm}]"
    return None

# -----------------------------------------------------------------------------
# Decode I-type
# -----------------------------------------------------------------------------
def decode_i(b: str) -> str | None:
    op10 = b[:10]
    if op10 in opcode_map and opcode_map[op10][1] == 'I':
        m, _ = opcode_map[op10]
        imm, Rn, Rd = u(b[10:22]), u(b[22:27]), u(b[27:32])
        return f"{m} X{Rd}, X{Rn}, #{imm}"
    return None

# -----------------------------------------------------------------------------
# Decode IM-type
# -----------------------------------------------------------------------------
def decode_im(b: str) -> str | None:
    op9 = b[:9]
    if op9 in opcode_map and opcode_map[op9][1] == 'IM':
        m, _ = opcode_map[op9]
        hw, imm, Rd = u(b[9:11]), u(b[11:27]), u(b[27:32])
        return f"{m} X{Rd}, #{imm << (hw * 16)}"
    return None

# -----------------------------------------------------------------------------
# Decode B-type
# -----------------------------------------------------------------------------
def decode_b(b: str) -> str | None:
    op6 = b[:6]
    if op6 in opcode_map and opcode_map[op6][1] == 'B':
        m = opcode_map[op6][0]
        disp = u(b[6:32]) << 2
        if disp & (1 << 25): disp -= (1 << 26)
        return f"{m} #{disp}"
    return None

# -----------------------------------------------------------------------------
# Decode CB-type
# -----------------------------------------------------------------------------
def decode_cb(b: str) -> str | None:
    op8 = b[:8]
    if op8 in opcode_map and opcode_map[op8][1] == 'CB':
        m = opcode_map[op8][0]
        disp = u(b[8:27]) << 2
        if disp & (1 << 18): disp -= (1 << 19)
        Rt = u(b[27:32])
        return f"{m} X{Rt}, #{disp}"
    return None

# -----------------------------------------------------------------------------
# Main dispatcher
# -----------------------------------------------------------------------------
def decode(hexcode: str) -> str:
    h = hexcode.strip().lower().removeprefix('0x').zfill(8)
    b = bin(int(h, 16))[2:].zfill(32)

    for fn in (decode_r, decode_d, decode_i, decode_im, decode_b, decode_cb):
        res = fn(b)
        if res:
            return res

    return f".word 0x{h.upper()}    // unknown"

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: legv8_disasm.py <HEX1> [<HEX2> …]")
        sys.exit(1)
    for hx in sys.argv[1:]:
        print(f"{hx.upper():>10} → {decode(hx)}")

if __name__ == "__main__":
    main()
