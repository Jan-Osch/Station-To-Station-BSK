import sys
from Queue import Queue

from Client import Client
from Server import Server
from Utils import *

g = 6
p = 17
rsa_alice = RSA(17, 31, 7)
rsa_bob = RSA(17, 31, 19)
keys = {'alice': (7, 17 * 31), 'bob': (19, 17 * 31)}
queue_to_client = Queue()
queue_to_server = Queue()
alice = Client(name='alice',
               g=g,
               p=p,
               input_queue=queue_to_client,
               output_queue=queue_to_server,
               rsa_obj=rsa_alice,
               keys=keys,
               server_id='bob')
bob = Server(name='bob',
             g=g,
             p=p,
             input_queue=queue_to_server,
             output_queue=queue_to_client,
             rsa_obj=rsa_bob,
             keys=keys,
             client_id='alice')

assert alice.K is None
assert bob.K is None
assert alice.finished_successfully is None
assert bob.finished_successfully is None
alice.start()
bob.start()
alice.join(timeout=50)
bob.join(timeout=50)
killed = False
if alice.is_alive():
    alice._Thread__stop()
    killed = True
if bob.is_alive():
    bob._Thread__stop()
    killed = True
if killed:
    sys.exit(1)
assert alice.finished_successfully is True
assert bob.finished_successfully is True
assert alice.K == bob.K
