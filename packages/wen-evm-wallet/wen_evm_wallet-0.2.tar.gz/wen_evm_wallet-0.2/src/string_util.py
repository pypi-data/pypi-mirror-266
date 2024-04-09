import base64
import random


def form_hex_data(string):
    if not isinstance(string, str):
        raise ValueError('Input must be a string.')

    if len(string) > 64:
        raise ValueError('String length exceeds 64 characters.')

    return '0' * (64 - len(string)) + string


def form_hex_data_behand(string):
    if not isinstance(string, str):
        raise ValueError('Input must be a string.')

    if len(string) > 64:
        raise ValueError('String length exceeds 64 characters.')

    return string + '0' * (64 - len(string))


def to_decimal_number(hex_string):
    return int(hex_string, 16)


def to_string_base64(text):
    encoded_bytes = base64.b64encode(text.encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string


def decode_base64(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string


def generate_random_string(a):
    b = random.randint(1, 9)
    if type(a) is int:
        return float(str(a) + '.' + str(b))

    return float(str(a) + str(b))


if __name__ == '__main__':
    print(generate_random_string(0.2))