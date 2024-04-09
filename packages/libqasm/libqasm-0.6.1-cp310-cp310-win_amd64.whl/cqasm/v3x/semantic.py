import functools
import struct
import cqasm.v3x.instruction
import cqasm.v3x.primitives
import cqasm.v3x.types
import cqasm.v3x.values


_typemap = {}


def _cbor_read_intlike(cbor, offset, info):
    """Parses the additional information and reads any additional bytes it
    specifies the existence of, and returns the encoded integer. offset
    should point to the byte immediately following the initial byte. Returns
    the encoded integer and the offset immediately following the object."""

    # Info less than 24 is a shorthand for the integer itself.
    if info < 24:
        return info, offset

    # 24 is 8-bit following the info byte.
    if info == 24:
        return cbor[offset], offset + 1

    # 25 is 16-bit following the info byte.
    if info == 25:
        val, = struct.unpack('>H', cbor[offset:offset+2])
        return val, offset + 2

    # 26 is 32-bit following the info byte.
    if info == 26:
        val, = struct.unpack('>I', cbor[offset:offset+4])
        return val, offset + 4

    # 27 is 64-bit following the info byte.
    if info == 27:
        val, = struct.unpack('>Q', cbor[offset:offset+8])
        return val, offset + 8

    # Info greater than or equal to 28 is illegal. Note that 31 is used for
    # indefinite lengths, so this must be checked prior to calling this
    # method.
    raise ValueError("invalid CBOR: illegal additional info for integer or object length")


def _sub_cbor_to_py(cbor, offset):
    """Converts the CBOR object starting at cbor[offset] to its Python
    representation for as far as tree-gen supports CBOR. Returns this Python
    representation and the offset immediately following the CBOR representation
    thereof. Supported types:

     - 0: unsigned integer (int)
     - 1: negative integer (int)
     - 2: byte string (bytes)
     - 3: UTF-8 string (str)
     - 4: array (list)
     - 5: map (dict)
     - 6: semantic tag (ignored)
     - 7.20: false (bool)
     - 7.21: true (bool)
     - 7.22: null (NoneType)
     - 7.27: double-precision float (float)

    Both definite-length and indefinite-length notation is supported for sized
    objects (strings, arrays, maps). A ValueError is thrown if the CBOR is
    invalid or contains unsupported structures."""

    # Read the initial byte.
    initial = cbor[offset]
    typ = initial >> 5
    info = initial & 0x1F
    offset += 1

    # Handle unsigned integer (0) and negative integer (1).
    if typ <= 1:
        value, offset = _cbor_read_intlike(cbor, offset, info)
        if typ == 1:
            value = -1 - value
        return value, offset

    # Handle byte string (2) and UTF-8 string (3).
    if typ <= 3:

        # Gather components of the string in here.
        if info == 31:

            # Handle indefinite length strings. These consist of a
            # break-terminated (0xFF) list of definite-length strings of the
            # same type.
            value = []
            while True:
                sub_initial = cbor[offset]; offset += 1
                if sub_initial == 0xFF:
                    break
                sub_typ = sub_initial >> 5
                sub_info = sub_initial & 0x1F
                if sub_typ != typ:
                    raise ValueError('invalid CBOR: illegal indefinite-length string component')

                # Seek past definite-length string component. The size in
                # bytes is encoded as an integer.
                size, offset = _cbor_read_intlike(cbor, offset, sub_info)
                value.append(cbor[offset:offset + size])
                offset += size
            value = b''.join(value)

        else:

            # Handle definite-length strings. The size in bytes is encoded as
            # an integer.
            size, offset = _cbor_read_intlike(cbor, offset, info)
            value = cbor[offset:offset + size]
            offset += size

        if typ == 3:
            value = value.decode('UTF-8')
        return value, offset

    # Handle array (4) and map (5).
    if typ <= 5:

        # Create result container.
        container = [] if typ == 4 else {}

        # Handle indefinite length arrays and maps.
        if info == 31:

            # Read objects/object pairs until we encounter a break.
            while cbor[offset] != 0xFF:
                if typ == 4:
                    value, offset = _sub_cbor_to_py(cbor, offset)
                    container.append(value)
                else:
                    key, offset = _sub_cbor_to_py(cbor, offset)
                    if not isinstance(key, str):
                        raise ValueError('invalid CBOR: map key is not a UTF-8 string')
                    value, offset = _sub_cbor_to_py(cbor, offset)
                    container[key] = value

            # Seek past the break.
            offset += 1

        else:

            # Handle definite-length arrays and maps. The amount of
            # objects/object pairs is encoded as an integer.
            size, offset = _cbor_read_intlike(cbor, offset, info)
            for _ in range(size):
                if typ == 4:
                    value, offset = _sub_cbor_to_py(cbor, offset)
                    container.append(value)
                else:
                    key, offset = _sub_cbor_to_py(cbor, offset)
                    if not isinstance(key, str):
                        raise ValueError('invalid CBOR: map key is not a UTF-8 string')
                    value, offset = _sub_cbor_to_py(cbor, offset)
                    container[key] = value

        return container, offset

    # Handle semantic tags.
    if typ == 6:

        # We don't use semantic tags for anything, but ignoring them is
        # legal and reading past them is easy enough.
        _, offset = _cbor_read_intlike(cbor, offset, info)
        return _sub_cbor_to_py(cbor, offset)

    # Handle major type 7. Here, the type is defined by the additional info.
    # Additional info 24 is reserved for having the type specified by the
    # next byte, but all such values are unassigned.
    if info == 20:
        # false
        return False, offset

    if info == 21:
        # true
        return True, offset

    if info == 22:
        # null
        return None, offset

    if info == 23:
        # Undefined value.
        raise ValueError('invalid CBOR: undefined value is not supported')

    if info == 25:
        # Half-precision float.
        raise ValueError('invalid CBOR: half-precision float is not supported')

    if info == 26:
        # Single-precision float.
        raise ValueError('invalid CBOR: single-precision float is not supported')

    if info == 27:
        # Double-precision float.
        value, = struct.unpack('>d', cbor[offset:offset+8])
        return value, offset + 8

    if info == 31:
        # Break value used for indefinite-length objects.
        raise ValueError('invalid CBOR: unexpected break')

    raise ValueError('invalid CBOR: unknown type code')


