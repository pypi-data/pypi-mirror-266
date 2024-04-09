import functools
import struct
import cqasm.v3x.primitives


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


class Expression(Node):
    __slots__ = []

    def __init__(self):
        super().__init__()

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
        if typ == 'BooleanLiteral':
            return BooleanLiteral._deserialize(cbor, seq_to_ob, links)
        if typ == 'IntegerLiteral':
            return IntegerLiteral._deserialize(cbor, seq_to_ob, links)
        if typ == 'FloatLiteral':
            return FloatLiteral._deserialize(cbor, seq_to_ob, links)
        if typ == 'Index':
            return Index._deserialize(cbor, seq_to_ob, links)
        if typ == 'Identifier':
            return Identifier._deserialize(cbor, seq_to_ob, links)
        if typ == 'FunctionCall':
            return FunctionCall._deserialize(cbor, seq_to_ob, links)
        if typ == 'UnaryMinusExpression':
            return UnaryMinusExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'BitwiseNotExpression':
            return BitwiseNotExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'LogicalNotExpression':
            return LogicalNotExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'PowerExpression':
            return PowerExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ProductExpression':
            return ProductExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'DivisionExpression':
            return DivisionExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ModuloExpression':
            return ModuloExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'AdditionExpression':
            return AdditionExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'SubtractionExpression':
            return SubtractionExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ShiftLeftExpression':
            return ShiftLeftExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ShiftRightExpression':
            return ShiftRightExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpGtExpression':
            return CmpGtExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpLtExpression':
            return CmpLtExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpGeExpression':
            return CmpGeExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpLeExpression':
            return CmpLeExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpEqExpression':
            return CmpEqExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpNeExpression':
            return CmpNeExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'BitwiseAndExpression':
            return BitwiseAndExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'BitwiseXorExpression':
            return BitwiseXorExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'BitwiseOrExpression':
            return BitwiseOrExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'LogicalAndExpression':
            return LogicalAndExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'LogicalXorExpression':
            return LogicalXorExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'LogicalOrExpression':
            return LogicalOrExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'TernaryConditionalExpression':
            return TernaryConditionalExpression._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Expression'}

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiExpression(_Multiple):
    """Wrapper for an edge with multiple Expression objects."""

    _T = Expression


_typemap['Expression'] = Expression

class BinaryExpression(Expression):
    __slots__ = [
        '_attr_lhs',
        '_attr_rhs',
    ]

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    @property
    def lhs(self):
        return self._attr_lhs

    @lhs.setter
    def lhs(self, val):
        if val is None:
            del self.lhs
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('lhs must be of type Expression')
            val = Expression(val)
        self._attr_lhs = val

    @lhs.deleter
    def lhs(self):
        self._attr_lhs = None

    @property
    def rhs(self):
        return self._attr_rhs

    @rhs.setter
    def rhs(self, val):
        if val is None:
            del self.rhs
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('rhs must be of type Expression')
            val = Expression(val)
        self._attr_rhs = val

    @rhs.deleter
    def rhs(self):
        self._attr_rhs = None

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
        if typ == 'PowerExpression':
            return PowerExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ProductExpression':
            return ProductExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'DivisionExpression':
            return DivisionExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ModuloExpression':
            return ModuloExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'AdditionExpression':
            return AdditionExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'SubtractionExpression':
            return SubtractionExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ShiftLeftExpression':
            return ShiftLeftExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ShiftRightExpression':
            return ShiftRightExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpGtExpression':
            return CmpGtExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpLtExpression':
            return CmpLtExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpGeExpression':
            return CmpGeExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpLeExpression':
            return CmpLeExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpEqExpression':
            return CmpEqExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpNeExpression':
            return CmpNeExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'BitwiseAndExpression':
            return BitwiseAndExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'BitwiseXorExpression':
            return BitwiseXorExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'BitwiseOrExpression':
            return BitwiseOrExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'LogicalAndExpression':
            return LogicalAndExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'LogicalXorExpression':
            return LogicalXorExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'LogicalOrExpression':
            return LogicalOrExpression._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'BinaryExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiBinaryExpression(_Multiple):
    """Wrapper for an edge with multiple BinaryExpression objects."""

    _T = BinaryExpression


_typemap['BinaryExpression'] = BinaryExpression

