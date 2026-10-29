"""Conservative local audit of owner-selected Claude Code, Codex and Cursor sources."""
from datetime import datetime, timezone
from .json_input import load_json
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
from urllib.parse import unquote

PROVIDERS = {'claude', 'codex', 'cursor'}
PR_STATES = {'OPEN', 'CLOSED', 'MERGED', 'NONE'}
PATH_KEYS = {'cwd', 'workdir', 'file_path', 'path', 'absolute_path', 'directory',
             'working_directory'}
RECENT_SECONDS = 4 * 86400
SIMPLE_COMMANDS = {'cat', 'ls', 'head', 'tail', 'wc', 'stat', 'rg', 'grep',
                   'git', 'pwd', 'readlink', 'realpath'}
SIMPLE_FLAGS = {
    'cat': {'-n', '-b', '-s', '-v', '-E', '-T', '-u'},
    'ls': {'-a', '-A', '-l', '-h', '-d', '-R', '-1', '-F', '-p', '-t', '-r', '-S', '-la', '-al', '-lh'},
    'head': {'-n', '-c'}, 'tail': {'-n', '-c', '-f'},
    'wc': {'-c', '-l', '-w', '-m'}, 'stat': set(),
    'rg': {'-n', '-i', '-l', '-q', '-v', '-c', '-w', '-F', '--line-number', '--files', '--hidden', '--no-ignore'},
    'grep': {'-n', '-i', '-l', '-L', '-q', '-v', '-c', '-s', '-r', '-R', '-w', '-x', '-F', '-E', '-G'},
    'git': {'--short', '-s', '--branch', '-b', '--porcelain', '--porcelain=v1', '--porcelain=v2'},
    'pwd': {'-L', '-P'}, 'readlink': {'-f', '-e', '-m'}, 'realpath': {'-e', '-m', '-s'},
}
PATH_TOOLS = {'Read', 'Write', 'Edit'}


def text_strings(value, decode_arguments=True):
    if isinstance(value, dict):
        for key, child in value.items():
            if decode_arguments and key == 'arguments' and isinstance(child, str):
                try:
                    child = load_json(child)
                except ValueError as exc:
                    raise ValueError('unreadable encoded function arguments') from exc
            yield from text_strings(child, decode_arguments)
    elif isinstance(value, list):
        for child in value:
            yield from text_strings(child, decode_arguments)
    elif isinstance(value, str):
        yield value


def context_paths(value, keys=PATH_KEYS):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in keys:
                if child is not None and not isinstance(child, str):
                    raise ValueError('invalid operation path field')
                if child:
                    yield child
            if key == 'arguments' and isinstance(child, str):
                child = load_json(child)
            yield from context_paths(child, keys)
    elif isinstance(value, list):
        for child in value:
            yield from context_paths(child, keys)


def resolve_operation_path(path, directory):
    target = Path(path)
    return str((target if target.is_absolute() else Path(directory) / target).resolve())


def shell_paths(command):
    if not isinstance(command, str) or not command.strip():
        raise ValueError('missing shell command')
    # Expansions, compound commands and arbitrary programs cannot be resolved
    # reliably from a transcript. Hold coverage rather than guess their paths.
    if any(char in command for char in '$`*?[]{};|&<>\n\r'):
        raise ValueError('unsupported shell expansion or compound command')
    tokens = shlex.split(command)
    program = Path(tokens[0]).name if tokens else None
    if (program not in SIMPLE_COMMANDS or tokens[0] not in
            {program, '/bin/' + program, '/usr/bin/' + program}):
        raise ValueError('unsupported shell program; activity coverage unavailable')
    paths = []
    directory = Path('.')
    index = 1
    git_subcommand = None
    operands_only = False
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not operands_only and program == 'git' and (token == '-C' or token.startswith('-C')):
            if token == '-C':
                if index >= len(tokens):
                    raise ValueError('git -C lacks a directory')
                target = tokens[index]
                index += 1
            else:
                target = token[2:]
            if not target or target.startswith('~'):
                raise ValueError('unsupported git working directory')
            directory = Path(target) if Path(target).is_absolute() else directory / target
            paths.append(str(directory))
            continue
        if not operands_only and token == '--':
            operands_only = True
            continue
        if not operands_only and token.startswith('-'):
            if token not in SIMPLE_FLAGS[program]:
                raise ValueError('unsupported shell option; activity coverage unavailable')
            if program in {'head', 'tail'} and token in {'-n', '-c'}:
                if index >= len(tokens) or not tokens[index].isdigit():
                    raise ValueError('unsupported shell count option')
                index += 1
            continue
        if token.startswith('~'):
            raise ValueError('unsupported shell home expansion')
        if token:
            if Path(tokens[0]).name == 'git' and git_subcommand is None:
                git_subcommand = token
                if git_subcommand != 'status':
                    raise ValueError('unsupported Git program; only literal status operands are scanned')
            paths.append(str(Path(token) if Path(token).is_absolute() else directory / token))
    if Path(tokens[0]).name == 'git' and git_subcommand is None:
        raise ValueError('Git command lacks supported subcommand')
    return paths


