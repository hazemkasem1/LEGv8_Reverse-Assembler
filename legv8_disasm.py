#!/usr/bin/env python3
import sys

# -----------------------------------------------------------------------------
# 1) Fixed-shamt map: 11-bit opcode + 6-bit shamt → mnemonic
# -----------------------------------------------------------------------------
fixed_shamt_map = {
    # Single-precision FP
    '00011110001' + '000010': 'FMULS',
    '00011110001' + '000110': 'FDIVS',
    '00011110001' + '001000': 'FCMPS',
    '00011110001' + '001010': 'FADDS',
    '00011110001' + '001110': 'FSUBS',
    # Double-precision FP
    '00011110011' + '000010': 'FMULD',
    '00011110011' + '000110': 'FDIVD',
    '00011110011' + '001000': 'FCMPD',
    '00011110011' + '001010': 'FADDD',
    '00011110011' + '001110': 'FSUBD',
    # Integer fixed-shamt
    '10011010110' + '000010': 'SDIV',
    '10011010110' + '000011': 'UDIV',
    '10011011000' + '011111': 'MUL',
}

# -----------------------------------------------------------------------------
# 2) Primary opcode map: opcode prefix → (mnemonic, format)
#    Formats: 'R','I','D','B','CB','IM'
# -----------------------------------------------------------------------------
opcode_map = {
    # R-types (variable-shamt)
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

    # I-types (immediate ALU)
    '1001000100':  ('ADDI',  'I'),
    '1001001000':  ('ANDI',  'I'),
    '1011000100':  ('ADDIS', 'I'),
    '1011001000':  ('ORRI',  'I'),
    '1101001000':  ('EORI',  'I'),
    '1111000100':  ('SUBIS', 'I'),
    '1111001000':  ('ANDIS', 'I'),

    # D-types (load/store)
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

    # B-types (unconditional branch)
    '000101': ('B',  'B'),
    '100101': ('BL', 'B'),

    # CB-types (conditional branch)
    '01010100': ('B.cond','CB'),
    '10110100': ('CBZ',   'CB'),
    '10110101': ('CBNZ',  'CB'),

    # IM-types (MOVZ/MOVK)
    '110100101': ('MOVZ','IM'),
    '111100101': ('MOVK','IM'),
}

# -----------------------------------------------------------------------------
# Decode a single 32-bit hex or binary string into LEGv8 assembly
# -----------------------------------------------------------------------------
def decode_inst(code: str) -> str:
    # normalize to 8-digit hex, build 32-bit binary string
    h = code.strip().lower().removeprefix('0x').zfill(8)
    b = bin(int(h,16))[2:].zfill(32)

    # 1) Fixed-shamt formats (FP and special integer)
    key17 = b[:17]
    if key17 in fixed_shamt_map:
        mnem = fixed_shamt_map[key17]
        Rm = int(b[11:16],2)
        Rn = int(b[22:27],2)
        Rd = int(b[27:32],2)
        return f"{mnem} X{Rd}, X{Rn}, X{Rm}"

    # 2) Primary 11-bit opcode
    op11 = b[:11]
    if op11 in opcode_map:
        mnem, fmt = opcode_map[op11]

        # — R-type (variable shamt) —
        if fmt == 'R':
            Rm   = int(b[11:16],2)
            sh   = int(b[16:22],2)
            Rn   = int(b[22:27],2)
            Rd   = int(b[27:32],2)
            suf  = f", LSL #{sh}" if sh else ""
            return f"{mnem} X{Rd}, X{Rn}, X{Rm}{suf}"

        # — D-type —
        elif fmt == 'D':
            imm  = int(b[11:20],2)      # bits20–12
            Rn   = int(b[22:27],2)      # bits9–5
            Rt   = int(b[27:32],2)      # bits4–0
            return f"{mnem} X{Rt}, [X{Rn}, #{imm}]"

    # 3) I-type (10-bit opcode)
    op10 = b[:10]
    if op10 in opcode_map:
        mnem, _ = opcode_map[op10]
        imm = int(b[10:22],2)
        Rn  = int(b[22:27],2)
        Rd  = int(b[27:32],2)
        return f"{mnem} X{Rd}, X{Rn}, #{imm}"

    # 4) IM-type (9-bit opcode)
    op9 = b[:9]
    if op9 in opcode_map:
        mnem, _ = opcode_map[op9]
        hw  = int(b[9:11],2)
        imm = int(b[11:27],2)
        Rd  = int(b[27:32],2)
        return f"{mnem} X{Rd}, #{imm << (hw*16)}"

    # 5) B-type (6-bit opcode)
    op6 = b[:6]
    if op6 in opcode_map:
        mnem = opcode_map[op6][0]
        disp = int(b[6:32],2) << 2
        # sign-extend 26→32
        if disp & (1<<25): disp -= (1<<26)
        return f"{mnem} #{disp}"

    # 6) CB-type (8-bit opcode)
    op8 = b[:8]
    if op8 in opcode_map:
        mnem = opcode_map[op8][0]
        disp = int(b[8:27],2) << 2
        if disp & (1<<18): disp -= (1<<19)
        Rt = int(b[27:32],2)
        return f"{mnem} X{Rt}, #{disp}"

    # unknown
    return f".word 0x{h.upper()}  // unknown"

# -----------------------------------------------------------------------------
# CLI wrapper
# -----------------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: legv8_disasm.py <HEX1> [<HEX2> …]")
        sys.exit(1)
    for tok in sys.argv[1:]:
        asm = decode_inst(tok)
        print(f"{tok.upper():>10}  →  {asm}")

if __name__=="__main__":
    main()
