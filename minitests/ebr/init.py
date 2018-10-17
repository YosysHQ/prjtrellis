import random
random.seed(1)
for i in range(2048):
    print("{:03x}".format(random.randint(0, 511)))
