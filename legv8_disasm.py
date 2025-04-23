#!/usr/bin/env python3
import sys

# -----------------------------------------------------------------------------
# 1) Fixed-shamt map for ops that share a primary opcode but differ by a constant
#    6-bit shift field. Keys are 17 bits = 11-bit primary opcode + 6-bit shamt.
# -----------------------------------------------------------------------------
fixed_shamt_map = {
    # — Floating-point ops —
    '00011100001' + '000010': 'FMULS',
    '00011100010' + '000110': 'FDIVS',
    '00011100110' + '001000': 'FCMPS',
    '00011101000' + '001010': 'FADDS',
    '00011101001' + '001110': 'FSUBS',
    '00011110000' + '000010': 'FMULD',
    '00011110001' + '000110': 'FDIVD',
    '00011110110' + '001000': 'FCMPD',
    '00011111000' + '001010': 'FADDD',
    '00011111001' + '001110': 'FSUBD',

    # — Fixed-shamt integer ops —
    '10011010110' + '000010': 'SDIV',
    '10011010110' + '000011': 'UDIV',
    '10011011000' + '011111': 'MUL',
}

# -----------------------------------------------------------------------------
# 2) All other instructions, keyed by their primary bits.
#    The tuple is (mnemonic, format), where format ∈ {'R','I','D','B','CB','IM'}.
# -----------------------------------------------------------------------------
opcode_map = {
    # — R-type (variable-shamt) —
    '10001011000': ('ADD',   'R'),
    '11001011000': ('SUB',   'R'),
    '10001010000': ('AND',   'R'),
    '10101010000': ('ORR',   'R'),
    '11001010000': ('EOR',   'R'),
    '11101010000': ('ANDS',  'R'),
    '10101011000': ('ADDS',  'R'),
    '11101011000': ('SUBS',  'R'),
    '10011010110': ('SMULH', 'R'),
    '10011011110': ('UMULH', 'R'),
    '11010011011': ('LSL',   'R'),
    '11010011010': ('LSR',   'R'),
    '11010011001': ('ASR',   'R'),
    '11111100000': ('STURD', 'R'),
    '11111100010': ('LDURD', 'R'),

    # — I-type (10 bits) —
    '1001000100':  ('ADDI',  'I'),
    '1101000100':  ('SUBI',  'I'),
    '1001001000':  ('ANDI',  'I'),
    '1011001000':  ('ORRI',  'I'),
    '1101001000':  ('EORI',  'I'),
    '1111001000':  ('ANDIS', 'I'),
    '1011000100':  ('ADDIS', 'I'),
    '1111000100':  ('SUBIS', 'I'),

    # — D-type (11 bits) —
    '00111000000': ('STURB',  'D'),
    '00111000010': ('LDURB',  'D'),
    '01111000000': ('STURH',  'D'),
    '01111000010': ('LDURH',  'D'),
    '10111000000': ('STURW',  'D'),
    '11111000000': ('STUR',   'D'),
    '11111000010': ('LDUR',   'D'),
    '11111000011': ('LDURSW','D'),
    '11111000100': ('LDXR',   'D'),
    '11111000101': ('STXR',   'D'),

    # — B-type (6 bits) —
    '000101': ('B',  'B'),
    '100101': ('BL', 'B'),

    # — CB-type (8 bits) —
    '01010100': ('B.cond','CB'),
    '10110100': ('CBZ',   'CB'),
    '10110101': ('CBNZ',  'CB'),

    # — IM-type (9 bits) —
    '110100101': ('MOVZ',  'IM'),
    '111100101': ('MOVK',  'IM'),
}

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def bits(s, i, j):
    """Return substring of s from bit i up to (but not including) bit j."""
    return s[i:j]

def u(s):
    """Interpret binary string s as an unsigned integer."""
    return int(s, 2)

# -----------------------------------------------------------------------------
# Core decoder
# -----------------------------------------------------------------------------
def decode(hexcode: str) -> str:
    # Normalize to 8 hex digits
    h = hexcode.strip().lower().removeprefix('0x').zfill(8)
    # Full 32-bit binary string
    b = bin(int(h, 16))[2:].zfill(32)

    # 1) Fixed-shamt instructions (17-bit key)
    key17 = b[:17]
    if key17 in fixed_shamt_map:
        mnem = fixed_shamt_map[key17]
        Rm, Rn, Rd = u(b[11:16]), u(b[22:27]), u(b[27:32])
        return f"{mnem} X{Rd}, X{Rn}, X{Rm}"

    # 2) R-type & D-type (11 bits)
    op11 = b[:11]
    if op11 in opcode_map:
        mnem, fmt = opcode_map[op11]
        if fmt == 'R':
            Rm, shamt, Rn, Rd = u(b[11:16]), u(b[16:22]), u(b[22:27]), u(b[27:32])
            shift_suffix = f", LSL #{shamt}" if shamt else ""
            return f"{mnem} X{Rd}, X{Rn}, X{Rm}{shift_suffix}"
        elif fmt == 'D':
            imm, Rn, Rt = u(b[11:20]), u(b[20:25]), u(b[27:32])
            return f"{mnem} X{Rt}, [X{Rn}, #{imm}]"

    # 3) I-type (10 bits)
    op10 = b[:10]
    if op10 in opcode_map:
        mnem = opcode_map[op10][0]
        imm, Rn, Rd = u(b[10:22]), u(b[22:27]), u(b[27:32])
        return f"{mnem} X{Rd}, X{Rn}, #{imm}"

    # 4) IM-type (9 bits)
    op9 = b[:9]
    if op9 in opcode_map:
        mnem = opcode_map[op9][0]
        hw, imm, Rd = u(b[9:11]), u(b[11:27]), u(b[27:32])
        imm_val = imm << (hw * 16)
        return f"{mnem} X{Rd}, #{imm_val}"

    # 5) B-type (6 bits)
    op6 = b[:6]
    if op6 in opcode_map:
        mnem = opcode_map[op6][0]
        disp = u(b[6:32]) << 2
        # Sign-extend 26→32
        if disp & (1 << 25):
            disp -= (1 << 26)
        return f"{mnem} #{disp}"

    # 6) CB-type (8 bits)
    op8 = b[:8]
    if op8 in opcode_map:
        mnem = opcode_map[op8][0]
        disp = u(b[8:27]) << 2
        if disp & (1 << 18):
            disp -= (1 << 19)
        Rt = u(b[27:32])
        return f"{mnem} X{Rt}, #{disp}"

    # Unknown opcode
    return f".word 0x{h.upper()}    // unknown"

# -----------------------------------------------------------------------------
# Command-line interface
# -----------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: legv8_disasm.py <HEXCODE1> [<HEXCODE2> ...]")
        sys.exit(1)

    for hx in sys.argv[1:]:
        asm = decode(hx)
        print(f"{hx.upper():>10}  →  {asm}")

if __name__ == "__main__":
    main()
