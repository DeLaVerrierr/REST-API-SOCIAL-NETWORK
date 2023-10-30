from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
import json

private_keys_file = 'private_keys.json'

def save_to_private_keys(data):
    try:
        with open(private_keys_file, 'r') as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.append(data)

    with open(private_keys_file, 'w') as file:
        json.dump(existing_data, file)



def load_private_key_from_data(private_key_base64):
    private_key_pem = base64.b64decode(private_key_base64)
    private_key = serialization.load_pem_private_key(private_key_pem, password=None, backend=default_backend())
    return private_key


def load_public_key_from_pem(pem_bytes):
    # Сериализируем публичный ключ формата PEM
    public_key = serialization.load_pem_public_key(pem_bytes, backend=default_backend())
    return public_key

def encrypt_test(message, public_key):
    """
    Шифровка сообщение
    """
    # Сериализация ключа из базы
    public_key = load_public_key_from_pem(public_key)
    encrypted_message = public_key.encrypt(
        message.encode('utf-8'),  # Переводим текст в байты
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_message



def load_private_key_from_file(user_id):
    with open(private_keys_file, 'r') as file:
        private_keys = json.load(file)

    for user_list in private_keys:
        for user_info in user_list:
            if user_info.get("user_id") == user_id:
                private_key_data = user_info.get("private_key")
                #private_key = load_private_key_from_data(private_key_data)
                return private_key_data
    return None



def decrypt_test(encrypted_message, private_key):
    """
    Расшифровка сообщение
    """
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_message

def generate_rsa_key_pair():
    # Генерация ключей
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    return private_key, public_key





# Юзер айди
user_id = 2
#Генерация публичного и приватного ключа
private_key, public_key_user = generate_rsa_key_pair()
# Сохранение пбличного в базу
public_key_user = public_key_user.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
# перевод Приватного ключа в str
private_key_base64 = base64.b64encode(private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)).decode('utf-8')

# Патерн сохранение
private_key_data = [{"user_id": user_id, "private_key": private_key_base64}]
# сохранение ключа в json
save_to_private_keys(private_key_data)




#Сообщение которое надо зашифровать
message = 'Hello !'
# Шифрем его передаем сообщение и публичный ключ из базы
message_cript = encrypt_test(message, public_key_user)


# Получаем из json файла приватный ключ
key_from_json = load_private_key_from_file(user_id)
print(f"Получаем приватный ключ str из json {key_from_json}")
# Делаем из него объект криптографии
private_key = load_private_key_from_data(key_from_json)
print(f"Делаем из str объект криптографии {private_key}")
#расшифровываем сообщение с приватным ключом
print(f"Сообщение которое надо расшифровать {message_cript}")
print(f"Приватный ключ который мы используем для расшифровки {private_key}")
message_result = decrypt_test(message_cript, private_key)
print(f'Расшифрованное сообщение {message_result}')



# Из бд мы кидаем строку и делаем из нее байты
# def byte_string(string):
#     hex_string = string.replace('\\x', '').replace(' ', '')
#
#     # Преобразование в байтовую строку
#     byte_string = binascii.unhexlify(hex_string)
#     return byte_string