class ArithmeticExpression(BinaryExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

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
        if typ == 'PowerExpression':
            return PowerExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ProductExpression':
            return ProductExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'DivisionExpression':
            return DivisionExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ModuloExpression':
            return ModuloExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'AdditionExpression':
            return AdditionExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'SubtractionExpression':
            return SubtractionExpression._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'ArithmeticExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiArithmeticExpression(_Multiple):
    """Wrapper for an edge with multiple ArithmeticExpression objects."""

    _T = ArithmeticExpression


_typemap['ArithmeticExpression'] = ArithmeticExpression

class AdditionExpression(ArithmeticExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, AdditionExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('AdditionExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return AdditionExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return AdditionExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'AdditionExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected AdditionExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the AdditionExpression node.
        node = AdditionExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'AdditionExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiAdditionExpression(_Multiple):
    """Wrapper for an edge with multiple AdditionExpression objects."""

    _T = AdditionExpression


_typemap['AdditionExpression'] = AdditionExpression

class Annotated(Node):
    """Represents a node that carries annotation data"""

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
        """Zero or more annotations attached to this object."""
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
        if typ == 'Gate':
            return Gate._deserialize(cbor, seq_to_ob, links)
        if typ == 'MeasureInstruction':
            return MeasureInstruction._deserialize(cbor, seq_to_ob, links)
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
        if not isinstance(val, Identifier):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('interface must be of type Identifier')
            val = Identifier(val)
        self._attr_interface = val

    @interface.deleter
    def interface(self):
        self._attr_interface = None

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
        if not isinstance(val, Identifier):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('operation must be of type Identifier')
            val = Identifier(val)
        self._attr_operation = val

    @operation.deleter
    def operation(self):
        self._attr_operation = None

    @property
    def operands(self):
        """Any operands attached to the annotation."""
        return self._attr_operands

    @operands.setter
    def operands(self, val):
        if val is None:
            del self.operands
            return
        if not isinstance(val, ExpressionList):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('operands must be of type ExpressionList')
            val = ExpressionList(val)
        self._attr_operands = val

    @operands.deleter
    def operands(self):
        self._attr_operands = None

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
        if self.interface is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.interface.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('operation: ')
        if self.operation is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.operation.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('operands: ')
        if self.operands is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.operands.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_interface is not None:
            self._attr_interface.find_reachable(id_map)
        if self._attr_operation is not None:
            self._attr_operation.find_reachable(id_map)
        if self._attr_operands is not None:
            self._attr_operands.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_interface is None:
            raise NotWellFormed('interface is required but not set')
        if self._attr_interface is not None:
            self._attr_interface.check_complete(id_map)
        if self._attr_operation is None:
            raise NotWellFormed('operation is required but not set')
        if self._attr_operation is not None:
            self._attr_operation.check_complete(id_map)
        if self._attr_operands is None:
            raise NotWellFormed('operands is required but not set')
        if self._attr_operands is not None:
            self._attr_operands.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return AnnotationData(
            interface=self._attr_interface,
            operation=self._attr_operation,
            operands=self._attr_operands
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
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field interface')
        if field.get('@t', None) is None:
            f_interface = None
        else:
            f_interface = Identifier._deserialize(field, seq_to_ob, links)

        # Deserialize the operation field.
        field = cbor.get('operation', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field operation')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field operation')
        if field.get('@t', None) is None:
            f_operation = None
        else:
            f_operation = Identifier._deserialize(field, seq_to_ob, links)

        # Deserialize the operands field.
        field = cbor.get('operands', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field operands')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field operands')
        if field.get('@t', None) is None:
            f_operands = None
        else:
            f_operands = ExpressionList._deserialize(field, seq_to_ob, links)

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
        field = {'@T': '1'}
        if self._attr_interface is None:
            field['@t'] = None
        else:
            field.update(self._attr_interface._serialize(id_map))
        cbor['interface'] = field

        # Serialize the operation field.
        field = {'@T': '1'}
        if self._attr_operation is None:
            field['@t'] = None
        else:
            field.update(self._attr_operation._serialize(id_map))
        cbor['operation'] = field

        # Serialize the operands field.
        field = {'@T': '1'}
        if self._attr_operands is None:
            field['@t'] = None
        else:
            field.update(self._attr_operands._serialize(id_map))
        cbor['operands'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiAnnotationData(_Multiple):
    """Wrapper for an edge with multiple AnnotationData objects."""

    _T = AnnotationData


_typemap['AnnotationData'] = AnnotationData

class BitwiseExpression(BinaryExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

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
        if typ == 'BitwiseAndExpression':
            return BitwiseAndExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'BitwiseXorExpression':
            return BitwiseXorExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'BitwiseOrExpression':
            return BitwiseOrExpression._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'BitwiseExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiBitwiseExpression(_Multiple):
    """Wrapper for an edge with multiple BitwiseExpression objects."""

    _T = BitwiseExpression


_typemap['BitwiseExpression'] = BitwiseExpression

class BitwiseAndExpression(BitwiseExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, BitwiseAndExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('BitwiseAndExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return BitwiseAndExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return BitwiseAndExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'BitwiseAndExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected BitwiseAndExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the BitwiseAndExpression node.
        node = BitwiseAndExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'BitwiseAndExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiBitwiseAndExpression(_Multiple):
    """Wrapper for an edge with multiple BitwiseAndExpression objects."""

    _T = BitwiseAndExpression


_typemap['BitwiseAndExpression'] = BitwiseAndExpression

class UnaryExpression(Expression):
    __slots__ = [
        '_attr_expr',
    ]

    def __init__(
        self,
        expr=None,
    ):
        super().__init__()
        self.expr = expr

    @property
    def expr(self):
        return self._attr_expr

    @expr.setter
    def expr(self, val):
        if val is None:
            del self.expr
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('expr must be of type Expression')
            val = Expression(val)
        self._attr_expr = val

    @expr.deleter
    def expr(self):
        self._attr_expr = None

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
        if typ == 'UnaryMinusExpression':
            return UnaryMinusExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'BitwiseNotExpression':
            return BitwiseNotExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'LogicalNotExpression':
            return LogicalNotExpression._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'UnaryExpression'}

        # Serialize the expr field.
        field = {'@T': '1'}
        if self._attr_expr is None:
            field['@t'] = None
        else:
            field.update(self._attr_expr._serialize(id_map))
        cbor['expr'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiUnaryExpression(_Multiple):
    """Wrapper for an edge with multiple UnaryExpression objects."""

    _T = UnaryExpression


_typemap['UnaryExpression'] = UnaryExpression

class BitwiseNotExpression(UnaryExpression):
    """One's complement."""

    __slots__ = []

    def __init__(
        self,
        expr=None,
    ):
        super().__init__(expr=expr)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, BitwiseNotExpression):
            return False
        if self.expr != other.expr:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('BitwiseNotExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('expr: ')
        if self.expr is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.expr.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_expr is not None:
            self._attr_expr.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_expr is None:
            raise NotWellFormed('expr is required but not set')
        if self._attr_expr is not None:
            self._attr_expr.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return BitwiseNotExpression(
            expr=self._attr_expr
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return BitwiseNotExpression(
            expr=_cloned(self._attr_expr)
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
        if typ != 'BitwiseNotExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected BitwiseNotExpression')

        # Deserialize the expr field.
        field = cbor.get('expr', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field expr')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field expr')
        if field.get('@t', None) is None:
            f_expr = None
        else:
            f_expr = Expression._deserialize(field, seq_to_ob, links)

        # Construct the BitwiseNotExpression node.
        node = BitwiseNotExpression(f_expr)

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
        cbor = {'@i': id_map[id(self)], '@t': 'BitwiseNotExpression'}

        # Serialize the expr field.
        field = {'@T': '1'}
        if self._attr_expr is None:
            field['@t'] = None
        else:
            field.update(self._attr_expr._serialize(id_map))
        cbor['expr'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiBitwiseNotExpression(_Multiple):
    """Wrapper for an edge with multiple BitwiseNotExpression objects."""

    _T = BitwiseNotExpression


_typemap['BitwiseNotExpression'] = BitwiseNotExpression

class BitwiseOrExpression(BitwiseExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, BitwiseOrExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('BitwiseOrExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return BitwiseOrExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return BitwiseOrExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'BitwiseOrExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected BitwiseOrExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the BitwiseOrExpression node.
        node = BitwiseOrExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'BitwiseOrExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiBitwiseOrExpression(_Multiple):
    """Wrapper for an edge with multiple BitwiseOrExpression objects."""

    _T = BitwiseOrExpression


_typemap['BitwiseOrExpression'] = BitwiseOrExpression

class BitwiseXorExpression(BitwiseExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, BitwiseXorExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('BitwiseXorExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return BitwiseXorExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return BitwiseXorExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'BitwiseXorExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected BitwiseXorExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the BitwiseXorExpression node.
        node = BitwiseXorExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'BitwiseXorExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiBitwiseXorExpression(_Multiple):
    """Wrapper for an edge with multiple BitwiseXorExpression objects."""

    _T = BitwiseXorExpression


_typemap['BitwiseXorExpression'] = BitwiseXorExpression

class Block(Node):
    __slots__ = []

    def __init__(self):
        super().__init__()

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
        if typ == 'GlobalBlock':
            return GlobalBlock._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Block'}

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
        if typ == 'Variable':
            return Variable._deserialize(cbor, seq_to_ob, links)
        if typ == 'Gate':
            return Gate._deserialize(cbor, seq_to_ob, links)
        if typ == 'MeasureInstruction':
            return MeasureInstruction._deserialize(cbor, seq_to_ob, links)
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

class BlockStatement(Statement):
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
        if typ == 'Variable':
            return Variable._deserialize(cbor, seq_to_ob, links)
        if typ == 'Gate':
            return Gate._deserialize(cbor, seq_to_ob, links)
        if typ == 'MeasureInstruction':
            return MeasureInstruction._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'BlockStatement'}

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


class MultiBlockStatement(_Multiple):
    """Wrapper for an edge with multiple BlockStatement objects."""

    _T = BlockStatement


_typemap['BlockStatement'] = BlockStatement

class BooleanLiteral(Expression):
    __slots__ = [
        '_attr_value',
    ]

    def __init__(
        self,
        value=None,
    ):
        super().__init__()
        self.value = value

    @property
    def value(self):
        return self._attr_value

    @value.setter
    def value(self, val):
        if val is None:
            del self.value
            return
        if not isinstance(val, cqasm.v3x.primitives.Bool):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('value must be of type cqasm.v3x.primitives.Bool')
            val = cqasm.v3x.primitives.Bool(val)
        self._attr_value = val

    @value.deleter
    def value(self):
        self._attr_value = cqasm.v3x.primitives.Bool()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, BooleanLiteral):
            return False
        if self.value != other.value:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('BooleanLiteral(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('value: ')
        s.append(str(self.value) + '\n')
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
        return BooleanLiteral(
            value=self._attr_value
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return BooleanLiteral(
            value=_cloned(self._attr_value)
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
        if typ != 'BooleanLiteral':
            raise ValueError('found node serialization for ' + typ + ', but expected BooleanLiteral')

        # Deserialize the value field.
        field = cbor.get('value', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field value')
        if hasattr(cqasm.v3x.primitives.Bool, 'deserialize_cbor'):
            f_value = cqasm.v3x.primitives.Bool.deserialize_cbor(field)
        else:
            f_value = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Bool, field)

        # Construct the BooleanLiteral node.
        node = BooleanLiteral(f_value)

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
        cbor = {'@i': id_map[id(self)], '@t': 'BooleanLiteral'}

        # Serialize the value field.
        if hasattr(self._attr_value, 'serialize_cbor'):
            cbor['value'] = self._attr_value.serialize_cbor()
        else:
            cbor['value'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Bool, self._attr_value)

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiBooleanLiteral(_Multiple):
    """Wrapper for an edge with multiple BooleanLiteral objects."""

    _T = BooleanLiteral


_typemap['BooleanLiteral'] = BooleanLiteral

class EqualityExpression(BinaryExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

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
        if typ == 'CmpEqExpression':
            return CmpEqExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpNeExpression':
            return CmpNeExpression._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'EqualityExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiEqualityExpression(_Multiple):
    """Wrapper for an edge with multiple EqualityExpression objects."""

    _T = EqualityExpression


_typemap['EqualityExpression'] = EqualityExpression

class CmpEqExpression(EqualityExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, CmpEqExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('CmpEqExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return CmpEqExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return CmpEqExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'CmpEqExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected CmpEqExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the CmpEqExpression node.
        node = CmpEqExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'CmpEqExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiCmpEqExpression(_Multiple):
    """Wrapper for an edge with multiple CmpEqExpression objects."""

    _T = CmpEqExpression


_typemap['CmpEqExpression'] = CmpEqExpression

class ComparisonExpression(BinaryExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

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
        if typ == 'CmpGtExpression':
            return CmpGtExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpLtExpression':
            return CmpLtExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpGeExpression':
            return CmpGeExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'CmpLeExpression':
            return CmpLeExpression._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'ComparisonExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiComparisonExpression(_Multiple):
    """Wrapper for an edge with multiple ComparisonExpression objects."""

    _T = ComparisonExpression


_typemap['ComparisonExpression'] = ComparisonExpression

class CmpGeExpression(ComparisonExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, CmpGeExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('CmpGeExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return CmpGeExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return CmpGeExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'CmpGeExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected CmpGeExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the CmpGeExpression node.
        node = CmpGeExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'CmpGeExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiCmpGeExpression(_Multiple):
    """Wrapper for an edge with multiple CmpGeExpression objects."""

    _T = CmpGeExpression


_typemap['CmpGeExpression'] = CmpGeExpression

class CmpGtExpression(ComparisonExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, CmpGtExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('CmpGtExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return CmpGtExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return CmpGtExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'CmpGtExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected CmpGtExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the CmpGtExpression node.
        node = CmpGtExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'CmpGtExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiCmpGtExpression(_Multiple):
    """Wrapper for an edge with multiple CmpGtExpression objects."""

    _T = CmpGtExpression


_typemap['CmpGtExpression'] = CmpGtExpression

class CmpLeExpression(ComparisonExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, CmpLeExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('CmpLeExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return CmpLeExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return CmpLeExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'CmpLeExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected CmpLeExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the CmpLeExpression node.
        node = CmpLeExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'CmpLeExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiCmpLeExpression(_Multiple):
    """Wrapper for an edge with multiple CmpLeExpression objects."""

    _T = CmpLeExpression


_typemap['CmpLeExpression'] = CmpLeExpression

class CmpLtExpression(ComparisonExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, CmpLtExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('CmpLtExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return CmpLtExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return CmpLtExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'CmpLtExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected CmpLtExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the CmpLtExpression node.
        node = CmpLtExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'CmpLtExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiCmpLtExpression(_Multiple):
    """Wrapper for an edge with multiple CmpLtExpression objects."""

    _T = CmpLtExpression


_typemap['CmpLtExpression'] = CmpLtExpression

class CmpNeExpression(EqualityExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, CmpNeExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('CmpNeExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return CmpNeExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return CmpNeExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'CmpNeExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected CmpNeExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the CmpNeExpression node.
        node = CmpNeExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'CmpNeExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiCmpNeExpression(_Multiple):
    """Wrapper for an edge with multiple CmpNeExpression objects."""

    _T = CmpNeExpression


_typemap['CmpNeExpression'] = CmpNeExpression

class DivisionExpression(ArithmeticExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, DivisionExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('DivisionExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return DivisionExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return DivisionExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'DivisionExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected DivisionExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the DivisionExpression node.
        node = DivisionExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'DivisionExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiDivisionExpression(_Multiple):
    """Wrapper for an edge with multiple DivisionExpression objects."""

    _T = DivisionExpression


_typemap['DivisionExpression'] = DivisionExpression

class ExpressionList(Node):
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
        if not isinstance(val, MultiExpression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('items must be of type MultiExpression')
            val = MultiExpression(val)
        self._attr_items = val

    @items.deleter
    def items(self):
        self._attr_items = MultiExpression()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, ExpressionList):
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
        s.append('ExpressionList(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('items: ')
        if not self.items:
            s.append('-\n')
        else:
            s.append('[\n')
            for child in self.items:
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
        for el in self._attr_items:
            el.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        for child in self._attr_items:
            child.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return ExpressionList(
            items=self._attr_items.copy()
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return ExpressionList(
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
        if typ != 'ExpressionList':
            raise ValueError('found node serialization for ' + typ + ', but expected ExpressionList')

        # Deserialize the items field.
        field = cbor.get('items', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field items')
        if field.get('@T') != '*':
            raise ValueError('unexpected edge type for field items')
        data = field.get('@d', None)
        if not isinstance(data, list):
            raise ValueError('missing serialization of Any/Many contents')
        f_items = MultiExpression()
        for element in data:
            if element.get('@T') != '1':
                raise ValueError('unexpected edge type for Any/Many element')
            f_items.append(Expression._deserialize(element, seq_to_ob, links))

        # Construct the ExpressionList node.
        node = ExpressionList(f_items)

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
        cbor = {'@i': id_map[id(self)], '@t': 'ExpressionList'}

        # Serialize the items field.
        field = {'@T': '*'}
        lst = []
        for el in self._attr_items:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['items'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiExpressionList(_Multiple):
    """Wrapper for an edge with multiple ExpressionList objects."""

    _T = ExpressionList


_typemap['ExpressionList'] = ExpressionList

class FloatLiteral(Expression):
    __slots__ = [
        '_attr_value',
    ]

    def __init__(
        self,
        value=None,
    ):
        super().__init__()
        self.value = value

    @property
    def value(self):
        return self._attr_value

    @value.setter
    def value(self, val):
        if val is None:
            del self.value
            return
        if not isinstance(val, cqasm.v3x.primitives.Float):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('value must be of type cqasm.v3x.primitives.Float')
            val = cqasm.v3x.primitives.Float(val)
        self._attr_value = val

    @value.deleter
    def value(self):
        self._attr_value = cqasm.v3x.primitives.Float()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, FloatLiteral):
            return False
        if self.value != other.value:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('FloatLiteral(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('value: ')
        s.append(str(self.value) + '\n')
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
        return FloatLiteral(
            value=self._attr_value
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return FloatLiteral(
            value=_cloned(self._attr_value)
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
        if typ != 'FloatLiteral':
            raise ValueError('found node serialization for ' + typ + ', but expected FloatLiteral')

        # Deserialize the value field.
        field = cbor.get('value', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field value')
        if hasattr(cqasm.v3x.primitives.Float, 'deserialize_cbor'):
            f_value = cqasm.v3x.primitives.Float.deserialize_cbor(field)
        else:
            f_value = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Float, field)

        # Construct the FloatLiteral node.
        node = FloatLiteral(f_value)

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
        cbor = {'@i': id_map[id(self)], '@t': 'FloatLiteral'}

        # Serialize the value field.
        if hasattr(self._attr_value, 'serialize_cbor'):
            cbor['value'] = self._attr_value.serialize_cbor()
        else:
            cbor['value'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Float, self._attr_value)

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiFloatLiteral(_Multiple):
    """Wrapper for an edge with multiple FloatLiteral objects."""

    _T = FloatLiteral


_typemap['FloatLiteral'] = FloatLiteral

class FunctionCall(Expression):
    __slots__ = [
        '_attr_name',
        '_attr_arguments',
    ]

    def __init__(
        self,
        name=None,
        arguments=None,
    ):
        super().__init__()
        self.name = name
        self.arguments = arguments

    @property
    def name(self):
        return self._attr_name

    @name.setter
    def name(self, val):
        if val is None:
            del self.name
            return
        if not isinstance(val, Identifier):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('name must be of type Identifier')
            val = Identifier(val)
        self._attr_name = val

    @name.deleter
    def name(self):
        self._attr_name = None

    @property
    def arguments(self):
        return self._attr_arguments

    @arguments.setter
    def arguments(self, val):
        if val is None:
            del self.arguments
            return
        if not isinstance(val, ExpressionList):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('arguments must be of type ExpressionList')
            val = ExpressionList(val)
        self._attr_arguments = val

    @arguments.deleter
    def arguments(self):
        self._attr_arguments = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, FunctionCall):
            return False
        if self.name != other.name:
            return False
        if self.arguments != other.arguments:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('FunctionCall(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('name: ')
        if self.name is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.name.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('arguments: ')
        if self.arguments is None:
            s.append('-\n')
        else:
            s.append('<\n')
            s.append(self.arguments.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_name is not None:
            self._attr_name.find_reachable(id_map)
        if self._attr_arguments is not None:
            self._attr_arguments.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_name is None:
            raise NotWellFormed('name is required but not set')
        if self._attr_name is not None:
            self._attr_name.check_complete(id_map)
        if self._attr_arguments is not None:
            self._attr_arguments.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return FunctionCall(
            name=self._attr_name,
            arguments=self._attr_arguments
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return FunctionCall(
            name=_cloned(self._attr_name),
            arguments=_cloned(self._attr_arguments)
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
        if typ != 'FunctionCall':
            raise ValueError('found node serialization for ' + typ + ', but expected FunctionCall')

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field name')
        if field.get('@t', None) is None:
            f_name = None
        else:
            f_name = Identifier._deserialize(field, seq_to_ob, links)

        # Deserialize the arguments field.
        field = cbor.get('arguments', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field arguments')
        if field.get('@T') != '?':
            raise ValueError('unexpected edge type for field arguments')
        if field.get('@t', None) is None:
            f_arguments = None
        else:
            f_arguments = ExpressionList._deserialize(field, seq_to_ob, links)

        # Construct the FunctionCall node.
        node = FunctionCall(f_name, f_arguments)

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
        cbor = {'@i': id_map[id(self)], '@t': 'FunctionCall'}

        # Serialize the name field.
        field = {'@T': '1'}
        if self._attr_name is None:
            field['@t'] = None
        else:
            field.update(self._attr_name._serialize(id_map))
        cbor['name'] = field

        # Serialize the arguments field.
        field = {'@T': '?'}
        if self._attr_arguments is None:
            field['@t'] = None
        else:
            field.update(self._attr_arguments._serialize(id_map))
        cbor['arguments'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiFunctionCall(_Multiple):
    """Wrapper for an edge with multiple FunctionCall objects."""

    _T = FunctionCall


_typemap['FunctionCall'] = FunctionCall

class Instruction(BlockStatement):
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
        if typ == 'Gate':
            return Gate._deserialize(cbor, seq_to_ob, links)
        if typ == 'MeasureInstruction':
            return MeasureInstruction._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Instruction'}

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

class Gate(Instruction):
    __slots__ = [
        '_attr_name',
        '_attr_operands',
    ]

    def __init__(
        self,
        name=None,
        operands=None,
        annotations=None,
    ):
        super().__init__(annotations=annotations)
        self.name = name
        self.operands = operands

    @property
    def name(self):
        return self._attr_name

    @name.setter
    def name(self, val):
        if val is None:
            del self.name
            return
        if not isinstance(val, Identifier):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('name must be of type Identifier')
            val = Identifier(val)
        self._attr_name = val

    @name.deleter
    def name(self):
        self._attr_name = None

    @property
    def operands(self):
        return self._attr_operands

    @operands.setter
    def operands(self, val):
        if val is None:
            del self.operands
            return
        if not isinstance(val, ExpressionList):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('operands must be of type ExpressionList')
            val = ExpressionList(val)
        self._attr_operands = val

    @operands.deleter
    def operands(self):
        self._attr_operands = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Gate):
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
        s.append('Gate(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('name: ')
        if self.name is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.name.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('operands: ')
        if self.operands is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.operands.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_name is not None:
            self._attr_name.find_reachable(id_map)
        if self._attr_operands is not None:
            self._attr_operands.find_reachable(id_map)
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
        if self._attr_name is None:
            raise NotWellFormed('name is required but not set')
        if self._attr_name is not None:
            self._attr_name.check_complete(id_map)
        if self._attr_operands is None:
            raise NotWellFormed('operands is required but not set')
        if self._attr_operands is not None:
            self._attr_operands.check_complete(id_map)
        for child in self._attr_annotations:
            child.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return Gate(
            name=self._attr_name,
            operands=self._attr_operands,
            annotations=self._attr_annotations.copy()
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Gate(
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
        if typ != 'Gate':
            raise ValueError('found node serialization for ' + typ + ', but expected Gate')

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field name')
        if field.get('@t', None) is None:
            f_name = None
        else:
            f_name = Identifier._deserialize(field, seq_to_ob, links)

        # Deserialize the operands field.
        field = cbor.get('operands', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field operands')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field operands')
        if field.get('@t', None) is None:
            f_operands = None
        else:
            f_operands = ExpressionList._deserialize(field, seq_to_ob, links)

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

        # Construct the Gate node.
        node = Gate(f_name, f_operands, f_annotations)

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
        cbor = {'@i': id_map[id(self)], '@t': 'Gate'}

        # Serialize the name field.
        field = {'@T': '1'}
        if self._attr_name is None:
            field['@t'] = None
        else:
            field.update(self._attr_name._serialize(id_map))
        cbor['name'] = field

        # Serialize the operands field.
        field = {'@T': '1'}
        if self._attr_operands is None:
            field['@t'] = None
        else:
            field.update(self._attr_operands._serialize(id_map))
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


class MultiGate(_Multiple):
    """Wrapper for an edge with multiple Gate objects."""

    _T = Gate


_typemap['Gate'] = Gate

class GlobalBlock(Block):
    __slots__ = [
        '_attr_qubit_variable_declaration',
        '_attr_gates',
        '_attr_measure_instruction',
    ]

    def __init__(
        self,
        qubit_variable_declaration=None,
        gates=None,
        measure_instruction=None,
    ):
        super().__init__()
        self.qubit_variable_declaration = qubit_variable_declaration
        self.gates = gates
        self.measure_instruction = measure_instruction

    @property
    def qubit_variable_declaration(self):
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
    def gates(self):
        return self._attr_gates

    @gates.setter
    def gates(self, val):
        if val is None:
            del self.gates
            return
        if not isinstance(val, MultiGate):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('gates must be of type MultiGate')
            val = MultiGate(val)
        self._attr_gates = val

    @gates.deleter
    def gates(self):
        self._attr_gates = MultiGate()

    @property
    def measure_instruction(self):
        return self._attr_measure_instruction

    @measure_instruction.setter
    def measure_instruction(self, val):
        if val is None:
            del self.measure_instruction
            return
        if not isinstance(val, MeasureInstruction):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('measure_instruction must be of type MeasureInstruction')
            val = MeasureInstruction(val)
        self._attr_measure_instruction = val

    @measure_instruction.deleter
    def measure_instruction(self):
        self._attr_measure_instruction = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, GlobalBlock):
            return False
        if self.qubit_variable_declaration != other.qubit_variable_declaration:
            return False
        if self.gates != other.gates:
            return False
        if self.measure_instruction != other.measure_instruction:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('GlobalBlock(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('qubit_variable_declaration: ')
        if self.qubit_variable_declaration is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.qubit_variable_declaration.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('gates: ')
        if not self.gates:
            s.append('-\n')
        else:
            s.append('[\n')
            for child in self.gates:
                s.append(child.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + ']\n')
        s.append('  '*indent)
        s.append('measure_instruction: ')
        if self.measure_instruction is None:
            s.append('-\n')
        else:
            s.append('<\n')
            s.append(self.measure_instruction.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_qubit_variable_declaration is not None:
            self._attr_qubit_variable_declaration.find_reachable(id_map)
        for el in self._attr_gates:
            el.find_reachable(id_map)
        if self._attr_measure_instruction is not None:
            self._attr_measure_instruction.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_qubit_variable_declaration is None:
            raise NotWellFormed('qubit_variable_declaration is required but not set')
        if self._attr_qubit_variable_declaration is not None:
            self._attr_qubit_variable_declaration.check_complete(id_map)
        for child in self._attr_gates:
            child.check_complete(id_map)
        if self._attr_measure_instruction is not None:
            self._attr_measure_instruction.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return GlobalBlock(
            qubit_variable_declaration=self._attr_qubit_variable_declaration,
            gates=self._attr_gates.copy(),
            measure_instruction=self._attr_measure_instruction
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return GlobalBlock(
            qubit_variable_declaration=_cloned(self._attr_qubit_variable_declaration),
            gates=_cloned(self._attr_gates),
            measure_instruction=_cloned(self._attr_measure_instruction)
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
        if typ != 'GlobalBlock':
            raise ValueError('found node serialization for ' + typ + ', but expected GlobalBlock')

        # Deserialize the qubit_variable_declaration field.
        field = cbor.get('qubit_variable_declaration', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field qubit_variable_declaration')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field qubit_variable_declaration')
        if field.get('@t', None) is None:
            f_qubit_variable_declaration = None
        else:
            f_qubit_variable_declaration = Variable._deserialize(field, seq_to_ob, links)

        # Deserialize the gates field.
        field = cbor.get('gates', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field gates')
        if field.get('@T') != '*':
            raise ValueError('unexpected edge type for field gates')
        data = field.get('@d', None)
        if not isinstance(data, list):
            raise ValueError('missing serialization of Any/Many contents')
        f_gates = MultiGate()
        for element in data:
            if element.get('@T') != '1':
                raise ValueError('unexpected edge type for Any/Many element')
            f_gates.append(Gate._deserialize(element, seq_to_ob, links))

        # Deserialize the measure_instruction field.
        field = cbor.get('measure_instruction', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field measure_instruction')
        if field.get('@T') != '?':
            raise ValueError('unexpected edge type for field measure_instruction')
        if field.get('@t', None) is None:
            f_measure_instruction = None
        else:
            f_measure_instruction = MeasureInstruction._deserialize(field, seq_to_ob, links)

        # Construct the GlobalBlock node.
        node = GlobalBlock(f_qubit_variable_declaration, f_gates, f_measure_instruction)

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
        cbor = {'@i': id_map[id(self)], '@t': 'GlobalBlock'}

        # Serialize the qubit_variable_declaration field.
        field = {'@T': '1'}
        if self._attr_qubit_variable_declaration is None:
            field['@t'] = None
        else:
            field.update(self._attr_qubit_variable_declaration._serialize(id_map))
        cbor['qubit_variable_declaration'] = field

        # Serialize the gates field.
        field = {'@T': '*'}
        lst = []
        for el in self._attr_gates:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['gates'] = field

        # Serialize the measure_instruction field.
        field = {'@T': '?'}
        if self._attr_measure_instruction is None:
            field['@t'] = None
        else:
            field.update(self._attr_measure_instruction._serialize(id_map))
        cbor['measure_instruction'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiGlobalBlock(_Multiple):
    """Wrapper for an edge with multiple GlobalBlock objects."""

    _T = GlobalBlock


_typemap['GlobalBlock'] = GlobalBlock

class Identifier(Expression):
    __slots__ = [
        '_attr_name',
    ]

    def __init__(
        self,
        name=None,
    ):
        super().__init__()
        self.name = name

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

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Identifier):
            return False
        if self.name != other.name:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Identifier(')
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
        return Identifier(
            name=self._attr_name
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Identifier(
            name=_cloned(self._attr_name)
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
        if typ != 'Identifier':
            raise ValueError('found node serialization for ' + typ + ', but expected Identifier')

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if hasattr(cqasm.v3x.primitives.Str, 'deserialize_cbor'):
            f_name = cqasm.v3x.primitives.Str.deserialize_cbor(field)
        else:
            f_name = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Str, field)

        # Construct the Identifier node.
        node = Identifier(f_name)

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
        cbor = {'@i': id_map[id(self)], '@t': 'Identifier'}

        # Serialize the name field.
        if hasattr(self._attr_name, 'serialize_cbor'):
            cbor['name'] = self._attr_name.serialize_cbor()
        else:
            cbor['name'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Str, self._attr_name)

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiIdentifier(_Multiple):
    """Wrapper for an edge with multiple Identifier objects."""

    _T = Identifier


_typemap['Identifier'] = Identifier

class Index(Expression):
    __slots__ = [
        '_attr_expr',
        '_attr_indices',
    ]

    def __init__(
        self,
        expr=None,
        indices=None,
    ):
        super().__init__()
        self.expr = expr
        self.indices = indices

    @property
    def expr(self):
        return self._attr_expr

    @expr.setter
    def expr(self, val):
        if val is None:
            del self.expr
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('expr must be of type Expression')
            val = Expression(val)
        self._attr_expr = val

    @expr.deleter
    def expr(self):
        self._attr_expr = None

    @property
    def indices(self):
        return self._attr_indices

    @indices.setter
    def indices(self, val):
        if val is None:
            del self.indices
            return
        if not isinstance(val, IndexList):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('indices must be of type IndexList')
            val = IndexList(val)
        self._attr_indices = val

    @indices.deleter
    def indices(self):
        self._attr_indices = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Index):
            return False
        if self.expr != other.expr:
            return False
        if self.indices != other.indices:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Index(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('expr: ')
        if self.expr is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.expr.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('indices: ')
        if self.indices is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.indices.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_expr is not None:
            self._attr_expr.find_reachable(id_map)
        if self._attr_indices is not None:
            self._attr_indices.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_expr is None:
            raise NotWellFormed('expr is required but not set')
        if self._attr_expr is not None:
            self._attr_expr.check_complete(id_map)
        if self._attr_indices is None:
            raise NotWellFormed('indices is required but not set')
        if self._attr_indices is not None:
            self._attr_indices.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return Index(
            expr=self._attr_expr,
            indices=self._attr_indices
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Index(
            expr=_cloned(self._attr_expr),
            indices=_cloned(self._attr_indices)
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
        if typ != 'Index':
            raise ValueError('found node serialization for ' + typ + ', but expected Index')

        # Deserialize the expr field.
        field = cbor.get('expr', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field expr')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field expr')
        if field.get('@t', None) is None:
            f_expr = None
        else:
            f_expr = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the indices field.
        field = cbor.get('indices', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field indices')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field indices')
        if field.get('@t', None) is None:
            f_indices = None
        else:
            f_indices = IndexList._deserialize(field, seq_to_ob, links)

        # Construct the Index node.
        node = Index(f_expr, f_indices)

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
        cbor = {'@i': id_map[id(self)], '@t': 'Index'}

        # Serialize the expr field.
        field = {'@T': '1'}
        if self._attr_expr is None:
            field['@t'] = None
        else:
            field.update(self._attr_expr._serialize(id_map))
        cbor['expr'] = field

        # Serialize the indices field.
        field = {'@T': '1'}
        if self._attr_indices is None:
            field['@t'] = None
        else:
            field.update(self._attr_indices._serialize(id_map))
        cbor['indices'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiIndex(_Multiple):
    """Wrapper for an edge with multiple Index objects."""

    _T = Index


_typemap['Index'] = Index

class IndexEntry(Node):
    __slots__ = []

    def __init__(self):
        super().__init__()

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
        if typ == 'IndexItem':
            return IndexItem._deserialize(cbor, seq_to_ob, links)
        if typ == 'IndexRange':
            return IndexRange._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'IndexEntry'}

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiIndexEntry(_Multiple):
    """Wrapper for an edge with multiple IndexEntry objects."""

    _T = IndexEntry


_typemap['IndexEntry'] = IndexEntry

class IndexItem(IndexEntry):
    """Zero based."""

    __slots__ = [
        '_attr_index',
    ]

    def __init__(
        self,
        index=None,
    ):
        super().__init__()
        self.index = index

    @property
    def index(self):
        return self._attr_index

    @index.setter
    def index(self, val):
        if val is None:
            del self.index
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('index must be of type Expression')
            val = Expression(val)
        self._attr_index = val

    @index.deleter
    def index(self):
        self._attr_index = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, IndexItem):
            return False
        if self.index != other.index:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('IndexItem(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('index: ')
        if self.index is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.index.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_index is not None:
            self._attr_index.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_index is None:
            raise NotWellFormed('index is required but not set')
        if self._attr_index is not None:
            self._attr_index.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return IndexItem(
            index=self._attr_index
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return IndexItem(
            index=_cloned(self._attr_index)
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
        if typ != 'IndexItem':
            raise ValueError('found node serialization for ' + typ + ', but expected IndexItem')

        # Deserialize the index field.
        field = cbor.get('index', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field index')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field index')
        if field.get('@t', None) is None:
            f_index = None
        else:
            f_index = Expression._deserialize(field, seq_to_ob, links)

        # Construct the IndexItem node.
        node = IndexItem(f_index)

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
        cbor = {'@i': id_map[id(self)], '@t': 'IndexItem'}

        # Serialize the index field.
        field = {'@T': '1'}
        if self._attr_index is None:
            field['@t'] = None
        else:
            field.update(self._attr_index._serialize(id_map))
        cbor['index'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiIndexItem(_Multiple):
    """Wrapper for an edge with multiple IndexItem objects."""

    _T = IndexItem


_typemap['IndexItem'] = IndexItem

class IndexList(Node):
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
        if not isinstance(val, MultiIndexEntry):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('items must be of type MultiIndexEntry')
            val = MultiIndexEntry(val)
        self._attr_items = val

    @items.deleter
    def items(self):
        self._attr_items = MultiIndexEntry()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, IndexList):
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
        s.append('IndexList(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('items: ')
        if not self.items:
            s.append('!MISSING\n')
        else:
            s.append('[\n')
            for child in self.items:
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
        for el in self._attr_items:
            el.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if not self._attr_items:
            raise NotWellFormed('items needs at least one node but has zero')
        for child in self._attr_items:
            child.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return IndexList(
            items=self._attr_items.copy()
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return IndexList(
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
        if typ != 'IndexList':
            raise ValueError('found node serialization for ' + typ + ', but expected IndexList')

        # Deserialize the items field.
        field = cbor.get('items', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field items')
        if field.get('@T') != '+':
            raise ValueError('unexpected edge type for field items')
        data = field.get('@d', None)
        if not isinstance(data, list):
            raise ValueError('missing serialization of Any/Many contents')
        f_items = MultiIndexEntry()
        for element in data:
            if element.get('@T') != '1':
                raise ValueError('unexpected edge type for Any/Many element')
            f_items.append(IndexEntry._deserialize(element, seq_to_ob, links))

        # Construct the IndexList node.
        node = IndexList(f_items)

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
        cbor = {'@i': id_map[id(self)], '@t': 'IndexList'}

        # Serialize the items field.
        field = {'@T': '+'}
        lst = []
        for el in self._attr_items:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['items'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiIndexList(_Multiple):
    """Wrapper for an edge with multiple IndexList objects."""

    _T = IndexList


_typemap['IndexList'] = IndexList

class IndexRange(IndexEntry):
    """ Inclusive."""

    __slots__ = [
        '_attr_first',
        '_attr_last',
    ]

    def __init__(
        self,
        first=None,
        last=None,
    ):
        super().__init__()
        self.first = first
        self.last = last

    @property
    def first(self):
        return self._attr_first

    @first.setter
    def first(self, val):
        if val is None:
            del self.first
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('first must be of type Expression')
            val = Expression(val)
        self._attr_first = val

    @first.deleter
    def first(self):
        self._attr_first = None

    @property
    def last(self):
        return self._attr_last

    @last.setter
    def last(self, val):
        if val is None:
            del self.last
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('last must be of type Expression')
            val = Expression(val)
        self._attr_last = val

    @last.deleter
    def last(self):
        self._attr_last = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, IndexRange):
            return False
        if self.first != other.first:
            return False
        if self.last != other.last:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('IndexRange(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('first: ')
        if self.first is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.first.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('last: ')
        if self.last is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.last.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_first is not None:
            self._attr_first.find_reachable(id_map)
        if self._attr_last is not None:
            self._attr_last.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_first is None:
            raise NotWellFormed('first is required but not set')
        if self._attr_first is not None:
            self._attr_first.check_complete(id_map)
        if self._attr_last is None:
            raise NotWellFormed('last is required but not set')
        if self._attr_last is not None:
            self._attr_last.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return IndexRange(
            first=self._attr_first,
            last=self._attr_last
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return IndexRange(
            first=_cloned(self._attr_first),
            last=_cloned(self._attr_last)
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
        if typ != 'IndexRange':
            raise ValueError('found node serialization for ' + typ + ', but expected IndexRange')

        # Deserialize the first field.
        field = cbor.get('first', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field first')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field first')
        if field.get('@t', None) is None:
            f_first = None
        else:
            f_first = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the last field.
        field = cbor.get('last', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field last')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field last')
        if field.get('@t', None) is None:
            f_last = None
        else:
            f_last = Expression._deserialize(field, seq_to_ob, links)

        # Construct the IndexRange node.
        node = IndexRange(f_first, f_last)

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
        cbor = {'@i': id_map[id(self)], '@t': 'IndexRange'}

        # Serialize the first field.
        field = {'@T': '1'}
        if self._attr_first is None:
            field['@t'] = None
        else:
            field.update(self._attr_first._serialize(id_map))
        cbor['first'] = field

        # Serialize the last field.
        field = {'@T': '1'}
        if self._attr_last is None:
            field['@t'] = None
        else:
            field.update(self._attr_last._serialize(id_map))
        cbor['last'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiIndexRange(_Multiple):
    """Wrapper for an edge with multiple IndexRange objects."""

    _T = IndexRange


_typemap['IndexRange'] = IndexRange

class IntegerLiteral(Expression):
    __slots__ = [
        '_attr_value',
    ]

    def __init__(
        self,
        value=None,
    ):
        super().__init__()
        self.value = value

    @property
    def value(self):
        return self._attr_value

    @value.setter
    def value(self, val):
        if val is None:
            del self.value
            return
        if not isinstance(val, cqasm.v3x.primitives.Int):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('value must be of type cqasm.v3x.primitives.Int')
            val = cqasm.v3x.primitives.Int(val)
        self._attr_value = val

    @value.deleter
    def value(self):
        self._attr_value = cqasm.v3x.primitives.Int()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, IntegerLiteral):
            return False
        if self.value != other.value:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('IntegerLiteral(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('value: ')
        s.append(str(self.value) + '\n')
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
        return IntegerLiteral(
            value=self._attr_value
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return IntegerLiteral(
            value=_cloned(self._attr_value)
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
        if typ != 'IntegerLiteral':
            raise ValueError('found node serialization for ' + typ + ', but expected IntegerLiteral')

        # Deserialize the value field.
        field = cbor.get('value', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field value')
        if hasattr(cqasm.v3x.primitives.Int, 'deserialize_cbor'):
            f_value = cqasm.v3x.primitives.Int.deserialize_cbor(field)
        else:
            f_value = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Int, field)

        # Construct the IntegerLiteral node.
        node = IntegerLiteral(f_value)

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
        cbor = {'@i': id_map[id(self)], '@t': 'IntegerLiteral'}

        # Serialize the value field.
        if hasattr(self._attr_value, 'serialize_cbor'):
            cbor['value'] = self._attr_value.serialize_cbor()
        else:
            cbor['value'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Int, self._attr_value)

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiIntegerLiteral(_Multiple):
    """Wrapper for an edge with multiple IntegerLiteral objects."""

    _T = IntegerLiteral


_typemap['IntegerLiteral'] = IntegerLiteral

class Keyword(Node):
    __slots__ = [
        '_attr_name',
    ]

    def __init__(
        self,
        name=None,
    ):
        super().__init__()
        self.name = name

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

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Keyword):
            return False
        if self.name != other.name:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Keyword(')
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
        return Keyword(
            name=self._attr_name
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Keyword(
            name=_cloned(self._attr_name)
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
        if typ != 'Keyword':
            raise ValueError('found node serialization for ' + typ + ', but expected Keyword')

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if hasattr(cqasm.v3x.primitives.Str, 'deserialize_cbor'):
            f_name = cqasm.v3x.primitives.Str.deserialize_cbor(field)
        else:
            f_name = cqasm.v3x.primitives.deserialize(cqasm.v3x.primitives.Str, field)

        # Construct the Keyword node.
        node = Keyword(f_name)

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
        cbor = {'@i': id_map[id(self)], '@t': 'Keyword'}

        # Serialize the name field.
        if hasattr(self._attr_name, 'serialize_cbor'):
            cbor['name'] = self._attr_name.serialize_cbor()
        else:
            cbor['name'] = cqasm.v3x.primitives.serialize(cqasm.v3x.primitives.Str, self._attr_name)

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiKeyword(_Multiple):
    """Wrapper for an edge with multiple Keyword objects."""

    _T = Keyword


_typemap['Keyword'] = Keyword

class LogicalExpression(BinaryExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

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
        if typ == 'LogicalAndExpression':
            return LogicalAndExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'LogicalXorExpression':
            return LogicalXorExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'LogicalOrExpression':
            return LogicalOrExpression._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'LogicalExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiLogicalExpression(_Multiple):
    """Wrapper for an edge with multiple LogicalExpression objects."""

    _T = LogicalExpression


_typemap['LogicalExpression'] = LogicalExpression

class LogicalAndExpression(LogicalExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, LogicalAndExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('LogicalAndExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return LogicalAndExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return LogicalAndExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'LogicalAndExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected LogicalAndExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the LogicalAndExpression node.
        node = LogicalAndExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'LogicalAndExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiLogicalAndExpression(_Multiple):
    """Wrapper for an edge with multiple LogicalAndExpression objects."""

    _T = LogicalAndExpression


_typemap['LogicalAndExpression'] = LogicalAndExpression

class LogicalNotExpression(UnaryExpression):
    __slots__ = []

    def __init__(
        self,
        expr=None,
    ):
        super().__init__(expr=expr)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, LogicalNotExpression):
            return False
        if self.expr != other.expr:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('LogicalNotExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('expr: ')
        if self.expr is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.expr.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_expr is not None:
            self._attr_expr.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_expr is None:
            raise NotWellFormed('expr is required but not set')
        if self._attr_expr is not None:
            self._attr_expr.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return LogicalNotExpression(
            expr=self._attr_expr
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return LogicalNotExpression(
            expr=_cloned(self._attr_expr)
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
        if typ != 'LogicalNotExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected LogicalNotExpression')

        # Deserialize the expr field.
        field = cbor.get('expr', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field expr')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field expr')
        if field.get('@t', None) is None:
            f_expr = None
        else:
            f_expr = Expression._deserialize(field, seq_to_ob, links)

        # Construct the LogicalNotExpression node.
        node = LogicalNotExpression(f_expr)

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
        cbor = {'@i': id_map[id(self)], '@t': 'LogicalNotExpression'}

        # Serialize the expr field.
        field = {'@T': '1'}
        if self._attr_expr is None:
            field['@t'] = None
        else:
            field.update(self._attr_expr._serialize(id_map))
        cbor['expr'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiLogicalNotExpression(_Multiple):
    """Wrapper for an edge with multiple LogicalNotExpression objects."""

    _T = LogicalNotExpression


_typemap['LogicalNotExpression'] = LogicalNotExpression

class LogicalOrExpression(LogicalExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, LogicalOrExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('LogicalOrExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return LogicalOrExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return LogicalOrExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'LogicalOrExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected LogicalOrExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the LogicalOrExpression node.
        node = LogicalOrExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'LogicalOrExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiLogicalOrExpression(_Multiple):
    """Wrapper for an edge with multiple LogicalOrExpression objects."""

    _T = LogicalOrExpression


_typemap['LogicalOrExpression'] = LogicalOrExpression

class LogicalXorExpression(LogicalExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, LogicalXorExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('LogicalXorExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return LogicalXorExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return LogicalXorExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'LogicalXorExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected LogicalXorExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the LogicalXorExpression node.
        node = LogicalXorExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'LogicalXorExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiLogicalXorExpression(_Multiple):
    """Wrapper for an edge with multiple LogicalXorExpression objects."""

    _T = LogicalXorExpression


_typemap['LogicalXorExpression'] = LogicalXorExpression

class MeasureInstruction(Instruction):
    __slots__ = [
        '_attr_name',
        '_attr_operand',
    ]

    def __init__(
        self,
        name=None,
        operand=None,
        annotations=None,
    ):
        super().__init__(annotations=annotations)
        self.name = name
        self.operand = operand

    @property
    def name(self):
        return self._attr_name

    @name.setter
    def name(self, val):
        if val is None:
            del self.name
            return
        if not isinstance(val, Identifier):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('name must be of type Identifier')
            val = Identifier(val)
        self._attr_name = val

    @name.deleter
    def name(self):
        self._attr_name = None

    @property
    def operand(self):
        return self._attr_operand

    @operand.setter
    def operand(self, val):
        if val is None:
            del self.operand
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('operand must be of type Expression')
            val = Expression(val)
        self._attr_operand = val

    @operand.deleter
    def operand(self):
        self._attr_operand = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, MeasureInstruction):
            return False
        if self.name != other.name:
            return False
        if self.operand != other.operand:
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
        s.append('MeasureInstruction(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('name: ')
        if self.name is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.name.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('operand: ')
        if self.operand is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.operand.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_name is not None:
            self._attr_name.find_reachable(id_map)
        if self._attr_operand is not None:
            self._attr_operand.find_reachable(id_map)
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
        if self._attr_name is None:
            raise NotWellFormed('name is required but not set')
        if self._attr_name is not None:
            self._attr_name.check_complete(id_map)
        if self._attr_operand is None:
            raise NotWellFormed('operand is required but not set')
        if self._attr_operand is not None:
            self._attr_operand.check_complete(id_map)
        for child in self._attr_annotations:
            child.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return MeasureInstruction(
            name=self._attr_name,
            operand=self._attr_operand,
            annotations=self._attr_annotations.copy()
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return MeasureInstruction(
            name=_cloned(self._attr_name),
            operand=_cloned(self._attr_operand),
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
        if typ != 'MeasureInstruction':
            raise ValueError('found node serialization for ' + typ + ', but expected MeasureInstruction')

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field name')
        if field.get('@t', None) is None:
            f_name = None
        else:
            f_name = Identifier._deserialize(field, seq_to_ob, links)

        # Deserialize the operand field.
        field = cbor.get('operand', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field operand')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field operand')
        if field.get('@t', None) is None:
            f_operand = None
        else:
            f_operand = Expression._deserialize(field, seq_to_ob, links)

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

        # Construct the MeasureInstruction node.
        node = MeasureInstruction(f_name, f_operand, f_annotations)

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
        cbor = {'@i': id_map[id(self)], '@t': 'MeasureInstruction'}

        # Serialize the name field.
        field = {'@T': '1'}
        if self._attr_name is None:
            field['@t'] = None
        else:
            field.update(self._attr_name._serialize(id_map))
        cbor['name'] = field

        # Serialize the operand field.
        field = {'@T': '1'}
        if self._attr_operand is None:
            field['@t'] = None
        else:
            field.update(self._attr_operand._serialize(id_map))
        cbor['operand'] = field

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


class MultiMeasureInstruction(_Multiple):
    """Wrapper for an edge with multiple MeasureInstruction objects."""

    _T = MeasureInstruction


_typemap['MeasureInstruction'] = MeasureInstruction

class ModuloExpression(ArithmeticExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, ModuloExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('ModuloExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return ModuloExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return ModuloExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'ModuloExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected ModuloExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the ModuloExpression node.
        node = ModuloExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'ModuloExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiModuloExpression(_Multiple):
    """Wrapper for an edge with multiple ModuloExpression objects."""

    _T = ModuloExpression


_typemap['ModuloExpression'] = ModuloExpression

class PowerExpression(ArithmeticExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, PowerExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('PowerExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return PowerExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return PowerExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'PowerExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected PowerExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the PowerExpression node.
        node = PowerExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'PowerExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiPowerExpression(_Multiple):
    """Wrapper for an edge with multiple PowerExpression objects."""

    _T = PowerExpression


_typemap['PowerExpression'] = PowerExpression

class ProductExpression(ArithmeticExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, ProductExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('ProductExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return ProductExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return ProductExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'ProductExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected ProductExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the ProductExpression node.
        node = ProductExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'ProductExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiProductExpression(_Multiple):
    """Wrapper for an edge with multiple ProductExpression objects."""

    _T = ProductExpression


_typemap['ProductExpression'] = ProductExpression

class Root(Node):
    __slots__ = []

    def __init__(self):
        super().__init__()

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
        if typ == 'Program':
            return Program._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Root'}

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiRoot(_Multiple):
    """Wrapper for an edge with multiple Root objects."""

    _T = Root


_typemap['Root'] = Root

class Program(Root):
    __slots__ = [
        '_attr_version',
        '_attr_block',
    ]

    def __init__(
        self,
        version=None,
        block=None,
    ):
        super().__init__()
        self.version = version
        self.block = block

    @property
    def version(self):
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
    def block(self):
        return self._attr_block

    @block.setter
    def block(self, val):
        if val is None:
            del self.block
            return
        if not isinstance(val, GlobalBlock):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('block must be of type GlobalBlock')
            val = GlobalBlock(val)
        self._attr_block = val

    @block.deleter
    def block(self):
        self._attr_block = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Program):
            return False
        if self.version != other.version:
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
        s.append('version: ')
        if self.version is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.version.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_block is not None:
            self._attr_block.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return Program(
            version=self._attr_version,
            block=self._attr_block
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Program(
            version=_cloned(self._attr_version),
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

        # Deserialize the block field.
        field = cbor.get('block', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field block')
        if field.get('@T') != '?':
            raise ValueError('unexpected edge type for field block')
        if field.get('@t', None) is None:
            f_block = None
        else:
            f_block = GlobalBlock._deserialize(field, seq_to_ob, links)

        # Construct the Program node.
        node = Program(f_version, f_block)

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

        # Serialize the version field.
        field = {'@T': '1'}
        if self._attr_version is None:
            field['@t'] = None
        else:
            field.update(self._attr_version._serialize(id_map))
        cbor['version'] = field

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

class ShiftExpression(BinaryExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

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
        if typ == 'ShiftLeftExpression':
            return ShiftLeftExpression._deserialize(cbor, seq_to_ob, links)
        if typ == 'ShiftRightExpression':
            return ShiftRightExpression._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'ShiftExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiShiftExpression(_Multiple):
    """Wrapper for an edge with multiple ShiftExpression objects."""

    _T = ShiftExpression


_typemap['ShiftExpression'] = ShiftExpression

class ShiftLeftExpression(ShiftExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, ShiftLeftExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('ShiftLeftExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return ShiftLeftExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return ShiftLeftExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'ShiftLeftExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected ShiftLeftExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the ShiftLeftExpression node.
        node = ShiftLeftExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'ShiftLeftExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiShiftLeftExpression(_Multiple):
    """Wrapper for an edge with multiple ShiftLeftExpression objects."""

    _T = ShiftLeftExpression


_typemap['ShiftLeftExpression'] = ShiftLeftExpression

class ShiftRightExpression(ShiftExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, ShiftRightExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('ShiftRightExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return ShiftRightExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return ShiftRightExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'ShiftRightExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected ShiftRightExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the ShiftRightExpression node.
        node = ShiftRightExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'ShiftRightExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiShiftRightExpression(_Multiple):
    """Wrapper for an edge with multiple ShiftRightExpression objects."""

    _T = ShiftRightExpression


_typemap['ShiftRightExpression'] = ShiftRightExpression

class SubtractionExpression(ArithmeticExpression):
    __slots__ = []

    def __init__(
        self,
        lhs=None,
        rhs=None,
    ):
        super().__init__(lhs=lhs, rhs=rhs)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, SubtractionExpression):
            return False
        if self.lhs != other.lhs:
            return False
        if self.rhs != other.rhs:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('SubtractionExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('lhs: ')
        if self.lhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.lhs.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('rhs: ')
        if self.rhs is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.rhs.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_lhs is not None:
            self._attr_lhs.find_reachable(id_map)
        if self._attr_rhs is not None:
            self._attr_rhs.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_lhs is None:
            raise NotWellFormed('lhs is required but not set')
        if self._attr_lhs is not None:
            self._attr_lhs.check_complete(id_map)
        if self._attr_rhs is None:
            raise NotWellFormed('rhs is required but not set')
        if self._attr_rhs is not None:
            self._attr_rhs.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return SubtractionExpression(
            lhs=self._attr_lhs,
            rhs=self._attr_rhs
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return SubtractionExpression(
            lhs=_cloned(self._attr_lhs),
            rhs=_cloned(self._attr_rhs)
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
        if typ != 'SubtractionExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected SubtractionExpression')

        # Deserialize the lhs field.
        field = cbor.get('lhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field lhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field lhs')
        if field.get('@t', None) is None:
            f_lhs = None
        else:
            f_lhs = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the rhs field.
        field = cbor.get('rhs', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field rhs')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field rhs')
        if field.get('@t', None) is None:
            f_rhs = None
        else:
            f_rhs = Expression._deserialize(field, seq_to_ob, links)

        # Construct the SubtractionExpression node.
        node = SubtractionExpression(f_lhs, f_rhs)

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
        cbor = {'@i': id_map[id(self)], '@t': 'SubtractionExpression'}

        # Serialize the lhs field.
        field = {'@T': '1'}
        if self._attr_lhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_lhs._serialize(id_map))
        cbor['lhs'] = field

        # Serialize the rhs field.
        field = {'@T': '1'}
        if self._attr_rhs is None:
            field['@t'] = None
        else:
            field.update(self._attr_rhs._serialize(id_map))
        cbor['rhs'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiSubtractionExpression(_Multiple):
    """Wrapper for an edge with multiple SubtractionExpression objects."""

    _T = SubtractionExpression


_typemap['SubtractionExpression'] = SubtractionExpression

class TernaryConditionalExpression(Expression):
    __slots__ = [
        '_attr_cond',
        '_attr_if_true',
        '_attr_if_false',
    ]

    def __init__(
        self,
        cond=None,
        if_true=None,
        if_false=None,
    ):
        super().__init__()
        self.cond = cond
        self.if_true = if_true
        self.if_false = if_false

    @property
    def cond(self):
        return self._attr_cond

    @cond.setter
    def cond(self, val):
        if val is None:
            del self.cond
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('cond must be of type Expression')
            val = Expression(val)
        self._attr_cond = val

    @cond.deleter
    def cond(self):
        self._attr_cond = None

    @property
    def if_true(self):
        return self._attr_if_true

    @if_true.setter
    def if_true(self, val):
        if val is None:
            del self.if_true
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('if_true must be of type Expression')
            val = Expression(val)
        self._attr_if_true = val

    @if_true.deleter
    def if_true(self):
        self._attr_if_true = None

    @property
    def if_false(self):
        return self._attr_if_false

    @if_false.setter
    def if_false(self, val):
        if val is None:
            del self.if_false
            return
        if not isinstance(val, Expression):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('if_false must be of type Expression')
            val = Expression(val)
        self._attr_if_false = val

    @if_false.deleter
    def if_false(self):
        self._attr_if_false = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, TernaryConditionalExpression):
            return False
        if self.cond != other.cond:
            return False
        if self.if_true != other.if_true:
            return False
        if self.if_false != other.if_false:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('TernaryConditionalExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('cond: ')
        if self.cond is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.cond.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('if_true: ')
        if self.if_true is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.if_true.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('if_false: ')
        if self.if_false is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.if_false.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_cond is not None:
            self._attr_cond.find_reachable(id_map)
        if self._attr_if_true is not None:
            self._attr_if_true.find_reachable(id_map)
        if self._attr_if_false is not None:
            self._attr_if_false.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_cond is None:
            raise NotWellFormed('cond is required but not set')
        if self._attr_cond is not None:
            self._attr_cond.check_complete(id_map)
        if self._attr_if_true is None:
            raise NotWellFormed('if_true is required but not set')
        if self._attr_if_true is not None:
            self._attr_if_true.check_complete(id_map)
        if self._attr_if_false is None:
            raise NotWellFormed('if_false is required but not set')
        if self._attr_if_false is not None:
            self._attr_if_false.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return TernaryConditionalExpression(
            cond=self._attr_cond,
            if_true=self._attr_if_true,
            if_false=self._attr_if_false
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return TernaryConditionalExpression(
            cond=_cloned(self._attr_cond),
            if_true=_cloned(self._attr_if_true),
            if_false=_cloned(self._attr_if_false)
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
        if typ != 'TernaryConditionalExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected TernaryConditionalExpression')

        # Deserialize the cond field.
        field = cbor.get('cond', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field cond')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field cond')
        if field.get('@t', None) is None:
            f_cond = None
        else:
            f_cond = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the if_true field.
        field = cbor.get('if_true', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field if_true')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field if_true')
        if field.get('@t', None) is None:
            f_if_true = None
        else:
            f_if_true = Expression._deserialize(field, seq_to_ob, links)

        # Deserialize the if_false field.
        field = cbor.get('if_false', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field if_false')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field if_false')
        if field.get('@t', None) is None:
            f_if_false = None
        else:
            f_if_false = Expression._deserialize(field, seq_to_ob, links)

        # Construct the TernaryConditionalExpression node.
        node = TernaryConditionalExpression(f_cond, f_if_true, f_if_false)

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
        cbor = {'@i': id_map[id(self)], '@t': 'TernaryConditionalExpression'}

        # Serialize the cond field.
        field = {'@T': '1'}
        if self._attr_cond is None:
            field['@t'] = None
        else:
            field.update(self._attr_cond._serialize(id_map))
        cbor['cond'] = field

        # Serialize the if_true field.
        field = {'@T': '1'}
        if self._attr_if_true is None:
            field['@t'] = None
        else:
            field.update(self._attr_if_true._serialize(id_map))
        cbor['if_true'] = field

        # Serialize the if_false field.
        field = {'@T': '1'}
        if self._attr_if_false is None:
            field['@t'] = None
        else:
            field.update(self._attr_if_false._serialize(id_map))
        cbor['if_false'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiTernaryConditionalExpression(_Multiple):
    """Wrapper for an edge with multiple TernaryConditionalExpression objects.
    """

    _T = TernaryConditionalExpression


_typemap['TernaryConditionalExpression'] = TernaryConditionalExpression

class Type(Node):
    __slots__ = [
        '_attr_name',
        '_attr_size',
    ]

    def __init__(
        self,
        name=None,
        size=None,
    ):
        super().__init__()
        self.name = name
        self.size = size

    @property
    def name(self):
        return self._attr_name

    @name.setter
    def name(self, val):
        if val is None:
            del self.name
            return
        if not isinstance(val, Keyword):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('name must be of type Keyword')
            val = Keyword(val)
        self._attr_name = val

    @name.deleter
    def name(self):
        self._attr_name = None

    @property
    def size(self):
        return self._attr_size

    @size.setter
    def size(self, val):
        if val is None:
            del self.size
            return
        if not isinstance(val, IntegerLiteral):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('size must be of type IntegerLiteral')
            val = IntegerLiteral(val)
        self._attr_size = val

    @size.deleter
    def size(self):
        self._attr_size = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Type):
            return False
        if self.name != other.name:
            return False
        if self.size != other.size:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Type(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('name: ')
        if self.name is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.name.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('size: ')
        if self.size is None:
            s.append('-\n')
        else:
            s.append('<\n')
            s.append(self.size.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_name is not None:
            self._attr_name.find_reachable(id_map)
        if self._attr_size is not None:
            self._attr_size.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_name is None:
            raise NotWellFormed('name is required but not set')
        if self._attr_name is not None:
            self._attr_name.check_complete(id_map)
        if self._attr_size is not None:
            self._attr_size.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return Type(
            name=self._attr_name,
            size=self._attr_size
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Type(
            name=_cloned(self._attr_name),
            size=_cloned(self._attr_size)
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
        if typ != 'Type':
            raise ValueError('found node serialization for ' + typ + ', but expected Type')

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field name')
        if field.get('@t', None) is None:
            f_name = None
        else:
            f_name = Keyword._deserialize(field, seq_to_ob, links)

        # Deserialize the size field.
        field = cbor.get('size', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field size')
        if field.get('@T') != '?':
            raise ValueError('unexpected edge type for field size')
        if field.get('@t', None) is None:
            f_size = None
        else:
            f_size = IntegerLiteral._deserialize(field, seq_to_ob, links)

        # Construct the Type node.
        node = Type(f_name, f_size)

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
        cbor = {'@i': id_map[id(self)], '@t': 'Type'}

        # Serialize the name field.
        field = {'@T': '1'}
        if self._attr_name is None:
            field['@t'] = None
        else:
            field.update(self._attr_name._serialize(id_map))
        cbor['name'] = field

        # Serialize the size field.
        field = {'@T': '?'}
        if self._attr_size is None:
            field['@t'] = None
        else:
            field.update(self._attr_size._serialize(id_map))
        cbor['size'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiType(_Multiple):
    """Wrapper for an edge with multiple Type objects."""

    _T = Type


_typemap['Type'] = Type

class UnaryMinusExpression(UnaryExpression):
    """Two's complement."""

    __slots__ = []

    def __init__(
        self,
        expr=None,
    ):
        super().__init__(expr=expr)

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, UnaryMinusExpression):
            return False
        if self.expr != other.expr:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('UnaryMinusExpression(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('expr: ')
        if self.expr is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.expr.dump(indent + 1, annotations, links) + '\n')
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
        if self._attr_expr is not None:
            self._attr_expr.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_expr is None:
            raise NotWellFormed('expr is required but not set')
        if self._attr_expr is not None:
            self._attr_expr.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return UnaryMinusExpression(
            expr=self._attr_expr
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return UnaryMinusExpression(
            expr=_cloned(self._attr_expr)
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
        if typ != 'UnaryMinusExpression':
            raise ValueError('found node serialization for ' + typ + ', but expected UnaryMinusExpression')

        # Deserialize the expr field.
        field = cbor.get('expr', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field expr')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field expr')
        if field.get('@t', None) is None:
            f_expr = None
        else:
            f_expr = Expression._deserialize(field, seq_to_ob, links)

        # Construct the UnaryMinusExpression node.
        node = UnaryMinusExpression(f_expr)

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
        cbor = {'@i': id_map[id(self)], '@t': 'UnaryMinusExpression'}

        # Serialize the expr field.
        field = {'@T': '1'}
        if self._attr_expr is None:
            field['@t'] = None
        else:
            field.update(self._attr_expr._serialize(id_map))
        cbor['expr'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(cqasm.v3x.primitives.serialize(key, val))

        return cbor


class MultiUnaryMinusExpression(_Multiple):
    """Wrapper for an edge with multiple UnaryMinusExpression objects."""

    _T = UnaryMinusExpression


_typemap['UnaryMinusExpression'] = UnaryMinusExpression

class Variable(BlockStatement):
    """One variable declaration of some type."""

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
        if not isinstance(val, Identifier):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('name must be of type Identifier')
            val = Identifier(val)
        self._attr_name = val

    @name.deleter
    def name(self):
        self._attr_name = None

    @property
    def typ(self):
        return self._attr_typ

    @typ.setter
    def typ(self, val):
        if val is None:
            del self.typ
            return
        if not isinstance(val, Type):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('typ must be of type Type')
            val = Type(val)
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
        if self.name is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.name.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
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
        if self._attr_name is not None:
            self._attr_name.find_reachable(id_map)
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
        if self._attr_name is None:
            raise NotWellFormed('name is required but not set')
        if self._attr_name is not None:
            self._attr_name.check_complete(id_map)
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
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field name')
        if field.get('@t', None) is None:
            f_name = None
        else:
            f_name = Identifier._deserialize(field, seq_to_ob, links)

        # Deserialize the typ field.
        field = cbor.get('typ', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field typ')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field typ')
        if field.get('@t', None) is None:
            f_typ = None
        else:
            f_typ = Type._deserialize(field, seq_to_ob, links)

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
        field = {'@T': '1'}
        if self._attr_name is None:
            field['@t'] = None
        else:
            field.update(self._attr_name._serialize(id_map))
        cbor['name'] = field

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

