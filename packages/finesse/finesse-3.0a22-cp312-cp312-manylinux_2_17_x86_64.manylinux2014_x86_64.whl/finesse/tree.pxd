cdef class TreeNode:
    cdef:
        public bint empty
        public list children
        public TreeNode parent
        str __name
