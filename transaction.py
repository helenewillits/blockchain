# Description:
# This file defines the transaction data structure that allows for value transactions on the network

from user import User

class Transaction:

    def __init__(self, id=None, input=[], output={}, signature=[], type=None):
        self.data = {
            'transaction': 
            {
                'id': id,                             # hash of this block 
                'input': input,                       # list of transactions that we refer to  
                'output': output,                     # transaction details : {public key of reciever : amount to be transferred}
                'signature': signature,               # 
                #following items are done after mining
                'ptr_prev_trans': None,               # reference to the transaction immediately before this one in "time"
                'nonce': 0,                           # the guess that solved the blockchain genesis
                'proof_of_work': 0x00                 # hash (this transaction) that satisfies proof requirements; deinsentivising cheating
            }
        }
        self.type = type
        
    def is_valid(self, unverified_transaction_pool, verified_transaction_pool):
        # checks if a transaction is a valid input to the unverified transaction pool
        if not self.has_valid_req_structure(): 
            print("structural error")
            return False
        if not self.has_valid_sender(unverified_transaction_pool, verified_transaction_pool): 
            print("valid sender error")
            return False
        if not self.has_sufficient_funds(unverified_transaction_pool, verified_transaction_pool): 
            print("insufficient funds")
            return False
        return True

    def has_valid_req_structure(self):
        # vefify that the structure of the required fields is correct

        # verify that the input is structured properly
        if type(self.data['transaction']['input']) != list: return False
        if len(self.data['transaction']['input']) < 1: return False
        for input in self.data['transaction']['input']:
            if type(input) != str: return False
            # if len(input) != 1: return False

        # verify that the output is structured properly
        if type(self.data['transaction']['output']) != dict: return False
        if len(self.data['transaction']['output']) != 1: return False
        if type(list(self.data['transaction']['output'].keys())[0]) != str: return False
        if type(list(self.data['transaction']['output'].values())[0]) != int: return False
        if not list(self.data['transaction']['output'].values())[0] > 0: return False

        # verify that the signature is structured properly
        if type(self.data['transaction']['signature']) != list: return False
        if len(self.data['transaction']['input']) != len(self.data['transaction']['signature']): return False
        for signature in self.data['transaction']['signature']:
            if type(signature) != str: return False

        if not self.has_valid_type(): return False

        return True

    def has_valid_addl_structure(self):
        # vefify that the structure of the optional fields is correct (fields that are added before it is appended to the blockchain)

        # verify that the ptr_prev_trans is structured properly
        if type(self.data['transaction']['ptr_prev_trans']) != str: return False

        # verify that the nonce is structured properly
        if type(self.data['transaction']['nonce']) != int: return False

        # verify that the proof of work is structured properly
        if type(self.data['transaction']['proof_of_work']) != str: return False

        return True

    def find_trans_output(self, idx,  unverified_transaction_pool, verified_transaction_pool):
        id = self.data['transaction']['input'][idx]
        outputs = {}
        # add all matching transaction outputs from the unverified transaction pool
        if id in unverified_transaction_pool.keys():
            for key in unverified_transaction_pool[id].data['transaction']['output']:
                outputs[key] = unverified_transaction_pool[id].data['transaction']['output'][key]
        # add all matching transaction outputs from the verified transaction pool
        for trans in verified_transaction_pool:
            if id == trans.data['transaction']['id']:
                for key in trans.data['transaction']['output']:
                    outputs[key] = trans.data['transaction']['output'][key]
        return outputs 

    def has_valid_sender(self, unverified_transaction_pool, verified_transaction_pool):
        # verify the sender on the previous transaction
        for input in range(len(self.data['transaction']['input'])):
            signature = self.data['transaction']['signature'][input]
            # check each public key in the input, in case it is the genesis block
            public_keys = self.find_trans_output(input, unverified_transaction_pool, verified_transaction_pool).keys()
            found = False
            for key in public_keys:
                try:
                    User.verify_signature(key, signature)
                    found = True
                    break
                except:
                    continue
            if not found:
                return False
        return True

    def has_sufficient_funds(self, unverified_transaction_pool, verified_transaction_pool):
        sender_funds = {}
        # find the funds allocated by each sender and verify they are sufficient
        for input in range(len(self.data['transaction']['input'])):
            # keep track of which sender we are looking for using the signature
            signature = self.data['transaction']['signature'][input]
            # check each public key in the input, in case it is the genesis block
            output = self.find_trans_output(input, unverified_transaction_pool, verified_transaction_pool)
            # found = False
            for key in output.keys():
                try:
                    User.verify_signature(key, signature)
                    # we have found a sender
                    if key in sender_funds.keys():
                        sender_funds[key] = sender_funds[key] + output[key]
                    else:
                        sender_funds[key] = output[key]
                    # found = True
                    # break
                except:
                    continue
            # if not found:
            #     return False
        return sum(list(sender_funds.values())) >= list(self.data['transaction']['output'].values())[0]

    # def has_sufficient_funds(self, unverified_transaction_pool):
    #     # verify that the sender has sufficient funds to cover the transaction
    #     funds = 0
    #     for input in self.data['transaction']['input']:
    #         transaction =unverified_transaction_pool[input] 
    #         transfer = transaction.data['transaction']['output']
    #         for pair in transfer:
    #             if pair.key() == self.data['transaction']['in']: 
    #                 funds += pair.value()
    #     return funds >= list(self.data['transaction']['output'].values())[0]

    # def get_excess_funds(self, public_key):
    #     # get the amount of excess funds that were not spent by the sender
    #     funds = 0
    #     for input in self.data['transaction']['input']:
    #         if type(input) == dict:
    #             funds += sum(input.getValues())
    #     return funds - sum(self.data['transaction']['output'].getValues())
        
    def has_valid_type(self):
        # verify transaction types
        if self.type == 'TRANS':
            # one input 
            # one output
            if len(self.data['transaction']['input']) != 1: return False
            if len(self.data['transaction']['output']) != 1: return False
                
        elif self.type == 'MERGE':
            # multiple inputs
            # one output
            if len(self.data['transaction']['input']) == 1: return False
            if len(self.data['transaction']['output']) != 1: return False
            # inputs are all from the same entity
            # set removes duplicates
            # senders_without_dups = set(map(lambda output: list(output.keys())[0], self.data['transaction']['input']))
            # if len(senders_without_dups) != 1:
            #     return False

        elif self.type == 'JOIN':
            # multiple inputs
            # one output
            if len(self.data['transaction']['input']) == 1: return False
            if len(self.data['transaction']['output']) != 1: return False
            # inputs are from multiple entities
            # set removes duplicates
            # senders_without_dups = set(map(lambda output: list(output.keys())[0], self.data['transaction']['input']))
            # if len(senders_without_dups) == 1:
            #     return False

        else:
            raise ValueError()

        return True

    def display(self):
        if len(self.data['transaction']['input']) == 0:
            print("\n   GENESIS TRANSACTION")
        else:
            print("\n   transaction")
        print("\tid:             {}".format(self.data['transaction']['id']))
        for input in self.data['transaction']['input']:
            if input == self.data['transaction']['input'][0]:
                print("\tinput(s):       {}".format(input))
            else:
                print("\t                {}".format(input))
        print("\toutput:         {}".format(self.data['transaction']['output']))
        for signature in self.data['transaction']['signature']:
            if signature == self.data['transaction']['signature'][0]:
                print("\tsignature(s):   {}...".format(signature[:10]))
            else:
                print("\t                {}...".format(signature[:10]))
        print("\tptr_prev_trans: {}".format(self.data['transaction']['ptr_prev_trans']))
        print("\tnonce:          {}".format(self.data['transaction']['nonce']))
        print("\tproof_of_work:  {}".format(self.data['transaction']['proof_of_work']))
        print("\ttype:           {}".format(self.type))
        print()