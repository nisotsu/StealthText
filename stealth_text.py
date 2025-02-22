import argparse
import mimetypes
import base64

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="あらゆるデータをテキストに埋め込むプログラム."
    )
    
    # 通常時の入力
    parser.add_argument("target_string", nargs='*', help="encode:データを隠したい文字列, decode:データが隠された文字列 を指定.")
    
    # 読み込みファイルの位置を指定するオプション引数
    parser.add_argument(
        "-i", "--input-file",
        type=str,
        help="読み込みファイルのパス."
    )
    
    # 圧縮するか否かを指定するオプション引数（存在する場合のみ圧縮）
    parser.add_argument(
        "-c", "--compress",
        action="store_true",
        help="隠すデータを圧縮するか否かの指定."
    )
    
    # エンコード/デコードを指定する引数
    # 明示的に --encode, --decode を指定でき、何も指定しなければエンコードがデフォルト
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--encode",
        dest="mode",
        action="store_const",
        const="encode",
        help="エンコードを実行する（デフォルト）."
    )
    group.add_argument(
        "--decode",
        dest="mode",
        action="store_const",
        const="decode",
        help="デコードを実行する."
    )
    parser.set_defaults(mode="encode")
    
    # 解凍するか否かを指定するオプション引数（存在する場合のみ解凍）
    parser.add_argument(
        "-d", "--decompress",
        action="store_true",
        help="圧縮された隠しデータを解凍する."
    )
    
    # 書き込みファイルの位置を指定するオプション引数
    parser.add_argument(
        "-o", "--output-file",
        type=str,
        help="書き込みファイルのパス."
    )

    # バイナリで書き込むか否かを指定するオプション引数
    parser.add_argument(
        "-b", "--binary-write",
        action="store_true",
        help="バイナリで出力するかの指定."
    )
    
    return parser.parse_args()

def byte_to_variation_selector(byte: int) -> str:
    if byte < 16:
        return chr(0xFE00 + byte)
    else:
        return chr(0xE0100 + (byte - 16))

def encode(base: str, s: str) -> str:
    if not base:
        raise('target_string is none.')
    vs_list = []
    byte_list = string_to_bytes(s)
    q = len(byte_list) // len(base)
    r = len(byte_list) % len(base)
    pv = 0
    count = 0
    tmp_list = []
    result = ""
    if len(byte_list) < len(base):
        raise('Hidden string is too short')
    for i in range(1,len(byte_list)+1):
        tmp_list.append(byte_to_variation_selector(byte_list[pv]))
        if pv >= len(byte_list)-1:
            if tmp_list:
                vs_list.append(tmp_list) 
            break
        if i%q == 0 and count < r:
            count += 1
            pv += 1
            tmp_list.append(byte_to_variation_selector(byte_list[pv]))
            vs_list.append(tmp_list)
            tmp_list = []
        elif i%q == 0:
            vs_list.append(tmp_list)
            tmp_list = []
        pv += 1

    for i,b in enumerate(base):
        result += b + ''.join(vs_list[i])

    return result

def string_to_bytes(s: str) -> list:
    byte_list = list(s.encode('utf-8'))
    return byte_list

def variation_selector_to_byte(variation_selector: str) -> int | None:
    vs = ord(variation_selector)
    if 0xFE00 <= vs <= 0xFE0F:
        return vs - 0xFE00
    elif 0xE0100 <= vs <= 0xE01EF:
        return vs - 0xE0100 + 16
    else:
        return None

def decode(variation_selectors: str) -> list[int]:
    if not variation_selectors:
        raise('target_string is none.')
    result = []
    for ch in variation_selectors:
        byte = variation_selector_to_byte(ch)
        if byte is not None:
            result.append(byte)

    return bytes_to_string(result)

def bytes_to_string(byte_list: list[int]) -> str:
    s = bytes(byte_list).decode('utf-8')
    return s

def is_text_file(file_path):
    mime_type = mimetypes.guess_type(file_path)[0]
    return mime_type is not None and mime_type.startswith("text")

if __name__ == '__main__':
    args = parse_arguments()
    # target_str
    # encodeのとき: hidden_dataを隠す文字列
    # decodeのとき: hidden_dataが隠された文字列
    if args.target_string:
        target_str = args.target_string[0]
    if args.mode == 'encode':
        if args.input_file:
            if is_text_file(args.input_file):
                with open(args.input_file, mode='r', encoding='utf-8') as f:
                    hidden_data = f.read()
                    print(hidden_data)
            else:
                with open(args.input_file, mode='br') as f:
                    hidden_data = f.read()
                    hidden_data = base64.b64encode(hidden_data).decode('utf-8')
                    print(hidden_data)
        else:
            hidden_data = input('Hidden string:')
        result = encode(target_str, hidden_data)
        if args.output_file:
            with open(args.output_file, mode='w', encoding='utf-8') as f:
                f.write(result)
        else:
            print(result)
    elif args.mode == 'decode':
        if args.input_file:
            with open(args.input_file, mode='r', encoding='utf-8') as f:
                target_str = f.read()
        result = decode(target_str)
        if args.output_file:
            if args.binary_write:
                with open(args.output_file, mode='bw') as f:
                    result = base64.b64decode(result)
                    f.write(result)
            else:
                with open(args.output_file, mode='w', encoding='utf-8') as f:
                    f.write(result)
        else:
            print(result)