# Description:
# Defines a node that can verify unverified transactions.

from transaction import Transaction


from pprint import pprint
import hashlib
import nacl.utils
from nacl.public import PrivateKey, Box
import time
import random 
import os


class Node:
    EMPTY = 0

    def __init__(self, network):
        self.network = network
        self.simulation_finished = False

        self.local_chain = []
    
    def run(self):
        print("created a node")
        while not self.simulation_finished:
            # update the local chain
            self.update_local_chain()
            # if the unverified transaction pool is empty, wait
            while len(self.network.unverified_transaction_pool) == 0 and not self.simulation_finished:
                time.sleep(0.001)
            if self.simulation_finished:
                break
            # select a new transaction at random to verify
            transaction = random.choice(list(self.network.unverified_transaction_pool.values()))
            # print("node is working on transaction {}...\n".format(transaction.data['transaction']['id'][:20]))
            # verify it
            if self.network.is_double_spent(transaction): 
                self.network.handle_double_spent(transaction)
            elif transaction.is_valid(self.network.unverified_transaction_pool, self.network.verified_transaction_pool):
                # add hash pointer to the last transaction of the node's chain
                transaction.data['transaction']['ptr_prev_trans'] = self.local_chain[-1].data['transaction']['id']
                # then, verify the transaction by running  proof of work
                nonce, proof_of_work = self.mine(transaction)
                if nonce is not None:
                    # add the nonce and proof of work to the transaction
                    transaction.data['transaction']['nonce'] = nonce
                    transaction.data['transaction']['proof_of_work'] = proof_of_work
                    # remove it from the unverified transaction pool and add it to the blockchain                    
                    self.network.push_transaction_vtp(transaction)
                    time.sleep(5)
        print("node exiting")
        print("--------------------------------------------------------------------------------------------")
        self.update_local_chain()
        self.display_node_list()
        print("--------------------------------------------------------------------------------------------")
    
    def display_node_list(self): 
        for t in self.local_chain:
            t.display()
    
    def input_exists(self, transaction):
        for trans in self.network.verified_trans_pool:
            if trans['transaction']['id'] == transaction['transaction']['id']:
                return True
        return False
    
    def detect_forks(self):
        # Find any repeated transactions
        dups = {}
        # check all of the blocks after the genesis for forks
        for trans in self.local_chain[1:]:
            # Store the pointers to previous transactions in the dups dict
            # if it tries to add one that already exists, it has found a fork
            if dups[trans.data['transaction']['ptr_prev_trans']] == "found":
                return True 
            dups[trans.data['transaction']['ptr_prev_trans']] = "found"
        return False  
    
    def resolve_forks(self):
        # resolve the forks
        fork_keys = []
        dups = {}
        for trans in self.local_chain[1:]:
            if trans.data['transaction']['ptr_prev_trans'] in dups.keys():
                # store all of the transactions that point at the previous transaction at its key
                dups[trans.data['transaction']['ptr_prev_trans']].append(trans) 
                # TODO this might need some fixing?
                fork_keys.append(trans.data['transaction']['ptr_prev_trans'])
            dups[trans.data['transaction']['ptr_prev_trans']] = [trans]

        # resolve forks starting with the one fathest down the chain
        if fork_keys is not None:
            fork_keys = set(sorted(fork_keys, reverse=True)) # set removes duplicates
        # keep track of the branches that need to be removed from the local chain
        shorter_branches = []
        for fork in fork_keys: 
            branch_heads = dups[fork]
            longest_branch = []
            # shorter_branches = []
            # traverse each branch to find its length
            for head in branch_heads:
                this_branch = [head]
                transaction = head
                # while there is a trans that points at this one, add it to this branch
                while dups[transaction.data['transaction']['id']]:
                    this_branch.append(dups[transaction.data['transaction']['id']])
                    transaction = dups[transaction.data['transaction']['id']]
                # update the longest branch and shorter branches
                if len(this_branch) > len(longest_branch):
                    shorter_branches.append(longest_branch)
                    longest_branch = this_branch
                else:
                    shorter_branches.append(this_branch)

        # remove the branches that are not the longest branch from the local chain
        had_fork = False
        for branch in shorter_branches:
            for i, transaction in enumerate(self.local_chain):
                if transaction in branch:
                    # remove from verified transaction pool
                    removed_trans = self.local_chain.pop(i)
                    # add to unverified transaction pool
                    self.network.push_transaction_utp(removed_trans)
                    had_fork = True
        
        if had_fork:
            print("resolved a fork in local chain\n" + self.display())
    
    def update_local_chain(self):
        # update local chain to match the blockchain in the network
        if len(self.local_chain) < len(self.network.verified_transaction_pool):
            # handle the genesis block
            if len(self.local_chain) == 0:
                self.local_chain.append(self.network.verified_transaction_pool[0])
            # find blocks that are not in the local chain
            for trans in self.network.verified_transaction_pool:
                if trans not in self.local_chain:
                    # verify the transaction is valid
                    if not trans.is_valid(self.network.unverified_transaction_pool, self.network.verified_transaction_pool):
                        raise ValueError("invalid transaction")
                    # verify the proof of work
                    if not self.has_valid_proof_of_work(trans):
                        raise ValueError("invalid proof of work")
                    # verify hash pointer to previous transaction
                    if trans.data['transaction']['ptr_prev_trans'] not in [t.data['transaction']['id'] for t in self.local_chain]:
                        raise ValueError("invalid hash")

                    self.local_chain.append(trans)
                    #  detect and handle forks in local chain
                    self.resolve_forks()

        # print("updated node's local chain" + self.display())

    def mine(self, transaction):
        # return false if another miner has found the solution
        # return true if this miner has found the soution
        trans = str(transaction)
        proof_of_work = 0
        # while no more blocks added to the chain:
        while len(self.local_chain) == len(self.network.verified_transaction_pool) and not self.simulation_finished:
            # generate a random nonce
            nonce = random.randint(0, 4294967294)  # to 2^32-1
            # get the proof of work
            proof_of_work = hashlib.sha256((trans+str(nonce)).encode()).hexdigest()
            # calculate the upper bound on a valid proof of work
            upper_bound = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF >> self.network.min_zeros_msb*4
            # check that there are the correct number of leading zeros
            if int(proof_of_work, 16) <= upper_bound:
                return (nonce, proof_of_work)
        return (None, None)

    def has_valid_proof_of_work(self, transaction):
        # verify that the proof of work for the transaction is correct
        proof_of_work = hashlib.sha256((str(transaction)+str(transaction.data['transaction']['nonce'])).encode()).hexdigest()
        # calculate the upper bound on a valid proof of work
        upper_bound = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF >> self.network.min_zeros_msb*4
        # check that there are the correct number of leading zeros
        return int(proof_of_work, 16) <= upper_bound

    def display(self):
        string = '\n'
        for trans in self.local_chain:
            string += '\t'+trans.data['transaction']['id'][:10]+'...\n' 
        string += '\n'
        return string