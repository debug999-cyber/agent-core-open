#!/usr/bin/env python3
"""Дайджест веб-страницы вместо целой страницы — экономит контекст (лимиты).

Зачем: целые страницы попадают в контекст по 100–150 тыс. символов и оплачиваются
в каждом следующем запросе. Дайджест даёт заголовок, подзаголовки и начало текста —
обычно этого хватает, чтобы вынести вердикт по находке.

Использование:
  web-digest.py <url>                     # заголовок + подзаголовки + ~4000 символов
  web-digest.py <url> --chars 8000        # больше текста
  web-digest.py <url> --grep скилл        # разделы/абзацы со словом (лучший способ достать факт)
  web-digest.py <url> --headings          # только заголовки
  web-digest.py <url> --full              # весь текст (когда реально нужен целиком)
"""
import argparse, gzip, html, re, sys, urllib.request

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124 Safari/537.36')

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'gzip'})
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    return raw.decode('utf-8', 'replace')

def clean(h):
    h = re.sub(r'(?is)<(script|style|svg|noscript|nav|footer|head)[^>]*>.*?</\1>', ' ', h)
    h = re.sub(r'(?is)<a[^>]*>\s*#\s*</a>', ' ', h)                      # якоря заголовков
    h = re.sub(r'(?is)<h([1-6])[^>]*>(.*?)</h\1>',
               lambda m: '\n' + '#' * int(m.group(1)) + ' ' + re.sub(r'(?s)<[^>]+>', ' ', m.group(2)) + '\n', h)
    h = re.sub(r'(?is)<li[^>]*>', '\n- ', h)
    h = re.sub(r'(?is)<(p|div|br|tr|section|article|pre)[^>]*>', '\n', h)
    h = re.sub(r'(?s)<[^>]+>', ' ', h)
    h = html.unescape(h)
    h = re.sub(r'[ \t\xa0]+', ' ', h)
    h = re.sub(r'\n\s*\n+', '\n\n', h)
    out = []
    for line in h.split('\n'):
        if re.match(r'^#{1,6}\s*$', line) or re.match(r'^#$', line.strip()):
            continue                                                       # пустые заголовки — вон
        out.append(line.replace('\u200b', '').rstrip())
    return '\n'.join(out).strip()

def sections(text):
    """Режем текст на секции по заголовкам: [(заголовок, тело), ...]"""
    parts, cur_head, cur = [], '(начало)', []
    for line in text.split('\n'):
        if re.match(r'^#{1,6} ', line):
            parts.append((cur_head, '\n'.join(cur).strip()))
            cur_head, cur = line, []
        else:
            cur.append(line)
    parts.append((cur_head, '\n'.join(cur).strip()))
    return [(h, b) for h, b in parts if b or not h.startswith('(')]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('--chars', type=int, default=4000)
    ap.add_argument('--grep')
    ap.add_argument('--headings', action='store_true')
    ap.add_argument('--full', action='store_true')
    a = ap.parse_args()
    try:
        text = clean(fetch(a.url))
    except Exception as e:
        print(f'не удалось взять страницу: {e}')
        sys.exit(1)
    print(f'URL: {a.url}\nВСЕГО символов текста на странице: {len(text)} (в контекст идёт только выжимка)')
    if len(text) < 1500:
        print('ВНИМАНИЕ: текста почти нет — страница, похоже, собирается скриптами. '
              'Возьми другой источник или используй веб-фетч с точным вопросом.')
    heads = [l for l in text.split('\n') if re.match(r'^#{1,3} ', l)]
    if heads:
        print('\nЗАГОЛОВКИ:')
        for l in heads[:25]:
            print('  ' + l)
        if len(heads) > 25:
            print(f'  … ещё {len(heads)-25}')
    if a.headings:
        return
    if a.grep:
        hits = [(h, b) for h, b in sections(text)
                if a.grep.lower() in h.lower() or a.grep.lower() in b.lower()]
        print(f'\nСОВПАДЕНИЯ ({len(hits)}), показаны первые 6:')
        for h, b in hits[:6]:
            print('- ' + (h.strip() + ': ' if h.strip() else '') + b[:900])
        return
    body = text if a.full else text[:a.chars]
    print('\nТЕКСТ:')
    print(body)
    if not a.full and len(text) > a.chars:
        print(f'\n… обрезано, ещё {len(text)-a.chars} символов. '
              f'Достать нужное: --grep <слово> или --chars <N>')

if __name__ == '__main__':
    main()
