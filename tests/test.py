class CurValueIteratorDescriptor:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class IteratorDescriptor:
    def __init__(self, name, start_value, end_value):
        self.name = name
        self.start_value = start_value
        self.end_value = end_value
        self.cur_value = start_value


iterators = dict()
iterators['i'] = IteratorDescriptor('i', 1, 6)
iterators['j'] = IteratorDescriptor('j', 10, 49)


def inc(cur_iter_values):
    cur_iter_values[-1].value += 1
    for i in reversed(range(len(cur_iter_values))):
        if cur_iter_values[i].value > iterators[cur_iter_values[i].name].end_value:
            cur_iter_values[i].value = iterators[cur_iter_values[i].name].start_value
            if i != 0:
                cur_iter_values[i - 1].value += 1
            else:
                break


def printValues(cur_iter_values):
    res = ''
    for i in range(len(cur_iter_values)):
        res += f'{cur_iter_values[i].name} = {cur_iter_values[i].value}, '
    print(res)


def main():
    cur_iter_values = [ CurValueIteratorDescriptor('i', 1), CurValueIteratorDescriptor('j', 10)]
    for i in range(240):
        inc(cur_iter_values)
        printValues(cur_iter_values)

if __name__ == '__main__':
    main()