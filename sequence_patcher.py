import mmap
import argparse
import re


def __get_patches(file_name, reverse):
    pattern = r"\[([\w ]+?\|?\w+?)\]\n((?:[a-fA-F0-9]+ ?)+)\n((?:[a-fA-F0-9]+ ?)+)"
    patch_list = []

    with open(file_name, 'r') as f:
        read = f.read()
        patches = re.findall(pattern, read)

    for patch in patches:
        sequence_at = -1
        sequence_key, sequence_from, sequence_to = patch[0], patch[1], patch[2]
        if reverse:
            sequence_from, sequence_to = sequence_to, sequence_from
        if len(patch[0].split('|')) > 1:
            sequence_key = patch[0].split('|')[0]
            sequence_at = int.from_bytes(
                bytes.fromhex(patch[0].split('|')[1]), 'big')
        patch_list.append({'key': sequence_key,
                           'at': sequence_at,
                           'from': bytes.fromhex(sequence_from),
                           'to': bytes.fromhex(sequence_to)})

    return patch_list


def patch_file(target_file, patch_file, reverse=False, force=False, quiet=False):
    patches = __get_patches(patch_file, reverse)

    with open(target_file, 'r+b') as f:
        mm = mmap.mmap(f.fileno(), 0)
        for patch in patches:
            pos = mm.find(patch['from'])

            if pos == -1:
                if force:
                    if not quiet:
                        print(f"skipping unfound patch \"{patch['key']}.")
                    continue
                choice = input(
                    f"Could not find sequence for patch \"{patch['key']}.\" Move to next patch? (y/n): ")
                if choice.lower() == 'y':
                    if not quiet:
                        print(f"skipping unfound patch \"{patch['key']}.")
                    continue
                else:
                    break

            multiple_matches = mm.find(patch['from'], pos+1) > pos+1
            if multiple_matches:
                if not force:
                    choice = input(
                        'multiple matches found, force patch first instance anyway? (y/n): ')
                    if choice.lower() != 'y':
                        continue
                if not quiet:
                    print('Applying patch to first match')

            if patch['at'] != -1 and pos != patch['at']:
                if not force:
                    choice = input(
                        f"offset hint was {patch['at']}, but byte sequence was found at {pos}. Continue anyway? (y/n): ")
                    if choice.lower() != 'y':
                        if not quiet: print('skipping')
                        continue

            mm.seek(pos)
            mm.write(patch['to'])
            if not quiet:
                if not reverse:
                    print(f"- Applied patch {patch['key']}")
                else:
                    print(f"- Removed patch {patch['key']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', help='target file to patch')
    parser.add_argument(
        'patch', help='file containing one or more patches to apply')
    parser.add_argument('--reverse', dest='reverse', action='store_true',
                        help='reverse patch')
    parser.add_argument('--force', dest='force', action='store_true',
                        help='skips warnings and ignores multiple matches')
    parser.add_argument('--quiet', dest='quiet', action='store_true',
                        help='skips all non-essential output')
    parser.set_defaults(reverse=False)
    parser.set_defaults(forcee=False)
    args = parser.parse_args()

    patch_file(args.target, args.patch, args.reverse, args.force, args.quiet)


if __name__ == '__main__':
    main()