def patch_paths(text):
    if not isinstance(text, str):
        raise ValueError('unsupported patch envelope')
    lines = text.splitlines()
    if not lines or lines[0] != '*** Begin Patch' or lines[-1] != '*** End Patch':
        raise ValueError('unsupported patch envelope')
    paths, mode, hunk, body, moved, eof = [], None, False, False, False, False
    for line in lines[1:-1]:
        match = re.fullmatch(r'\*\*\* (Add File|Update File|Delete File): (.+)', line)
        if match:
            if mode == 'Update File' and (not hunk or not body):
                raise ValueError('patch update lacks a supported hunk')
            mode, path = match.groups()
            if not path.strip():
                raise ValueError('patch operation lacks a path')
            paths.append(path)
            hunk = body = moved = eof = False
        elif line.startswith('*** Move to: '):
            if mode != 'Update File' or hunk or moved or not line[13:].strip():
                raise ValueError('unsupported patch move directive')
            paths.append(line[13:])
            moved = True
        elif mode == 'Update File' and (line == '@@' or line.startswith('@@ ')):
            if eof or hunk and not body:
                raise ValueError('patch hunk follows end-of-file marker')
            hunk = True
            body = False
        elif mode == 'Update File' and line == '*** End of File' and hunk and body and not eof:
            eof = True
        elif mode == 'Add File' and line.startswith('+'):
            continue
        elif mode == 'Update File' and hunk and not eof and line.startswith((' ', '+', '-')):
            body = True
        else:
            raise ValueError('unknown or malformed patch directive/content')
    if not paths:
        raise ValueError('patch has no operation paths')
    if mode == 'Update File' and (not hunk or not body):
        raise ValueError('patch update lacks a supported hunk')
    return paths


def hint_paths(value, inherited=None):
    """Conservative path hints only; never evidence of complete parsing."""
    if isinstance(value, dict):
        try:
            cwd = local_context(value, inherited)
        except ValueError:
            cwd = None
        for key, child in value.items():
            if key == 'arguments' and isinstance(child, str):
                try:
                    child = load_json(child)
                except ValueError:
                    pass
            if key in PATH_KEYS and isinstance(child, str) and child and (Path(child).is_absolute() or cwd):
                yield resolve_operation_path(child, cwd)
            yield from hint_paths(child, cwd)
    elif isinstance(value, list):
        for child in value:
            yield from hint_paths(child, inherited)
    elif isinstance(value, str):
        for path in re.findall(r'^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$', value, re.M):
            if Path(path).is_absolute() or inherited:
                yield resolve_operation_path(path, inherited)


def local_context(value, inherited):
    result = inherited
    for key in ('cwd', 'workdir'):
        if key not in value or value[key] is None:
            continue
        path = value[key]
        if not isinstance(path, str) or not path:
            raise ValueError('invalid operation working directory')
        if not Path(path).is_absolute() and not result:
            raise ValueError('relative working directory lacks parent context')
        result = resolve_operation_path(path, result)
    return result


def validate_fields(args, required, optional):
    if set(args) - set(required) - set(optional) - {'cwd', 'workdir'}:
        raise ValueError('unknown native tool argument fields')
    for key, expected in {**required, **optional}.items():
        if key not in args:
            if key in required:
                raise ValueError('missing native tool argument: ' + key)
            continue
        value = args[key]
        if type(value) is not expected:
            raise ValueError('malformed native tool argument: ' + key)
        if key in {'file_path', 'command', 'cmd'} and not value.strip():
            raise ValueError('empty native tool argument: ' + key)
        if expected is int and value <= 0:
            raise ValueError('nonpositive native tool argument: ' + key)
        if expected is list and not all(isinstance(item, str) for item in value):
            raise ValueError('malformed native tool argument list: ' + key)
        if key == 'sandbox_permissions' and value not in {'use_default', 'require_escalated'}:
            raise ValueError('unknown sandbox permission metadata')
        if key == 'shell' and value not in {'/bin/sh', '/bin/bash', '/bin/zsh', 'sh', 'bash', 'zsh'}:
            raise ValueError('unsupported shell metadata')


