class Stack:
    def __init__(self):
        self.stack = []

    @property
    def length(self):
        return len(self.stack)

    def peek(self):
        if len(self.stack) == 0:
            return None
        return self.stack[self.length - 1]

    def push(self, f):
        self.stack.append(f)

    def pop(self):
        if len(self.stack) == 0:
            return None
        return self.stack.pop()

    def __iter__(self):
        return iter(self.stack)
