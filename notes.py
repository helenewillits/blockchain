"""
Written in Python 3

Task 1: Define a Transaction

Creating a definition for a "ZC" transaction block:
*Our block will only hold one transaction
    Use JSON to represent the block (transferable to python dict) with the fields:
        1. Transaction identifier (a SHA256 hash) 
        2. Input pointer (Q: Wouldn't it only be a single pointer?)
        3. Output (a set public key-coin values ) (Q: what does public key-coin mean?)
                                                    A: public key of users along with the coin values
        4. Signature(s) (Q: If there is only one transaction why do we need multiple signatures?)
                        (A: signatures of the sender and reciever)
        5. Hash pointer to a previous transaction
        6. Nonce 
            This is the actual number that a "miner" would need to find from bruteforcing the SHA 
        7. Proof of work (a SHA256 hash)

    Types of allowed transactions:
        1. transfer (one input -> one output)
        2. merge (multiple inputs from single entity  -> one output)
        3. join (multiple input from multiple entities -> one output) (Q: how can there be multiple inputs)
    
    Questions:
        1. Are we doing the whole transaction fees thing?

        
        
        
    NOW: 
        1. Does not work for 2 transactions only
        2. Does not work when its like 1->2->3->2 edit : it doesn't work for any thing mroe than 3 
"""