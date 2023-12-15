from Blockchain import Blockchain
from Block import Block
from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import hashlib
import json

app = Flask(__name__)
blockchain = Blockchain()
peers = []

key = Fernet.generate_key()
cipher_suite = Fernet(key)

@app.route("/new_transaction", methods=["POST"])
def new_transaction():
    file_data = request.get_json()

    required_fields = ["user", "v_file", "file_data", "file_size"]

    for field in required_fields:
        if not file_data.get(field):
            return "Transaction does not have valid fields!", 404

    encrypted_data = cipher_suite.encrypt(file_data["file_data"].encode())
    encrypted_transaction = {
        "user": file_data["user"],
        "v_file": file_data["v_file"],
        "file_data": encrypted_data.decode(),
        "file_size": file_data["file_size"]
    }
    print(encrypted_data)
    blockchain.add_pending(encrypted_transaction)
    return "Success", 201

@app.route("/get_file_data/<int:transaction_id>", methods=["GET"])
def get_file_data(transaction_id):
    transaction = blockchain.get_transaction(transaction_id)
    if not transaction:
        return "Transaction not found", 404
    
    encrypted_data = transaction.get("file_data", "")
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode()).decode()

    return jsonify({"file_data": decrypted_data})

@app.route("/verify_integrity/<int:transaction_id>", methods=["GET"])
def verify_integrity(transaction_id):
    transaction = blockchain.get_transaction(transaction_id)
    if not transaction:
        return "Transaction not found", 404
    
    encrypted_data = transaction.get("file_data", "")

    decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
    hash_func = hashlib.sha256()
    hash_func.update(decrypted_data)
    calculated_hash = hash_func.hexdigest()
    known_hash = ''

    if calculated_hash == known_hash:
        return "Integrity verified. Data has not been altered."
    else:
        return "Integrity check failed. Data may have been altered."

@app.route("/chain", methods=["GET"])
def get_chain():
    chain = []
    for block in blockchain.chain:
        chain.append(block.__dict__)

    print("Chain Len: {0}".format(len(chain)))
    return json.dumps({"length": len(chain), "chain": chain})

@app.route("/mine", methods=["GET"])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if result:
        return f"Block #{result} mined successfully."
    else:
        return "No pending transactions to mine."

@app.route("/pending_tx", methods=["GET"])
def get_pending_tx():
    return json.dumps(blockchain.pending)

@app.route("/add_block", methods=["POST"])
def validate_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"], block_data["transactions"], block_data["prev_hash"])
    hashl = block_data["hash"]
    added = blockchain.add_block(block, hashl)
    if not added:
        return "The Block was discarded by the node.", 400
    return "The block was added to the chain.", 201

if __name__ == "__main__":
    app.run(port=8800, debug=True)
