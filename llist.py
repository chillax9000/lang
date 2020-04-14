from dataclasses import dataclass
import operator


@dataclass
class Pointer:
    prev: 'Pointer' = None
    next: 'Pointer' = None
    value: None = None


class DLList:
    """ with a <-> b meaning a.next == b and b.prev == a:
    None <- element_0 <-> ... <-> element_n -> None
    element_0 <- sentinel -> element_n
    """
    def __init__(self, iterable):
        self.sentinel = Pointer()
        for e in iterable:
            self.append(e)

    def _first(self, element):
        pointer = Pointer(value=element)
        self.sentinel.next = pointer
        self.sentinel.prev = pointer

    def append(self, element):
        if self.sentinel.next is None:  # empty list
            self._first(element)
        else:
            _last_pointer = self.sentinel.prev
            pointer = Pointer(value=element,
                              prev=_last_pointer)
            _last_pointer.next = pointer
            self.sentinel.prev = pointer

    def insert_after(self, element, new_element):
        for ptr in self.ptr_itr():
            if ptr.value == element:
                _next_ptr = ptr.next
                new_ptr = Pointer(value=new_element,
                                  prev=ptr,
                                  next=_next_ptr)
                ptr.next = new_ptr
                if _next_ptr is not None:
                    _next_ptr.prev = new_ptr

    def remove(self, element):
        for ptr in self.ptr_itr():
            if ptr.value == element:
                if ptr.prev is not None:
                    ptr.prev.next = ptr.next
                else:  # removing first element
                    self.sentinel.next = ptr.next
                if ptr.next is not None:
                    ptr.next.prev = ptr.prev
                else:  # removing last element
                    self.sentinel.prev = ptr.prev

    def ptr_itr(self):
        pointer = self.sentinel.next
        while pointer is not None:
            yield pointer
            pointer = pointer.next

    def __iter__(self):
        yield from map(operator.attrgetter("value"), self.ptr_itr())

    def __repr__(self):
        return " -> ".join(map(str, self))

    def __len__(self):
        n = 0
        for ptr in self.ptr_itr():
            n += 1
        return n
