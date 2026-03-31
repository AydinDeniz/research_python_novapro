from web3 import Web3
from solcx import compile_standard, install_solc
import json

# Install Solidity compiler
install_solc('0.8.0')

# Connect to local Ethereum node
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Set default account (replace with your account)
w3.eth.default_account = w3.eth.accounts[0]

# Solidity source code for identity verification contract
contract_source_code = '''
pragma solidity ^0.8.0;

contract IdentityVerification {
    struct Identity {
        string name;
        string documentNumber;
        bool verified;
    }

    mapping(address => Identity) public identities;

    function registerIdentity(string memory name, string memory documentNumber) public {
        identities[msg.sender] = Identity(name, documentNumber, false);
    }

    function verifyIdentity(address user) public {
        require(msg.sender == owner, "Only owner can verify identities");
        identities[user].verified = true;
    }

    function getIdentity(address user) public view returns (string memory, string memory, bool) {
        Identity memory identity = identities[user];
        return (identity.name, identity.documentNumber, identity.verified);
    }
}
'''

# Compile the contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "IdentityVerification.sol": {
            "content": contract_source_code
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "evm.bytecode"]
            }
        }
    }
})

# Extract bytecode and ABI
bytecode = compiled_sol['contracts']['IdentityVerification.sol']['IdentityVerification']['evm']['bytecode']['object']
abi = compiled_sol['contracts']['IdentityVerification.sol']['IdentityVerification']['abi']

# Deploy the contract
IdentityVerification = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = IdentityVerification.constructor().transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Get contract address
contract_address = tx_receipt.contractAddress

# Create contract instance
identity_verification = w3.eth.contract(address=contract_address, abi=abi)

# Function to register identity
def register_identity(name, document_number):
    tx_hash = identity_verification.functions.registerIdentity(name, document_number).transact()
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Identity registered for {name}")

# Function to verify identity
def verify_identity(user_address):
    tx_hash = identity_verification.functions.verifyIdentity(user_address).transact()
    w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Identity verified for {user_address}")

# Function to get identity
def get_identity(user_address):
    name, document_number, verified = identity_verification.functions.getIdentity(user_address).call()
    print(f"Name: {name}, Document Number: {document_number}, Verified: {verified}")

# Example usage
register_identity("John Doe", "123456789")
verify_identity(w3.eth.accounts[0])
get_identity(w3.eth.accounts[0])