def _cbor_to_py(cbor):
    """Converts the given CBOR object (bytes) to its Python representation for
    as far as tree-gen supports CBOR. Supported types:

     - 0: unsigned integer (int)
     - 1: negative integer (int)
     - 2: byte string (bytes)
     - 3: UTF-8 string (str)
     - 4: array (list)
     - 5: map (dict)
     - 6: semantic tag (ignored)
     - 7.20: false (bool)
     - 7.21: true (bool)
     - 7.22: null (NoneType)
     - 7.27: double-precision float (float)

    Both definite-length and indefinite-length notation is supported for sized
    objects (strings, arrays, maps). A ValueError is thrown if the CBOR is
    invalid or contains unsupported structures."""

    value, length = _sub_cbor_to_py(cbor, 0)
    if length < len(cbor):
        raise ValueError('invalid CBOR: garbage at the end')
    return value


class _Cbor(bytes):
    """Marker class indicating that this bytes object represents CBOR."""
    pass


def _cbor_write_intlike(value, major=0):
    """Converts the given integer to its minimal representation in CBOR. The
    major code can be overridden to write lengths for strings, arrays, and
    maps."""

    # Negative integers use major code 1.
    if value < 0:
        major = 1
        value = -1 - value
    initial = major << 5

    # Use the minimal representation.
    if value < 24:
        return struct.pack('>B', initial | value)
    if value < 0x100:
        return struct.pack('>BB', initial | 24, value)
    if value < 0x10000:
        return struct.pack('>BH', initial | 25, value)
    if value < 0x100000000:
        return struct.pack('>BI', initial | 26, value)
    if value < 0x10000000000000000:
        return struct.pack('>BQ', initial | 27, value)

    raise ValueError('integer too large for CBOR (bigint not supported)')


def _py_to_cbor(value, type_converter=None):
    """Inverse of _cbor_to_py(). type_converter optionally specifies a function
    that takes a value and either converts it to a primitive for serialization,
    converts it to a _Cbor object manually, or raises a TypeError if no
    conversion is known. If no type_converter is specified, a TypeError is
    raised in all cases the type_converter would otherwise be called. The cbor
    serialization is returned using a _Cbor object, which is just a marker class
    behaving just like bytes."""
    if isinstance(value, _Cbor):
        return value

    if isinstance(value, int):
        return _Cbor(_cbor_write_intlike(value))

    if isinstance(value, float):
        return _Cbor(struct.pack('>Bd', 0xFB, value))

    if isinstance(value, str):
        value = value.encode('UTF-8')
        return _Cbor(_cbor_write_intlike(len(value), 3) + value)

    if isinstance(value, bytes):
        return _Cbor(_cbor_write_intlike(len(value), 2) + value)

    if value is False:
        return _Cbor(b'\xF4')

    if value is True:
        return _Cbor(b'\xF5')

    if value is None:
        return _Cbor(b'\xF6')

    if isinstance(value, (list, tuple)):
        cbor = [_cbor_write_intlike(len(value), 4)]
        for val in value:
            cbor.append(_py_to_cbor(val, type_converter))
        return _Cbor(b''.join(cbor))

    if isinstance(value, dict):
        cbor = [_cbor_write_intlike(len(value), 5)]
        for key, val in sorted(value.items()):
            if not isinstance(key, str):
                raise TypeError('dict keys must be strings')
            cbor.append(_py_to_cbor(key, type_converter))
            cbor.append(_py_to_cbor(val, type_converter))
        return _Cbor(b''.join(cbor))

    if type_converter is not None:
        return _py_to_cbor(type_converter(value))

    raise TypeError('unsupported type for conversion to cbor: %r' % (value,))


class NotWellFormed(ValueError):
    """Exception class for well-formedness checks."""

    def __init__(self, msg):
        super().__init__('not well-formed: ' + str(msg))


