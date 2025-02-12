E-Voting System using Blockchain & FastAPI

📌 Project Overview

This project is a secure and transparent e-voting system built using Blockchain and FastAPI. It ensures tamper-proof voting by leveraging the decentralized nature of blockchain technology. The system records votes as transactions in a blockchain, preventing unauthorized modifications and ensuring election integrity.

✨ Features

Secure Voting: Each vote is stored as a blockchain transaction, preventing tampering.

Decentralized Ledger: Votes are validated by nodes in the network, ensuring transparency.

FastAPI Backend: Handles voting requests and blockchain operations efficiently.

Jinja2 Templating: Dynamic frontend using HTML & Jinja2.

Peer-to-Peer Networking: Nodes communicate to sync the latest blockchain state.

Real-time Vote Counting: Instantly updates vote results as new votes are recorded.

Easy Resync & Mining: Users can request mining and view the blockchain data.

🛠️ Tech Stack

Backend: FastAPI (Python), Redis (for caching and temporary storage)

Blockchain: Custom-built blockchain using Python

Frontend: HTML, CSS, Jinja2 (templating)

Database: In-memory blockchain storage

🚀 Installation & Setup

1️⃣ Clone the Repository

 git clone https://github.com/yourusername/e-voting-blockchain.git
 cd e-voting-blockchain

2️⃣ Install Dependencies

 pip install -r requirements.txt

3️⃣ Run the FastAPI Server

 uvicorn main:app --reload

4️⃣ Access the Application

Open your browser and go to:

 http://127.0.0.1:8000/

🏗️ Project Structure

├── main.py                 # FastAPI main application
├── blockchain.py           # Blockchain implementation
├── p2p.py                  # Peer-to-peer networking
├── templates/              # HTML Templates
│   ├── base.html
│   ├── index.html
├── static/                 # CSS & JS files
│   ├── styles.css
├── requirements.txt        # Dependencies
├── README.md               # Project Documentation

📌 Usage

Vote: Select a political party and enter a valid voter ID.

Request Mining: After voting, request mining to add the vote to the blockchain.

View Blockchain: Check the complete voting record and vote distribution.

🤝 Contributing

Feel free to contribute! Fork the repo, create a new branch, and submit a pull request.

📜 License

This project is open-source and available under the MIT License.

🚀 Let's revolutionize digital voting with blockchain!

