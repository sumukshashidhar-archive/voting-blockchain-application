# this is a simple terminal app to add data to our database for the user hashes
from hashlib import sha256
import random
def add_user(fname, lname, password):
    """
    Function adds a user to our database.

    To protect user anonyminity and prevent vote suppression, we will not be storing the actual identity
    of these voters, rather we will be storing a hash based on details, that we can verify later on.

    This returns the voterid for the person. We will be generating a voterid here, only ONCE.
    """
    voter_id = random.randint(10000000, 999999999)
    details_string = fname + lname + password + voter_id
    hashed = sha256(details_string.encode()).hexdigest()

    ## now add this to the mysql database. Just make one column called voters, and store this hash.

    return voter_id


def verify_exists(fname, lname, password, voter_id):
    """
    This function is to ensure that a certain voter exists.

    It takes in some data, and computes the hash. If the hash exists, it returns True, else false.
    """
    details_string = fname + lname + password + voter_id
    hashed = sha256(details_string.encode()).hexdigest()

    # now verify that this hash exists in the voters column in the database.

    return True



def make_candidates_table():
    return


def get_candidates():
    return


