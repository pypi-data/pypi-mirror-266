from finesse.tracing.tree cimport TraceTree, DependencyType

cdef class tree_container:
    cdef:
        list trees
        Py_ssize_t size

        # All the optical nodes covered by all the trees
        set node_coverage

    cdef clear(self) noexcept
    cdef append(self, TraceTree tree) noexcept
    cdef remove(self, TraceTree tree) noexcept
    cdef _update_after_sub_remove(self, TraceTree sub_tree) noexcept


cdef class TraceForest:
    cdef public:
        bint symmetric # Should beam traces on this forest set opposite node q to -q*?

    cdef readonly:
        tree_container forest

        # The list of TraceDependency objects in order of tracing priority
        list dependencies

        object model

    ### Planting and clearing ###

    cpdef void clear(self) noexcept
    cdef void trim(self) noexcept

    cdef int _add_internal_cavity_trees(self, list cavities) except -1
    cdef int _handle_overlapping_cavities(self) except -1
    cdef int _add_external_cavity_tree(self, object cav) except -1
    cdef int _add_gauss_tree(self, object gauss) except -1

    cdef int _add_beamsplitter_branch_trees(self) except -1
    cdef int _add_backwards_nonsymm_trees(self) except -1

    cpdef set find_untraversed_nodes(self) noexcept

    ### Searching and attributes ###

    cpdef Py_ssize_t size(self) noexcept
    cpdef bint empty(self) noexcept

    cpdef bint contains(self, object o) noexcept

    # Get a list of trees based on a predicate
    cdef list _get_trees_upred(self, bint (*predicate)(TraceTree))
    cdef list _get_trees_bpred(self, bint (*predicate)(TraceTree, object), object o)

    cpdef list trees_of_dependency(self, object dependency) noexcept
    cdef list get_internal_cavity_trees(self) noexcept
    cdef list get_external_cavity_trees(self) noexcept
    cdef list get_gauss_trees(self) noexcept

    cpdef TraceTree find_tree_from_node(self, object node) noexcept
    cpdef object find_dependency_from_node(self, object node, bint raise_not_found=?) noexcept

    cdef object node_from_name(self, name) noexcept

    ### Changing geometric parameter forest algorithms ###

    cpdef TraceForest make_changing_forest(self) noexcept

    ### Automatic mode mismatch coupling determination ###

    cpdef tuple find_potential_mismatch_couplings(self, TraceForest other=?) noexcept
    cpdef tuple find_intersection_couplings(self, TraceForest other=?) noexcept
    cpdef tuple get_mirror_reflection_couplings(
        self,
        bint ignore_internal_cavities=?,
        list skip_dependencies=?,
    ) noexcept

    ### Drawing ###

    cpdef draw_by_dependency(self) noexcept
    cpdef draw(self) noexcept

    ### Propagating beams ###

    cpdef dict trace_beam(self) noexcept