class Node(object):
    """Base class for nodes."""

    __slots__ = ['_annot']

    def __init__(self):
        super().__init__()
        self._annot = {}

    def __getitem__(self, key):
        """Returns the annotation object with the specified key, or raises
        KeyError if not found."""
        if not isinstance(key, str):
            raise TypeError('indexing a node with something other than an '
                            'annotation key string')
        return self._annot[key]

    def __setitem__(self, key, val):
        """Assigns the annotation object with the specified key."""
        if not isinstance(key, str):
            raise TypeError('indexing a node with something other than an '
                            'annotation key string')
        self._annot[key] = val

    def __delitem__(self, key):
        """Deletes the annotation object with the specified key."""
        if not isinstance(key, str):
            raise TypeError('indexing a node with something other than an '
                            'annotation key string')
        del self._annot[key]

    def __contains__(self, key):
        """Returns whether an annotation exists for the specified key."""
        return key in self._annot

    @staticmethod
    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it. Note that this is overridden
        by the actual node class implementations; this base function does very
        little."""
        if id_map is None:
            id_map = {}
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes. Note that this is
        overridden by the actual node class implementations; this base function
        always raises an exception."""
        raise NotWellFormed('found node of abstract type ' + type(self).__name__)

    def check_well_formed(self):
        """Checks whether the tree starting at this node is well-formed. That
        is:

         - all One, Link, and Many edges have (at least) one entry;
         - all the One entries internally stored by Any/Many have an entry;
         - all Link and filled OptLink nodes link to a node that's reachable
           from this node;
         - the nodes referred to be One/Maybe only appear once in the tree
           (except through links).

        If it isn't well-formed, a NotWellFormed is thrown."""
        self.check_complete()

    def is_well_formed(self):
        """Returns whether the tree starting at this node is well-formed. That
        is:

         - all One, Link, and Many edges have (at least) one entry;
         - all the One entries internally stored by Any/Many have an entry;
         - all Link and filled OptLink nodes link to a node that's reachable
           from this node;
         - the nodes referred to be One/Maybe only appear once in the tree
           (except through links)."""
        try:
            self.check_well_formed()
            return True
        except NotWellFormed:
            return False

    def copy(self):
        """Returns a shallow copy of this node. Note that this is overridden by
        the actual node class implementations; this base function always raises
        an exception."""
        raise TypeError('can\'t copy node of abstract type ' + type(self).__name__)

    def clone(self):
        """Returns a deep copy of this node. Note that this is overridden by
        the actual node class implementations; this base function always raises
        an exception."""
        raise TypeError('can\'t clone node of abstract type ' + type(self).__name__)

    @classmethod
    def deserialize(cls, cbor):
        """Attempts to deserialize the given cbor object (either as bytes or as
        its Python primitive representation) into a node of this type."""
        if isinstance(cbor, bytes):
            cbor = _cbor_to_py(cbor)
        seq_to_ob = {}
        links = []
        root = cls._deserialize(cbor, seq_to_ob, links)
        for link_setter, seq in links:
            ob = seq_to_ob.get(seq, None)
            if ob is None:
                raise ValueError('found link to nonexistent object')
            link_setter(ob)
        return root

    def serialize(self):
        """Serializes this node into its cbor representation in the form of a
        bytes object."""
        id_map = self.find_reachable()
        self.check_complete(id_map)
        return _py_to_cbor(self._serialize(id_map))

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        node_type = _typemap.get(cbor.get('@t'), None)
        if node_type is None:
            raise ValueError('unknown node type (@t): ' + str(cbor.get('@t')))
        return node_type._deserialize(cbor, seq_to_ob, links)


@functools.total_ordering
class _Multiple(object):
    """Base class for the Any* and Many* edge helper classes. Inheriting
    classes must set the class constant _T to the node type they are made
    for."""

    __slots__ = ['_l']

    def __init__(self,  *args, **kwargs):
        super().__init__()
        self._l = list(*args, **kwargs)
        for idx, val in enumerate(self._l):
            if not isinstance(val, self._T):
                raise TypeError(
                    'object {!r} at index {:d} is not an instance of {!r}'
                    .format(val, idx, self._T))

    def __repr__(self):
        return '{}({!r})'.format(type(self).__name__, self._l)

    def clone(self):
        return self.__class__(map(lambda node: node.clone(), self._l))

    def __len__(self):
        return len(self._l)

    def __getitem__(self, idx):
        return self._l[idx]

    def __setitem__(self, idx, val):
        if not isinstance(val, self._T):
            raise TypeError(
                'object {!r} is not an instance of {!r}'
                .format(val, idx, self._T))
        self._l[idx] = val

    def __delitem__(self, idx):
        del self._l[idx]

    def __iter__(self):
        return iter(self._l)

    def __reversed__(self):
        return reversed(self._l)

    def __contains__(self, val):
        return val in self._l

    def append(self, val):
        if not isinstance(val, self._T):
            raise TypeError(
                'object {!r} is not an instance of {!r}'
                .format(val, self._T))
        self._l.append(val)

    def extend(self, iterable):
        for val in iterable:
            self.append(val)

    def insert(self, idx, val):
        if not isinstance(val, self._T):
            raise TypeError(
                'object {!r} is not an instance of {!r}'
                .format(val, self._T))
        self._l.insert(idx, val)

    def remote(self, val):
        self._l.remove(val)

    def pop(self, idx=-1):
        return self._l.pop(idx)

    def clear(self):
        self._l.clear()

    def idx(self, val, start=0, end=-1):
        return self._l.idx(val, start, end)

    def count(self, val):
        return self._l.count(val)

    def sort(self, key=None, reverse=False):
        self._l.sort(key=key, reverse=reverse)

    def reverse(self):
        self._l.reverse()

    def copy(self):
        return self.__class__(self)

    def __eq__(self, other):
        if not isinstance(other, _Multiple):
            return False
        return self._l == other._l

    def __lt__(self, other):
        return self._l < other._l

    def __iadd__(self, other):
        self.extend(other)

    def __add__(self, other):
        copy = self.copy()
        copy += other
        return copy

    def __imul__(self, other):
        self._l *= other

    def __mul__(self, other):
        copy = self.copy()
        copy *= other
        return copy

    def __rmul__(self, other):
        copy = self.copy()
        copy *= other
        return copy


class MultiNode(_Multiple):
    """Wrapper for an edge with multiple Node objects."""

    _T = Node


