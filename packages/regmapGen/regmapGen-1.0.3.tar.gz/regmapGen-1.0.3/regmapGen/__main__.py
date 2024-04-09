#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Run regmapGen from command line with arguments.
"""

import sys
import os
import argparse
from pathlib import Path
import regmapGen
from . import utils
from contextlib import contextmanager
import importlib.util

__all__ = ['main']


@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


class ArgumentParser(argparse.ArgumentParser):
    """Inherit ArgumentParser to override the behaviour of error method."""

    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, '\n%s: error: %s\n' % (self.prog, message))


def parse_arguments():
    """Parse and validate arguments."""
    parser = ArgumentParser(prog=regmapGen.__title__,
                            description=regmapGen.__description__)
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s v' + regmapGen.__version__)
    parser.add_argument(metavar='WORKDIR',
                        nargs='?',
                        dest='workdir_path',
                        default=os.getcwd(),
                        help='working directory (default is the current directory)')
    parser.add_argument('-r',
                        metavar='REGMAP',
                        dest='regmap_path',
                        help='read register map from file')
    parser.add_argument('-c',
                        metavar='CONFIG',
                        dest='config_path',
                        help='read configuration from file')
    template_choices = ['json', 'yaml', 'txt']
    parser.add_argument('-t',
                        metavar='FORMAT',
                        choices=template_choices,
                        dest='template_format',
                        help='create templates (choose from %s)' % ', '.join(template_choices))
    return parser.parse_args()


def generate_templates(format):
    print("... templates format: '%s'" % format)
    # global configuration
    globcfg = regmapGen.config.default_globcfg()
    globcfg['data_width'] = 32
    globcfg['address_width'] = 16
    globcfg['register_reset'] = 'sync_pos'
    regmapGen.config.set_globcfg(globcfg)

    # targets
    targets = {}
    targets.update(regmapGen.generators.SystemVerilog(path="hw/regs.sv").make_target('sv_module'))
    targets.update(regmapGen.generators.SystemVerilogWrapper(path="hw/regs_wrapper.svh").make_target('sv_wrapper'))
    targets.update(regmapGen.generators.SystemVerilogHeader(path="hw/regs.svh").make_target('sv_header'))
    targets.update(regmapGen.generators.SystemVerilogPackage(path="hw/regs_pkg.sv").make_target('sv_pkg'))
    targets.update(regmapGen.generators.Python(path="sw/regs.py").make_target('py'))
    targets.update(regmapGen.generators.CHeader(path="sw/regs.h").make_target('c_header'))
    targets.update(regmapGen.generators.CmsisSvd(path="sw/regs.svd").make_target('cmsis_svd'))
    targets.update(regmapGen.generators.IpxactXml(path="sw/regs.xml").make_target('ipxact_xml'))
    targets.update(regmapGen.generators.Markdown(path="doc/regs.md", image_dir="md_img").make_target('md_doc'))
    targets.update(regmapGen.generators.Asciidoc(path="doc/regs.adoc", image_dir="adoc_img").make_target('asciidoc_doc'))
    targets.update(regmapGen.generators.Rst(path="doc/regs.rst", image_dir="rst_img").make_target('rst_doc'))
    targets.update(regmapGen.generators.Docx(path="doc/regs.docx").make_target('docx_doc'))

    # create templates
    if format == 'txt':
        rmap = regmapGen.utils.create_template_simple()
    else:
        rmap = regmapGen.utils.create_template()
    # register map template
    if format == 'json':
        gen = regmapGen.generators.Json(rmap)
        regmap_path = 'regs.json'
    elif format == 'yaml':
        gen = regmapGen.generators.Yaml(rmap)
        regmap_path = 'regs.yaml'
    elif format == 'txt':
        gen = regmapGen.generators.Txt(rmap)
        regmap_path = 'regs.txt'
    print("... generate register map file '%s'" % regmap_path)
    gen.generate()
    # configuration file template
    config_path = 'config'
    globcfg['regmap_path'] = regmap_path
    print("... generate configuration file '%s'" % config_path)
    regmapGen.config.write_config(config_path, globcfg, targets)


def die(msg):
    print("Error: %s" % msg)
    exit(1)


def finish():
    print('Success!')
    exit(0)


def app(args):
    print("... set working directory '%s'" % args.workdir_path)

    # check if teplates are needed
    if args.template_format:
        generate_templates(args.template_format)
        finish()

    # check if configuration file path was provided
    if args.config_path:
        config_path = Path(args.config_path)
    else:
        config_path = Path('config')
    # check it existance
    if not config_path.is_file():
        die("Can't find configuration file '%s'!" % config_path)
    # try to read it
    print("... read configuration file '%s'" % config_path)
    globcfg, targets = regmapGen.config.read_config(config_path)

    # Execute Xls2Yaml target if present, before anything else
    pre_target = next((target for target in targets.values() if target.get('generator') == 'Xls2Yaml'), None)
    pre_target_name = next((key for key, value in targets.items() if value.get('generator') == 'Xls2Yaml'), None)
    if pre_target:
        # Generate YAML from Excel before reading regmap
        print("... make '%s': Xls2Yaml -> '%s':" % (pre_target_name, pre_target.get('path')))
        regmapGen.generators.Xls2Yaml(path=pre_target.get('path'), input_xls=pre_target.get('input_xls')).generate()
        # Remove Xls2Yaml target from targets to avoid its re-execution in make targets section
        targets.pop(pre_target_name, None)

    # check if regiter map file path was provided
    if args.regmap_path:
        regmap_path = Path(args.regmap_path)
        globcfg['regmap_path'] = regmap_path
    elif 'regmap_path' in globcfg.keys():
        regmap_path = Path(globcfg['regmap_path'])
    else:
        regmap_path = None
        print("Warning: No register map file was specified!")
    regmapGen.config.set_globcfg(globcfg)

    if regmap_path:
        # check it existance
        if not regmap_path.is_file():
            die("Can't find register map file '%s'!" % regmap_path)

        # try to read it
        print("... read register map file '%s'" % regmap_path)
        rmap = regmapGen.RegisterMap()
        rmap.read_file(regmap_path)
        print("... validate register map")
        rmap.validate()
    else:
        rmap = None

    # make targets
    if not targets:
        die("No targets were specified! Nothing to do!")
    for t in targets:
        print("... make '%s': " % t, end='')
        if 'generator' not in targets[t].keys():
            die("No generator was specified for the target!")

        if '.py::' in targets[t]['generator']:
            custom_module_path, custom_generator_name = targets[t]['generator'].split('::')
            custom_module_name = utils.get_file_name(custom_module_path)
            spec = importlib.util.spec_from_file_location(custom_module_name, custom_module_path)
            custom_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(custom_module)
            try:
                gen_obj = getattr(custom_module, custom_generator_name)
                gen_name = custom_generator_name
            except AttributeError:
                die("Generator '%s' from module '%s' does not exist!" % (custom_generator_name, custom_module_path))
        else:
            gen_name = targets[t]['generator']
            try:
                gen_obj = getattr(regmapGen.generators, gen_name)
            except AttributeError:
                die("Generator '%s' does not exist!" % gen_name)

        gen_args = targets[t]
        print("%s -> '%s': " % (gen_name, gen_args['path']))
        gen_obj(rmap, **gen_args).generate()


def main():
    """Program main"""
    # parse arguments
    args = parse_arguments()

    # do all the things inside working directory
    args.workdir_path = str(Path(args.workdir_path).absolute())
    with cwd(args.workdir_path):
        app(args)
    finish()


if __name__ == '__main__':
    main()
