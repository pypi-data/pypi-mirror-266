"""
Absfuyu: Obfuscator
-------------------
Obfuscate code

Version: 2.0.2
Date updated: 05/04/2024 (dd/mm/yyyy)
"""

# Module level
###########################################################################
__all__ = ["Obfuscator"]


# Library
###########################################################################
import base64
import codecs
import random
import zlib

from absfuyu.general.data_extension import Text
from absfuyu.general.generator import Charset
from absfuyu.general.generator import Generator as gen
from absfuyu.logger import logger


# Class
###########################################################################
class ObfuscatorLibraryList:
    BASE64_ONLY = ["base64"]
    FULL = ["base64", "codecs", "zlib"]


class Obfuscator:
    """Obfuscate code"""

    def __init__(
        self,
        code: str,
        *,
        base64_only: bool = False,
        split_every: int = 60,
        variable_length: int = 12,
        fake_data: bool = False,
    ) -> None:
        """
        code: Code text
        base64_only: False: base64, compress, rot13 (default) | True: encode in base64 form only
        split_every: Split the long line of code every `x` character
        variable_length: Length of variable name (when data string split). Minimum is 7
        fake_data: Generate additional meaningless data
        """
        self.base_code = code
        self.base64_only = base64_only
        self.split_every_length = split_every
        self.variable_length = variable_length if variable_length > 6 else 7
        self.fake_data = fake_data

        # Setting
        self._library_import_variable_length = self.variable_length - 1
        self._splited_variable_length = self.variable_length
        self._decode_variable_length = self.variable_length + 3
        # logger.debug("Class initiated.")

    def __str__(self) -> str:
        # temp = self.__dict__
        temp = {
            "base_code": "...",
            "base64_only": self.base64_only,
            "split_every_length": self.split_every_length,
            "variable_length": self.variable_length,
            "fake_data": self.fake_data,
        }
        return f"{self.__class__.__name__}({temp})"

    def __repr__(self) -> str:
        return self.__str__()

    def to_single_line(self) -> str:
        """
        Convert multiple lines of code into one line

        :returns: Converted code
        :rtype: str
        """
        newcode = self.base_code.encode("utf-8").hex()
        logger.debug(newcode)
        output = f"exec(bytes.fromhex('{newcode}').decode('utf-8'))"
        return output

    def _obfuscate(self) -> str:
        """
        Convert multiple lines of code through multiple transformation
        (base64 -> compress -> base64 -> caesar (13))
        """
        code = self.base_code
        logger.debug("Encoding...")

        b64_encode = base64.b64encode(code.encode())
        if self.base64_only:
            output = b64_encode.decode()
        else:
            compressed_data = zlib.compress(b64_encode)
            # log_debug(compressed_data)
            logger.debug(f"Compressed data: {compressed_data}")  # type: ignore
            b64_encode_2 = base64.b64encode(compressed_data)
            # log_debug(b64_encode_2)
            logger.debug(f"Base64 encode 2: {b64_encode_2}")  # type: ignore
            caesar_data = codecs.encode(b64_encode_2.decode(), "rot_13")
            output = caesar_data

        logger.debug(f"Output: {output}")
        logger.debug("Code encoded.")
        return output

    @staticmethod
    def _convert_to_base64_decode(text: str, raw: bool = False) -> str:
        """
        Convert text into base64 and then return a code that decode that base64 code

        text: Code that need to convert
        raw: Return hex form only
        """
        encode_codec = "rot_13"
        b64_encode_codec = base64.b64encode(encode_codec.encode()).decode()
        b64_decode_codec = f"base64.b64decode('{b64_encode_codec}'.encode())"
        hex = Text(b64_decode_codec).to_hex()
        out = f"eval('{hex}').decode()"
        if raw:
            return hex
        return out

    def _obfuscate_out(self) -> list:  # type: ignore
        """
        Convert multiple lines of code through multiple transformation
        (base64 -> compress -> base64 -> caesar (13))

        Then return a list (obfuscated code) that can
        be print or export into .txt file
        """
        # Obfuscated code
        input_str = Text(self._obfuscate())

        # Generate output
        output = []

        # Import library
        library_list = (
            ObfuscatorLibraryList.BASE64_ONLY
            if self.base64_only
            else ObfuscatorLibraryList.FULL
        )
        temp = [f"import {lib}" for lib in library_list]
        logger.debug(f"Lib: {temp}")
        lib_hex = Text("\n".join(temp)).to_hex()  # Convert to hex
        output.append(f"exec('{lib_hex}')")
        logger.debug(f"Current output (import library): {output}")

        # Append divided long text list
        input_list = input_str.divide_with_variable(
            split_size=self.split_every_length,
            split_var_len=self._splited_variable_length,
        )
        encoded_str = input_list[-1]  # Main var name that will later be used
        output.extend(input_list[:-1])  # Append list minus the last element
        logger.debug(f"Current output (encoded code): {output}")

        # Decode: encoded_str
        dc_name_lst = gen.generate_string(
            charset=Charset.ALPHABET, size=self._decode_variable_length, times=3
        )
        encode_codec = "rot_13"  # full
        if not self.base64_only:  # full
            hex_0 = self._convert_to_base64_decode(encode_codec)
            output.append(f"{dc_name_lst[0]}={hex_0}")
        hex_1 = Text("<string>").to_hex()
        output.append(f"{dc_name_lst[1]}='{hex_1}'")
        hex_2 = Text("exec").to_hex()
        output.append(f"{dc_name_lst[2]}='{hex_2}'")
        logger.debug(f"Current output (decode variables): {output}")

        if self.base64_only:  # b64
            pre_hex = (
                f"eval(compile(base64."
                f"b64decode({encoded_str}),{dc_name_lst[1]},"
                f"{dc_name_lst[2]}))"
            )
        else:  # full
            pre_hex = (
                f"eval(compile(base64."
                f"b64decode(zlib.decompress(base64."
                f"b64decode(codecs."
                f"encode({encoded_str},{dc_name_lst[0]})."
                f"encode()))),{dc_name_lst[1]},{dc_name_lst[2]}))"
            )
        t_hex = Text(pre_hex).to_hex()
        output.append(f"exec('{t_hex}')")
        logger.debug(f"Current output (decode code): {output}")

        # Fake data
        if self.fake_data:
            f1 = gen.generate_string(
                charset=Charset.DEFAULT,
                size=len(input_str),
                times=1,
                string_type_if_1=True,
            )  # Generate fake data with len of original data
            f2 = Text(f1).divide_with_variable(
                self.split_every_length, self._splited_variable_length
            )
            output.extend(f2[:-1])

            # Random data
            bait_lst = gen.generate_string(
                charset=Charset.ALPHABET, size=self._splited_variable_length, times=25
            )
            for x in bait_lst:
                output.append(
                    f"{x}='{gen.generate_string(charset=Charset.DEFAULT,size=self.split_every_length,times=1,string_type_if_1=True)}'"
                )

            random_eval_text = str(random.randint(1, 100))
            for _ in range(random.randint(10, 50)):
                random_eval_text += f"+{random.randint(1, 100)}"
            random_eval_text_final = Text(random_eval_text).to_hex()
            output.append(f"eval('{random_eval_text_final}')")

        logger.debug("Code obfuscated.")
        return output

    def obfuscate(self) -> str:
        """
        Obfuscate code

        :returns: Obfuscated code
        :rtype: str
        """
        return "\n".join(self._obfuscate_out())


# Run
###########################################################################
if __name__ == "__main__":
    logger.setLevel(10)
    code = "print('Hello World')"
    test = Obfuscator(code, fake_data=True)
    print(test.obfuscate())
