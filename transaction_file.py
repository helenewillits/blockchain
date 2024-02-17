import json
import hashlib

from transaction import Transaction
from user import User

import nacl.utils
from nacl.public import PrivateKey, Box

# instruction to simulate a set of transactions


def create():
    # Create 5 distinct identities ( public - key pairs )
    user1 = User()
    user2 = User()
    user3 = User()
    user4 = User()
    user5 = User()

    # Create 10 transactions including atleast one of transfer, join, and merge
    # In these 10 transactions :
    # - one should be a double spend
    # - one invalid transaction
    # i.e one either improperly signed, transfer more coins than possible, etc.
    data = {
        'transactions': []
    }

    # 0 : genesis
    input = []
    output = {User.get_serialized_public_key(user1.public_key) : 15, User.get_serialized_public_key(user2.public_key): 5, User.get_serialized_public_key(user3.public_key): 5}
    signature_fields = []

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': 'TRANS',
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signatures on the three fields
    })

    # 1 : valid TRANS
    type = 'TRANS'
    input = [data['transactions'][0]['NUMBER']]
    output = {User.get_serialized_public_key(user1.public_key): 15}
    signature_fields = [user1.sign(type+''.join(input)+str(output))] 

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': type,
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signaturess on the three fields
    })

    # 2 : valid TRANS 
    type = 'TRANS'
    input = [data['transactions'][0]['NUMBER']]
    output = {User.get_serialized_public_key(user2.public_key) : 5}
    signature_fields = [user2.sign(type+''.join(input)+str(output))]

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': type,
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signaturess on the three fields
    })

    # 3 : valid TRANS
    type = 'TRANS'
    input = [data['transactions'][0]['NUMBER']]
    output = {User.get_serialized_public_key(user3.public_key) : 5}
    signature_fields = [user3.sign(type+''.join(input)+str(output))]

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': type,
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signaturess on the three fields
    })

    # 4 : valid JOIN
    type = 'JOIN'
    input = [data['transactions'][2]['NUMBER'], data['transactions'][3]['NUMBER']]
    output = {User.get_serialized_public_key(user1.public_key) : 10}
    signature_fields = [user2.sign(type+''.join(input)+str(output)), user3.sign(type+''.join(input)+str(output))]

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': type,
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signaturess on the three fields
    })

    # 5 : valid MERGE
    type = 'MERGE'
    input = [data['transactions'][1]['NUMBER'], data['transactions'][4]['NUMBER']]
    output = {User.get_serialized_public_key(user1.public_key) : 25}
    signature_fields = [user1.sign(type+''.join(input)+str(output)), user1.sign(type+''.join(input)+str(output))]

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': type,
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signaturess on the three fields
    })

    # 6 : double-spent TRANS (1) --- should be the right one
    type = 'TRANS'
    input = [data['transactions'][5]['NUMBER']]
    output = {User.get_serialized_public_key(user2.public_key) : 25}
    signature_fields = [user1.sign(type+''.join(input)+str(output))]

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': type,
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signaturess on the three fields
    })

    # 7 : double-spent TRANS (2)
    type = 'TRANS'
    input = [data['transactions'][5]['NUMBER']]
    output = {User.get_serialized_public_key(user3.public_key) : 25}
    signature_fields = [user1.sign(type+''.join(input)+str(output))]

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': type,
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signaturess on the three fields
    })

    # 8 : TRANS VALID
    type = 'TRANS'
    input = [data['transactions'][6]['NUMBER']]
    output = {User.get_serialized_public_key(user4.public_key) : 25}
    signature_fields = [user2.sign(type+''.join(input)+str(output))]

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': type,
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signaturess on the three fields
    })
    
    # 9: TRANS INvalid wrong signature
    type = 'TRANS'
    input = [data['transactions'][8]['NUMBER']]
    output = {User.get_serialized_public_key(user5.public_key) : 25}
    signature_fields = [user5.sign(type+''.join(input)+str(output))]

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': type,
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signaturess on the three fields
    })
    
    # # 10 : TRANS Valid 
    type = 'TRANS'
    input = [data['transactions'][8]['NUMBER']]
    output = {User.get_serialized_public_key(user5.public_key) : 25}
    signature_fields = [user4.sign(type+''.join(input)+str(output))]

    data['transactions'].append({
        'NUMBER': hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
        'TYPE': type,
        'INPUT': input,                # a set of transaction numbers
        'OUTPUT': output,              # a set of (value:public key) pairs
        'SIGNATURE': signature_fields  # set of signaturess on the three fields
    })
    
    
    
    
    # convert to json object
    with open('genesis_transaction_file.json', 'w') as outfile:
        json.dump(data, outfile)

def main():
    create()

if __name__ == '__main__':
    main()
