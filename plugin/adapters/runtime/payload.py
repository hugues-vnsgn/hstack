"""Resolve the approved installed payload, independent of consumer Git refs."""
import hashlib
from .json_input import load_json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shlex
import stat

PIN = 'hstack-native-v1'
ANCHORS = {'adapters/runtime/payload.json', 'adapters/runtime/payload.py', 'adapters/host_tools.py'}
# Created after install by the bundled Bun bootstrap or the host OS; never workflow inputs.
GENERATED_TREES = {'skills/hugues-mode/scripts/node_modules'}
HOST_METADATA = {'.DS_Store'}
# A run of path characters names a file when it holds a slash or follows a Git revision's colon;
# a bare SKILL.md in prose names none.
PATH_RUN = re.compile(r'(:?)([\w./-]+)')
MANIFEST_SHA256 = '79c8e1d4895931a347438e64a0872a4a44f0bc5b981f812f9c8aba1dc675cc6a'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_file(root, relative):
    parts = PurePosixPath(relative).parts
    if not parts or '..' in parts or '\\' in relative or PurePosixPath(relative).is_absolute():
        raise ValueError('unsafe payload path')
    path = root
    for part in parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('symlink in installed payload')
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError('missing installed payload file: ' + relative)
    return path


def mode_matches(actual, approved):
    # Installs differ in umask and archive modes; only world-write and the executable bit matter.
    return not actual & stat.S_IWOTH and bool(actual & stat.S_IXUSR) == bool(approved & stat.S_IXUSR)


def is_skill_body(path):
    # . and .. move between skill folders, and case-insensitive hosts open SKILL.MD as SKILL.md.
    return posixpath.basename(posixpath.normpath(path)).lower() == 'skill.md'


def names_skill_body(text):
    unquoted = re.sub(r'[\'"`\\]', '', text)
    return any((revision or '/' in run) and is_skill_body(run)
               for revision, run in PATH_RUN.findall(unquoted))


def names_skill_directory(text):
    unquoted = re.sub(r"['\"\\]", '', text)
    return bool(re.search(r'(?<![\w.-])skills(?=/|$|[\s;|&<>()$`{}\[\]*?~])', unquoted, re.I))


def names_skill_token(text):
    unquoted = re.sub(r"['\"\\]", '', text)
    return bool(re.search(r'(?<![\w.-])skill\.md(?![\w.-])', unquoted, re.I))


def reject_container_code(line):
    # Container blocks are outside this helper's Markdown subset. Do not let
    # their fences or indentation turn executable code into unchecked prose.
    content = line
    container = False
    while True:
        marker = re.match(r'^ {0,3}(?:>[ \t]?|(?:[-+*]|[0-9]{1,9}[.)])[ \t])', content)
        if not marker:
            break
        container = True
        content = content[marker.end():]
    if container and re.match(r'^(?: {0,3}(?:`{3,}|~{3,})| {4}|\t)', content):
        raise ValueError('use top-level code blocks in Markdown plans')


def unreadable(error):
    raise error


def verify(root):
    for name in ANCHORS:
        if not mode_matches(stat.S_IMODE(checked_file(root, name).stat().st_mode), 0o644):
            raise ValueError('installed trust anchor mode drift: ' + name)
    manifest = checked_file(root, 'adapters/runtime/payload.json')
    if digest(manifest) != MANIFEST_SHA256:
        raise ValueError('installed payload manifest differs from approved revision')
    rows = load_json(manifest.read_text())
    if rows['schema_version'] != 2 or rows['revision'] != PIN:
        raise ValueError('installed payload revision differs')
    for row in rows['files']:
        path = checked_file(root, row['path'])
        if (digest(path) != row['sha256']
                or not mode_matches(stat.S_IMODE(path.stat().st_mode), int(row['mode'][-3:], 8))):
            raise ValueError('installed workflow bytes/mode drift: ' + row['path'])
    if set(inventory(root, allow_runtime_cache=True)) != {row['path'] for row in rows['files']} | ANCHORS:
        raise ValueError('installed payload inventory differs')
    return rows


