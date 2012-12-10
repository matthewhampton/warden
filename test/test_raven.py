from raven import Client
import time

client  = Client('http://1ebbaaaf4a67410e8cb052d830cc082b:b2584562c7ff4e8fb5b26dfbbeebc292@localhost:8000/2')

client.captureMessage('Hello World')

for i in range(1000):
    client.captureMessage('Bing')
    time.sleep(0.1)
