# ---------------------------------------------------------------------------------------------------------------
# piwiPre project
# This program and library is licenced under the European Union Public Licence v1.2 (see LICENCE)
# developed by fabien.battini(at)gmail.com
# ---------------------------------------------------------------------------------------------------------------

import argparse
import re
import sys
import os
import pprint
import datetime
import locale

from piwiPre.pwpConfig import PwpConfig
from piwiPre.pwpErrors import PwpConfigError, LOGGER


class ArgHeader:
    def __init__(self, config: str, lang='en'):
        self.config = config
        self.lang = lang

    @staticmethod
    def is_in_config():
        return False

    def write_rst(self, stream, lang='en'):
        if lang != self.lang:
            return
        stream.write("\n")
        for line in self.config.splitlines():
            stream.write(line + '\n')
        stream.write("\n")

    def write_ini_file(self, stream, lang='en'):
        if lang != self.lang:
            return
        stream.write("\n")
        for line in self.config.splitlines():
            stream.write('# ' + line + '\n')
        stream.write("\n")


class ArgIniItem:
    def __init__(self, name: str, config: str, location: str, help_str: str, default, arg, i_type,
                 fr_help: str, fr_config: str, fr_default: str or None):
        self.name = name
        self.config = config
        self.fr_config = fr_config
        self.location = location
        self.help = help_str
        self.fr_help = fr_help
        self.default = default
        self.fr_default = fr_default
        self.arg = arg
        self.i_type = i_type
        if self.i_type == dict and self.default == '':
            self.default = {}
        if not isinstance(self.default, self.i_type) and self.default is not None:
            raise PwpConfigError(f"Parameter '{name}' default value {default} should have type {str(i_type)} ")

    def print_fr(self, full=False):

        def fit(val, explain):
            if len(val) > 24:
                if explain:
                    return f"{val}\n{'':>26}{explain}"
                else:
                    return f"{val}"
            else:
                return f"{val:<24}{explain}"

        def right(val):
            if val == '':
                return ''
            res = ""
            cur_line = ""
            sp = val.split(" ")
            for elem in sp:
                if len(cur_line) + len(elem) > 50:
                    res += f"{cur_line}\n{'':>26}"
                    cur_line = ""
                cur_line += elem + " "
            res += cur_line
            return res

        if not self.arg:
            # this is not a cmd-line arg
            return

        name = '--' + self.name + " "
        if not self.arg.const:
            sep = ''
            if self.arg.choices:
                name += '{'
                for item in getattr(self.arg, 'choices'):
                    name += f"{sep}'{item}'"
                    sep = ', '
                name += '}'
            else:
                name += getattr(self.arg, 'dest').upper()  # noqa

        print(f"  {fit(name, right(self.fr_help))}")
        if full and self.fr_config:
            for line in self.fr_config.split('\n'):
                print("                  |  " + line)

    def is_in_config(self):
        return self.location != 'args'

    def write_rst(self, stream, lang='en'):

        default = self.get_ini_value(self.default, "   ", ini_file=False)
        # default = 'false' if default is False else 'true' if default is True else default

        if lang == 'en':
            location = 'configration files only' if self.location == 'config' else \
                'cmd-line arguments only' if self.location == 'args' \
                else 'both configuration files and cmd-line arguments'
        else:  # if lang == 'fr':
            location = 'uniquement dans les fichiers de configuration ' if self.location == 'config' else \
                'uniquement sur la ligne de commande ' if self.location == 'args' \
                else 'dans les fichiers de configuration ou sur la ligne de commande'
        default = ("``" + default + "``") if default else ''
        stream.write(f"\n**{self.name}** : {default}\n\n")
        if lang == 'en':
            stream.write(f"  where: {location}\n\n")
            config = self.config
            helps = self.help
        else:
            stream.write(f"   où: {location}\n\n")
            config = self.fr_config
            helps = self.fr_help
        stream.write(f"   {helps}\n")
        for line in config.splitlines():
            stream.write(f"   {line}\n")
        stream.write("\n")

    def get_ini_value(self, item, prefix, level=0, ini_file=True):
        if item is False:
            return 'false'
        if item is True:
            return 'true'
        if isinstance(item, str):
            if re.search(r'[+\-/]', item):
                return "'" + item + "'"
            return item

        if type(item) is dict:
            if len(item.keys()) == 0:
                return ""
            if level == 0:
                if ini_file:
                    res = '\n'
                else:
                    res = '\n ::\n\n'
            else:
                res = '\n'
            for key, value in item.items():
                k = self.get_ini_value(key, "", level=level+1, ini_file=ini_file)
                val = self.get_ini_value(value, prefix + "   ", level=level+1, ini_file=ini_file)
                res += f"{prefix}   {k} : {val}\n"
            if level == 0:
                if not ini_file:
                    res += "\n\n#  *(end of the structure)*\n"
            return res

        return str(item)

    def write_ini_file(self, stream, lang='en'):
        default = self.get_ini_value(self.default, "   ", ini_file=True)

        if lang == 'en':
            location = 'configration files only' if self.location == 'config' else \
                'cmd-line arguments only' if self.location == 'args' \
                else 'both configuration files and cmd-line arguments'
        else:  # if lang == 'fr':
            location = 'uniquement dans les fichiers de configuration ' if self.location == 'config' else \
                'uniquement sur la ligne de commande ' if self.location == 'args' \
                else 'dans les fichiers de configuration ou sur la ligne de commande'

        if self.location == 'args':
            header = '# '
            name = '--' + self.name
        else:
            header = ''
            name = self.name

        stream.write(f"\n{header}{name} : {default}\n")
        if lang == 'en':
            stream.write(f"#   where: {location}\n\n")
        else:
            stream.write(f"#   où: {location}\n\n")
        stream.write(f"#   {self.help}\n")
        for line in self.config.splitlines():
            stream.write(f"#   {line}\n")
        stream.write("\n")


