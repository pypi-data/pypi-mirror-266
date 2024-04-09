import typing

GenericType = typing.TypeVar("GenericType")

class I18n:
    """ """

    parsers: typing.Any
    """ """

    py_file: typing.Any
    """ """

    writers: typing.Any
    """ """

    def check_py_module_has_translations(self, src, settings):
        """

        :param src:
        :param settings:
        """
        ...

    def escape(self, do_all):
        """

        :param do_all:
        """
        ...

    def parse(self, kind, src, langs):
        """

        :param kind:
        :param src:
        :param langs:
        """
        ...

    def parse_from_po(self, src, langs):
        """

        :param src:
        :param langs:
        """
        ...

    def parse_from_py(self, src, langs):
        """

        :param src:
        :param langs:
        """
        ...

    def print_stats(self, prefix, print_msgs):
        """

        :param prefix:
        :param print_msgs:
        """
        ...

    def unescape(self, do_all):
        """

        :param do_all:
        """
        ...

    def update_info(self):
        """ """
        ...

    def write(self, kind, langs):
        """

        :param kind:
        :param langs:
        """
        ...

    def write_to_po(self, langs):
        """

        :param langs:
        """
        ...

    def write_to_py(self, langs):
        """

        :param langs:
        """
        ...

class I18nMessage:
    """ """

    comment_lines: typing.Any
    """ """

    is_commented: typing.Any
    """ """

    is_fuzzy: typing.Any
    """ """

    is_tooltip: typing.Any
    """ """

    msgctxt: typing.Any
    """ """

    msgctxt_lines: typing.Any
    """ """

    msgid: typing.Any
    """ """

    msgid_lines: typing.Any
    """ """

    msgstr: typing.Any
    """ """

    msgstr_lines: typing.Any
    """ """

    settings: typing.Any
    """ """

    sources: typing.Any
    """ """

    def copy(self):
        """ """
        ...

    def do_escape(self, txt):
        """

        :param txt:
        """
        ...

    def do_unescape(self, txt):
        """

        :param txt:
        """
        ...

    def escape(self, do_all):
        """

        :param do_all:
        """
        ...

    def normalize(self, max_len):
        """

        :param max_len:
        """
        ...

    def unescape(self, do_all):
        """

        :param do_all:
        """
        ...

class I18nMessages:
    """ """

    parsers: typing.Any
    """ """

    writers: typing.Any
    """ """

    def check(self, fix):
        """

        :param fix:
        """
        ...

    def clean_commented(self):
        """ """
        ...

    def escape(self, do_all):
        """

        :param do_all:
        """
        ...

    def find_best_messages_matches(
        self, msgs, msgmap, rna_ctxt, rna_struct_name, rna_prop_name, rna_enum_name
    ):
        """

        :param msgs:
        :param msgmap:
        :param rna_ctxt:
        :param rna_struct_name:
        :param rna_prop_name:
        :param rna_enum_name:
        """
        ...

    def gen_empty_messages(
        self, uid, blender_ver, blender_hash, bl_time, default_copyright, settings
    ):
        """

        :param uid:
        :param blender_ver:
        :param blender_hash:
        :param bl_time:
        :param default_copyright:
        :param settings:
        """
        ...

    def invalidate_reverse_cache(self, rebuild_now):
        """

        :param rebuild_now:
        """
        ...

    def merge(self, msgs, replace):
        """

        :param msgs:
        :param replace:
        """
        ...

    def normalize(self, max_len):
        """

        :param max_len:
        """
        ...

    def parse(self, kind, key, src):
        """

        :param kind:
        :param key:
        :param src:
        """
        ...

    def parse_messages_from_po(self, src, key):
        """

        :param src:
        :param key:
        """
        ...

    def print_info(self, prefix, output, print_stats, print_errors):
        """

        :param prefix:
        :param output:
        :param print_stats:
        :param print_errors:
        """
        ...

    def rtl_process(self):
        """ """
        ...

    def unescape(self, do_all):
        """

        :param do_all:
        """
        ...

    def update(self, ref, use_similar, keep_old_commented):
        """

        :param ref:
        :param use_similar:
        :param keep_old_commented:
        """
        ...

    def update_info(self):
        """ """
        ...

    def write(self, kind, dest):
        """

        :param kind:
        :param dest:
        """
        ...

    def write_messages_to_mo(self, fname):
        """

        :param fname:
        """
        ...

    def write_messages_to_po(self, fname, compact):
        """

        :param fname:
        :param compact:
        """
        ...

def enable_addons(addons, support, disable, check_only):
    """ """

    ...

def find_best_isocode_matches(uid, iso_codes):
    """ """

    ...

def get_best_similar(data):
    """ """

    ...

def get_po_files_from_dir(root_dir, langs):
    """ """

    ...

def is_valid_po_path(path):
    """ """

    ...

def list_po_dir(root_path, settings):
    """ """

    ...

def locale_explode(locale):
    """ """

    ...

def locale_match(loc1, loc2):
    """ """

    ...