def inventory(root, allow_runtime_cache=False):
    files = []
    for directory, folders, names in os.walk(root, onerror=unreadable):
        base = Path(directory)
        for name in list(folders):
            path = base / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise ValueError('unsafe installed payload entry: ' + relative)
            if allow_runtime_cache and relative in GENERATED_TREES:
                folders.remove(name)
        for name in names:
            path = base / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or not path.is_file():
                raise ValueError('unsafe installed payload entry: ' + relative)
            # Interpreter caches and host metadata are generated, never workflow inputs.
            if allow_runtime_cache and (name in HOST_METADATA or (
                    relative.startswith('adapters/runtime/__pycache__/') and path.suffix == '.pyc')):
                continue
            files.append(relative)
    return sorted(files)


def bind(root):
    verify(root)
    assets = [name for name in inventory(root, allow_runtime_cache=True) if not name.startswith('core/')]
    return {'schema_version': 1, 'revision': PIN, 'payload_sha256': MANIFEST_SHA256,
            'plugin_root': str(root),
            'adapter_sha256': {name: digest(checked_file(root, name)) for name in assets},
            'adapter_modes': {name: stat.S_IMODE(checked_file(root, name).stat().st_mode)
                              for name in assets}}


def load_binding(root, path):
    recorded = load_json(path.read_text())
    if recorded != bind(root):
        raise ValueError('approved installed binding changed; stop and reconcile the program')
    return recorded


def resolve_source(rows, source):
    return rows['legacy_paths'].get(source, source)


def workflow(root, source):
    rows = verify(root)
    source = resolve_source(rows, source)
    if is_skill_body(source) or names_skill_body(source):
        raise ValueError('native skill invocation required; a guarded file read grants no invocation permission')
    known = {row['path'] for row in rows['files']}
    if source not in known or not source.endswith('.md'):
        raise ValueError('workflow is not in approved installed payload')
    return checked_file(root, source).read_bytes()


def command(root, binding, verb, operand):
    return shlex.join(['python3', str(root / 'adapters/host_tools.py'), verb,
                       '--binding', str(binding), '--', operand])


