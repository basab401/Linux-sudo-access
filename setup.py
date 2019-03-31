from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import os
import sys

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

reqs = parse_requirements('requirements.txt', session=False)
requirements = [str(ir.req) for ir in reqs]

g_use_supervisor = 0

if '--use_supervisor' in sys.argv:
    index = sys.argv.index('--use_supervisor')
    sys.argv.pop(index)
    g_use_supervisor = sys.argv.pop(index)

class InstallCmd(install):
  def run(self):
    install.run(self)
    if not g_use_supervisor:
        # Use systemd to manage the service
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        install_script_path = os.path.join(current_dir_path, 'install_service', 'create_systemd_service.sh')
        subprocess.check_output([install_script_path])

setup(name='sudo-access',
      version='1.0.1',
      description='sudo access grant service',
      license='Apache 2.0',
      author='Basabjit',
      author_email='basab401@yahoo.co.in',
      python_requires='>=2.7.*,>=3.5.*',
      packages=find_packages(),
      scripts=['bin/sudo-access'],
      cmdclass={'install': InstallCmd},
      install_requires=requirements,
      classifiers=[
        'Intended Audience :: Linux Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
      ],
      keywords='sudo'
)

