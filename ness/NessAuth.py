from base64 import b64encode
from base64 import b64decode
from base64 import b32encode
from base64 import b32decode
from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.public import PrivateKey, PublicKey, SealedBox
import json
import urllib.parse
import requests


class NessAuth:

    def get_by_auth_id(self, node_full_url: str, user_private_key: str, node_url: str, node_nonce: str, username: str, shadowname: str,
                       user_nonce: str):
        """
        Authenticate user by Authentication ID and return data from the node
        
        :param node_full_url: The full URL of the node you're querying
        :type node_full_url: str
        :param user_private_key: The private key of the user who is trying to authenticate
        :type user_private_key: str
        :param node_url: The URL of the node you're connecting to
        :type node_url: str
        :param node_nonce: cryptographic salt
        :type node_nonce: str
        :param username: The username of the user who is connecting to node
        :type username: str
        :param user_nonce: cryptographic salt
        :type user_nonce: str
        :return: Data returned by the node.
        """
        auth_id = self.auth_id(user_private_key, node_url, node_nonce, username, user_nonce)
        url = node_full_url + "/" + shadowname + "/" + urllib.parse.quote_plus(auth_id)
        # print (url, auth_id)
        return json.loads(requests.get(url, verify=False).text)

    def post_data_by_auth_id(self, data: bytes, node_full_url: str, user_private_key: str, node_url: str, node_nonce: str, username: str, shadowname: str,
                       user_nonce: str):
        auth_id = self.auth_id(user_private_key, node_url, node_nonce, username, user_nonce)

        url = node_full_url + "/" + shadowname + "/" + urllib.parse.quote_plus(auth_id)
        result = requests.post(url, data = data, verify=False).text
        return json.loads(result)

    def get_responce_by_auth_id(self, node_full_url: str, user_private_key: str, node_url: str, node_nonce: str, username: str, shadowname: str,
                       user_nonce: str, headers):
        auth_id = self.auth_id(user_private_key, node_url, node_nonce, username, user_nonce)

        url = node_full_url + "/" + shadowname + "/" + urllib.parse.quote_plus(auth_id)
        return requests.get(url, headers=headers, stream=True, verify=False)


    def get_by_two_way_encryption(self, node_full_url: str, data: str, node_public_key: str, user_private_key: str,
                                  username: str, additional_params = {}):
        """
        Authenticate user by Two-Way encription and return data from the node
        
        :param node_full_url: The full url of the node you want to get data from
        :type node_full_url: str
        :param data: The data you want to send to the node
        :type data: str
        :param node_public_key: The public key of the node you're sending the data to
        :type node_public_key: str
        :param user_private_key: The private key of the user who is requesting the data
        :type user_private_key: str
        :param username: The username of the user who is requesting the data
        :type username: str
        :return: Data returned by the node..
        """
        encrypted_data = self.encrypt(data, node_public_key)
        signature = self.sign(user_private_key, encrypted_data)

        url = node_full_url
        params = {'data': encrypted_data, 'sig': signature, 'username': username}
        params.update(additional_params)

        return json.loads(
            requests.post(url, params, verify=False).text
        )

    def verify_two_way_result(self, node_verify_key: str, result: dict):
        """
        Verify the signature of the data in the result dictionary using the node's verify key
        
        :param node_verify_key: The verify key of the node you're sending the request to
        :type node_verify_key: str
        :param result: Data returned by the node
        :type result: dict
        :return: The result of the verification.
        """
        return self.verify(node_verify_key, result['data'], result['sig'])

    def decrypt_two_way_result(self, result: dict, user_private_key: str):
        """
        Decrypt  the data in the result dictionary using user's private key
        
        :param result: Data returned by the node
        :type result: dict
        :param user_private_key: The private key of the user that you want to decrypt the data for
        :type user_private_key: str
        :return: The decrypted data.
        """
        return self.decrypt(b64decode(result['data']), user_private_key)

    def auth_id(self, private_key: str, node_url, node_nonce: str, username: str, user_nonce: str):
        """
        `auth_id` returns Authentication ID neede for user to authenticate to node
        
        :param private_key: The private key of the user
        :type private_key: str
        :param node_url: The URL of the node you're connecting to
        :param node_nonce: cryptographic salt
        :type node_nonce: str
        :param username: The username of the user you want to authenticate
        :type username: str
        :param user_nonce: cryptographic salt
        :type user_nonce: str
        :return: The auth_id is being returned.
        """
        message = node_url + "-" + node_nonce + "-" + username + '-' + user_nonce
        return self.sign(private_key, message)

    def alternative_id(self, private_key: str, node_url, node_nonce: str, username: str, user_nonce: str):
        """
        `auth_id` returns Authentication ID neede for user to authenticate to node
        
        :param private_key: The private key of the user
        :type private_key: str
        :param node_url: The URL of the node you're connecting to
        :param node_nonce: cryptographic salt
        :type node_nonce: str
        :param username: The username of the user you want to authenticate
        :type username: str
        :param user_nonce: cryptographic salt
        :type user_nonce: str
        :return: The auth_id is being returned.
        """
        message = node_url + "-" + node_nonce + "-" + username + '-' + user_nonce + '-alternative'
        return self.sign(private_key, message)

    def sign(self, private_key: str, data: str):
        """
        It takes a private key and a string of data, and returns a signature
        
        :param private_key: The private key for signing the data
        :type private_key: str
        :param data: The data to be signed
        :type data: str
        :return: The signature of the data.
        """
        signing_key = SigningKey(b64decode(private_key))
        signed = signing_key.sign(data.encode('utf-8'))
        return b32encode(signed.signature).decode('utf-8')

    def verify(self, verify_key: str, data: str, sig: str):
        """
        It takes a base64 encoded public key, a string of data, and a base32 encoded signature, and
        returns True if the signature is valid for the data and public key, and False otherwise
        
        :param verify_key: The public key of the user or node who signed the data
        :type verify_key: str
        :param data: The data to be signed
        :type data: str
        :param sig: The signature of the data
        :type sig: str
        :return: True or False
        """
        # print(verify_key, data, sig)
        verify_key = VerifyKey(b64decode(verify_key))
        return verify_key.verify(data.encode('utf-8'), b32decode(sig))

    def encrypt(self, data: str, public_key: str):
        """
        It encrypts the data using the public key.
        
        :param data: The data to be encrypted
        :type data: str
        :param public_key: The public key for encrypting data
        :type public_key: str
        :return: The encrypted data.
        """
        public_key = PublicKey(b64decode(public_key))
        box = SealedBox(public_key)
        return b64encode(box.encrypt(data.encode('utf-8'))).decode('utf-8')

    def decrypt(self, encrypted_data: str, private_key: str):
        """
        It decrypts the encrypted data using the private key.
        
        :param encrypted_data: The encrypted data that you want to decrypt
        :type encrypted_data: str
        :param private_key: The private key for decrypting the data
        :type private_key: str
        :return: The decrypted data.
        """
        private_key = PrivateKey(b64decode(private_key))
        sb = SealedBox(private_key)
        text = sb.decrypt(encrypted_data)
        return text.decode('utf-8')