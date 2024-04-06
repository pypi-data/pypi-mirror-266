import random
import re
import string
import base64
import hashlib
import ast
import xml.etree.ElementTree as ET

from ...const.common import CommonTypeUsageConst, StringFormatConst
from .path_util import PathUtil

class StringUtil:

    @staticmethod
    def generate_random_number(length: int = 5) -> int:
        """
        Example: 12312312312
        """
        text = ""
        for _ in range(length):
            text += f"{random.choice(string.digits)}"
        return int(text)

    @staticmethod
    def generate_random_string(number_words: int = 5, is_contain_space: bool = False, is_upper_case: bool = False) -> str:
        text = ""
        alphabet = string.ascii_lowercase if not is_upper_case else string.ascii_uppercase

        if is_contain_space:
            for _ in range(number_words):
                new_length = random.randrange(1, number_words)
                text += ''.join(random.choice(alphabet)
                                for _ in range(new_length)) + ' '
        else:
            text = ''.join(random.choice(alphabet)
                           for _ in range(number_words))
        return text

    @staticmethod
    def generate_random_number_string(number_words: int = 5, is_contain_space: bool = False, is_upper_case: bool = False) -> str:
        text :str = ""
        alphabet = string.ascii_lowercase if not is_upper_case else string.ascii_uppercase
        number = string.digits

        if is_contain_space:
            for _ in range(number_words):
                new_length = random.randrange(1, number_words)
                text += ''.join(random.choice(alphabet) + random.choice(number)
                                for _ in range(new_length)) + ' '
        else:
            text = ''.join(random.choice(alphabet) + random.choice(number)
                           for _ in range(number_words))[:number_words]
        return text

    @staticmethod
    def generate_random_special_characters(number_words: int = 5, is_contain_space: bool = False) -> str:
        text = ""
        alphabet = string.punctuation
        number = string.digits

        if is_contain_space:
            for _ in range(number_words):
                new_length = random.randrange(1, number_words)
                text += ''.join(random.choice(alphabet) + random.choice(number)
                                for _ in range(new_length)) + ' '
        else:
            text = ''.join(random.choice(alphabet) + random.choice(number)
                           for _ in range(number_words))[:number_words]
        return text

    @staticmethod
    def generate_random_text_by_type(text_tp: str, number_words: int = 5, is_combine: bool = False, is_contain_space: bool = False, is_upper_case: bool = False):
        if is_combine:
            return StringUtil.generate_random_number_string(number_words=number_words, is_contain_space=is_contain_space, is_upper_case=is_upper_case)
        if text_tp == 'str':
            return StringUtil.generate_random_string(number_words=number_words, is_contain_space=is_contain_space, is_upper_case=is_upper_case)
        elif text_tp == 'int':
            return StringUtil.generate_random_number(length=number_words)
        else:
            return StringUtil.generate_random_special_characters(number_words=number_words, is_contain_space=is_contain_space)

    @staticmethod
    def decode_str(data):
        """
        Convert encoded string to base64 string
        :return: string in byte format
        """
        decoded = base64.b64decode(data)
        return decoded.decode().encode()

    @staticmethod
    def base64_encode_text(data):
        """
        Convert string to base64 string
        :return: string in base64 format
        """
        return base64.b64encode(data.encode(encoding='utf-8'))

    @staticmethod
    def base64_decode_text(encoded_data: bytes):
        """
        Convert string to base64 string
        :return: string
        """
        return base64.b64decode(encoded_data).decode(encoding='utf-8')

    @staticmethod
    def format_string_with_re(re_format, value, repl: str = CommonTypeUsageConst.EMPTY):
        return re.sub(re_format, repl, value)

    @staticmethod
    def remove_all_except_text(value):
        return StringUtil.format_string_with_re(StringFormatConst.REMOVE_ALL_CHARACTERS_EXCEPT_TEXT, value)

    @staticmethod
    def convert_string_to_md5(text) -> str:
        """
            convert string to hash md5 hexstring
            :var text: input as string
            :return: md5 hashed string
        """
        result = hashlib.md5(text.encode())
        return result.hexdigest()

    @staticmethod
    def remove_space(value):
        """
        remove start space and end space
        :return: string
        """
        return re.sub(' +', ' ', value.lstrip(" ").rstrip(" "))

    @staticmethod
    def is_sorted(my_list: list, condition: str = 'asc') -> bool:
        if condition.lower() == 'asc':
            return all(my_list[i] <= my_list[i + 1] for i in range(len(my_list) - 1))
        elif condition.lower() == 'desc':
            return all(my_list[i] >= my_list[i+1] for i in range(len(my_list)-1))
        else:
            raise f'Do not support condition: {condition}. Valid value must be asc or desc!'

    @staticmethod
    def split_the_list(input_list: list = None, list_length: int = 50) -> dict:
        smaller_lists = {}

        for i in range(len(input_list) // list_length):
            smaller_lists[i] = input_list[i * list_length: (i + 1) * list_length]

        # Handling any remaining items
        if len(input_list) % list_length != 0:
            smaller_lists[len(input_list) // list_length] = input_list[(
                len(input_list) // list_length) * list_length:]

        return smaller_lists

    @staticmethod
    def convert_string_like_list_to_list(input_str: str) -> list:
        try:
            return ast.literal_eval(input_str)
        except Exception as e:
            raise f"Input str not in the string like list format {input_str}"
        
    @staticmethod
    def generate_random_phone_with_prefix(prefix: str = '090') -> str:
        return f'{prefix}{StringUtil.generate_random_number(length=7)}'
    

    @staticmethod
    def generate_random_tkgt() -> str:
        return f'E0{StringUtil.generate_random_number(length=8)}'
    
    @staticmethod
    def generate_random_pwd(length: int = 6) -> str:
        """_summary_

        Args:
            length (int, optional): the password length that you want to generated. Defaults to 8.

        Raises:
            ValueError: in case the requested length did not meet the requirement

        Returns:
            str: password. e.g V-zusp@y9=mI
        """
        if not length >= 6:
            raise ValueError('Generated pwd length must be from 6 or above')
            # Define character sets
        uppercase_letters = string.ascii_uppercase
        lowercase_letters = string.ascii_lowercase
        digits = string.digits
        # special_characters = string.punctuation
        special_characters = "@,!,#,$,%,&,',*,+,-,/,=,?,^,_,`,{,|,},~"

        # Combine character sets
        all_chars = uppercase_letters + lowercase_letters + digits + special_characters

        # Ensure at least one character from each set
        pwd = (
            random.choice(uppercase_letters) +
            random.choice(lowercase_letters) +
            random.choice(digits) +
            random.choice(special_characters) +
            ''.join(random.choice(all_chars) for _ in range(length - 4))
        )
        return pwd
    
    @staticmethod
    def params_parser(is_dict: bool = True, **kwargs) -> str | dict:
        """_summary_

        Args:
            kwargs: abc=def, abd=dfe

        Returns:
            str = abc=def&abd=df
            dict = {
                'abc'='def',
                'abd'='dfe'
            }
        """
        if is_dict:
            tmp = {}
            for x in [{k: v} for k, v in kwargs.items() if (v and v != '')]:
                tmp |= x
        else:
            tmp = '&'.join(f'{k}={v}' for k, v in kwargs.items())
        return tmp

    @staticmethod
    def validate_amount_string(input_str: str = None, sep: str = '.', currency: str = 'đ') -> bool | int:
        """_summary_

        Args:
            input_str (str, optional): string that need to check. Defaults to None. the format will be follow 'xxx.xxx.xxx currency'
            sep (str, optional): the separator character, support only: '.' and ','
            currency (str, optional): the currency character that need to check. Defaults to 'đ'.

        Returns:
            bool | int: if valid it will return the number (string formated as int16)
        """
        # Define the regex pattern
        pattern = r'^(\d{1,3}(?:\%(sep)s\d{3})*)' % {'sep': sep} + re.escape(currency)

        # Compile the regex pattern
        regex = re.compile(pattern)

        # Match the input string against the pattern
        match = regex.match(input_str)

        # Check if the input string matches the pattern
        if match:
            # Extract the number part and remove the dots
            number = match.group(1).replace(sep, '')
            return int(number)
        else:
            return False

    @staticmethod
    def parse_int_to_currency_format(input_int: int, sep: str = '.'):
        # Convert the integer to a string with commas for thousands separator
        formatted_amount = "{:,.0f}đ".format(input_int)
        # Concatenate the currency symbol
        return formatted_amount.replace(',', sep)

    @staticmethod
    def parse_xml_to_string(xml_file_path: str):
        """_summary_

        Args:
            xml_file_path (str): the location of the xml file

        Returns:
            _type_: parsing the xml's content into string
        """
        
        with open((PathUtil.join_prj_root_path(xml_file_path)), "r") as my_input_xml:
            return my_input_xml.read()