def operation_paths(value, inherited=None):
    """Resolve each native operation in its own enclosing context."""
    if isinstance(value, list):
        for child in value:
            yield from operation_paths(child, inherited)
        return
    if not isinstance(value, dict):
        return
    cwd = local_context(value, inherited)
    kind = value.get('type')
    if kind in {'tool_call', 'tool-call'} or any(key in value for key in ('tool_calls', 'function_call')):
        raise ValueError('unsupported native tool envelope')
    if kind not in {'function_call', 'custom_tool_call', 'tool_use'}:
        for child in value.values():
            yield from operation_paths(child, cwd)
        return
    name = value.get('name')
    if not isinstance(name, str):
        raise ValueError('tool operation lacks a name')
    name = name.rsplit('.', 1)[-1]
    if kind == 'function_call':
        if not isinstance(value.get('arguments'), str):
            raise ValueError('function call lacks encoded arguments')
        args = load_json(value['arguments'])
        if not isinstance(args, dict):
            raise ValueError('function arguments must decode to an object')
    elif kind == 'tool_use':
        args = value.get('input')
        if not isinstance(args, dict):
            raise ValueError('malformed Claude tool operation')
    else:
        args = {'input': value.get('input')}
        if name != 'apply_patch':
            raise ValueError('unsupported custom tool operation')
    cwd = local_context(args, cwd)
    if name in {'Bash', 'exec_command'}:
        if name == 'Bash':
            validate_fields(args, {'command': str}, {'timeout': int, 'description': str,
                            'run_in_background': bool, 'dangerouslyDisableSandbox': bool})
        else:
            validate_fields(args, {'cmd': str}, {'yield_time_ms': int, 'max_output_tokens': int,
                            'sandbox_permissions': str, 'justification': str, 'prefix_rule': list,
                            'shell': str, 'login': bool, 'tty': bool})
        paths = shell_paths(args.get('command') if name == 'Bash' else args.get('cmd'))
    elif name == 'apply_patch':
        if set(args) - {'patch', 'input', 'cwd', 'workdir'} or ('patch' in args and 'input' in args):
            raise ValueError('unknown or ambiguous patch arguments')
        paths = patch_paths(args.get('patch') or args.get('input'))
    elif kind == 'tool_use' and name in PATH_TOOLS:
        required = {'file_path': str}
        optional = {}
        if name == 'Read':
            optional = {'offset': int, 'limit': int, 'pages': str}
        elif name == 'Write':
            required['content'] = str
        else:
            required.update(old_string=str, new_string=str)
            optional = {'replace_all': bool}
        validate_fields(args, required, optional)
        paths = [args['file_path']]
    else:
        raise ValueError('unsupported native operation')
    if not cwd and not any(Path(path).is_absolute() for path in paths):
        raise ValueError('native operation lacks absolute working-directory/path context')
    if cwd:
        yield cwd
    for path in paths:
        if not Path(path).is_absolute() and not cwd:
            raise ValueError('relative operation path lacks working-directory context')
        yield resolve_operation_path(path, cwd)


def cursor_operation_paths(block):
    """Resolve one Cursor tool operation into the paths it touched.

    Cursor's own tool set names its file argument `path`, its write payload
    `contents`, and its shell argument `command` with an optional
    `working_directory`. Unlike Claude Code, Cursor records no record-level
    working directory, so a relative path cannot be resolved and holds
    coverage rather than being guessed.
    """
    name = block.get('name')
    args = block.get('input')
    if not isinstance(name, str) or not isinstance(args, dict):
        raise ValueError('malformed Cursor tool operation')
    name = name.rsplit('.', 1)[-1]
    cwd = None
    if 'working_directory' in args:
        directory = args['working_directory']
        if not isinstance(directory, str) or not directory.strip():
            raise ValueError('invalid operation working directory')
        if not Path(directory).is_absolute():
            raise ValueError('relative working directory lacks parent context')
        cwd = str(Path(directory).resolve())
    if name == 'Shell':
        allowed = {'command', 'description', 'working_directory', 'block_until_ms',
                   'required_permissions', 'request_smart_mode_approval',
                   'smart_mode_block_reason'}
        if set(args) - allowed:
            raise ValueError('unknown native tool argument fields')
        command = args.get('command')
        if not isinstance(command, str) or not command.strip():
            raise ValueError('missing shell command')
        paths = shell_paths(command)
    elif name in {'Read', 'Write', 'Edit', 'StrReplace'}:
        allowed = {'path', 'contents', 'old_string', 'new_string', 'offset',
                   'limit', 'replace_all', 'working_directory'}
        if set(args) - allowed:
            raise ValueError('unknown native tool argument fields')
        path = args.get('path')
        if not isinstance(path, str) or not path.strip():
            raise ValueError('missing native tool argument: path')
        paths = [path]
    elif name == 'Grep':
        allowed = {'pattern', 'path', 'output_mode', 'head_limit', 'offset',
                   '-A', '-B', '-C', '-i', 'glob', 'type'}
        if set(args) - allowed:
            raise ValueError('unknown native tool argument fields')
        path = args.get('path')
        if path is not None and (not isinstance(path, str) or not path.strip()):
            raise ValueError('invalid native tool argument: path')
        paths = [path] if path else []
    elif name == 'Glob':
        allowed = {'glob_pattern', 'target_directory'}
        if set(args) - allowed:
            raise ValueError('unknown native tool argument fields')
        directory = args.get('target_directory')
        if directory is not None and (not isinstance(directory, str) or not directory.strip()):
            raise ValueError('invalid native tool argument: target_directory')
        paths = [directory] if directory else []
    else:
        raise ValueError('unsupported native operation')
    if cwd:
        yield cwd
    for path in paths:
        if not Path(path).is_absolute():
            if not cwd:
                raise ValueError('relative operation path lacks working-directory context')
            path = str(Path(cwd) / path)
        yield str(Path(path).resolve())