def translate(root, binding, text, *, markdown=False):
    rows = verify(root)
    known = {row['path'] for row in rows['files'] if row['path'].endswith('.md')}
    known |= {old for old, new in rows['legacy_paths'].items() if new in known}
    helpers = {'pstack/skills/poteto-mode/scripts/check-plan.mjs', 'skills/hugues-mode/scripts/check-plan.mjs'}
    operands = [re.compile(r'(?<![\w./:-])(?:origin/main:)?' + re.escape(source) + r'(?![\w./-])')
                for source in known | helpers]

    joined = re.sub(r'\\\r?\n', '', text)
    if joined != text or '<<' in text:
        raise ValueError('continued commands and heredocs are not supported in bundled plans')

    def refuse_skill_body(value):
        if names_skill_body(value):
            raise ValueError('native skill invocation required; plan cannot substitute raw skill reads')

    def fragment(value, *, prose=False):
        # Ahead of parsing and every form-specific branch, so no early return skips it.
        refuse_skill_body(value)
        if prose:
            return value
        skill_directory = names_skill_directory(value)
        skill_name = names_skill_token(value)
        try:
            words = shlex.split(value)
        except ValueError:
            if 'pstack/' in value or skill_directory or skill_name:
                raise ValueError('unresolved quoting in plan reference')
            return value
        if words:
            source = words[-1]
            if source in known and value == command(root, binding, 'read-workflow', source):
                return value
            if (not names_skill_directory(source) and not is_skill_body(source)
                    and value == command(root, binding, 'plan-check', source)):
                return value
        if (skill_directory or skill_name) and re.search(r'[$`(){}\[\]*?~]', value):
            raise ValueError('shell expansion near a skill name; name the skill to apply')
        bundled = any(pattern.search(content) for pattern in operands
                      for content in (value, ' '.join(words)))
        if bundled and re.search(r'[;&|<>$`(){}\[\]*?~]', value):
            raise ValueError('shell syntax is not supported in bundled commands; use a literal standalone command')
        if len(words) == 1 and words[0] in known:
            return command(root, binding, 'read-workflow', words[0])
        if len(words) == 3 and words[:2] == ['git', 'show']:
            revision, separator, source = words[2].partition(':')
            if separator and revision == 'origin/main':
                if source in known:
                    return command(root, binding, 'read-workflow', source)
        if len(words) == 2 and words[0] == 'cat' and words[1] in known:
            return command(root, binding, 'read-workflow', words[1])
        if (len(words) == 3 and words[0] == 'node' and words[1] in helpers
                and not names_skill_directory(words[2]) and not is_skill_body(words[2])):
            return command(root, binding, 'plan-check', words[2])
        if skill_directory:
            raise ValueError('unsupported skill-directory command; name the skill to apply')
        if bundled:
            raise ValueError('unsupported bundled command; use a standalone guarded read')
        return value

    result = []
    standalone = 0
    nonempty = 0
    fence = None
    list_indents = []
    for line in text.splitlines(keepends=True):
        nonempty += bool(line.strip())
        # Whole line too: splitting it into code spans must not split a path apart.
        refuse_skill_body(line)
        prose = markdown
        if markdown:
            content_line = line.expandtabs(4)
            item = None
            if fence is None or fence[1]:
                indent = len(content_line) - len(content_line.lstrip(' '))
                if content_line.strip():
                    while list_indents and indent < list_indents[-1]:
                        list_indents.pop()
                base_indent = list_indents[-1] if list_indents else 0
                content_line = content_line[base_indent:]
                reject_container_code(content_line)
                item = re.match(r'^ {0,3}(?:[-+*]|[0-9]{1,9}[.)]) +', content_line)
                thematic_break = re.fullmatch(r' {0,3}(?:(?:- *){3,}|(?:\* *){3,}|(?:_ *){3,})',
                                              content_line.rstrip('\r\n'))
                if thematic_break:
                    item = None
                if item:
                    list_indents.append(base_indent + item.end())
            delimiter = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', content_line.rstrip('\r\n'))
            if delimiter and fence is None:
                if list_indents:
                    raise ValueError('use top-level code blocks in Markdown plans')
                fence = (delimiter[1], delimiter[2].strip().lower() in {'md', 'markdown'})
                result.append(line)
                continue
            if (delimiter and fence and delimiter[1][0] == fence[0][0]
                    and len(delimiter[1]) >= len(fence[0]) and not delimiter[2].strip()):
                fence = None
                result.append(line)
                continue
            # List-shaped indented code is ambiguous. Allow inline resource
            # references, but command-check its surroundings as in default mode.
            indented = line.expandtabs(4).startswith('    ')
            prose = not indented
            if (fence and not fence[1]) or (indented and not item):
                content = line.strip()
                translated = fragment(content)
                result.append(line if translated == content else line.replace(content, translated, 1))
                continue
        if not prose and '`' in line and names_skill_token(line):
            fragment(line.strip())
        if '`' in line:
            inline = r'(?<!`)`([^`\n]+)`(?!`)'
            surrounding = re.sub(inline, '', line).strip()
            if markdown and '`' in surrounding:
                raise ValueError('use complete single-backtick code spans in Markdown plans')
            if fragment(surrounding, prose=prose) != surrounding:
                raise ValueError('mixed bundled command and inline syntax; use a standalone guarded read')
            result.append(re.sub(inline, lambda match: '`' + fragment(match[1]) + '`', line))
        else:
            content = line.strip()
            translated = fragment(content, prose=prose)
            standalone += translated != content
            result.append(line if translated == content else line.replace(content, translated, 1))
    if fence:
        raise ValueError('unclosed code fence in Markdown plan')
    if standalone and standalone != nonempty:
        raise ValueError('standalone command input must contain only supported standalone commands; use inline references in Markdown plans')
    return ''.join(result)
