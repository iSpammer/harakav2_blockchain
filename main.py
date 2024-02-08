from blockchain2 import Blockchain
from block2 import Block

the_blockchain = Blockchain(20)

data = ''
while data != "False":
    data = input("Enter transactions to add to block: ")
    if data == "False":
        continue
    results = data.split(',')
    the_blockchain.add_to_transactions(results[0], results[1], results[2], results[0], results[1], results[2], results[0], results[2])
    the_blockchain.mine_transactions()
    print(the_blockchain)
   
    
print("\n")
print(Blockchain.validate_chain(the_blockchain))
print(type(the_blockchain.chain[-1]) == Block)


# Block Hash: 0000067ecc886edfd7af7fcc83957e64b8c9f7d570167d1062d6034238f2c1a7
# Block Number: 1
#
# Block Hash: 0000093b26239f23b99dac60c876a507179c3bb57195c123863da3d548883094
# Block Number: 2