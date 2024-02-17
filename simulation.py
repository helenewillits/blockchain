
from pprint import pprint

from node import Node
import threading
import time
import transaction_file
from transaction import Transaction
import json
from network import Network
import random 

# unverified_trans_pool = {}
# verified_transaction_pool = []


def sample():
    print("hi" +str(int(time.time())))


def main():
    # initalize the network
    network = Network()

    # simulate a set of transactions using a transaction file
    process_transaction_file(network)
    expected_blockchain_length = 9

    # for testing : check that the unverified transaction pool matches our expectations
    network.display_unverified_transaction_pool()

    # create nodes to mine the network
    nodes, thread_nodes = create_nodes(network, num_nodes=10)

    # wait for the nodes to add all of the transactions to the blockchain
    while len(network.verified_transaction_pool) != expected_blockchain_length:
        time.sleep(0.01)

    # kill the nodes
    kill_nodes(nodes, thread_nodes)

    # display the network
    network.display()

# create a transaction file, read it, and add the transactions to the network
def process_transaction_file(network):
    transaction_file.create()

    # read the transaction file
    with open('genesis_transaction_file.json', "r") as f:
        trans_file = json.loads(f.read())
    pprint(trans_file)
    
    # add each transaction from the transaction file to the network
    for i, t in enumerate(trans_file['transactions']):
        # create a transaction object
        trans = Transaction(
            id=t['NUMBER'],
            # input=list(map(lambda number: network.unverified_transaction_pool[str(number)].data['transaction']['output'], t['INPUT'])), 
            input = t['INPUT'],
            output=t['OUTPUT'], 
            signature=t['SIGNATURE'], 
            #  value_if_true if condition else value_if_false
            type=t['TYPE'])
        # add the transaction the unverified transaction pool
        if network.push_transaction_utp(trans) is False:
            print("Transaction {} of the transaction file cound not be added.\n".format(i))
            # exit()
        # directly add the genesis block
        if i == 0:
            network.push_transaction_vtp(trans)
  
        # sleep between 0 to 2 seconds between transactions
        # time.sleep(random.random(0, 2+1))

def create_nodes(network, num_nodes):
    # creating nodes and thread them to start at the same time
    nodes = []
    thread_nodes = []
    for i in range(num_nodes):
        # add a new node using threading
        noder = Node(network)
        n = threading.Thread(target=noder.run)
        n.start()
        # add this node to the nodes array
        nodes.append(noder)
        thread_nodes.append(n)
    return nodes, thread_nodes

def kill_nodes(nodes, thread_nodes):
    # signal to the nodes that the simulation has finished
    for node in range(len(nodes)):
        print("The thread "+str(node))
        nodes[node].simulation_finished = True
        thread_nodes[node].join()

    # join the nodes together
    # for node in thread_nodes:
        # node.join()

# def signal_handler(signal, frame):
#     if signal == signal.SIGINT:
#         kill_nodes()
#         sys.exit(0)
        




    

    



if __name__ == '__main__':
    main()