def mentions_worktree(value, worktree, decode_arguments=True):
    variants = {str(worktree)}
    # macOS Git canonicalizes /tmp and /var to /private/...; native records may
    # retain those system aliases. Do not miss activity because of spelling.
    for alias in ('/tmp', '/var'):
        canonical = str(Path(alias).resolve())
        if str(worktree).startswith(canonical + '/'):
            variants.add(alias + str(worktree)[len(canonical):])
    home = Path.home().resolve()
    canonical = worktree.resolve()
    for ancestor in (canonical, *canonical.parents):
        try:
            if ancestor == home or ancestor.samefile(home):
                relative = canonical.relative_to(ancestor)
                variants.add('~' if relative == Path('.') else '~/' + relative.as_posix())
                break
        except FileNotFoundError:
            continue
    patterns = [(re.compile('(' + re.escape(path) + r')(?![\w-])', re.IGNORECASE), path)
                for path in variants]
    for text in text_strings(value, decode_arguments):
        representations = [text]
        for _ in range(3):
            decoded = unquote(representations[-1], errors='strict')
            if decoded == representations[-1]:
                break
            representations.append(decoded)
        if unquote(representations[-1], errors='strict') != representations[-1]:
            raise ValueError('path encoding exceeds supported depth')
        for representation in representations:
            if re.search(r'~[^/\s]+/', representation):
                raise ValueError('other-user home path cannot be resolved')
            for pattern, path in patterns:
                for match in pattern.finditer(representation):
                    if match[1] == path:
                        return True
                    candidate = (home / match[1][2:] if match[1].startswith('~/') else Path(match[1]))
                    try:
                        if candidate.samefile(worktree):
                            return True
                    except FileNotFoundError:
                        pass
    return False


def contains_worktree(scope, worktree):
    """Parent scopes use filesystem identity when letter case differs."""
    for ancestor in (worktree, *worktree.parents):
        if scope == ancestor:
            return True
        try:
            if scope.samefile(ancestor):
                return True
        except FileNotFoundError:
            continue
    return False


def timestamp(record, fallback):
    value = record.get('timestamp')
    if value is None:
        return fallback, 'file-mtime-conservative'
    if isinstance(value, bool):
        raise ValueError('invalid transcript timestamp')
    if isinstance(value, (int, float)):
        result = float(value)
    elif isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError('timestamp lacks timezone')
        result = parsed.timestamp()
    else:
        raise ValueError('invalid transcript timestamp')
    if not (0 <= result < 253402300800):
        raise ValueError('invalid transcript timestamp')
    return result, 'record-timestamp'


def text_leaves(value, kinds):
    return isinstance(value, list) and all(
        isinstance(item, dict) and not (set(item) - {'type', 'text'})
        and item.get('type') in kinds and isinstance(item.get('text'), str)
        for item in value)


def codex_payload(payload):
    if not isinstance(payload, dict):
        return False
    kind = payload.get('type')
    if kind == 'message':
        return (not (set(payload) - {'type', 'id', 'role', 'content', 'phase'})
                and all(payload.get(key) is None or isinstance(payload[key], str)
                        for key in ('id', 'phase'))
                and payload.get('role') in {'user', 'assistant', 'system', 'developer'}
                and text_leaves(payload.get('content'), {'input_text', 'output_text'}))
    if kind in {'function_call', 'custom_tool_call'}:
        # The operation decoder validates tool names, arguments and context.
        operand = 'arguments' if kind == 'function_call' else 'input'
        return (not (set(payload) - {'type', 'name', operand, 'id', 'call_id', 'status', 'cwd', 'workdir'})
                and all(payload.get(key) is None or isinstance(payload[key], str)
                        for key in ('id', 'call_id', 'status')))
    if kind in {'function_call_output', 'custom_tool_call_output'}:
        return (not (set(payload) - {'type', 'call_id', 'output', 'cwd', 'workdir'})
                and isinstance(payload.get('call_id'), str) and bool(payload['call_id'])
                and isinstance(payload.get('output'), str))
    if kind == 'reasoning':
        return (not (set(payload) - {'type', 'id', 'summary', 'content', 'encrypted_content'})
                and (payload.get('id') is None or isinstance(payload['id'], str))
                and text_leaves(payload.get('summary'), {'summary_text'})
                and (payload.get('content') is None
                     or text_leaves(payload['content'], {'reasoning_text'}))
                and payload.get('encrypted_content') is None)
    return False


