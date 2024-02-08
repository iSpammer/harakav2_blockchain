import ast
import sys
from uuid import uuid4

import numpy
from flask import Flask, request, jsonify
from flask_sslify import SSLify
from BlockchainEncoder import BlockChainEncoder
from blockchain2 import Blockchain
from block2 import Block
import numpy as np
import json
server_pki = np.load("CA_pki.npz", allow_pickle=True)
pub_key_s_h = server_pki["pub_key_s"]
country = server_pki["country"] # Country name
state_code = server_pki["state_code"] # State or province name
state = server_pki["state"] # Locality name
org = server_pki["org"] # Organization name
org_unit = server_pki["org_unit"] # Organizational unit name
cname = server_pki["cname"] # Common name
email = server_pki["email"] # Email address
# pub_key_s=server_pki['pub_key_s_h']
secret_h=server_pki['secret_h']
secret_f=server_pki['secret_f']
secret_g=server_pki["secret_g"]

print("country ",country)
print("state_code ",state_code)
print("state ",state)
print("org ",org)
print("org_unit ",org_unit)
print("cname ",cname)
print("email ",email)
print("pub_key_s_h ",pub_key_s_h)

app = Flask(__name__)
sslify = SSLify(app) # This will automatically redirect all incoming requests to HTTPS

blockchain = Blockchain(1) # constructs a blockchain with 20 difficulty
blockchain_node = str(uuid4()).replace('-', '') # generates a unique universal identifier that identifies the node

@app.route('/')
def welcome():
    '''
    Welcome message that is shown upon connection to the server. 
    '''
    return "Welcome to the blockchain.\nYou can use http requests to view the current blockchain, submit transactions, and mine blocks."


@app.route('/new_transaction', methods = ['POST'])
def new_transaction():
    '''
    This endpoint collects a transaction that is sent from the client. It checks for the requires details and then 
    adds the transaction to the transaction list of the blockchain. 
    '''
    transaction = request.get_json()  # transaction submitted in json format from the client (likewise for all other inputs)
    required_details = ['country', 'state_code', 'state', 'org', 'org_unit', 'cname', 'email', 'pub_key_s_h'] # ensures that these details are part of a submitted transaction
    for key in transaction:
        if key not in required_details:
            return 'Failure: Transaction has missing values.', 400
    blockchain.add_to_transactions(transaction['country'], transaction['state_code'], transaction['state'], transaction['org'], transaction['org_unit'], transaction['cname'], transaction['email'], transaction['pub_key_s_h']) # transaction added
    return "Success: Transaction is ready to be added to the blockchain.", 201 
   

@app.route('/mine', methods = ['GET'])
def mine():
    '''
    This endpoint takes a pending transaction from the transaction list and mines it into a block that gets
    added to the blockchain. Additonally, another block is mined, which represents the reward that is given 
    to the node that mined the transaction. 
    '''
    result = blockchain.mine_transactions()
    if type(result) == Block: # if the block was succesfully mined
        blockchain.add_to_transactions(country,state_code, state,
                                       org, org_unit, cname,
                                       email,pub_key_s_h)  # transaction added

        result2 = blockchain.mine_transactions()
        sys.stdout.flush()
        return str(result) + '\n' + str(result2), 200 # string of the two blocks is returned along with succesful http status code
    else:
        sys.stdout.flush()

        return "Failure: Did not mine the blockchain.", 400


@app.route('/chain', methods = ['GET'])
def chain():
    '''
    This endpoint displays the entire blockchain.
    '''
    return str(blockchain) # string representation of object


