import sublime, sublime_plugin
import json
import os
import platform
import subprocess

if platform.system() == 'Darwin':
    os_name = 'osx'
elif  platform.system() == 'Windows':
    os_name = 'windows'
else:
    os_name = 'linux'

# /usr/local/lib/node_modules/lebab/bin/index.js

BIN_PATH = os.path.join(
    sublime.packages_path(),
    os.path.dirname(os.path.realpath(__file__)),
    'lebab-transform.js'
)

class LebabCommand(sublime_plugin.TextCommand):
    def description():
        return "Description works"
    def run(self, edit):
        print("BIN_PATH:",BIN_PATH)
        selected_text = self.get_text()
        code = self.lebabify(selected_text)
        print("Code:\n"+code)

        if code:
            w = sublime.Window.new_file(self.view.window())
            w.settings().set('default_extension', 'js')
            w.set_syntax_file(self.view.settings().get('syntax'))
            w.set_scratch(True)
            w.insert(edit, 0, code)
        else:
            print("Lebab: No code returned")

    def get_text(self):
        if not self.has_selection():
            region = sublime.Region(0, self.view.size())
            return self.view.substr(region)

        selected_text = ''
        for region in self.view.sel():
            selected_text = selected_text + self.view.substr(region) + '\n'
        return selected_text

    def has_selection(self):
        for sel in self.view.sel():
            if sel.a != sel.b:
                return True
        return False

    def get_setting(self, key):
        settings = self.view.settings().get('Babel')
        if settings is None:
            settings = sublime.load_settings('Babel.sublime-settings')
        return settings.get(key)

    def get_setting_by_os(self, key):
        setting = self.get_setting(key)
        if setting:
            return setting.get(os_name)

    def lebabify(self, data):
        try:
            return node_bridge(data, BIN_PATH, [json.dumps({
                # from sublime
                'filename': self.view.file_name(),
                'newline_at_eof': self.view.settings().get('ensure_newline_at_eof_on_save'),
                # from babel-sublime settings
                'debug': True, # self.get_setting('debug'),
                'use_local_babel': self.get_setting('use_local_babel'),
                'node_modules': self.get_setting_by_os('node_modules'),
                'options': self.get_setting('options')
            })])
        except Exception as e:
            return str(e)

def node_bridge(data, bin, args=[]):
    env = os.environ.copy()
    startupinfo = None
    if os_name == 'osx':
        # GUI apps in OS X don't contain .bashrc/.zshrc set paths
        env['PATH'] += ':/usr/local/bin'
    elif os_name == 'windows':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    try:
        p = subprocess.Popen(
            ['node', bin] + args,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            startupinfo=startupinfo
        )
    except OSError:
        raise Exception('Error: Couldn\'t find "node" in "%s"' % env['PATH'])
    stdout, stderr = p.communicate(input=data.encode('utf-8'))
    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')
    if stderr:
        raise Exception('Error: %s' % stderr)
    else:
        return stdout
