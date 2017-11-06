"""Script for converting V2 trivia lists to YAML (used in V3 trivia)."""
import sys
import pathlib
import logging
import argparse
import chardet
import yaml
from yaml.events import (NodeEvent, AliasEvent, ScalarEvent,
                         CollectionStartEvent)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    args = parse_args(args)

    list_paths = {a: pathlib.Path(a) for a in args.source}
    list_files = []
    for arg, path in list_paths.items():
        if path.is_dir():
            list_files.extend(path.glob("*.txt"))
        elif path.is_file() and path.suffix == ".txt":
            list_files.append(path)
        else:
            logging.error("Invalid source \"%s\"", arg)
            return 1
    if not list_files:
        logging.error("No trivia lists found.")
        return 1
    yaml_path = pathlib.Path(args.target)
    if not yaml_path.is_dir():
        logging.info("Creating output directory \"%s\"", yaml_path)
        yaml_path.mkdir()
    for file in list_files:
        logging.info("Reading %s...", file)
        data = parse_trivia_list(
            file, single_quotes_only=args.single_quotes_only)
        filename = file.stem
        newpath = yaml_path / (filename + '.yaml')
        logging.info("Outputting to %s...", newpath)
        output_yaml(data, newpath)
    print("Success.")
    return 0


def parse_args(args):
    parser = argparse.ArgumentParser(description="Convert .txt trivia lists "
                                     "to YAML for V3 trivia.")
    parser.add_argument(
        "--target",
        "-t",
        default="yaml_output",
        help="Specify a directory where YAML files will be dumped.")
    parser.add_argument(
        "--single-quotes-only",
        action="store_true",
        help=("Replace all double quotes with single quotes. This is useful "
              "for avoiding double quotes being escaped with a backslash."))
    parser.add_argument(
        "source",
        action="append",
        help="Directories or files which are being parsed.")

    return parser.parse_args(args)


def parse_trivia_list(path: pathlib.Path, **kwargs):
    """Parse a .txt trivia file.

    Returns
    -------
    dict
        A dict mapping questions (`str`) to answers (`list`).

    """
    ret = {}
    single_quotes_only = kwargs.pop("single_quotes_only", False)

    with path.open("rb") as file:
        try:
            encoding = chardet.detect(file.read())["encoding"]
        except:
            encoding = "ISO-8859-1"

    with path.open('r', encoding=encoding) as file:
        trivia_list = file.readlines()

    for line in trivia_list:
        if '`' not in line:
            continue
        if single_quotes_only:
            line = line.replace("\"", "'")
        line = line.split('`')
        question = line[0].strip()
        answers = []
        for ans in line[1:]:
            ans = ans.strip()
            if ans.isdigit():
                ans = int(ans)
            answers.append(ans)
        if len(line) >= 2 and question and answers:
            ret.update({question: answers})

    if not ret:
        raise ValueError('Empty trivia list.')

    return ret


def output_yaml(data: object, path: pathlib.Path):
    """Output the python objects in `data` to the path at `path`."""
    # data is in form {question: List[answers]}
    with path.open('w', encoding="utf-8") as stream:
        yaml.dump(
            data,
            stream,
            width=1000,
            default_flow_style=False,
            allow_unicode=True,
            Dumper=MyDumper)


class MyDumper(yaml.Dumper):

    # I've overwritten this method from yaml's emitter so we can remove the
    # maximum key length (for some reason it is hard-coded at 128).
    def check_simple_key(self):
        length = 0
        if isinstance(self.event, NodeEvent) and self.event.anchor is not None:
            if self.prepared_anchor is None:
                self.prepared_anchor = self.prepare_anchor(self.event.anchor)
            length += len(self.prepared_anchor)
        if (isinstance(self.event, (ScalarEvent, CollectionStartEvent))
                and self.event.tag is not None):
            if self.prepared_tag is None:
                self.prepared_tag = self.prepare_tag(self.event.tag)
            length += len(self.prepared_tag)
        if isinstance(self.event, ScalarEvent):
            if self.analysis is None:
                self.analysis = self.analyze_scalar(self.event.value)
            length += len(self.analysis.scalar)
        return (isinstance(self.event, AliasEvent) or
                (isinstance(self.event, ScalarEvent)
                 and not self.analysis.empty and not self.analysis.multiline)
                or self.check_empty_sequence() or self.check_empty_mapping())

    # I've overwritten this method from yaml's emitter so that scalars starting
    # or ending in quotes (' or ") are surrounded by double quotes, not single
    # quotes.
    def choose_scalar_style(self):
        if self.analysis is None:
            self.analysis = self.analyze_scalar(self.event.value)
        if self.event.style == '"' or self.canonical:
            return '"'
        if not self.event.style and self.event.implicit[0]:
            empty = (
                not (self.simple_key_context and
                     (self.analysis.empty or self.analysis.multiline)) and
                (self.flow_level and self.analysis.allow_flow_plain or
                 (not self.flow_level and self.analysis.allow_block_plain)))
            if empty:
                return ''
        if self.event.style and self.event.style in '|>':
            if (not self.flow_level and not self.simple_key_context
                    and self.analysis.allow_block):
                return self.event.style
        return '"'


if __name__ == '__main__':
    sys.exit(main())