@app.route('/chain_details', methods = ['GET'])
def chain_details():
    '''
    This endpoint returns the current chain of the blockchain as well as its length.
    '''
    print("conn , ",blockchain.chain)
    # This endpoint returns the current chain of the blockchain as well as its length.
    encoder = BlockChainEncoder()  # create an instance of the custom encoder class
    chain = []  # create an empty list to store the JSON strings
    for block in blockchain.chain:  # iterate over the list of blocks
        json_block = encoder.encode(block)  # encode each block using the encode method
        chain.append(json_block)  # append the JSON string to the chain list
    length = len(blockchain.chain)
    result = {'chain' : chain, "len" : length}
    return result , 200  # jsonify the result and return it with status code 200

    # jsonify the result and return it with status code 200
    # jsonpickle.set_preferred_backend('json')
    # jsonpickle.set_encoder_options('json', ensure_ascii=True)
    #
    # chain = jsonpickle.encode(blockchain.chain) # chain is serialized to json because it is a complex object that needs to be transferred
    # length = len(blockchain.chain)
    # result = {'Chain': chain, 'Length': length}
    # return result, 200


@app.route('/chain_details_get', methods = ['GET'])
def chain_details_get():
    '''
    This endpoint returns the current chain of the blockchain as well as its length.
    It also takes 3 optional query parameters: name, surname, and age, and filters the chain by those values.
    For example, /chain_details?name=John&surname=Doe&age=22 will return only the blocks that have those values in their transactions.
    '''
    print("conn , ",blockchain.chain)
    # This endpoint returns the current chain of the blockchain as well as its length.
    encoder = BlockChainEncoder()  # create an instance of the custom encoder class
    chain = []  # create an empty list to store the JSON strings
    # Get the query parameters from the request
    pub_key_s_h_rec = ast.literal_eval(request.args.get('hashid'))
    print("got ",type(pub_key_s_h_rec))
    # surname = request.args.get('surname')
    # age = request.args.get('age')
    for block in blockchain.chain:  # iterate over the list of blocks
        # Check if the block matches the query parameters
        # Check if the transactions value is a dictionary or not
        if isinstance(block.transactions, dict):
            print("TRYING WITH ",block.transactions.get('pub_key_s_h'))
            # Use the get() method on the transactions dictionary
            if (numpy.array(block.transactions.get('pub_key_s_h')) == numpy.array(pub_key_s_h_rec)).all():
               # (surname is None or block.transactions.get('surname') == surname) and \
               # (age is None or block.transactions.get('age') == int(age)):
                json_block = encoder.encode(block)  # encode each block using the encode method
                chain.append(json_block)  # append the JSON string to the chain list
        # if (hashid is None or block.hashid == hashid):
        #     # (surname is None or block.transactions.get('surname') == surname) and \
        #     # (age is None or block.transactions.get('age') == int(age)):
        #     json_block = encoder.encode(block)  # encode each block using the encode method
        #     chain.append(json_block)  # append the JSON string to the chain list
        else:
            # Skip the block if the transactions value is not a dictionary
            continue
    length = len(chain)
    result = {'chain' : chain, "len" : length}
    return result , 200  # jsonify the result and return it with status code 200

@app.route('/add_nodes', methods = ['POST'])
def add_nodes():
    '''
    This endpoint collects a node url from the client and proceeds to add it to the set of nodes that is 
    recognized by the blockchain. 
    '''
    result = request.get_json()
    nodes = result["Nodes"]
    if len(nodes) == 0: # ensures that a node has been submitted 
        return "Failure: Please enter a list of nodes", 400
    for node in nodes:
        blockchain.register_node(node) # the node is registered by the blockchain 
    return "Success: Added another node on the network", 201

@app.route('/consensus', methods = ['GET'])
def consensus():
    '''
    This endpoint looks at all the chains of all the other nodes and proceeds to replace the current blockchain of the
    client, if a longer and accurate alternate blockchain is found. 
    '''
    new_chain = blockchain.find_longest_chain() # looks for an alternate chain that is superior
    if new_chain:
        return "Chain was replaced by another longer chain.", 201
    else:
        return "Chain was not replaced. Current chain is the longest.", 201

import logging
logging.basicConfig(level=logging.DEBUG)
if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0", ssl_context=('cert.pem', 'key.pem'))  # allows for multiple nodes on the network and objective of consensus

    # answer = input("Please enter the node that you want to use on the network: ")
    # if answer == "1":
    # if answer == "2":
    #     app.run(port= 5001, host="0.0.0.0") # allows for multiple nodes on the network and objective of consensus
