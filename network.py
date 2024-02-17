# Description:
# This file holds the network for the cryptocurrency.

from pprint import pprint
from transaction import Transaction
from user import User 
import json
import hashlib

class Network:

    def __init__(self):
        # store transactions until they have been verified and can be added to the blockchain
        self.unverified_transaction_pool = {}
        # store the global verified transactions
        self.verified_transaction_pool = [] 
        # store the minimum number of zeros for a valid proof of work
        self.min_zeros_msb = 5
        
    # functions that allow users to interact with the network
    def push_transaction_utp(self, transaction):
        # if it is not the genesis block, verify that the transaction is valid
        if not self.network_is_empty():
            if not transaction.is_valid(self.unverified_transaction_pool, self.verified_transaction_pool): return False
            if self.is_double_spent(transaction): return False
        
        # attempt to add the transaction
        self.unverified_transaction_pool[transaction.data['transaction']['id']] = transaction

        # print("\npushed a transaction to the unverified transaction pool")
        # print("transaction id: {}\n".format(transaction.data['transaction']['id']))

        # check that the transaction was added correctly and return success or failure
        return self.utp_contains_transaction(transaction)

    def push_transaction_vtp(self, transaction):
        print("\n...")
        print("attempt to add a transaction to the verified transaction pool")
        print("...\n")
        # if it is not the genesis block, verify that the transaction is valid
        if not self.vtp_is_empty():
            if not transaction.is_valid(self.unverified_transaction_pool, self.verified_transaction_pool):
                print("not valid") 
                return False
            if self.is_double_spent(transaction): 
                print("double spent")
                return False
            # check the structure of the fields that have been updated since the object was first verified
            if not transaction.has_valid_addl_structure(): 
                print("structure error")
                return False
            # check that the previous pointer points at the last block on the chain
            if transaction.data['transaction']['ptr_prev_trans'] != self.verified_transaction_pool[-1].data['transaction']['id']: return False
            if not self.has_valid_proof_of_work(transaction): 
                print("proof of work error")
                return False
        
        # remove the transaction from the unverified transaction pool
        self.unverified_transaction_pool.pop(transaction.data['transaction']['id'])

        # add the transsaction to the verified transaction pool
        self.verified_transaction_pool.append(transaction)

        print("\npushed a transaction to the verified transaction pool")
        print("transaction id: {}\n".format(transaction.data['transaction']['id']))

        # check that the transaction was added correctly
        if not self.vtp_contains_transaction(transaction): return False

        # add a transaction to reallocate excess funds
        # self.reallocate_excess_funds(transaction)

        return True

    # functions that regulate the unverified_transaction_pool
    def utp_contains_transaction(self, transaction):
        return self.unverified_transaction_pool.get(transaction.data['transaction']['id']) != None

    def vtp_contains_transaction(self, transaction):
        return self.unverified_transaction_pool.get(transaction.data['transaction']['id']) != None

    def is_double_spent(self, transaction):
        # check for double spending in the verified transaction pool
        # otherwise, check each transaction for repeated inputs
        for trans in self.verified_transaction_pool[1:]:
            for input in transaction.data['transaction']['input']:
                # ignore transactions that refer to the genesis block
                if input != self.verified_transaction_pool[0].data['transaction']['id']:
                    for id in trans.data["transaction"]['input']:
                        if input == id:
                            return True
        return False

    def handle_double_spent(self, transaction):
        # remove double spent transactions from the unverified transaction pool and report an error
        if self.is_double_spent(transaction):
            # remove the transaction
            if self.utp_contains_transaction(transaction):
                self.unverified_transaction_pool.pop(transaction.data['transaction']['id'])
                # report an error
                print("Error: double spend detected. Removing malicious transaction from the unverified transaction pool.")
                print("Removed item:")
                transaction.display()
                return True
        return False

    def has_valid_proof_of_work(self, transaction):
        # verify that the proof of work for the transaction is correct
        proof_of_work = hashlib.sha256((str(transaction)+str(transaction.data['transaction']['nonce'])).encode()).hexdigest()
        # calculate the upper bound on a valid proof of work
        upper_bound = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF >> self.min_zeros_msb*4
        # check that there are the correct number of leading zeros
        return int(proof_of_work, 16) <= upper_bound

    def display_unverified_transaction_pool(self):
        print("\nUnverified Transaction Pool")
        for transaction in self.unverified_transaction_pool.values():
            transaction.display()
        print()

    def display_verified_transaction_pool(self):
        print("\nVerified Transaction Pool")
        for transaction in self.verified_transaction_pool:
            transaction.display()


    def display(self):
        self.display_unverified_transaction_pool()
        self.display_verified_transaction_pool()

    def network_is_empty(self):
        return len(self.unverified_transaction_pool) == 0 and len(self.verified_transaction_pool) == 0

    def vtp_is_empty(self):
        return len(self.verified_transaction_pool) == 0


    # def reallocate_excess_funds(self, transaction):
    #     # This is for later development 
    #     if transation.type == 'MERGE':
    # #     # get the amount of excess funds that were not spent by the sender
    #         funds = 0
    #         for input in transaction.data['transaction']['input']:
    #             funds += sum(list(input.values()))
    #         funds -= sum(list(transaction.data['transaction']['output'].values()))
    #         input = transaction.data['transaction']['id']
    #         public_key = list(transaction.data['transaction']['input'][0].keys())[0]
    #         output = {}
    #         trans = Transaction(
    #             id= hashlib.sha256((''.join(input) + str(output) + ''.join(signature_fields)).encode()).hexdigest(),
    #             input=list(map(lambda number: network.unverified_transaction_pool[str(number)].data['transaction']['output'], t['INPUT'])), 
    #             output=, 
    #             signature=, 
    #             #  value_if_true if condition else value_if_false
    #             type=
    #             )
    #     # add the transaction the unverified transaction pool
    #     if network.push_transaction_utp(trans) is False:
    #         print("Transaction {} of the transaction file cound not be added. \nExiting.\n".format(i))
    #         exit()
    #     return funds - sum(self.data['transaction']['output'].getValues()


# def main():
#     Network()
    
# if __name__=='__main__':
#     main()
    