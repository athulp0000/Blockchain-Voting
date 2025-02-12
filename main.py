from pydantic import BaseModel
import time
import json
import requests
from blockchain import Blockchain, Block
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from frontend import router as frontend_router
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles



app=FastAPI()

# Add session middleware (needed for flash messages)
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(frontend_router)
# the node's copy of blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# the address to other participating members of the network
peers = set()

class Node(BaseModel):
    node_address: str

# Pydantic models for request validation
class Transaction(BaseModel):
    voter_id: str
    party: str


# Pydantic Model for Validation
class BlockData(BaseModel):
    index: int
    transactions: list[dict]
    timestamp: float
    previous_hash: str
    nonce: int
    hash: str



@app.post("/new_transaction")
async def new_transaction(tx_data: Transaction):
    """Submit a new transaction to the blockchain."""
    transaction = tx_data.dict()
    transaction["timestamp"] = time.time()
    blockchain.add_new_transaction(transaction)
    return {"message": "Transaction added successfully","status": 201}

@app.get("/chain")
def get_chain():
    chain_data = [block.__dict__ for block in blockchain.chain]
    return {
        "length": len(chain_data),
        "chain": chain_data,
        "peers": list(peers)
    }


@app.get("/mine")
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    
    if not result:
        return JSONResponse(content={"message": "No transactions to mine"}, status_code=200)
    
    # Ensure we have the longest chain before announcing the new block
    chain_length = len(blockchain.chain)
    consensus()
    
    if chain_length == len(blockchain.chain):
        announce_new_block(blockchain.last_block)
    
    return JSONResponse(content={"message": f"Block #{blockchain.last_block.index} is mined."}, status_code=201)




def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)


@app.post("/register_node")
def register_new_peers(node: Node):
    node_address = node.node_address

    if not node_address:
        raise HTTPException(status_code=400, detail="Invalid data")

    # Add the node to the peer list
    peers.add(node_address)

    # Return the updated blockchain to sync the new node
    return get_chain()


@app.post("/register_with")
async def register_with_existing_node(node: Node):
    node_address = node.node_address

    if not node_address:
        raise HTTPException(status_code=400, detail="Invalid data")

    data = {"node_address": "http://127.0.0.1:8000"}  # Replace with dynamic host URL
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{node_address}/register_node", json=data, headers=headers)

    if response.status_code == 200:
        global blockchain, peers
        chain_dump = response.json().get("chain", [])
        blockchain = create_chain_from_dump(chain_dump).chain
        peers.update(response.json().get("peers", []))
        return {"message": "Registration successful", "status": 200}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)



def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain



@app.post("/add_block")
def verify_and_add_block(block_data: BlockData):
    block = Block(
        index=block_data.index,
        transactions=block_data.transactions,
        timestamp=block_data.timestamp,
        previous_hash=block_data.previous_hash,
        nonce=block_data.nonce,
    )

    proof = block_data.hash
    added = blockchain.add_block(block, proof)

    if not added:
        raise HTTPException(status_code=400, detail="The block was discarded by the node")

    return {"message": "Block added to the chain", "status": 201}


@app.get("/pending_tx", response_model=list[dict])
def get_pending_tx():
    return blockchain.unconfirmed_transactions

# Run FastAPI locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)