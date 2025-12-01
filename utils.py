import jaconv
import re
import unicodedata

class CommonUtils:
    @staticmethod
    def normalize_text(text):
        """
        テキストに対して、空白の削除並びに半角全角の統一を行う
        """        
        if not isinstance(text, str):
            raise ValueError("入力は文字列である必要があります")
        
        # jaconvで変換されない記号を手動で置換
        symbol_map = {
            '・': '･', # 全角中黒 → 半角中黒
            '·' : '･', # 中点 → 半角中黒
            '（': '(',
            '）': ')',
            '【': '[',
            '】': ']',
        }
        for k, v in symbol_map.items():
            text = text.replace(k, v)
        
        # NFKC正規化
        normalized = unicodedata.normalize('NFKC', jaconv.z2h(text, ascii=True, digit=True, kana=True))

        # 全ての空白文字を削除
        normalized = re.sub(r'\s+', '', normalized)
        return normalized
    
    def to_half_angle(text):
        """
        全角→半角
        """
        if text is None:
            text = ""

        text = unicodedata.normalize('NFKC', text.strip())

        # jaconvで変換されない記号を手動で置換
        symbol_map = {
            '・': '･', # 全角中黒 → 半角中黒
            '·' : '･', # 中点 → 半角中黒
            '（': '(',
            '）': ')',
            '【': '[',
            '】': ']',
        }
        for k, v in symbol_map.items():
            text = text.replace(k, v)
        
        return jaconv.z2h(text, ascii=True, digit=True, kana=True)
    
    @staticmethod
    def to_full_angle(text):
        """
        半角→全角
        """
        if text is None:
            text = ""

        # jaconvで変換されない記号を手動で置換
        symbol_map = {
            '･': '・', # 半角中黒 → 全角中黒
            '(': '（',
            ')': '）',
            '[': '【',
            ']': '】',
        }
        for k, v in symbol_map.items():
            text = text.replace(k, v)
        
        return jaconv.h2z(text, ascii=True, digit=True, kana=True)

    @staticmethod
    def extract_first_number_as_int(text):
        """
        テキストから数字を抽出し、1つ目の数字をint型で返す
        """
        numbsers = CommonUtils.extract_numbers(text)
        if numbsers:
            return int(numbsers[0])
        return None

    @staticmethod
    def extract_first_number_as_float(text):
        """
        テキストから数字を抽出し、1つ目の数字をfloat型で返す
        """
        numbsers = CommonUtils.extract_numbers(text)
        if numbsers:
            return float(numbsers[0])
        return None

    @staticmethod
    def extract_first_number_as_str(text):
        """
        テキストから数字を抽出し、1つ目の数字をstr型で返す
        """
        if text is None:
            text = ""
        candidates = re.findall(r'[-0-9,.]+', text)
        for s in candidates:
            if not s:
                continue
            if s.count('.') > 1:
                continue
            if s.count('-') > 1:
                continue
            if '-' in s and s.find('-') != 0:
                continue
            if s.startswith('.'):
                continue
            if s.startswith(','):
                continue
            if s.startswith('-,'):
                continue
            if ',' in s:
                pattern = r'^-?\d{1,3}(,\d{3})*(\.\d+)?$'
                if not re.match(pattern, s):
                    continue
            clean_s = s.replace(',', '')
            if not any(ch.isdigit() for ch in clean_s):
                continue
            return s
        return None
    
    @staticmethod
    def extract_numbers(text: str) -> list:
        """
        文字列から特定の規則に適合する数値を抽出します。
        
        規則の概要:
        1. 使用可能な文字は [-], [,], [.], [0-9]。
        2. 妥当性チェック:
        - 先頭が [.] または [,] または [-,] であってはならない。
        - [.] と [-] の個数はそれぞれ 1 を超えてはならない。
        - [-] がある場合は先頭でなければならない。
        - [,] を含む場合は千位区切り形式に一致する必要がある（例: 1,234.56）。
        3. 型変換:
        - [.] を含む場合は float に変換。
        - それ以外は int に変換。
        """
    
        # 1. 予備抽出: 数字と特定記号からなる連続ブロックを取得
        # 正規表現 [-0-9,.]+ で候補を抽出
        candidates = re.findall(r'[-0-9,.]+', text)
        
        valid_numbers = []
        
        
        for s in candidates:
            # --- 2. 不正な数値判定（基本規則） ---
            
            # 空文字列を除外（念のため）
            if not s:
                continue
                
            # 規則: [.] の個数が1を超える（例: 127.0.0.1 -> 不正）
            if s.count('.') > 1:
                continue
                
            # 規則: [-] の個数が1を超える（例: --1 -> 不正）
            if s.count('-') > 1:
                continue
                
            # 規則: [-] がある場合は先頭でなければならない
            if '-' in s and s.find('-') != 0:
                continue
                
            # 規則: [.] は先頭に置けない（例: .67 -> 不正）
            if s.startswith('.'):
                continue
                
            # 規則: [,] は先頭に置けない（例: ,67 -> 不正）
            if s.startswith(','):
                continue
                
            # 規則: [-,] は先頭に置けない（例: "-,67" は不可）
            if s.startswith('-,'):
                continue

            # --- 2. 不正な数値判定（カンマ/千位区切り規則） ---
            if ',' in s:
                # 正規表現で千位区切り形式を厳密に照合
                # ^-?       : 先頭に任意の負号
                # \d{1,3}   : 1〜3桁の数字
                # (,\d{3})* : 0個以上の「カンマ+3桁数字」の繰り返し
                # (\.\d+)?$ : 任意の小数部（. の後に1桁以上）で終端
                # 注意: 小数部の数字を必須としない場合は \d+ を \d* に変更可能だが、一般的には . の後に数字が必要
                pattern = r'^-?\d{1,3}(,\d{3})*(\.\d+)?$'
                if not re.match(pattern, s):
                    continue

            # --- 3. 特例処理と型変換 ---
            
            # 変換に備えてカンマを除去
            clean_s = s.replace(',', '')
            
            try:
                # 数字を含むこと（"-" や "." のみのケースを排除）
                if not any(char.isdigit() for char in clean_s):
                    continue

                if '.' in clean_s:
                    # 場合: [.] を含む -> そのままでもカンマ除去後でも float を使用
                    num_val = float(clean_s)
                    valid_numbers.append(num_val)
                else:
                    # 場合: [.] を含まない -> int へ変換を試みる
                    num_val = int(clean_s)
                    valid_numbers.append(num_val)
                        
            except ValueError:
                # 変換に失敗した場合（例: 文字列が "-"）はスキップ
                continue

        return valid_numbers


