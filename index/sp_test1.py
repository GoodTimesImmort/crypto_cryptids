# LEARNING TO USE THE SMARTPY LIBRARY
# We can start with an example: a very simple contract StoreValue that stores
# some value that we call storedValue and enable its users to either
# replace it by calling replace, double it by calling double or divide it by calling divide.

# import the library 'smartpy'and shorten it's name for functionality sake to 'sp'
import smartpy as sp

# Create a Class called 'StoredValue' with the argument 'Contract' called from the SmartPy library (sp)
class StoreValue(sp.Contract):
    # define a function called __init__ that takes the 'self' and 'value' arguments
    def __init__(self, value):
        # from self get __init__ with storedValue parameter 
        self.init(storedValue = value)

    @sp.entry_point
    def replace(self, params):
        self.data.storedValue = params.value
