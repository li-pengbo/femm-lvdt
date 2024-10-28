def moving_config(init_position, step_size, steps):
    """
    Define the config for the moving coil.
    Args:
    init_position: float, the initial position of the moving coil.
    step_size: float, the size of the step.
    steps: int, the number of steps
    """
    return {'init_position': init_position, 'step_size': step_size, 'steps': steps}

def params_iter(param1, param2):
    for p1 in param1:
        for p2 in param2:
            yield (p1, p2)
            
# def alu_cyld_iter(outer_diam, inner_diam):
#     pairs = []
#     for od in outer_diam:
#         for id in inner_diam:
#             yield (od, id)

# def magnet_core_iter(diameter, length):
#     for diam in diameter:
#         for len in length:
#             yield (diam, len)