def codex_event(payload):
    if not isinstance(payload, dict):
        return False
    kind = payload.get('type')
    field = {'agent_message': 'message', 'agent_reasoning': 'text',
             'user_message': 'message'}.get(kind)
    if field is None or not isinstance(payload.get(field), str):
        return False
    # Only textual events have reviewed schemas. Images and other event formats
    # cannot supply complete activity coverage through this bounded adapter.
    return (not (set(payload) - {'type', field, 'images', 'local_images', 'text_elements'})
            and all(payload.get(key, []) == []
                    for key in ('images', 'local_images', 'text_elements')))


def codex_context(payload):
    if not isinstance(payload, dict):
        return False
    fields = {'cwd', 'id', 'turn_id', 'timestamp', 'originator', 'cli_version',
              'model_provider', 'source', 'model', 'effort', 'summary',
              'approval_policy', 'instructions'}
    if set(payload) - fields - {'git'}:
        return False
    directory = payload.get('cwd')
    if not isinstance(directory, str) or not Path(directory).is_absolute():
        return False
    if any(value is not None and not isinstance(value, str)
           for key, value in payload.items() if key in fields):
        return False
    metadata = payload.get('git')
    return (metadata is None or isinstance(metadata, dict)
            and not (set(metadata) - {'branch', 'commit_hash', 'repository_url'})
            and all(value is None or isinstance(value, str) for value in metadata.values()))


def cursor_record(row):
    """Validate one Cursor agent-transcript record.

    Cursor's own store writes a `{"role", "message"}` envelope whose content
    blocks are `text` or `tool_use`, and closes a turn with a `turn_ended`
    record. Observed records carry no `cwd` and no record-level timestamp, so
    recency falls back to file mtime and only absolute paths resolve.
    """
    if set(row) - {'role', 'message', 'type', 'status', 'error'}:
        return False
    if 'type' in row:
        # A turn marker. Only the observed two shapes are accepted.
        if row.get('type') != 'turn_ended':
            return False
        if set(row) - {'type', 'status', 'error'}:
            return False
        if row.get('status') not in {'success', 'error'}:
            return False
        if 'error' in row and not isinstance(row['error'], str):
            return False
        return True
    if set(row) != {'role', 'message'}:
        return False
    if row.get('role') not in {'user', 'assistant'}:
        return False
    message = row.get('message')
    if not isinstance(message, dict) or set(message) != {'content'}:
        return False
    content = message.get('content')
    if not isinstance(content, list) or not content:
        return False
    for block in content:
        if not isinstance(block, dict):
            return False
        kind = block.get('type')
        if kind == 'text':
            if set(block) != {'type', 'text'} or not isinstance(block['text'], str):
                return False
        elif kind == 'tool_use':
            if set(block) - {'type', 'name', 'input'}:
                return False
            if not isinstance(block.get('name'), str) or not block['name'].strip():
                return False
            if not isinstance(block.get('input'), dict):
                return False
        else:
            # Any other block kind is an unexamined schema, so it holds coverage.
            return False
    return True


def cursor_operations(row):
    """Yield Cursor tool operations in their own decoded input shape.

    Cursor writes tool inputs as decoded objects rather than encoded argument
    strings, so the Claude `tool_use` envelope is reused with the Cursor tool
    names the host actually exposes.
    """
    message = row.get('message')
    if not isinstance(message, dict):
        return
    for block in message.get('content', []):
        if isinstance(block, dict) and block.get('type') == 'tool_use':
            yield block


def claude_message(message):
    if not isinstance(message, dict):
        return False
    fields = {'id', 'type', 'role', 'model', 'stop_reason', 'stop_sequence'}
    if set(message) - fields - {'content', 'usage'}:
        return False
    if any(value is not None and not isinstance(value, str)
           for key, value in message.items() if key in fields):
        return False
    usage = message.get('usage')
    if usage is not None:
        counts = {'input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens'}
        if (not isinstance(usage, dict) or set(usage) - counts
                or any(type(value) is not int or value < 0 for value in usage.values())):
            return False
    return isinstance(message.get('content'), (str, list))


