import _zengl


class _state:
    original_compile_error = _zengl.compile_error
    original_linker_error = _zengl.linker_error
    original_program = _zengl.program
    disable_source_manipulation = False
    force_gles = False
    colors_available = None


def _color_error(err):
    return f'\x1b[31m{err}\x1b[m' if _state.colors_available else f'{err}'


def _compile_error(shader: bytes, shader_type: int, log: bytes):
    import io
    import re
    from collections import defaultdict

    log = log.rstrip(b'\x00').strip().decode().splitlines()
    errors = defaultdict(list)
    for line in log:
        match = re.search(r'\d+:(\d+):', line)
        if not match:
            errors[-1].append(line)
            continue
        line_number = int(match.group(1))
        errors[line_number].append(line[match.span()[1]:].strip())
    res = io.StringIO()
    if shader_type == 0x8B31:
        print('Vertex Shader', file=res)
        print('=============', file=res)
    if shader_type == 0x8B30:
        print('Fragment Shader', file=res)
        print('===============', file=res)
    for i, line in enumerate(shader.decode().split('\n'), 1):
        print(f'{i:4d} | {line}', file=res)
        for error in errors[i]:
            print(f'     | ' + _color_error(error), file=res)
    for error in errors[-1]:
        print(f'     | ' + _color_error(error), file=res)
    if not log:
        print(f'     | ' + _color_error('Cannot find the entrypoint, the compiler log is empty'), file=res)
    raise ValueError(f'GLSL Compile Error:\n\n{res.getvalue()}')


def _linker_error(vertex_shader: bytes, fragment_shader: bytes, log: bytes):
    import io

    print(vertex_shader, fragment_shader)
    res = io.StringIO()
    print(f'log = {log}')
    print('Vertex Shader', file=res)
    print('=============', file=res)
    for i, line in enumerate(vertex_shader.decode().split('\n'), 1):
        print(f'{i:4d} | {line}', file=res)
    print('', file=res)
    print('Fragment Shader', file=res)
    print('===============', file=res)
    for i, line in enumerate(fragment_shader.decode().split('\n'), 1):
        print(f'{i:4d} | {line}', file=res)
    print('', file=res)
    error = log.rstrip(b'\x00').decode().strip()
    print(_color_error(error), file=res)
    raise ValueError(f'GLSL Linker Error:\n\n{res.getvalue()}')


def enable_custom_shader_errors():
    try:
        import colorama
        colorama.init()
        _state.colors_available = True
    except:
        _state.colors_available = False

    _zengl.compile_error = _compile_error
    _zengl.linker_error = _linker_error


def _program(vertex_shader, fragment_shader, layout, includes):
    if _state.disable_source_manipulation:
        if includes:
            raise ValueError('Source manipulation disabled with includes present')
        bindings = []
        for obj in sorted(layout, key=lambda x: x["name"]):
            bindings.extend((obj["name"], obj["binding"]))
        vert = vertex_shader.encode()
        frag = fragment_shader.encode()
        res = (vert, 0x8B31), (frag, 0x8B30), tuple(bindings)

    else:
        res = _state.original_program(vertex_shader, fragment_shader, layout, includes)

    if _state.force_gles:
        if not res[0][0].startswith(b'#version 300 es\n'):
            raise ValueError('the vertex_shader does not strictly starts with "#version 300 es"')

        if not res[1][0].startswith(b'#version 300 es\n'):
            raise ValueError('the fragment_shader does not strictly starts with "#version 300 es"')

    return res


def disable_source_manipulation():
    _state.disable_source_manipulation = True
    _zengl.program = _program


def force_gles():
    _state.force_gles = True
    _zengl.program = _program
