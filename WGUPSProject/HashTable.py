class HashTable:
    # table uses 53 for capacity being a prime number above the 40 total package amount
    # time complexity O(n)
    def __init__(self, initial_capacity=53):
        self.table = []
        for i in range(initial_capacity):
            self.table.append([])

    # inserts package object into hash table for indexing. If already exists, updates package object correctly
    # time complexity O(1) due to one item per bucket
    def insert(self, key, item):
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]
        for kv in bucket_list:
            if kv[0] == key:
                kv[1] = item
                return True
        bucket_list.append([key, item])
        return True

    # returns package object from hash table using package id as key
    # time complexity O(1) due to one item per bucket
    def search(self, key):
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        if key in bucket_list[0]:
            return bucket_list[0][1]
        else:
            return None

    # removes package object from hash table
    # time complexity O(1) due to one item per bucket
    def remove(self, key):
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]
        if key in bucket_list:
            bucket_list.remove(key)
