import os, logging, tempfile, setuptools, shutil
import zc.buildout
from zc.recipe.cmmi import getFromCache

__author__ = 'joaoalf'

class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        logger = logging.getLogger(self.name)
        dest = self.options['location']
        url = self.options['url']
        fname = getFromCache(
            url, self.name, self.download_cache, self.install_from_cache)

        tmp = tempfile.mkdtemp('buildout-'+self.name)
        logger.info('Unpacking and configuring')
        setuptools.archive_util.unpack_archive(fname, tmp)

        here = os.getcwd()
        if not os.path.exists(dest):
            os.mkdir(dest)

        try:
            os.chdir(tmp)
            try:
                if not os.path.exists('setup.py'):
                    entries = os.listdir(tmp)
                    if len(entries) == 1:
                        os.chdir(entries[0])
                    else:
                        raise ValueError("Couldn't find setup.py")
                logger.info('Fixing setup.py')
                os.rename('setup.py', 'setup.py.orig')
                with open('setup.py.orig') as setup_orig:
                    setup_new = []
                    inside_includes_dir = False
                    done_includes_dir = False
                    inside_libdirs = False
                    done_libdirs = False

                    for line in setup_orig.readlines():
                        if line.find('includes_dir = ['):
                            inside_includes_dir = True

                        if line.find('libdirs = ['):
                            inside_libdirs = True

                        if inside_includes_dir:
                            if not done_includes_dir:
                                setup_new.append(
                                    ''.join(["'", self.options['libiconv-include-dir'], "'", ',']))
                                setup_new.append(
                                    ''.join(["'", self.options['libxml2-include-dir'], "'", ',']))
                                setup_new.append(
                                    ''.join(["'", self.options['libxslt-include-dir'], "'", ',']))
                                done_includes_dir = True

                            else:
                                if line == ']' or line == '];':
                                    inside_includes_dir = False
                                    setup_new.append(']')
                            continue

                        if inside_libdirs:
                            if not done_libdirs_dir:
                                setup_new.append(
                                    ''.join(["'", self.options['libiconv-lib-dir'], "'", ',']))
                                setup_new.append(
                                    ''.join(["'", self.options['libxml2-lib-dir'], "'", ',']))
                                setup_new.append(
                                    ''.join(["'", self.options['libxslt-lib-dir'], "'", ',']))
                                done_libdirs = True

                            else:
                                if line == ']' or line == '];':
                                    inside_libdirs = False
                                    setup_new.append(']')
                            continue

                        setup_new.append(line)

                    try:
                        f = open('setup.py', 'w')
                        f.writelines(setup_new)
                        f.close()
                    except:
                        logger.info('Error fixing setup.py')
                        raise

                    


                os.system("./configure --prefix=%s %s" %
                       (dest, extra_options))
                os.system("make")
                os.system("make install")
            finally:
                os.chdir(here)
        except:
            shutil.rmtree(dest)
            raise

        return dest
        