class PwpArgsIni(argparse.ArgumentParser):

    def __init__(self, **_kwargs):
        super().__init__(prog='piwiPre', allow_abbrev=False, exit_on_error=False)
        self.args_dico = {}
        self.items_list = []        # a list of ArgHeader or ArgIniItem
        self.home_config = None

    def add_header(self, prologue: str, lang='en'):
        item = ArgHeader(prologue, lang=lang)
        self.items_list.append(item)

    def add_item(self, name_or_flags: str, **kwargs):
        # location should be 'config' or 'args'. any other value = 'both'. default = 'both'
        location = 'both'
        if 'location' in kwargs:
            location = kwargs['location']
            kwargs.pop('location')
        config = ''
        if 'config' in kwargs:
            config = kwargs['config']
            kwargs.pop('config')

        if 'fr_config' in kwargs:
            fr_config = kwargs['fr_config']
            kwargs.pop('fr_config')
        else:
            fr_config = ''

        help_str = '' if 'help' not in kwargs else kwargs['help']

        if 'fr_help' in kwargs:
            fr_help_str = kwargs['fr_help']
            kwargs.pop('fr_help')
        else:
            fr_help_str = ''

        if 'fr_default' in kwargs:
            fr_default_str = kwargs['fr_default']
            kwargs.pop('fr_default')
        else:
            fr_default_str = None

        default = '' if 'default' not in kwargs else kwargs['default']
        if 'pwp_type' in kwargs:
            i_type = kwargs['pwp_type']
            kwargs.pop('pwp_type')
        else:
            i_type = str

        arg = super().add_argument('--'+name_or_flags, **kwargs) if location != 'config' else None
        item = ArgIniItem(name_or_flags, config, location, help_str, default, arg, i_type,
                          fr_help=fr_help_str, fr_config=fr_config, fr_default=fr_default_str)
        self.args_dico[name_or_flags] = item
        self.items_list.append(item)

    def print_fr(self, full=False):
        print("")
        print("Les options:")
        for arg in self.args_dico:
            self.args_dico[arg].print_fr(full)
        print("")

    def build_rst(self, filename: str, lang='en'):
        abs_path = os.path.abspath(filename)
        LOGGER.debug(f"Build RST file {abs_path} , lang={lang}")
        with open(filename, 'w', encoding="utf-8") as f:
            start = datetime.datetime.now()
            if lang == 'en':
                f.write(f".. comment : CAVEAT: This text is automatically generated by pwpPatcher.py on {start}\n")
                f.write(".. comment :         from the code in pwpParser.py\n")
            else:
                f.write(f".. comment : ATTENTION: Ce fichier est a été généré par pwpPatcher.py le {start}\n")
                f.write(".. comment :             à partir du code dans pwpParser.py\n")

            for item in self.items_list:
                item.write_rst(f, lang)

    def build_ini_file(self, filename: str, lang='en'):
        with open(filename, 'w', encoding="utf-8") as f:
            for item in self.items_list:
                item.write_ini_file(f, lang=lang)

    def build_initial_config(self, language):
        """
        builds the default configuration
        some values are computed depending on the language, which may have been set on the cmdline
        :param language: 'en' or 'fr'
        :return: dict
        """
        dico = {}
        for v in self.items_list:
            if v.is_in_config():
                dico[v.name] = v.default if language == 'en' or v.fr_default is None else v.fr_default
        dico['help'] = None
        res = PwpConfig(content_str=None, filename="INITIAL VALUES", dico=dico)
        return res

    @staticmethod
    def stringify(value: str):
        if isinstance(value, str) and '--' in value[1:]:
            LOGGER.warning(f"argument '{value}' contains '--', this is probably an error with 2 flags concatenated")
        if value is True or isinstance(value, str) and value.lower() == 'true':
            return 'true'
        if value is False or isinstance(value, str) and value.lower() == 'false':
            return 'false'
        if value is None or isinstance(value, str) and value.lower() == 'none':
            return 'none'
        if isinstance(value, int):
            return int(value)

        return value

    def parse_args_and_ini(self, program: str, ini_to_parse, arguments, with_config=True):
        initial_config = None
        real_args = arguments if arguments is not None else []

        # check if actual arguments prevent from using the default .ini
        def get_val(flag):
            if flag in real_args:
                index = real_args.index(flag)
                if index > len(real_args):
                    raise PwpConfigError(f"argument {flag} without a value")
                return real_args[index + 1]
            return None

        if '--quiet' not in real_args:
            LOGGER.start()

        if get_val("--language") == 'fr':
            language = 'fr'
        elif get_val("--language") == 'en':
            language = "en"
        else:
            loc, _ = locale.getlocale()
            language = 'fr' if loc == 'fr_FR' else 'en'

        if (value := get_val('--ini-file')) is not None:
            ini_to_parse = os.path.basename(value)

        if (new_dir := get_val('--chdir')) is not None:
            if not os.path.isdir(new_dir):
                raise PwpConfigError(f"--chdir '{new_dir}' : non existing directory")
            LOGGER.msg(f"chdir '{new_dir}'")
            os.chdir(new_dir)

        if '--help' in real_args:
            if language == 'en':
                self.print_help()
                # if we do exit(0) or raisePwpConfigError, (on program_3) on test 400, Paramiko exits on error!
                # msg is:  'ValueError: I/O operation on closed file'
                # this seems to be an issue with stdin, probably closed before Paramiko ends
                # Trick: We return None, so that the program is ended gracefully
                return None
            self.print_usage()
            self.print_fr()
            return None

        if '--full-help' in real_args:
            if language == 'en':
                self.print_usage()
                return None
            self.print_fr(full=True)
            return None

        if with_config:
            initial_config = self.build_initial_config(language=language)

        home_ini_path = os.path.expanduser("~") + '/.' + ini_to_parse
        config = initial_config

        if with_config and os.path.isfile(home_ini_path):
            first_ini = PwpConfig.parse_ini_file(home_ini_path)
            # if not ACTOR.is_mode_protected(home_ini_path):
            #    raise PwpError(f"HOME ini file {home_ini_path} MUST be protected by chmod 0x600 o 0x400")
            # chmod has limited meaning in windows universe
            config = first_ini.merge_ini(initial_config)

        self.home_config = config

        if with_config and os.path.isfile(ini_to_parse):
            first_ini = PwpConfig.parse_ini_file(ini_to_parse)
            config = first_ini.merge_ini(config)

        LOGGER.msg(f"{program}: reading configuration from cmd-line arguments")
        string_args = [self.stringify(a) for a in real_args]
        try:
            args = super().parse_args(args=string_args)
        except argparse.ArgumentError:
            super().print_help()
            raise PwpConfigError("Error on arguments, internal")
        except SystemExit:
            super().print_help()
            # return None
            raise PwpConfigError("Error on arguments")

        if with_config:
            config = config.merge_ini_args(args, real_args)
        else:
            config = PwpConfig.args_to_dict(args)

        return config


