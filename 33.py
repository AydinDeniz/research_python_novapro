from web3 import Web3
from web3.middleware import geth_poa_middleware
import ipfshttpclient
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity

# Initialize Flask app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
jwt = JWTManager(app)

# Connect to Ethereum node
infura_url = "https://mainnet.infura.io/v3/your_infura_project_id"
web3 = Web3(Web3.HTTPProvider(infura_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Connect to IPFS
client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

# Smart contract ABI and address
contract_abi = [...]  # Your contract ABI
contract_address = '0xYourContractAddress'
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Authentication route
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    # Validate username and password (dummy validation for example)
    if username != 'admin' or password != 'password':
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Upload file to IPFS and register ownership on Ethereum
@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    file = request.files['file']
    file_content = file.read()
    
    # Upload to IPFS
    res = client.add(file_content)
    file_hash = res['Hash']
    
    # Register ownership on Ethereum
    account = web3.eth.account.privateKeyToAccount('your_private_key')
    web3.eth.defaultAccount = account.address
    
    tx_hash = contract.functions.registerFile(file_hash).transact({'from': account.address})
    web3.eth.waitForTransactionReceipt(tx_hash)
    
    return jsonify({"ipfs_hash": file_hash, "tx_hash": tx_hash.hex()})

# Retrieve file from IPFS
@app.route('/retrieve/<file_hash>', methods=['GET'])
@jwt_required()
def retrieve_file(file_hash):
    # Verify ownership on Ethereum
    owner = contract.functions.getOwner(file_hash).call()
    current_user = get_jwt_identity()
    
    if owner.lower() != current_user.lower():
        return jsonify({"msg": "Unauthorized"}), 403
    
    # Retrieve from IPFS
    res = client.cat(file_hash)
    return res

# Share file by updating ownership on Ethereum
@app.route('/share/<file_hash>', methods=['POST'])
@jwt_required()
def share_file(file_hash):
    new_owner = request.json.get('new_owner', None)
    
    # Verify current ownership
    owner = contract.functions.getOwner(file_hash).call()
    current_user = get_jwt_identity()
    
    if owner.lower() != current_user.lower():
        return jsonify({"msg": "Unauthorized"}), 403
    
    # Update ownership on Ethereum
    account = web3.eth.account.privateKeyToAccount('your_private_key')
    web3.eth.defaultAccount = account.address
    
    tx_hash = contract.functions.transferFile(file_hash, new_owner).transact({'from': account.address})
    web3.eth.waitForTransactionReceipt(tx_hash)
    
    return jsonify({"msg": "File shared successfully", "tx_hash": tx_hash.hex()})

if __name__ == '__main__':
    app.run(debug=True)