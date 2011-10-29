import os, logging, tempfile, setuptools, shutil, tarfile
import zc.buildout
import zc.buildout.download
import zc.buildout.easy_install
import zc.recipe.egg

__author__ = 'joaoalf'

class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.url = self.options['url']

        location = options.get(
            'location', buildout['buildout']['parts-directory'])
        options['location'] = os.path.join(location, name)
        options['prefix'] = options['location']


    def install(self):
        logger = logging.getLogger(self.name)
        dest = self.options['location']
        url = self.options['url']
        download = zc.buildout.download.Download(
            self.buildout['buildout'], namespace='cmmi', hash_name=True,
            logger=logger)

#        if self.shared:
#            if os.path.isdir(self.shared):
#                logger.info('using existing shared build')
#                return self.shared

        fname, is_temp = download(self.url, md5sum=self.options.get('md5sum'))

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
                        os.chdir(os.path.join(entries[0], 'python'))
                    else:
                        raise ValueError("Couldn't find setup.py")

                logger.info('Fixing setup.py')
                os.rename('setup.py', 'setup.py.orig')
                setup_orig = open('setup.py.orig')
                setup_new = []
                found_import = False
                inside_includes_dir = False
                done_includes_dir = False
                inside_libdirs = False
                done_libdirs = False
                #setup_orig = open("")
                for line in setup_orig.readlines():
                    if line.find('from distutils.core import setup') != -1:
                        if not found_import:
                            line = 'from setuptools import setup, Extension\n'
                            found_import = True

                    elif line.find('includes_dir = [') != -1:
                        inside_includes_dir = True
                    elif line.find('libdirs = [') != -1:
                        inside_libdirs = True
                    elif inside_includes_dir:
                        if not done_includes_dir:
                            setup_new.append(
                                ''.join(["'", self.options['libiconv-include-dir'], "'", ',']) + '\n')
                            setup_new.append(
                                ''.join(["'", self.options['libxml2-include-dir'], "'", ',']) + '\n')
                            setup_new.append(
                                ''.join(["'", self.options['libxslt-include-dir'], "'", ',']) + '\n')
                            done_includes_dir = True

                        else:
                            if line == ']\n' or line == '];\n':
                                inside_includes_dir = False
                                setup_new.append(']\n')
                        continue

                    elif inside_libdirs:
                        if not done_libdirs:
                            setup_new.append(
                                ''.join(["'", self.options['libiconv-lib-dir'], "'", ',']) + '\n')
                            setup_new.append(
                                ''.join(["'", self.options['libxml2-lib-dir'], "'", ',']) + '\n')
                            setup_new.append(
                                ''.join(["'", self.options['libxslt-lib-dir'], "'", ',']) + '\n')
                            done_libdirs = True

                        else:
                            if line == ']\n' or line == '];\n':
                                inside_libdirs = False
                                setup_new.append(']\n')
                        continue

                    setup_new.append(line)

                try:
                    f = open('setup.py', 'w')
                    f.writelines(setup_new)
                    f.close()
                except:
                    logger.info('Error fixing setup.py')
                    raise

                libxml2_version = os.listdir('../..')[0][8:]

                #os.system("python setup.py sdist")
                os.system("python setup.py bdist_egg")
                distr_name = os.listdir('dist')[0]
                if os.path.exists(os.path.join(here, distr_name)):
                    os.unlink(os.path.join(here, distr_name))

                os.rename(os.path.join('dist', os.listdir('dist')[0]), os.path.join(here, distr_name))
                #try:
                #    with tarfile.open(
                #        os.path.join(
                #            here,  distr_name), "w:gz") as tar:
                #        for name in os.listdir('.'):
                #            tar.add(name)
                #except:
                #    raise
                
                #os.system("python setup.py bdist_egg --dist-dir %s" % self.buildout['buildout']['eggs-directory'])
                #os.system("make install")
                #logger.info("Dir: %s", tmp)
                #logger.info("")
            finally:
                os.chdir(here)
        except:
            shutil.rmtree(dest)
            raise

        return dest

    update = install



