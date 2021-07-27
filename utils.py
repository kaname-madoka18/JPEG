from typing import Tuple

"""
convert a unsigned int to binary string with fixed length (add leading zeros)
"""
def int2string(k, length):
    s = ''
    i = 1 << (length-1)
    while i:
        if k & i:
            s += '1'
        else:
            s += '0'
        i >>= 1
    return s

"""
convert binary string to bytes
"""
def string2bytes(s, left_padding=False):
    padding = 8 - (len(s) % 8)
    res = []
    p = 0
    if left_padding:
        res.append(int(s[:8-padding], 2).to_bytes(1, 'little'))
        p = 8-padding
    while p + 8 <= len(s):
        res.append(int(s[p:p+8], 2).to_bytes(1,'little'))
    if p != len:
        res.append(int(s[p:]+'0'*padding, 2).to_bytes(1, 'little'))
    return b''.join(res)

"""
returns encoder, decoder
"""
def parse_huffman_tree(huf_siri: bytes)->Tuple[list, dict]:
    huf_size, huf_value = huf_siri[:16], huf_siri[16:]
    code = 0
    huf_encoder = [""] * 256
    huf_decoder = {}
    cnt = 0
    for i in range(len(huf_size)):
        for j in range(huf_size[i]):
            huf_encoder[huf_value[cnt]] = int2string(code, i+1)
            huf_decoder[code] = huf_value[cnt]
            cnt += 1
            code += 1
        code <<= 1
    return huf_encoder, huf_decoder

"""
calculate the highest bit of unsigned int k
"""
def MSB(k:int):
    cnt = 0
    while k:
        k >>= 1
        cnt += 1
    return cnt

def main():
    from includes import DHT_l_dc
    encoder, decoder = parse_huffman_tree(DHT_l_dc)
    print(encoder, decoder)

if __name__ == "__main__":
    main()