from flask import Flask, render_template, request, redirect, url_for
from web3 import Web3
from dotenv import load_dotenv
import os
import json

# Load values from .env
load_dotenv()

app = Flask(__name__)

# Get configuration
#RPC_URL = os.getenv("SEPOLIA_RPC_URL")
#PRIVATE_KEY = os.getenv("PRIVATE_KEY")
#CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

RPC_URL = "https://sepolia.infura.io/v3/f9dc8031e5184796ba3ebba75a8b2461"
PRIVATE_KEY = "47b13d190fdb8224f64e70a73dfd39054d4043ecefae268cd81e97a0abe597ca"
CONTRACT_ADDRESS = "0x79402eBC256B1d80366b79eF62F12BbE3105121f"

# Connect to Sepolia
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Load test wallet
account = w3.eth.account.from_key(PRIVATE_KEY)

# Load smart contract ABI
with open("contract_abi.json") as file:
    abi = json.load(file)

# Connect to deployed MessageStorage contract
contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=abi
)


@app.route("/")
def index():

    # Read data from the blockchain
    current_message = contract.functions.getMessage().call()
    owner = contract.functions.owner().call()

    return render_template(
        "index.html",
        message=current_message,
        owner=owner,
        wallet=account.address
    )


@app.route("/set-message", methods=["POST"])
def set_message():

    new_message = request.form["message"]

    # Get transaction nonce
    nonce = w3.eth.get_transaction_count(
        account.address
    )

    # Build blockchain transaction
    transaction = contract.functions.setMessage(
        new_message
    ).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "chainId": 11155111,
        "gas": 200000,
        "gasPrice": w3.eth.gas_price
    })

    # Sign transaction
    signed_transaction = w3.eth.account.sign_transaction(
        transaction,
        PRIVATE_KEY
    )

    # Send transaction to Sepolia
    tx_hash = w3.eth.send_raw_transaction(
        signed_transaction.raw_transaction
    )

    # Wait until transaction is confirmed
    w3.eth.wait_for_transaction_receipt(tx_hash)

    return redirect(url_for("index"))


if __name__ == "__main__":

    print("Connected to Sepolia:", w3.is_connected())
    print("Flask Wallet:", account.address)
    print("Contract:", CONTRACT_ADDRESS)

    app.run(debug=True)