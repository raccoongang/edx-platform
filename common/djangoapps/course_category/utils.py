def add_nodes(nodes, prefix, course_category_options):
    """
    This is a recursive function for traversing tree nodes.
    This is a procedural function that takes a list as an argument 'course_category_options' and adds elements to it.
    This list will be used from an external context.
    This behavior is normal :-)
    """

    assert isinstance(course_category_options, list), "Argument 'course_category_options' must be a list."
    for node in nodes:
        path = prefix and u'{}/{}'.format(prefix, node.name) or node.name
        course_category_options.append((node.id, path))
        if not node.is_leaf_node():
            add_nodes(node.children.all(), path, course_category_options)
