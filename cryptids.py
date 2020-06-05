# Trying to create a smart contract for Crypto Cryptids!

import smartpy as sp

class CryptoCryptids(sp.Contract):
    def __init__(self, creator, newAuctionDuration):
        self.newAuctionDuration = newAuctionDuration
        self.init(creature = {}, creator = creator)

# Is build neccessary?
    @sp.entry_point
    def build(self, params):
        sp.verify(self.data.creator == sp.sender)
        sp.verify(params.creature.isNew)
        sp.set_type(params.creature.creatureId, sp.TInt)
        self.data.creature[params.creature.creatureId] = params.creature

# SELL
    @sp.entry_point
    def sell(self, params):
        sp.verify(sp.mutez(0) <= params.price)
        self.data.creature[params.creatureId].price = params.price

# BUY
    @sp.entry_point
    def buy(self, params):
        creature = self.data.creature[params.creatureId]
        sp.verify(sp.mutez(0) < creature.price)
        sp.verify(creature.price <= params.price)
        sp.verify(sp.amount == params.price)
        sp.send(creature.owner, params.price)
        creature.owner = sp.sender
        sp.if creature.isNew:
            creature.isNew = False
            creature.auction = sp.now.add_seconds(self.newAuctionDuration)
        sp.verify(sp.now <= creature.auction)
        sp.if sp.now <= creature.auction:
            creature.price = params.price + sp.mutez(1)



# NEW CREATURE
    def newCreature(self, creatureId):
        return sp.record(creatureId = creatureId, owner = sp.sender, price = sp.mutez(0), isNew = False, auction = sp.timestamp(0))


@sp.add_test(name = "Crypto Cryptids")
def test():
    creator = sp.test_account("Creator")
    alice   = sp.test_account("Alice")
    bob     = sp.test_account("Robert")

    c1 = CryptoCryptids(creator.address, newAuctionDuration = 10)
    scenario  = sp.test_scenario()
    scenario += c1
    def newCreature(creatureId, price):
        return sp.record(creatureId = creatureId, owner = creator.address, price = sp.mutez(price), isNew = True, auction = sp.timestamp(0))
    scenario += c1.build(creature = newCreature(0, 10)).run(sender = creator)
    scenario += c1.build(creature = newCreature(1, 10)).run(sender = creator)
    scenario += c1.build(creature = newCreature(2, 10)).run(sender = creator)
    scenario += c1.build(creature = newCreature(3, 10)).run(sender = creator)
    scenario += c1.buy(  creatureId = 1, price = sp.mutez(10)).run(sender = alice, amount = sp.mutez(10))
    scenario += c1.buy(  creatureId = 2, price = sp.mutez(10)).run(sender = alice, amount = sp.mutez(10))
    scenario += c1.buy(  creatureId = 1, price = sp.mutez(11)).run(sender = bob, amount = sp.mutez(11), now = sp.timestamp(3))
    scenario += c1.buy(  creatureId = 1, price = sp.mutez(15)).run(sender = alice, amount = sp.mutez(15), now = sp.timestamp(9))
    scenario.h2("A bad execution")
    scenario += c1.buy(  creatureId = 1, price = sp.mutez(20)).run(sender = bob, amount = sp.mutez(20), now = sp.timestamp(13), valid = False)