def claude_envelope(row):
    fields = {'cwd', 'uuid', 'parentUuid', 'userType', 'sessionId', 'version',
              'gitBranch', 'slug', 'requestId', 'agentId', 'sourceToolAssistantUUID',
              'sourceToolUseID', 'summary', 'leafUuid'}
    flags = {'isSidechain', 'isApiErrorMessage', 'isMeta', 'isCompactSummary'}
    return (not (set(row) - fields - flags - {'type', 'timestamp', 'message'})
            and all(value is None or isinstance(value, str)
                    for key, value in row.items() if key in fields)
            and all(type(value) is bool for key, value in row.items() if key in flags))


def records(provider, path, body, mtime):
    if path.suffix != '.jsonl':
        raise ValueError('unsupported transcript format')
    for line in body.splitlines():
        if not line.strip():
            continue
        row = load_json(line)
        if not isinstance(row, dict):
            raise ValueError('transcript record is not an object')
        kind = row.get('type')
        if provider == 'claude':
            if not claude_envelope(row):
                raise ValueError('unsupported Claude envelope metadata')
            supported = (kind == 'summary' and isinstance(row.get('summary'), str)
                         and not (set(row) - {'type', 'summary', 'timestamp', 'cwd',
                                            'leafUuid', 'uuid', 'parentUuid'}))
            if kind in {'user', 'assistant'}:
                supported = claude_message(row.get('message'))
                content = row['message'].get('content') if isinstance(row.get('message'), dict) else None
                if supported and isinstance(content, list):
                    supported = all(isinstance(item, dict) and item.get('type') in
                                    {'text', 'tool_use', 'tool_result', 'thinking'}
                                    for item in content)
                    if supported:
                        for block in content:
                            block_type = block['type']
                            if block_type == 'text':
                                supported = supported and text_leaves([block], {'text'})
                            elif block_type == 'thinking':
                                supported = (supported and isinstance(block.get('thinking'), str)
                                             and not (set(block) - {'type', 'thinking', 'signature'})
                                             and ('signature' not in block or isinstance(block['signature'], str)))
                            elif block_type == 'tool_result':
                                result = block.get('content')
                                # Result arrays are bounded to nonoperative text
                                # leaves. Opaque or nested block schemas hold.
                                valid_result = isinstance(result, str) or text_leaves(result, {'text'})
                                supported = (supported and isinstance(block.get('tool_use_id'), str)
                                             and bool(block['tool_use_id']) and valid_result
                                             and not (set(block) - {'type', 'tool_use_id', 'content', 'is_error', 'cwd', 'workdir'})
                                             and ('is_error' not in block or type(block['is_error']) is bool))
                            elif block_type == 'tool_use':
                                supported = (supported and not (set(block) - {'type', 'id', 'name', 'input', 'cwd', 'workdir'})
                                             and ('id' not in block or isinstance(block['id'], str)))
        elif provider == 'codex':
            if set(row) - {'type', 'timestamp', 'payload'}:
                raise ValueError('unsupported Codex envelope metadata')
            supported = kind in {'session_meta', 'response_item', 'event_msg', 'turn_context'} and isinstance(row.get('payload'), dict)
            if kind in {'session_meta', 'turn_context'}:
                supported = codex_context(row.get('payload'))
            if kind == 'response_item':
                supported = codex_payload(row.get('payload'))
            if kind == 'event_msg':
                supported = codex_event(row.get('payload'))
        elif provider == 'cursor':
            supported = cursor_record(row)
        else:
            supported = False
        if not supported:
            raise ValueError('unsupported ' + provider + ' record envelope')
        ts, origin = timestamp(row, mtime)
        yield row, ts, origin


def selected_files(source):
    if not isinstance(source, dict):
        raise ValueError('source entry must be an object')
    if set(source) - {'provider', 'root', 'files', 'authorization', 'coverage'}:
        raise ValueError('unknown source fields')
    if source.get('provider') not in PROVIDERS or not isinstance(source.get('authorization'), str) or not source['authorization'].strip():
        raise ValueError('provider and explicit source authorization required')
    if ('root' in source) == ('files' in source):
        raise ValueError('select one source root or explicit file list')
    if 'root' in source:
        root = Path(source['root'])
        if not root.is_absolute() or root.is_symlink() or not root.is_dir():
            raise ValueError('source root unavailable or unsafe')
        files = []
        def failed(exc):
            raise exc
        for directory, dirs, names in os.walk(root, followlinks=False, onerror=failed):
            for name in dirs + names:
                if (Path(directory) / name).is_symlink():
                    raise ValueError('symlink in selected transcript root')
            files.extend(Path(directory) / name for name in names)
        if not files:
            raise ValueError('selected source contains no transcript files')
        return sorted(files)
    if not isinstance(source['files'], list) or not all(isinstance(p, str) for p in source['files']):
        raise ValueError('source files must be an explicit absolute list')
    files = [Path(p) for p in source['files']]
    if not files:
        raise ValueError('selected source contains no transcript files')
    if any(not p.is_absolute() for p in files):
        raise ValueError('source files must be absolute')
    return files