def args_ini_main(arguments):
    parser = PwpArgsIni()
    parser.add_header('Unified parser for .ini files and cmdline flags')
    parser.add_header('===============================================')
    parser.add_header('\nParameters when executing pwpArgsIni as a program\n')
    parser.add_item('build-ini-file',
                    help='builds the ini-file argument',
                    action='store_true',
                    location='args')
    parser.add_item('ini-file',
                    help='sets the ini-file to build',
                    action='store',
                    default="test.ini")
    parser.add_item('build-rst-file',
                    help='builds the rst-file argument',
                    action='store_true',
                    location='args')
    parser.add_item('rst-file',
                    help='sets the rst-file to build',
                    action='store',
                    default="test.rst")
    parser.add_item('dump-config',
                    help='dumps the configuration and exits',
                    action='store_true',
                    location='args')
    parser.add_item('auto-test',
                    help='performs the auto-test and exits',
                    action='store_true',
                    location='args')

    # check if actual arguments ask for new configuration items just for test

    if '--auto-test' in arguments:
        # The following data is fake, just to test if args-ini works OK
        parser.add_header("""
#######################
Flags and configuration
#######################""")
        parser.add_header("""
File usage
==========

This file is the default configuration of piwiPre.

Unless stated otherwise, the  configuration items have a command line argument counterpart, 
with the same name, starting with -- .

The default value is given as an argument.

The configuration file uses the yaml syntax,
and uses pyYaml  to read/write the configuration file""")
        parser.add_item('version', help="Prints piwiPre version number and exits.",
                        action='store_true', location='args')

        parser.add_header("""
Management of directories
=========================""")

        parser.add_item('triage',
                        help='Sets the root directory for TRIAGE pictures to manage.',
                        action='store',
                        default='TRIAGE',
                        config="""
- value = 'directory': Sets the root directory for TRIAGE pictures to manage
- value = None: renaming  has already been done, so the TRIAGE directory is not processed
""")

        parser.add_item('month-name',
                        help='The name for each month, used to compute month_name.',
                        action='store',
                        pwp_type=list,
                        default=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                        location='config')

        parser.add_item('piwigo-thumbnails',
                        help='A dictionary if thumbnail specifications',
                        pwp_type=dict,
                        default={
                            "{f}-sq.jpg": {'width': 120, 'height': 120, 'crop': True},
                            "{f}-th.jpg": {'width': 144, 'height': 144, 'crop': False},
                            "{f}-me.jpg": {'width': 792, 'height': 594, 'crop': False},
                            "{f}-cu_e250.jpg": {'width': 250, 'height': 250, 'crop': True},
                        },
                        location='config')
        parser.add_item('dates',
                        help='A dictionary of dates corrections',
                        action='store',
                        pwp_type=dict,
                        default={},
                        location='config')
        parser.add_item('verify-album',
                        help='true/false/list of directories in ALBUMS to be processed ',
                        action='append',
                        pwp_type=list,
                        default=[])
        parser.add_item('process-rename',  # is used to test ambiguous arguments
                        help='Enables files renaming',
                        action='store',
                        choices=['true', 'false'],
                        default='false')
    # end of auto-test case
    config = parser.parse_args_and_ini("autotest", "tests.ini", arguments)

    if config['build-rst-file'] or config['auto-test']:
        parser.build_rst(config['rst-file'] or "../results/test-result.rst")
    if config['build-ini-file'] or config['auto-test']:
        parser.build_ini_file(config['ini-file'] or "../results/test-result.ini")
    if config['auto-test']:
        pprint.pprint(config)
        pprint.pprint(config)
        parser.print_help()
        return
    if config['help']:
        parser.print_help()


# by default, --auto-test is launched from the tests/argsini directory  # noqa

if __name__ == "__main__":
    sys.exit(args_ini_main(sys.argv[1:]))
