# Creating a blockchain

import datetime
from hashlib import sha256
import json
from flask import Flask, jsonify, request
import requests 
from uuid import uuid4
from urllib.parse import urlparse

# Building the blockchain

def getTimeStamp():
        return str(datetime.datetime.now())
class BlockChain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.create_block(proof = 1, previous_hash = "0")
        
    def create_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": getTimeStamp(),
            "proof": proof,
            "previous_hash": previous_hash,
            "transactions": self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def getPreviousBlock(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof == False:
            hash_operation = sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[0:4] == "0000":
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            current_block = chain[block_index]
            current_proof = current_block['proof']
            previous_proof = previous_block['proof']
            hash_operation = sha256(str(current_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if current_block['previous_hash'] != blockchain.hash(previous_block) or hash_operation[:4] != '0000':
                return False
            previous_block = current_block
            block_index += 1
        return True

    def add_transaction(self, sender, reciever, amount):
        self.transactions.append({
                "sender": sender, 
                "reciever": reciever, 
                "amount": amount
            })
        previous_block = self.getPreviousBlock()
        return (previous_block['index'] + 1)

    def add_node(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f"http://{node}/getChain")
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        
# Mining Part        


app = Flask(__name__)

# Creating an address for the node on port 5000
node_address = str(uuid4()).replace('-', '')

#Blockchain 

blockchain = BlockChain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.getPreviousBlock()
    previous_proof = previous_block["proof"]
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, reciever = 'Miner3', amount = 25)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, You just mined a block',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']}
    return jsonify(response), 200

@app.route('/getChain', methods = ['GET'])
def getChain():
    response = {'chain': blockchain.chain,
        'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid')
def is_valid():
    is_valid_chain = blockchain.is_chain_valid(blockchain.chain)
    if is_valid_chain:
        response = {
            'message': "The Blockchain is Valid"
        }
        return jsonify(response), 200
    else:
        response = {
            'message': "The Blockchain is Not Valid"
        }
        return jsonify(response), 400


# Adding a transaction
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'reciever', 'amount']
    if not all (key in json for key in transaction_keys):
        return jsonify({"message": 'Some Elements of the Transaction are Missing.'}), 400
    index = blockchain.add_transaction(json['sender'], json['reciever'], json['amount'])
    return jsonify({"message": f"This transaction will be added to block number {index}"}), 201


# Connecting new Nodes
@app.route('/connect_node', methods = ['POST']) 
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No Nodes Present", 400
    for node in nodes: 
        blockchain.add_node(node)
    response = {
        'message': "Nodes Connected. Blockchain contains following nodes: ",
        'total_nodes': list(blockchain.nodes)
    }
    return jsonify(response), 201

# Replacing the chain by longest chain 
@app.route('/replace_chain')
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {
            'message': "The nodes had different chains. The chain is replaced by the longest chain.",
            "new_chain": blockchain.chain
        }
        return jsonify(response), 200
    else:
        response = {
            'message': "All good. The chain is the largest one.",
            "actual_chain": blockchain.chain
        }
        return jsonify(response), 400


app.run(host = '0.0.0.0', port = 5002)

