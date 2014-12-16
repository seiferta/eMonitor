import sys


def translateStrings(language_code):
    """
    Translate all strings used in templates and code

    :param language_code: de|en
    """
    from translate_admin import translateAdminStrings
    from translate_frontend import translateFrontendStrings
    from translate_help import translateHelpStrings
    from translate_login import translateLoginStrings

    translateAdminStrings(language_code)
    translateFrontendStrings(language_code)
    translateHelpStrings(language_code)
    translateLoginStrings(language_code)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "usage: tr_init <language-code>"
        sys.exit(1)
    else:
        translateStrings(sys.argv[1])
