#!/usr/bin/env python3

import os
import re
import argparse
import multiprocessing
import mmap
import sys

def transform_pattern(pattern):
    parts = re.split(r'([A-Z][a-z]*|\d+)', pattern)
    transformed = []
    for part in parts:
        if part:
            transformed.append(re.escape(part.lower()))
    return r'[-_]?'.join(transformed)

def search_file(file_path, pattern, search_contents, colorize):
    results = []
    try:
        if not search_contents:
            if pattern.search(os.path.basename(file_path)):
                results.append(format_output(file_path, 0, "", colorize))
            return results

        with open(file_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                for i, line in enumerate(iter(mm.readline, b''), 1):
                    try:
                        line = line.decode('utf-8')
                    except UnicodeDecodeError:
                        continue
                    if pattern.search(line):
                        results.append(format_output(file_path, i, line.strip(), colorize))
    except (IOError, ValueError):
        pass
    return results

def format_output(file_path, line_num, line_content, colorize):
    if colorize:
        return f"\033[35m{file_path}\033[0m" + (f":\033[32m{line_num}\033[0m:{line_content}" if line_num else "")
    else:
        return f"{file_path}" + (f":{line_num}:{line_content}" if line_num else "")

def worker(file_queue, pattern, result_queue, search_contents, colorize):
    while True:
        try:
            file_path = file_queue.get_nowait()
        except:
            break
        results = search_file(file_path, pattern, search_contents, colorize)
        if results:
            result_queue.put(results)

def super_grep(directory, pattern, num_workers, search_contents, colorize, depth):
    transformed_pattern = transform_pattern(pattern)
    regex = re.compile(transformed_pattern, re.IGNORECASE)

    file_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    for root, _, files in os.walk(directory):
        rel_path = os.path.relpath(root, directory)
        current_depth = 0 if rel_path == '.' else len(rel_path.split(os.sep))
        if depth is not None and current_depth > depth:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            file_queue.put(file_path)

    processes = []
    for _ in range(num_workers):
        p = multiprocessing.Process(target=worker, args=(file_queue, regex, result_queue, search_contents, colorize))
        p.start()
        processes.append(p)

    printed = 0
    try:
        while any(p.is_alive() for p in processes) or not result_queue.empty():
            try:
                results = result_queue.get_nowait()
                for result in results:
                    print(result, flush=True)
                    printed += 1
            except:
                pass
    except KeyboardInterrupt:
        print("\nInterrupted by user. Stopping gracefully...", file=sys.stderr)
        for p in processes:
            p.terminate()

    for p in processes:
        p.join()

    while not result_queue.empty():
        results = result_queue.get()
        for result in results:
            print(result, flush=True)
            printed += 1

    if printed == 0:
        print("No matches found.")

def main():
    parser = argparse.ArgumentParser(
        description="Super Grep: Python implementation with depth control and format-agnostic search",
        epilog="""
Examples:
  Search only in the given directory:
    super-grep /path/to/search "FooBar|first_name"

  Search up to 2 levels deep:
    super-grep /path/to/search "FooBar|first_name" --depth 2

  Search all subdirectories:
    super-grep /path/to/search "FooBar|first_name" --depth -1

  Search file contents up to 3 levels deep with colored output:
    super-grep /path/to/search "FooBar|first_name" --depth 3 --contents --color

  Use 8 worker processes:
    super-grep /path/to/search "FooBar|first_name" --workers 8
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("directory", help="Directory to search in")
    parser.add_argument("pattern", help="Search pattern")
    parser.add_argument("--workers", type=int, default=multiprocessing.cpu_count(), help="Number of worker processes (default: CPU count)")
    parser.add_argument("--contents", action="store_true", help="Search within file contents (default: search filenames only)")
    parser.add_argument("--color", action="store_true", help="Colorize the output")
    parser.add_argument("--depth", type=int, default=0, help="Depth of directory search (default: 0, search only in given directory; use -1 for unlimited depth)")
    args = parser.parse_args()

    super_grep(args.directory, args.pattern, args.workers, args.contents, args.color, args.depth)

if __name__ == "__main__":
    main()