def read_selected(path):
    if any(parent.is_symlink() for parent in [path, *path.parents]):
        raise ValueError('symlink in selected transcript path')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'r', encoding='utf-8') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > 64 * 1024 * 1024:
            raise ValueError('source must be a regular transcript of at most 64 MiB')
        body = stream.read()
        after = os.fstat(stream.fileno())
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError('transcript changed during scan')
        return body, after.st_mtime


def scan(manifest, worktrees, now):
    activity = {str(p): [] for p in worktrees}
    reports = []
    complete = manifest.get('coverage') == 'complete'
    sources = manifest.get('sources')
    if not isinstance(sources, list) or not sources:
        return activity, [{'coverage': 'unavailable', 'error': 'no authorized transcript sources'}], False
    supported_sources = 0
    for source in sources:
        report = {'provider': source.get('provider') if isinstance(source, dict) else None,
                  'coverage': 'unavailable', 'files_scanned': 0}
        reports.append(report)
        if isinstance(source, dict) and isinstance(source.get('provider'), str) and source['provider'] not in PROVIDERS:
            # An unsupported host contributes no evidence and no coverage, and
            # its transcripts are never read.
            report.update(coverage='ignored', reason='unsupported host; contributes no evidence')
            continue
        try:
            files = selected_files(source)
            supported_sources += 1
            unavailable = False
            for path in files:
                try:
                    body, mtime = read_selected(path)
                except (ValueError, OSError, UnicodeError) as exc:
                    report['error'] = str(exc)
                    unavailable = True
                    continue
                if not body.strip():
                    report['error'] = 'selected transcript contains no records'
                    unavailable = True
                cwd = None
                for line in body.splitlines():
                    if not line.strip():
                        continue
                    row, basis = line, 'validated-record'
                    try:
                        row, ts, origin = next(records(source['provider'], path, line, mtime))
                        list(text_strings(row))
                        next_cwd = cwd
                        if source['provider'] == 'claude' and row.get('cwd'):
                            next_cwd = row['cwd']
                        if source['provider'] == 'codex' and row['type'] in {'session_meta', 'turn_context'}:
                            next_cwd = row['payload']['cwd']
                        if next_cwd and (not isinstance(next_cwd, str) or not Path(next_cwd).is_absolute()):
                            raise ValueError('invalid session working directory')
                        if source['provider'] == 'cursor':
                            normalized = []
                            for block in cursor_operations(row):
                                normalized.extend(cursor_operation_paths(block))
                        else:
                            normalized = list(operation_paths(row, next_cwd))
                        for location in context_paths(row):
                            if Path(location).is_absolute():
                                normalized.append(str(Path(location).resolve()))
                        cwd = next_cwd
                    except (ValueError, OSError, TypeError, KeyError, UnicodeError) as exc:
                        report['error'] = str(exc)
                        unavailable = True
                        if isinstance(row, str):
                            try:
                                row = load_json(row)
                            except ValueError:
                                pass
                        try:
                            normalized = list(hint_paths(row, cwd))
                        except (ValueError, OSError, TypeError):
                            normalized = []
                        cwd = None  # Never inherit uncertain context across an opaque record.
                        ts, origin, basis = mtime, 'file-mtime-unparsed-conservative', 'unparsed-path-hint'
                    for wt in worktrees:
                        hit = (mentions_worktree(row, wt, basis == 'validated-record') or mentions_worktree(normalized, wt) or
                               any(contains_worktree(Path(p), wt) for p in normalized) or
                               bool(cwd and mentions_worktree({'cwd': str(Path(cwd).resolve())}, wt)))
                        if hit:
                            activity[str(wt)].append({'provider': source['provider'], 'source': str(path),
                                                     'timestamp': ts, 'timestamp_basis': origin,
                                                     'recent': now - ts <= RECENT_SECONDS, 'evidence_basis': basis})
                report['files_scanned'] += 1
            if not unavailable:
                report['coverage'] = 'complete' if source.get('coverage') == 'complete' else 'partial'
        except (ValueError, OSError, TypeError, KeyError, UnicodeError) as exc:
            report['error'] = str(exc)
        complete = complete and report['coverage'] == 'complete'
    return activity, reports, complete and supported_sources > 0