if __name__ == "__main__":
    # 全角を半角に変換する例
    full_angle_text = "デザイン"
    half_angle_text = CommonUtils.to_half_angle(full_angle_text)
    print("全角を半角に変換した結果：", half_angle_text)

    # 半角を全角に変換する例
    half_angle_text = "Hello,World!12345"
    full_angle_text = CommonUtils.to_full_angle(half_angle_text)
    print("半角を全角に変換した結果：", full_angle_text)

    # テキストから複数の数字を抽出する例
    text_with_numbers = "商品価格：￥1,234,234、数量：5個、割引後の価格：￥1,023.5"
    extracted_numbers = CommonUtils.extract_numbers(text_with_numbers)
    print("抽出した数字：", extracted_numbers)

    text_with_numbers = "商品価格：-1,234,234.90、数量：5個、割引後の価格：-50"
    extracted_numbers = CommonUtils.extract_numbers(text_with_numbers)
    print("抽出した数字：", extracted_numbers)
    # 最初の数字をint型で抽出する例
    first_number_int = CommonUtils.extract_first_number_as_int(text_with_numbers)
    print("最初の数字（int型）：", first_number_int)

    # 最初の数字を文字列型で抽出する例（カンマを保持）
    first_number_str = CommonUtils.extract_first_number_as_str(text_with_numbers)
    print("最初の数字（文字列型、カンマを保持）：", first_number_str)

    test_str = """
    ここにはいくつかの合法な数値があります:
    13,254,600.05（合法な float）
    -13,254,600.05（合法な負の float）
    123（合法な int）
    99999999999999999999999999（非常に大きい整数は）
    
    ここにはいくつかの不正な例があります:
    ,67（不正）
    -,67（不正）
    127.0.0.1（IP は不正）
    .67（先頭が点は不正）
    --1（二重の負号は不正）
    -13,2548,600.05（千位区切りの誤りで不正）
    1,23（カンマの後が桁数未満で不正）
    (100-50)
    """

    valid_numbers = CommonUtils.extract_numbers(test_str)
    print("合法な数値：", valid_numbers)
