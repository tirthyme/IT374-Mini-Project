# Creating a blockchain

import datetime
from hashlib import sha256
import json
from flask import Flask, jsonify

# Building the blockchain

def getTimeStamp():
        return str(datetime.datetime.now())
class BlockChain:

    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = "0")
        
    def create_block(self, proof, previous_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": getTimeStamp(),
            "proof": proof,
            "previous_hash": previous_hash
        }
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
        while (block_index < len(chain)):
            block = chain[block_index]
            if (block['previous_hash'] != self.hash(previous_block)):
                return False
            previous_proof = previous_block["proof"]
            proof = block["proof"]
            hash_operation = sha256(str(previous_proof**2 - proof**2).encode()).hexdigest()
            if hash_operation[0:4] != "0000":
                return False
            previous_block = block
            block_index += 1
        return True

# Mining Part        


app = Flask(__name__)

#Blockchain 

blockchain = BlockChain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.getPreviousBlock()
    previous_proof = previous_block["proof"]
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, You just mined a block',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']}
    return jsonify(response), 200

@app.route('/getChain', methods = ['GET'])
def getChain():
    response = {'chain': blockchain.chain,
        'length': len(blockchain.chain)}
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)


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
