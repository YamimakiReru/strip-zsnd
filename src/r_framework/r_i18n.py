from .log import _FrameworkLogMixin
import r_framework as r

import i18n
import gettext
import locale
import ctypes
from pathlib import Path
import os

class I18nConfigurator(_FrameworkLogMixin):
    GETTEXT_KEY_PREFIX = 'gettext.'
    NGETTEXT_KEY_PREFIX = 'ngettext.'
    FALLBACK = 'en'
    FORMAT = 'yml'

    def configure(self, app_name: str, app_dir: Path):
        locale_dir = app_dir / 'locales'

        i18n.set('fallback', self.FALLBACK)
        i18n.set('file_format', self.FORMAT)
        i18n.set('filename_format', f'{app_name}.{{locale}}.{{format}}')
        i18n.load_path.append(str(locale_dir))

        available_locales = []
        for msg_file in locale_dir.glob(f'{app_name}.*.{self.FORMAT}'):
            _, loc = msg_file.stem.split('.', 1)
            available_locales.append(loc)
        i18n.set('available_locales', available_locales)

        # reflect OS locale
        locale.setlocale(locale.LC_ALL, '')
        lang = self._determine_locale(available_locales)
        i18n.set('locale', lang or self.FALLBACK)

        i18n.set('on_missing_translation', self._on_missing_translation)
        self.hook_gettext()

    def hook_gettext(self):
        # gettext.gettext() calls dgettext() internally
        gettext.dgettext = self._gettext_hook_proc
        gettext.dngettext = self._ngettext_hook_proc

    @classmethod
    def _on_missing_translation(cls, key, locale, **kwargs):
        if not key.startswith(cls.GETTEXT_KEY_PREFIX):
            return key
        if r.DEBUG:
            cls.get_logger().debug(f'missing translation: [{key}]')
            return key
        return key.removeprefix(cls.GETTEXT_KEY_PREFIX)

    @classmethod
    def _gettext_hook_proc(cls, domain, key):
        return i18n.t(cls.GETTEXT_KEY_PREFIX + key)

    @classmethod
    def _ngettext_hook_proc(cls, domain, msgid1, msgid2, n):
        actual_key = cls.NGETTEXT_KEY_PREFIX + msgid1
        result = i18n.t(actual_key, count=n)
        if actual_key != result:
            return result
        alternative_key = cls.GETTEXT_KEY_PREFIX + msgid1
        result = i18n.t(alternative_key)
        if alternative_key != result:
            return result
        return msgid1

    def _determine_locale(self, available_locales: list[str]) -> str | None:
        locale_ids = locale.getlocale()
        if locale_ids:
            result = self._is_available_locale(locale_ids[0], available_locales)
            if result:
                return result

        result = self._is_available_locale(os.getenv('LANG'), available_locales) \
                or self._is_available_locale(os.getenv('LC_MESSAGES'), available_locales)
        if result:
            return result

        # On Windows, the locale ID may not be in POIX format
        if 'nt' == os.name:
            lcid = ctypes.windll.kernel32.GetUserDefaultLCID()
            if lcid in locale.windows_locale:
                actual_locale_id = locale.windows_locale[lcid]
                if actual_locale_id in available_locales:
                    return actual_locale_id
                lang = actual_locale_id.split('_')[0]
                if lang in available_locales:
                    return lang

    def _is_available_locale(self, locale_id: str|None, available_locales: list[str]) -> str|None:
        '''
        :return: When the locale_id is available, the locale_id or its language code. Otherwise None.
        '''
        if not locale_id:
            return None
        if locale_id in available_locales:
            return locale_id
        lang = locale_id.split('_')[0]
        if lang in available_locales:
            return lang
        return None
