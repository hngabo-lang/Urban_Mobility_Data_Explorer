# custom algorithm: Top K selection using a min_heap

class MinHeap:
    def __init__(self,key):
        self.items = []
        self.key = key

    def __len__(self):
        return len(self.items)

    def peek(self):
        return self.items[0]

    def push(self, item):
        self.items.append(item)
        self._sift_up(len(self.items) -1)

    def pop(self):
        """Remove and return the smallest item."""
        last = self.items.pop()
        if not self.items:
            return last
        smallest = self.items[0]
        self.items[0] = last
        self._sift_down(0)
        return smallest
    
    def replace_top(self, item):
        smallest = self.items[0]
        self.items[0] = item
        self._sift_down(0)
        return smallest

    def _swap(self, i, j):
        self.items[i], self.items[j] = self.items[j], self.items[i]

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self.key(self.items[i]) < self.key(self.items[parent]):
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        n = len(self.items)
        while True:
            left, right = 2 * i + 1, 2 * i + 2
            smallest = i
            if left < n and self.key(self.items[left]) < self.key(self.items[smallest]):
                smallest = left
            if right < n and self.key(self.items[right]) < self.key(self.items[smallest]):
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

# return items with the largest key, biggest first
def top_k(items, k, key):
    if k <= 0:
        return []
    heap = MinHeap(key)
    for item in items:
        if len(heap) < k:
            heap.push(item)                  # podium has space
        elif key(item) > key(heap.peek()):
            heap.replace_top(item)   

    result = []
    while len(heap) > 0:
        result.append(heap.pop()) 
    return result[::-1]

if __name__ == "__main__":
    import random

    data = [{"id": i, "trips": random.randint(0, 10_000)} for i in range(500)]
    by_trips = lambda d: d["trips"]

    for k in [1, 5, 10, 50, 500, 600]:
        ours = [d["trips"] for d in top_k(data, k, by_trips)]
        expected = [d["trips"] for d in sorted(data, key=by_trips, reverse=True)[:k]]
        assert ours == expected, f"Mismatch for k={k}"
        print(f"k={k:>3}: OK")

    print("All tests passed.")