def _cloned(obj):
    """Attempts to clone the given object by calling its clone() method, if it
    has one."""
    if hasattr(obj, 'clone'):
        return obj.clone()
    return obj


class Annotated(Node):
    """Represents a node that carries annotation data."""

    __slots__ = [
        '_attr_annotations',
    ]

    def __init__(
        self,
        annotations=None,
    ):
        super().__init__()
        self.annotations = annotations

    @property
    def annotations(self):
        return self._attr_annotations

    @annotations.setter
    def annotations(self, val):
        if val is None:
            del self.annotations
            return
        if not isinstance(val, MultiAnnotationData):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('annotations must be of type MultiAnnotationData')
            val = MultiAnnotationData(val)
        self._attr_annotations = val

    @annotations.deleter
    def annotations(self):
        self._attr_annotations = MultiAnnotationData()

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ == 'Variable':
            return Variable._deserialize(cbor, seq_to_ob, links)
        if typ == 'Instruction':
            return Instruction._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Annotated'}

        # Serialize the annotations field.
        field = {'@T': '*'}
        lst = []
        for el in self._attr_annotations:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['annotations'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiAnnotated(_Multiple):
    """Wrapper for an edge with multiple Annotated objects."""

    _T = Annotated


_typemap['Annotated'] = Annotated

class AnnotationData(Node):
    """Represents an annotation."""

    __slots__ = [
        '_attr_interface',
        '_attr_operation',
        '_attr_operands',
    ]

    def __init__(
        self,
        interface=None,
        operation=None,
        operands=None,
    ):
        super().__init__()
        self.interface = interface
        self.operation = operation
        self.operands = operands

    @property
    def interface(self):
        """The interface this annotation is intended for. If a target doesn't
        support an interface, it should silently ignore the annotation."""
        return self._attr_interface

    @interface.setter
    def interface(self, val):
        if val is None:
            del self.interface
            return
        if not isinstance(val, cqasm.v3x.primitives.Str):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('interface must be of type cqasm.v3x.primitives.Str')
            val = cqasm.v3x.primitives.Str(val)
        self._attr_interface = val

    @interface.deleter
    def interface(self):
        self._attr_interface = cqasm.v3x.primitives.Str()

    @property
    def operation(self):
        """The operation within the interface that this annotation is intended
        for. If a target supports the corresponding interface but not the
        operation, it should throw an error."""
        return self._attr_operation

    @operation.setter
    def operation(self, val):
        if val is None:
            del self.operation
            return
        if not isinstance(val, cqasm.v3x.primitives.Str):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('operation must be of type cqasm.v3x.primitives.Str')
            val = cqasm.v3x.primitives.Str(val)
        self._attr_operation = val

    @operation.deleter
    def operation(self):
        self._attr_operation = cqasm.v3x.primitives.Str()

    @property
    def operands(self):
        """Any operands attached to the annotation."""
        return self._attr_operands

    @operands.setter
    def operands(self, val):
        if val is None:
            del self.operands
            return
        if not isinstance(val, cqasm.v3x.values.MultiNode):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('operands must be of type cqasm.v3x.values.MultiNode')
            val = cqasm.v3x.values.MultiNode(val)
        self._attr_operands = val

    @operands.deleter
    def operands(self):
        self._attr_operands = cqasm.v3x.values.MultiNode()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, AnnotationData):
            return False
        if self.interface != other.interface:
            return False
        if self.operation != other.operation:
            return False
        if self.operands != other.operands:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('AnnotationData(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('interface: ')
        s.append(str(self.interface) + '\n')
        s.append('  '*indent)
        s.append('operation: ')
        s.append(str(self.operation) + '\n')
        s.append('  '*indent)
        s.append('operands: ')
        if not self.operands:
            s.append('-\n')
        else:
            s.append('[\n')
            for child in self.operands:
                s.append(child.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + ']\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        for el in self._attr_operands:
            el.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        for child in self._attr_operands:
            child.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return AnnotationData(
            interface=self._attr_interface,
            operation=self._attr_operation,
            operands=self._attr_operands.copy()
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return AnnotationData(
            interface=_cloned(self._attr_interface),
            operation=_cloned(self._attr_operation),
            operands=_cloned(self._attr_operands)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'AnnotationData':
            raise ValueError('found node serialization for ' + typ + ', but expected AnnotationData')

        # Deserialize the interface field.
        field = cbor.get('interface', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field interface')
        if hasattr(cqasm.v3x.primitives.Str, 'deserialize_cbor'):
            f_interface = cqasm.v3x.primitives.Str.deserialize_cbor(field)
        else:
            f_interface = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Str, field)

        # Deserialize the operation field.
        field = cbor.get('operation', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field operation')
        if hasattr(cqasm.v3x.primitives.Str, 'deserialize_cbor'):
            f_operation = cqasm.v3x.primitives.Str.deserialize_cbor(field)
        else:
            f_operation = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Str, field)

        # Deserialize the operands field.
        field = cbor.get('operands', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field operands')
        if field.get('@T') != '*':
            raise ValueError('unexpected edge type for field operands')
        data = field.get('@d', None)
        if not isinstance(data, list):
            raise ValueError('missing serialization of Any/Many contents')
        f_operands = cqasm.v3x.values.MultiNode()
        for element in data:
            if element.get('@T') != '1':
                raise ValueError('unexpected edge type for Any/Many element')
            f_operands.append(cqasm.v3x.values.Node._deserialize(element, seq_to_ob, links))

        # Construct the AnnotationData node.
        node = AnnotationData(f_interface, f_operation, f_operands)

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = cqasm.v3x.primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'AnnotationData'}

        # Serialize the interface field.
        if hasattr(self._attr_interface, 'serialize_cbor'):
            cbor['interface'] = self._attr_interface.serialize_cbor()
        else:
            cbor['interface'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Str, self._attr_interface)

        # Serialize the operation field.
        if hasattr(self._attr_operation, 'serialize_cbor'):
            cbor['operation'] = self._attr_operation.serialize_cbor()
        else:
            cbor['operation'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Str, self._attr_operation)

        # Serialize the operands field.
        field = {'@T': '*'}
        lst = []
        for el in self._attr_operands:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['operands'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiAnnotationData(_Multiple):
    """Wrapper for an edge with multiple AnnotationData objects."""

    _T = AnnotationData


_typemap['AnnotationData'] = AnnotationData

class Block(Node):
    __slots__ = [
        '_attr_statements',
    ]

    def __init__(
        self,
        statements=None,
    ):
        super().__init__()
        self.statements = statements

    @property
    def statements(self):
        return self._attr_statements

    @statements.setter
    def statements(self, val):
        if val is None:
            del self.statements
            return
        if not isinstance(val, MultiStatement):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('statements must be of type MultiStatement')
            val = MultiStatement(val)
        self._attr_statements = val

    @statements.deleter
    def statements(self):
        self._attr_statements = MultiStatement()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Block):
            return False
        if self.statements != other.statements:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Block(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('statements: ')
        if not self.statements:
            s.append('-\n')
        else:
            s.append('[\n')
            for child in self.statements:
                s.append(child.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + ']\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        for el in self._attr_statements:
            el.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        for child in self._attr_statements:
            child.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return Block(
            statements=self._attr_statements.copy()
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Block(
            statements=_cloned(self._attr_statements)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'Block':
            raise ValueError('found node serialization for ' + typ + ', but expected Block')

        # Deserialize the statements field.
        field = cbor.get('statements', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field statements')
        if field.get('@T') != '*':
            raise ValueError('unexpected edge type for field statements')
        data = field.get('@d', None)
        if not isinstance(data, list):
            raise ValueError('missing serialization of Any/Many contents')
        f_statements = MultiStatement()
        for element in data:
            if element.get('@T') != '1':
                raise ValueError('unexpected edge type for Any/Many element')
            f_statements.append(Statement._deserialize(element, seq_to_ob, links))

        # Construct the Block node.
        node = Block(f_statements)

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = cqasm.v3x.primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Block'}

        # Serialize the statements field.
        field = {'@T': '*'}
        lst = []
        for el in self._attr_statements:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['statements'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiBlock(_Multiple):
    """Wrapper for an edge with multiple Block objects."""

    _T = Block


_typemap['Block'] = Block

class Statement(Annotated):
    __slots__ = []

    def __init__(
        self,
        annotations=None,
    ):
        super().__init__(annotations=annotations)

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ == 'Instruction':
            return Instruction._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Statement'}

        # Serialize the annotations field.
        field = {'@T': '*'}
        lst = []
        for el in self._attr_annotations:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['annotations'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiStatement(_Multiple):
    """Wrapper for an edge with multiple Statement objects."""

    _T = Statement


_typemap['Statement'] = Statement

class Instruction(Statement):
    """Regular instruction (a gate, or a measure instruction)."""

    __slots__ = [
        '_attr_instruction_ref',
        '_attr_name',
        '_attr_operands',
    ]

    def __init__(
        self,
        instruction_ref=None,
        name=None,
        operands=None,
        annotations=None,
    ):
        super().__init__(annotations=annotations)
        self.instruction_ref = instruction_ref
        self.name = name
        self.operands = operands

    @property
    def instruction_ref(self):
        return self._attr_instruction_ref

    @instruction_ref.setter
    def instruction_ref(self, val):
        if val is None:
            del self.instruction_ref
            return
        if not isinstance(val, cqasm.v3x.instruction.InstructionRef):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('instruction_ref must be of type cqasm.v3x.instruction.InstructionRef')
            val = cqasm.v3x.instruction.InstructionRef(val)
        self._attr_instruction_ref = val

    @instruction_ref.deleter
    def instruction_ref(self):
        self._attr_instruction_ref = cqasm.v3x.instruction.InstructionRef()

    @property
    def name(self):
        return self._attr_name

    @name.setter
    def name(self, val):
        if val is None:
            del self.name
            return
        if not isinstance(val, cqasm.v3x.primitives.Str):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('name must be of type cqasm.v3x.primitives.Str')
            val = cqasm.v3x.primitives.Str(val)
        self._attr_name = val

    @name.deleter
    def name(self):
        self._attr_name = cqasm.v3x.primitives.Str()

    @property
    def operands(self):
        return self._attr_operands

    @operands.setter
    def operands(self, val):
        if val is None:
            del self.operands
            return
        if not isinstance(val, cqasm.v3x.values.MultiValueBase):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('operands must be of type cqasm.v3x.values.MultiValueBase')
            val = cqasm.v3x.values.MultiValueBase(val)
        self._attr_operands = val

    @operands.deleter
    def operands(self):
        self._attr_operands = cqasm.v3x.values.MultiValueBase()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Instruction):
            return False
        if self.instruction_ref != other.instruction_ref:
            return False
        if self.name != other.name:
            return False
        if self.operands != other.operands:
            return False
        if self.annotations != other.annotations:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Instruction(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('instruction_ref: ')
        s.append(str(self.instruction_ref) + '\n')
        s.append('  '*indent)
        s.append('name: ')
        s.append(str(self.name) + '\n')
        s.append('  '*indent)
        s.append('operands: ')
        if not self.operands:
            s.append('-\n')
        else:
            s.append('[\n')
            for child in self.operands:
                s.append(child.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + ']\n')
        s.append('  '*indent)
        s.append('annotations: ')
        if not self.annotations:
            s.append('-\n')
        else:
            s.append('[\n')
            for child in self.annotations:
                s.append(child.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + ']\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        for el in self._attr_operands:
            el.find_reachable(id_map)
        for el in self._attr_annotations:
            el.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        for child in self._attr_operands:
            child.check_complete(id_map)
        for child in self._attr_annotations:
            child.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return Instruction(
            instruction_ref=self._attr_instruction_ref,
            name=self._attr_name,
            operands=self._attr_operands.copy(),
            annotations=self._attr_annotations.copy()
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Instruction(
            instruction_ref=_cloned(self._attr_instruction_ref),
            name=_cloned(self._attr_name),
            operands=_cloned(self._attr_operands),
            annotations=_cloned(self._attr_annotations)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'Instruction':
            raise ValueError('found node serialization for ' + typ + ', but expected Instruction')

        # Deserialize the instruction_ref field.
        field = cbor.get('instruction_ref', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field instruction_ref')
        if hasattr(cqasm.v3x.instruction.InstructionRef, 'deserialize_cbor'):
            f_instruction_ref = cqasm.v3x.instruction.InstructionRef.deserialize_cbor(field)
        else:
            f_instruction_ref = cqasm.v3x.primitives.deserialize(cqasm.v3x.instruction.InstructionRef, field)

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if hasattr(cqasm.v3x.primitives.Str, 'deserialize_cbor'):
            f_name = cqasm.v3x.primitives.Str.deserialize_cbor(field)
        else:
            f_name = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Str, field)

        # Deserialize the operands field.
        field = cbor.get('operands', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field operands')
        if field.get('@T') != '*':
            raise ValueError('unexpected edge type for field operands')
        data = field.get('@d', None)
        if not isinstance(data, list):
            raise ValueError('missing serialization of Any/Many contents')
        f_operands = cqasm.v3x.values.MultiValueBase()
        for element in data:
            if element.get('@T') != '1':
                raise ValueError('unexpected edge type for Any/Many element')
            f_operands.append(cqasm.v3x.values.ValueBase._deserialize(element, seq_to_ob, links))

        # Deserialize the annotations field.
        field = cbor.get('annotations', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field annotations')
        if field.get('@T') != '*':
            raise ValueError('unexpected edge type for field annotations')
        data = field.get('@d', None)
        if not isinstance(data, list):
            raise ValueError('missing serialization of Any/Many contents')
        f_annotations = MultiAnnotationData()
        for element in data:
            if element.get('@T') != '1':
                raise ValueError('unexpected edge type for Any/Many element')
            f_annotations.append(AnnotationData._deserialize(element, seq_to_ob, links))

        # Construct the Instruction node.
        node = Instruction(f_instruction_ref, f_name, f_operands, f_annotations)

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = cqasm.v3x.primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Instruction'}

        # Serialize the instruction_ref field.
        if hasattr(self._attr_instruction_ref, 'serialize_cbor'):
            cbor['instruction_ref'] = self._attr_instruction_ref.serialize_cbor()
        else:
            cbor['instruction_ref'] = cqasm.v3x.primitives.serialize(cqasm.v3x.instruction.InstructionRef, self._attr_instruction_ref)

        # Serialize the name field.
        if hasattr(self._attr_name, 'serialize_cbor'):
            cbor['name'] = self._attr_name.serialize_cbor()
        else:
            cbor['name'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Str, self._attr_name)

        # Serialize the operands field.
        field = {'@T': '*'}
        lst = []
        for el in self._attr_operands:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['operands'] = field

        # Serialize the annotations field.
        field = {'@T': '*'}
        lst = []
        for el in self._attr_annotations:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['annotations'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiInstruction(_Multiple):
    """Wrapper for an edge with multiple Instruction objects."""

    _T = Instruction


_typemap['Instruction'] = Instruction

class Program(Node):
    __slots__ = [
        '_attr_api_version',
        '_attr_version',
        '_attr_qubit_variable_declaration',
        '_attr_block',
    ]

    def __init__(
        self,
        api_version=None,
        version=None,
        qubit_variable_declaration=None,
        block=None,
    ):
        super().__init__()
        self.api_version = api_version
        self.version = version
        self.qubit_variable_declaration = qubit_variable_declaration
        self.block = block

    @property
    def api_version(self):
        """API version. This may be greater than or equal to the file version.
        This controls which fields of the tree are used, where such usage
        depends on the version."""
        return self._attr_api_version

    @api_version.setter
    def api_version(self, val):
        if val is None:
            del self.api_version
            return
        if not isinstance(val, cqasm.v3x.primitives.Version):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('api_version must be of type cqasm.v3x.primitives.Version')
            val = cqasm.v3x.primitives.Version(val)
        self._attr_api_version = val

    @api_version.deleter
    def api_version(self):
        self._attr_api_version = cqasm.v3x.primitives.Version()

    @property
    def version(self):
        """File version."""
        return self._attr_version

    @version.setter
    def version(self, val):
        if val is None:
            del self.version
            return
        if not isinstance(val, Version):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('version must be of type Version')
            val = Version(val)
        self._attr_version = val

    @version.deleter
    def version(self):
        self._attr_version = None

    @property
    def qubit_variable_declaration(self):
        """Qubit variable."""
        return self._attr_qubit_variable_declaration

    @qubit_variable_declaration.setter
    def qubit_variable_declaration(self, val):
        if val is None:
            del self.qubit_variable_declaration
            return
        if not isinstance(val, Variable):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('qubit_variable_declaration must be of type Variable')
            val = Variable(val)
        self._attr_qubit_variable_declaration = val

    @qubit_variable_declaration.deleter
    def qubit_variable_declaration(self):
        self._attr_qubit_variable_declaration = None

    @property
    def block(self):
        """Global scope block."""
        return self._attr_block

    @block.setter
    def block(self, val):
        if val is None:
            del self.block
            return
        if not isinstance(val, Block):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('block must be of type Block')
            val = Block(val)
        self._attr_block = val

    @block.deleter
    def block(self):
        self._attr_block = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Program):
            return False
        if self.api_version != other.api_version:
            return False
        if self.version != other.version:
            return False
        if self.qubit_variable_declaration != other.qubit_variable_declaration:
            return False
        if self.block != other.block:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Program(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('api_version: ')
        s.append(str(self.api_version) + '\n')
        s.append('  '*indent)
        s.append('version: ')
        if self.version is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.version.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('qubit_variable_declaration: ')
        if self.qubit_variable_declaration is None:
            s.append('-\n')
        else:
            s.append('<\n')
            s.append(self.qubit_variable_declaration.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('block: ')
        if self.block is None:
            s.append('-\n')
        else:
            s.append('<\n')
            s.append(self.block.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        if self._attr_version is not None:
            self._attr_version.find_reachable(id_map)
        if self._attr_qubit_variable_declaration is not None:
            self._attr_qubit_variable_declaration.find_reachable(id_map)
        if self._attr_block is not None:
            self._attr_block.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_version is None:
            raise NotWellFormed('version is required but not set')
        if self._attr_version is not None:
            self._attr_version.check_complete(id_map)
        if self._attr_qubit_variable_declaration is not None:
            self._attr_qubit_variable_declaration.check_complete(id_map)
        if self._attr_block is not None:
            self._attr_block.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return Program(
            api_version=self._attr_api_version,
            version=self._attr_version,
            qubit_variable_declaration=self._attr_qubit_variable_declaration,
            block=self._attr_block
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Program(
            api_version=_cloned(self._attr_api_version),
            version=_cloned(self._attr_version),
            qubit_variable_declaration=_cloned(self._attr_qubit_variable_declaration),
            block=_cloned(self._attr_block)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'Program':
            raise ValueError('found node serialization for ' + typ + ', but expected Program')

        # Deserialize the api_version field.
        field = cbor.get('api_version', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field api_version')
        if hasattr(cqasm.v3x.primitives.Version, 'deserialize_cbor'):
            f_api_version = cqasm.v3x.primitives.Version.deserialize_cbor(field)
        else:
            f_api_version = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Version, field)

        # Deserialize the version field.
        field = cbor.get('version', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field version')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field version')
        if field.get('@t', None) is None:
            f_version = None
        else:
            f_version = Version._deserialize(field, seq_to_ob, links)

        # Deserialize the qubit_variable_declaration field.
        field = cbor.get('qubit_variable_declaration', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field qubit_variable_declaration')
        if field.get('@T') != '?':
            raise ValueError('unexpected edge type for field qubit_variable_declaration')
        if field.get('@t', None) is None:
            f_qubit_variable_declaration = None
        else:
            f_qubit_variable_declaration = Variable._deserialize(field, seq_to_ob, links)

        # Deserialize the block field.
        field = cbor.get('block', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field block')
        if field.get('@T') != '?':
            raise ValueError('unexpected edge type for field block')
        if field.get('@t', None) is None:
            f_block = None
        else:
            f_block = Block._deserialize(field, seq_to_ob, links)

        # Construct the Program node.
        node = Program(f_api_version, f_version, f_qubit_variable_declaration, f_block)

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = cqasm.v3x.primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Program'}

        # Serialize the api_version field.
        if hasattr(self._attr_api_version, 'serialize_cbor'):
            cbor['api_version'] = self._attr_api_version.serialize_cbor()
        else:
            cbor['api_version'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Version, self._attr_api_version)

        # Serialize the version field.
        field = {'@T': '1'}
        if self._attr_version is None:
            field['@t'] = None
        else:
            field.update(self._attr_version._serialize(id_map))
        cbor['version'] = field

        # Serialize the qubit_variable_declaration field.
        field = {'@T': '?'}
        if self._attr_qubit_variable_declaration is None:
            field['@t'] = None
        else:
            field.update(self._attr_qubit_variable_declaration._serialize(id_map))
        cbor['qubit_variable_declaration'] = field

        # Serialize the block field.
        field = {'@T': '?'}
        if self._attr_block is None:
            field['@t'] = None
        else:
            field.update(self._attr_block._serialize(id_map))
        cbor['block'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiProgram(_Multiple):
    """Wrapper for an edge with multiple Program objects."""

    _T = Program


_typemap['Program'] = Program

class Variable(Annotated):
    __slots__ = [
        '_attr_name',
        '_attr_typ',
    ]

    def __init__(
        self,
        name=None,
        typ=None,
        annotations=None,
    ):
        super().__init__(annotations=annotations)
        self.name = name
        self.typ = typ

    @property
    def name(self):
        return self._attr_name

    @name.setter
    def name(self, val):
        if val is None:
            del self.name
            return
        if not isinstance(val, cqasm.v3x.primitives.Str):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('name must be of type cqasm.v3x.primitives.Str')
            val = cqasm.v3x.primitives.Str(val)
        self._attr_name = val

    @name.deleter
    def name(self):
        self._attr_name = cqasm.v3x.primitives.Str()

    @property
    def typ(self):
        return self._attr_typ

    @typ.setter
    def typ(self, val):
        if val is None:
            del self.typ
            return
        if not isinstance(val, cqasm.v3x.types.TypeBase):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('typ must be of type cqasm.v3x.types.TypeBase')
            val = cqasm.v3x.types.TypeBase(val)
        self._attr_typ = val

    @typ.deleter
    def typ(self):
        self._attr_typ = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Variable):
            return False
        if self.name != other.name:
            return False
        if self.typ != other.typ:
            return False
        if self.annotations != other.annotations:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Variable(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('name: ')
        s.append(str(self.name) + '\n')
        s.append('  '*indent)
        s.append('typ: ')
        if self.typ is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.typ.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('annotations: ')
        if not self.annotations:
            s.append('-\n')
        else:
            s.append('[\n')
            for child in self.annotations:
                s.append(child.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + ']\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        if self._attr_typ is not None:
            self._attr_typ.find_reachable(id_map)
        for el in self._attr_annotations:
            el.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_typ is None:
            raise NotWellFormed('typ is required but not set')
        if self._attr_typ is not None:
            self._attr_typ.check_complete(id_map)
        for child in self._attr_annotations:
            child.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return Variable(
            name=self._attr_name,
            typ=self._attr_typ,
            annotations=self._attr_annotations.copy()
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Variable(
            name=_cloned(self._attr_name),
            typ=_cloned(self._attr_typ),
            annotations=_cloned(self._attr_annotations)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'Variable':
            raise ValueError('found node serialization for ' + typ + ', but expected Variable')

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if hasattr(cqasm.v3x.primitives.Str, 'deserialize_cbor'):
            f_name = cqasm.v3x.primitives.Str.deserialize_cbor(field)
        else:
            f_name = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Str, field)

        # Deserialize the typ field.
        field = cbor.get('typ', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field typ')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field typ')
        if field.get('@t', None) is None:
            f_typ = None
        else:
            f_typ = cqasm.v3x.types.TypeBase._deserialize(field, seq_to_ob, links)

        # Deserialize the annotations field.
        field = cbor.get('annotations', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field annotations')
        if field.get('@T') != '*':
            raise ValueError('unexpected edge type for field annotations')
        data = field.get('@d', None)
        if not isinstance(data, list):
            raise ValueError('missing serialization of Any/Many contents')
        f_annotations = MultiAnnotationData()
        for element in data:
            if element.get('@T') != '1':
                raise ValueError('unexpected edge type for Any/Many element')
            f_annotations.append(AnnotationData._deserialize(element, seq_to_ob, links))

        # Construct the Variable node.
        node = Variable(f_name, f_typ, f_annotations)

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = cqasm.v3x.primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Variable'}

        # Serialize the name field.
        if hasattr(self._attr_name, 'serialize_cbor'):
            cbor['name'] = self._attr_name.serialize_cbor()
        else:
            cbor['name'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Str, self._attr_name)

        # Serialize the typ field.
        field = {'@T': '1'}
        if self._attr_typ is None:
            field['@t'] = None
        else:
            field.update(self._attr_typ._serialize(id_map))
        cbor['typ'] = field

        # Serialize the annotations field.
        field = {'@T': '*'}
        lst = []
        for el in self._attr_annotations:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['annotations'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiVariable(_Multiple):
    """Wrapper for an edge with multiple Variable objects."""

    _T = Variable


_typemap['Variable'] = Variable

class Version(Node):
    __slots__ = [
        '_attr_items',
    ]

    def __init__(
        self,
        items=None,
    ):
        super().__init__()
        self.items = items

    @property
    def items(self):
        return self._attr_items

    @items.setter
    def items(self, val):
        if val is None:
            del self.items
            return
        if not isinstance(val, cqasm.v3x.primitives.Version):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('items must be of type cqasm.v3x.primitives.Version')
            val = cqasm.v3x.primitives.Version(val)
        self._attr_items = val

    @items.deleter
    def items(self):
        self._attr_items = cqasm.v3x.primitives.Version()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Version):
            return False
        if self.items != other.items:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Version(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('items: ')
        s.append(str(self.items) + '\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()

    def copy(self):
        """Returns a shallow copy of this node."""
        return Version(
            items=self._attr_items
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Version(
            items=_cloned(self._attr_items)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'Version':
            raise ValueError('found node serialization for ' + typ + ', but expected Version')

        # Deserialize the items field.
        field = cbor.get('items', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field items')
        if hasattr(cqasm.v3x.primitives.Version, 'deserialize_cbor'):
            f_items = cqasm.v3x.primitives.Version.deserialize_cbor(field)
        else:
            f_items = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Version, field)

        # Construct the Version node.
        node = Version(f_items)

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = cqasm.v3x.primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Version'}

        # Serialize the items field.
        if hasattr(self._attr_items, 'serialize_cbor'):
            cbor['items'] = self._attr_items.serialize_cbor()
        else:
            cbor['items'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Version, self._attr_items)

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiVersion(_Multiple):
    """Wrapper for an edge with multiple Version objects."""

    _T = Version


_typemap['Version'] = Version

