import smartpy as sp

class CryptoCryptids(sp.Contract):
    def __init__(self, creator, newAuctionDuration):

        self.newAuctionDuration = newAuctionDuration
        # I think here we instantiate the class with a map for the creatures and assign
        # the creator tot he creator variable
        self.init(creature = {}, creator = creator)

# Entry point for building a new creature
    @sp.entry_point
    def build(self, params):
        # Verify if the sender and creator are the same
        sp.verify(self.data.creator == sp.sender)
        # Verify this is a new creature
        sp.verify(params.creature.isNew)
        # calls the set_type function? takes 2 args one being an integer
        sp.set_type(params.creature.creatureId, sp.TInt)
        # Set creature params variable
        self.data.creature[params.creature.creatureId] = params.creature

# Entry Point for Selling Cryptid
    @sp.entry_point
    def sell(self, params):
        # Verify that the price parameters are greater than or equal to zero
        sp.verify(sp.mutez(0) <= params.price)
        # set price variable
        self.data.creature[params.creatureId].price = params.price

# Entry Point for Buying Cryptid
    @sp.entry_point
    def buy(self, params):
        # pack all the creature data and id into the variable creature
        creature = self.data.creature[params.creatureId]
        # verify that the creature price is greater than 0 mutez
        sp.verify(sp.mutez(0) < creature.price)
        # verify that the creature price is less than or equal to the params price
        sp.verify(creature.price <= params.price)
        # verify that the params price and the amount are the same
        sp.verify(sp.amount == params.price)
        # sends the params price to the the creature owner
        sp.send(creature.owner, params.price)
        # the creature owner becomes the sender of mutez
        creature.owner = sp.sender
        # if/else statement for is New
        sp.if creature.isNew:
            # If creature isnew is False
            creature.isNew = False
            #call a new auction duration?
            creature.auction = sp.now.add_seconds(self.newAuctionDuration)
        # Verify that the now(time?) is less than or equal to the creature auction time
        sp.verify(sp.now <= creature.auction)
        # another if statement for the verification statement above as true
        sp.if sp.now <= creature.auction:
            # Then take param price add 1 mutez and set it to creature price
            creature.price = params.price + sp.mutez(1)

# No Entry point. This happens internally. New Creature record?
    def newCreature(self, creatureId):
        # for a new creature return a record of - Timestamp of auction, isNew = False, price start empty at 0 mutez, the owner is the sender, and the creature Id
        return sp.record(creatureId = creatureId, owner = sp.sender, price = sp.mutez(0), isNew = False, auction = sp.timestamp(0))


@sp.add_test(name = "Crypto Cryptids Tests")
def test():
    # Assign 3 test accounts to 3 variables. creator being the manager of contract?
    creator = sp.test_account("Creator")
    alice   = sp.test_account("Alice")
    bob     = sp.test_account("Robert")
    # C1 is calling the CC class with the Auction duration and the address of the 'manager'
    c1 = CryptoCryptids(creator.address, newAuctionDuration = 10)
    # Call the smart py test_scenario function and assignit to variable
    scenario  = sp.test_scenario()
    # Add/Apply scenario to c1
    scenario += c1
    # I'm unclear why we 'remake' this function here
    def newCreature(creatureId, price):
        # The function here changes a few things returning- price is not 0 is is a variable called price, isNew is True
        return sp.record(creatureId = creatureId, owner = creator.address, price = sp.mutez(price), isNew = True, auction = sp.timestamp(0))

    # here we add test scenario to cryptid class where we call the build function, call self
    # (implicitly) and params (here params is New Creature function with creature Id set to 0
    # and price set to 10). We assign all of that to variable creature. Then once build is filled
    # with all that stuff collected, we use the run function which calls the address from creator
    # which is the sender to initiate the build! We do this 4 times  each time making a creature with
    # a new Id and building our catalog of creatures.
    scenario += c1.build(creature = newCreature(0, 10)).run(sender = creator)

    scenario += c1.build(creature = newCreature(1, 10)).run(sender = creator)

    scenario += c1.build(creature = newCreature(2, 10)).run(sender = creator)

    scenario += c1.build(creature = newCreature(3, 10)).run(sender = creator)

    # Now we test the buy function in the same way as the build.
    # buy requires params in this case we need the creature Id and the price of the creature
    # once we have that we again use the run method to get the address from alice accounts
    # and pull the amount of 10 mutesz from her. All the verifications within buy execute
    # although I am unclear on where we check to make sure sender has sufficient funds?
    # Alice buys 2 creatures, 1 and 2 ownership is transferred
    scenario += c1.buy(creatureId = 1, price = sp.mutez(10)).run(sender = alice, amount = sp.mutez(10))

    scenario += c1.buy(creatureId = 2, price = sp.mutez(10)).run(sender = alice, amount = sp.mutez(10))
    # Here Bob becomes the buyer aka the sender of funds to the owner of creature 1(alice) for 11 mutez
    # Now come the timestamps and I'm unclear what roll they play in the transaction, we add timestamp 3  to the now variable
    scenario += c1.buy(creatureId = 1, price = sp.mutez(11)).run(sender = bob, amount = sp.mutez(11), now = sp.timestamp(3))

    scenario += c1.buy(creatureId = 1, price = sp.mutez(15)).run(sender = alice, amount = sp.mutez(15), now = sp.timestamp(9))

    scenario.h2("A bad execution")

    scenario += c1.buy(  creatureId = 1, price = sp.mutez(20)).run(sender = bob, amount = sp.mutez(20), now = sp.timestamp(13), valid = False)
