class mfmTool:
    @staticmethod
    def rgb_to_hex(r, g, b) -> str:
        """RGBカラーモデルを16進数のカラーコードに変換します。

        Args:
            r (str): 赤
            g (str): 緑
            b (str): 青

        Returns:
            str: 16進数のカラーコード
        """
        return "{:02x}{:02x}{:02x}".format(r, g, b)

    class fg:
        def color(color: str, text: str) -> str:
            """文字色を変更します。

            Args:
                color (str): 変更したい色の16進数カラーコード
                text (str): 文字色を変えるテキスト

            Returns:
                str: MFM
            """
            return "$[fg.color={} {}]".format(color, text)

    class bg:
        def color(color: str, text: str) -> str:
            """背景色を変更します。

            Args:
                color (str): 変更したい色の16進数カラーコード
                text (str): 背景色を変えるテキスト

            Returns:
                str: MFM
            """
            return "$[bg.color={} {}]".format(color, text)

    def scale(scale: str, text: str) -> str:
        """文字の大きさを変えるMFMを生成します。

        Args:
            scale (str): 大きさ (2, 3, 4以外は変わりません。)
            text (str): 大きさを変えるテキスト

        Returns:
            str: MFM
        """
        return "$[x{} {}]".format(scale, text)

    def blur(text: str) -> str:
        """渡されたテキストをぼかすMFMを生成します。

        Args:
            text (str): ぼかすテキスト

        Returns:
            str: MFM
        """
        return "$[blur {}]".format(text)

    def unixtime(time: int) -> str:
        """指定された数字のunixtimeを表示するMFMを生成します。

        Args:
            time (int): タイムスタンプ

        Returns:
            str: MFM
        """
        return "$[unixtime {}]".format(time)