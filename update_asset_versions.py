import argparse
import hashlib
import html
import re
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlsplit, urlunsplit


ASSETS = {'.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.avif', '.ico', '.woff', '.woff2', '.ttf'}
FRAGMENTS = {'header.html', 'footer.html'}
ATTRIBUTES = re.compile(r'''(\b(?:src|href|poster)\s*=\s*)(["'])(.*?)\2''', re.I | re.S)
QUOTED_URLS = re.compile(r'''(["'])((?:\.\.?/|/)[^\s"'<>]*)\1''')
CSS_URLS = re.compile(r'''url\(\s*(["']?)([^\s)'"]+)\1\s*\)''', re.I)
SCRIPTS = re.compile(r'(<script\b[^>]*>)(.*?)(</script>)', re.I | re.S)


def update_asset_versions(directory):
    root = Path(directory).resolve()
    changed = []
    digests = {}

    def version_url(value, source, fragments=False):
        parts = urlsplit(value)
        if parts.scheme or parts.netloc or not parts.path:
            return value
        resolved = urljoin('/' + source.relative_to(root).as_posix(), parts.path)
        target = (root / unquote(resolved).lstrip('/')).resolve()
        try:
            relative = target.relative_to(root).as_posix()
        except ValueError:
            return value
        if target.suffix.lower() not in ASSETS and not (fragments and relative in FRAGMENTS):
            return value
        if not target.is_file():
            raise FileNotFoundError(f'{source.relative_to(root)}: {value}')
        if target not in digests:
            digests[target] = hashlib.sha256(target.read_bytes()).hexdigest()[:12]
        parameters = [(key, item) for key, item in parse_qsl(parts.query, keep_blank_values=True) if key != 'v']
        parameters.append(('v', digests[target]))
        return urlunsplit(('', '', parts.path, urlencode(parameters), parts.fragment))

    def raw_urls(text, source, fragments=False):
        def replace(match):
            value = version_url(match[2], source, fragments)
            return match[1] + value + match[1]
        return QUOTED_URLS.sub(replace, text)

    def css_urls(text, source):
        def replace(match):
            value = version_url(match[2], source)
            return match[0] if value == match[2] else 'url(' + match[1] + value + match[1] + ')'
        return CSS_URLS.sub(replace, text)

    def html_urls(text, source):
        def replace(match):
            value = html.unescape(match[3])
            versioned = version_url(value, source)
            if value == versioned:
                return match[0]
            return match[1] + match[2] + html.escape(versioned, quote=False) + match[2]
        text = ATTRIBUTES.sub(replace, text)
        return SCRIPTS.sub(lambda match: match[1] + raw_urls(match[2], source) + match[3], text)

    def rewrite(source, transform):
        before = source.read_bytes().decode('utf-8')
        after = transform(before, source)
        if before != after:
            source.write_bytes(after.encode('utf-8'))
            digests.pop(source, None)
            changed.append(source.relative_to(root).as_posix())

    sources = sorted(path for path in root.rglob('*') if path.is_file() and not any(part.startswith('.') for part in path.relative_to(root).parts))
    for source in sources:
        if source.suffix.lower() == '.css':
            rewrite(source, css_urls)
    for relative in sorted(FRAGMENTS):
        source = root / relative
        if source.is_file():
            rewrite(source, html_urls)
    for source in sources:
        if source.suffix.lower() == '.js':
            rewrite(source, lambda text, path: raw_urls(text, path, fragments=True))
    for source in sources:
        if source.suffix.lower() == '.html' and source.relative_to(root).as_posix() not in FRAGMENTS:
            rewrite(source, html_urls)
    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    changed = update_asset_versions(args.root)
    print(f'Updated asset versions in {len(changed)} files.')


if __name__ == '__main__':
    main()
