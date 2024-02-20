def download(filename: str, progress=None):
    import os
    import zipfile

    import requests

    def _progress(done, size):
        mb = 1024 * 1024
        end = '\n' if done == size else ''
        print(f'\rDownloading {filename} {done / mb:.2f}MB / {size / mb:.2f}MB', end=end)

    if progress is None:
        progress = _progress

    full_path = os.path.normpath(os.path.abspath(os.path.join('downloads', filename)))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    if os.path.isfile(full_path):
        return full_path

    CDN = 'https://f003.backblazeb2.com/file/zengl-data/examples'
    with requests.get(f'{CDN}/{filename}', stream=True) as request:
        if not request.ok:
            raise RuntimeError(request.text)

        done = 0
        size = int(request.headers.get('Content-Length'))
        progress(done, size)

        with open(full_path + '.temp', 'wb') as f:
            for chunk in request.iter_content(chunk_size=None):
                f.write(chunk)
                done += len(chunk)
                progress(done, size)

        os.rename(full_path + '.temp', full_path)

        if full_path.endswith('.zip'):
            with zipfile.ZipFile(full_path) as pack:
                pack.extractall(os.path.splitext(full_path)[0])


def require_gpu():
    try:
        from zengl_extras import cudart
    except ImportError:
        pass

    try:
        from zengl_extras import opencl
    except ImportError:
        pass


def enable_debug():
    import _zengl
    import colorama

    colorama.init()

    def _color_error(err):
        return f'\x1b[31m{err}\x1b[m'

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
            errors[line_number].append(line[match.span()[1] :].strip())
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

    _zengl.compile_error = _compile_error
    _zengl.linker_error = _linker_error


def init(debug=True, gpu=True):
    if debug:
        enable_debug()

    if gpu:
        require_gpu()
