# wzy_bt_print/__init__.py

def print_tree_helper(root, curr_index=0, index=False, delimiter='-'):
    if root is None:
        return '', 0, 0, 0

    line1 = []
    line2 = []
    try:
        node_repr = str(root.data)
    except:
        node_repr = str(root.val)

    if index:
        node_repr = f'{curr_index}{delimiter}{node_repr}'
    new_root_width = gap_size = len(node_repr)
    
    l_box, l_box_width, l_root_start, l_root_end = \
        print_tree_helper(root.left, 2 * curr_index + 1, index, delimiter)
    r_box, r_box_width, r_root_start, r_root_end = \
        print_tree_helper(root.right, 2 * curr_index + 2, index, delimiter)

    if l_box_width > 0:
        l_root = (l_root_start + l_root_end) // 2 + 1
        line1.append(' ' * (l_root + 1))
        line1.append('_' * (l_box_width - l_root))
        line2.append(' ' * l_root + '/')
        line2.append(' ' * (l_box_width - l_root))
        new_root_start = l_box_width + 1
        gap_size += 1
    else:
        new_root_start = 0

    line1.append(node_repr)
    line2.append(' ' * new_root_width)

    if r_box_width > 0:
        r_root = (r_root_start + r_root_end) // 2
        line1.append('_' * r_root)
        line1.append(' ' * (r_box_width - r_root + 1))
        line2.append(' ' * r_root + '\\')
        line2.append(' ' * (r_box_width - r_root))
        gap_size += 1
    new_root_end = new_root_start + new_root_width - 1

    gap = ' ' * gap_size
    new_box = [''.join(line1), ''.join(line2)]
    for i in range(max(len(l_box), len(r_box))):
        l_line = l_box[i] if i < len(l_box) else ' ' * l_box_width
        r_line = r_box[i] if i < len(r_box) else ' ' * r_box_width
        new_box.append(l_line + gap + r_line)

    return new_box, len(new_box[0]), new_root_start, new_root_end

def print_tree(root):
    '''
    Input: a root node
    Output: a vertical binary tree printout,
            without rotating your stiff neck :)
    - 4 Apr 2024, Dr.Z.Wang, at Singapore
    '''
    lines, *_ = print_tree_helper(root)
    for line in lines:
        print(line)