def git(repo, *args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
    return subprocess.run(['git', '-c', 'core.fsmonitor=false', '-C', str(repo), *args],
                          env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def classify(dirty, pr, merged, coverage, recent):
    if dirty.startswith('wip:'):
        return 'hold-wip'
    if pr == 'OPEN':
        return 'hold-open-pr'
    if not coverage:
        return 'hold-activity-unavailable'
    if pr == 'UNKNOWN' or merged is None or dirty == 'unavailable':
        return 'hold-metadata-unavailable'
    if recent:
        return 'verify-recent-chat'
    if dirty != 'clean':
        return 'review-scratch' if dirty.startswith('scratch:') else 'hold-metadata-unavailable'
    return 'verify-active-pinned' if merged or pr == 'MERGED' else 'review'


def audit(repo, source_path, pr_path=None, base='refs/remotes/origin/main'):
    listing = git(repo, 'worktree', 'list', '--porcelain', '-z')
    if listing.returncode:
        raise ValueError('consumer worktree list unavailable')
    trees = []
    for block in listing.stdout.decode().split('\0\0'):
        fields = dict(line.split(' ', 1) for line in block.split('\0') if ' ' in line)
        if 'worktree' in fields:
            trees.append((Path(fields['worktree']), fields.get('branch', '').removeprefix('refs/heads/')))
    paths = [p for p, _ in trees]
    try:
        manifest = load_json(source_path.read_text())
        if not isinstance(manifest, dict) or set(manifest) != {'schema_version', 'coverage', 'sources'} or manifest['schema_version'] != 1:
            raise ValueError('invalid source manifest')
        hits, reports, complete = scan(manifest, paths, datetime.now(timezone.utc).timestamp())
    except (ValueError, OSError, TypeError, UnicodeError) as exc:
        hits, reports, complete = {str(p): [] for p in paths}, [{'coverage': 'unavailable', 'error': str(exc)}], False
    prs = {}
    pr_error = 'PR snapshot not supplied'
    if pr_path:
        try:
            snapshot = load_json(pr_path.read_text())
            if (not isinstance(snapshot, dict) or set(snapshot) != {'coverage', 'states'}
                    or snapshot['coverage'] != 'complete' or not isinstance(snapshot['states'], dict)
                    or any(not isinstance(state, str) or state not in PR_STATES
                           for state in snapshot['states'].values())):
                raise ValueError('invalid or incomplete PR snapshot')
            prs = snapshot['states']
            pr_error = None
        except (ValueError, OSError, KeyError, TypeError) as exc:
            pr_error = str(exc)
    rows = []
    for index, (wt, branch) in enumerate(trees):
        status = git(wt, 'status', '--porcelain=v1', '-z', '--untracked-files=all')
        entries = [e for e in status.stdout.split(b'\0') if e]
        tracked = sum(not e.startswith(b'?? ') for e in entries)
        dirty = ('unavailable' if status.returncode else 'clean' if not entries else
                 f'wip:{tracked}' if tracked else f'scratch:{len(entries)}')
        merge = git(wt, 'merge-base', '--is-ancestor', 'HEAD', base)
        merged = None if merge.returncode not in (0, 1) else merge.returncode == 0
        known_states = {prs[key] for key in (branch, 'worktree:' + str(wt)) if key and key in prs}
        pr = next(iter(known_states)) if len(known_states) == 1 else 'UNKNOWN'
        metadata_errors = ([] if index == 0 else
                           (['pr-state-unknown'] if pr == 'UNKNOWN' else []) +
                           (['merge-state-unknown'] if merged is None else []) +
                           (['git-status-unavailable'] if dirty == 'unavailable' else []))
        evidence = hits[str(wt)]
        recent = any(row['recent'] for row in evidence)
        rows.append({'worktree': str(wt), 'branch': branch, 'main_worktree': index == 0,
                     'dirty': dirty, 'merged_into_local_base': merged, 'pr': pr,
                     'metadata_coverage': 'not-required' if index == 0 else 'unavailable' if metadata_errors else 'complete',
                     'metadata_errors': metadata_errors,
                     'activity': 'recent' if recent else 'no-recent-evidence' if complete else 'unavailable',
                     'evidence': evidence, 'bucket': 'hold-main-worktree' if index == 0 else
                     classify(dirty, pr, merged, complete, recent),
                     'active_pinned_gate': 'required-separately', 'deletion_authorized': False})
    metadata_complete = all(not row['metadata_errors'] for row in rows)
    return {'schema_version': 1, 'coverage': 'complete' if complete else 'unavailable',
            'metadata_coverage': 'complete' if metadata_complete else 'unavailable',
            'audit_status': 'complete' if complete and metadata_complete else 'hold',
            'pr_snapshot_error': pr_error,
            'sources': reports, 'local_base': base, 'base_freshness': 'not-fetched',
            'network_used': False, 'deletion_performed': False, 'worktrees': rows}
