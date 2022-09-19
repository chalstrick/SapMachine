import spi
import log
import re
import multiprocessing
import shutil
import subprocess
import os
import glob
import sys
import platform

from os import path
from os.path import join
from xmake_exceptions import XmakeException

class build(spi.BuildPlugin):
  def __init__(self, build_cfg):
    self.build_cfg = build_cfg
    self._root = self.build_cfg.component_dir()
    self.sapmachine_dir = path.abspath(path.join(self.build_cfg.src_dir(), '..'))

    # Don't change the two names without changing export.ads
    self.intel_name = 'intel64'
    self.aarch_name = 'aarch64'

    self.intel_build_dir = path.abspath(path.join(self.sapmachine_dir, self.intel_name))
    self.aarch_build_dir = path.abspath(path.join(self.sapmachine_dir, self.aarch_name))

    # Importing common Functionality
    template_NonPyPi = glob.glob(join(self._root,".xmake","buildplugins","xcode*","externalplugin","template"))
    commons_NonPyPi = glob.glob(join(self._root,".xmake","buildplugins","xcode*","externalplugin","commons"))
    template_PyPi_mob = glob.glob(join(self._root,".xmake","buildplugins",".eggs","xmake_xcode_plugin*","externalplugin","template"))
    commons_PyPi_mob = glob.glob(join(self._root,".xmake","buildplugins",".eggs","xmake_xcode_plugin*","externalplugin","commons"))
    template_PyPi_dev = glob.glob(join(self._root,".xmake","buildplugins","xcode",".eggs","xmake_xcode_plugin*","externalplugin","template"))
    commons_PyPi_dev = glob.glob(join(self._root,".xmake","buildplugins","xcode",".eggs","xmake_xcode_plugin*","externalplugin","commons"))

    if template_NonPyPi and commons_NonPyPi :
        self.template_path = template_NonPyPi[0]
        sys.path.append(self.template_path)
        sys.path.append(commons_NonPyPi[0])

    elif template_PyPi_mob and commons_PyPi_mob :
        self.template_path = template_PyPi_mob[0]
        sys.path.append(self.template_path)
        sys.path.append(commons_PyPi_mob[0])

    elif template_PyPi_dev and commons_PyPi_dev:
        self.template_path = template_PyPi_dev[0]
        sys.path.append(self.template_path)
        sys.path.append(commons_PyPi_dev[0])

    if glob.glob(join(self._root,".xmake","externalplugins","xcode*","externalplugin","template")) and glob.glob(join(self._root,".xmake","externalplugins","xcode*","externalplugin","commons")):
        self.template_path = glob.glob(join(self._root,".xmake","externalplugins","xcode*","externalplugin","template"))[0]
        sys.path.append(glob.glob(join(self._root,".xmake","externalplugins","xcode*","externalplugin","template"))[0])
        sys.path.append(glob.glob(join(self._root,".xmake","externalplugins","xcode*","externalplugin","commons"))[0])

    from commons import Commons
    self.common = Commons(self.build_cfg, '')

  def execute(self, args, cwd=None, env=None):
    log.info("==>> Executing: '" + " ".join(args) + "'\n")
    retcode = subprocess.Popen(args, cwd=cwd, env=env).wait()

    if retcode:
      raise XmakeException("command execution failed")

  def run(self):
    cfg_dir = self.build_cfg.cfg_dir()
    version_file = path.join(cfg_dir, 'VERSION')

    self.determine_signing_settings()

    with open(version_file, 'r') as f:
        sapmachine_version = f.readline()
        sapmachine_version = re.sub(r"[\n\r\s]*", "", sapmachine_version)

    buildnumber_file = path.join(cfg_dir, 'BUILD_NUMBER')

    with open(buildnumber_file, 'r') as f:
        sapmachine_build_number = f.readline()
        sapmachine_build_number = re.sub(r"[\n\r\s]*", "", sapmachine_build_number)

    releasetype_file = path.join(cfg_dir, 'RELEASE_TYPE')

    with open(releasetype_file, 'r') as f:
        sapmachine_release_type = f.readline()
        sapmachine_release_type = re.sub(r"[\n\r\s]*", "", sapmachine_release_type)

    sapmachine_version_parts = sapmachine_version.split('.')
    sapmachine_major = sapmachine_version_parts[0]
    sapmachine_version_extra = ''

    if len(sapmachine_version_parts) > 4:
        sapmachine_version_extra = '--with-version-extra1=' + sapmachine_version_parts[4]

    tools_cfg_file = path.join(cfg_dir, 'tools.cfg')

    with open(tools_cfg_file, 'r') as f:
        tools_content = f.read()
        bootjdk_version  = re.search('\[SAPMACHINE\][^\[]*version=(\S*)', tools_content, re.DOTALL).group(1)
        autoconf_version = re.search('\[AUTOCONF\][^\[]*version=(\S*)', tools_content, re.DOTALL).group(1)
        automake_version = re.search('\[AUTOMAKE\][^\[]*version=(\S*)', tools_content, re.DOTALL).group(1)
        m4_version       = re.search('\[M4\][^\[]*version=(\S*)', tools_content, re.DOTALL).group(1)
        devkit_version   = re.search('\[DEVKIT\][^\[]*version=(\S*)', tools_content, re.DOTALL).group(1)

    bootjdk        = path.join(self.build_cfg.tools()['SAPMACHINE'][bootjdk_version], 'sapmachine-jdk-{0}.jdk'.format(bootjdk_version), 'Contents', 'Home')
    autoconf       = path.join(self.build_cfg.tools()['AUTOCONF'][autoconf_version], 'autoconf-{0}-darwinintel64'.format(autoconf_version), 'bin')
    autoconf_share = path.join(self.build_cfg.tools()['AUTOCONF'][autoconf_version], 'autoconf-{0}-darwinintel64'.format(autoconf_version), 'share', 'autoconf')
    automake       = path.join(self.build_cfg.tools()['AUTOMAKE'][automake_version], 'automake-{0}-darwinintel64'.format(automake_version), 'bin')
    m4             = path.join(self.build_cfg.tools()['M4'][m4_version], 'm4-{0}-darwinintel64'.format(m4_version), 'bin')
    devkit         = path.join(self.build_cfg.tools()['DEVKIT'][devkit_version])

    log.info('autoconf={0}'.format(autoconf))
    log.info('automake={0}'.format(automake))
    log.info('m4={0}'.format(m4))
    log.info('devkit={0}'.format(devkit))

    child_env = os.environ.copy()

    child_env['PATH'] = autoconf + ':' + automake + ':' + m4 + ':' + child_env['PATH']
    child_env['AUTOM4TE'] = path.join(autoconf, 'autom4te')
    child_env['PERL5LIB'] = autoconf_share
    child_env['M4'] = path.join(m4, 'm4')
    child_env['AUTOM4TE_CFG'] = path.join(autoconf_share, 'autom4te.cfg')
    child_env['SDKROOT'] = path.join(devkit, 'Xcode.app', 'Contents', 'Developer', 'Platforms', 'MacOSX.platform', 'Developer', 'SDKs', 'MacOSX.sdk')

    with open(child_env['AUTOM4TE_CFG'], 'r') as f:
        automate_cfg = f.read()

    automate_cfg = automate_cfg.replace('//share/autoconf', autoconf_share)

    with open(child_env['AUTOM4TE_CFG'], 'w') as f:
        f.write(automate_cfg)

    p_out, _ = subprocess.Popen(['sw_vers'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()
    log.info('Mac Version (sw_vers output): {0}'.format(p_out.decode("utf-8").strip().replace('\n', '; ').replace('\t', ' ')))

    log.info('child PATH={0}'.format(child_env['PATH']))
    log.info('child SDKROOT={0}'.format(child_env['SDKROOT']))

    log.info('building SapMachine {0} buildnumber {1}'.format(sapmachine_version, sapmachine_build_number))

    version_opt = ''
    version_pre = ''
    if sapmachine_release_type == 'LTS':
        version_opt = 'LTS-'
    elif sapmachine_release_type == 'EA':
        version_pre = 'ea'

    configure_args = ['bash', '../configure',
        '--with-boot-jdk=' + bootjdk,
        '--with-version-feature=' + sapmachine_major,
        '--with-version-opt=' + version_opt + 'sapmachine',
        '--with-version-build=' + sapmachine_build_number,
        '--with-version-pre=' + version_pre,
        '--with-vendor-version-string=SapMachine',
        '--disable-warnings-as-errors',
        '--with-macosx-bundle-name-base=SapMachine',
        '--with-macosx-bundle-id-base=com.sap.openjdk',
        '--with-jdk-rc-name=SapMachine',
        '--with-vendor-name=SAP SE',
        '--with-vendor-url=https://sapmachine.io/',
        '--with-vendor-bug-url=https://github.com/SAP/SapMachine/issues/new',
        '--with-vendor-vm-bug-url=https://github.com/SAP/SapMachine/issues/new',
        '--with-freetype=bundled',
        '--with-devkit=' + devkit
    ]

    if sapmachine_version_extra:
        configure_args.append(sapmachine_version_extra)

    if self.codesign_identity is not None:
        configure_args.append('--with-macosx-codesign-identity=' + self.codesign_identity)

    intel_configure_args = configure_args.copy()
    aarch_configure_args = configure_args.copy()

    intel_configure_args.append('--openjdk-target=amd64-apple-darwin')
    aarch_configure_args.append('--openjdk-target=aarch64-apple-darwin')

    self.configure_and_make(intel_configure_args, self.intel_build_dir, self.intel_name, child_env)
    self.configure_and_make(aarch_configure_args, self.aarch_build_dir, self.aarch_name, child_env)

  def configure_and_make(self, configure_args, build_dir, build_name, child_env):

    self.execute(['rm', '-rf', build_dir])
    self.execute(['mkdir', build_dir])

    self.execute(configure_args, cwd=build_dir, env=child_env)
    self.execute(['make', 'clean'], cwd=build_dir, env=child_env)
    self.execute(['make', 'JOBS=' + str(multiprocessing.cpu_count()), 'product-bundles', 'legacy-bundles'], cwd=build_dir, env=child_env)

    self.make_exports(build_dir, build_name)

  def make_exports(self, build_dir, build_name):
    for bundle in glob.glob(path.join(build_dir, 'bundles', 'sapmachine-*_bin.tar.gz')):
        if 'sapmachine-jdk' in bundle:
            targz_dest = path.join(self.build_cfg.gen_dir(), 'sapmachine-' + build_name + '-jdk.tar.gz')
            dmg_dest = path.join(self.build_cfg.gen_dir(), 'sapmachine-' + build_name + '-jdk.dmg')
        else:
            targz_dest = path.join(self.build_cfg.gen_dir(), 'sapmachine-' + build_name + '-jre.tar.gz')
            dmg_dest = path.join(self.build_cfg.gen_dir(), 'sapmachine-' + build_name + '-jre.dmg')

        self.execute('rm -rf {0}'.format(targz_dest).split(' '))
        self.execute('rm -rf {0}'.format(dmg_dest).split(' '))
        self.execute('cp {0} {1}'.format(bundle, targz_dest).split(' '))
        self.make_dmg(bundle, os.path.splitext(os.path.splitext(os.path.basename(bundle))[0])[0], dmg_dest)

    for symbols in glob.glob(path.join(build_dir, 'bundles', 'sapmachine-*symbols.tar.gz')):
        dest = path.join(self.build_cfg.gen_dir(), 'sapmachine-' + build_name + '-symbols.tar.gz')

        try:
            os.remove(dest)
        except OSError:
            pass

        print(('copy "{0}" to "{1}" ..'.format(symbols, dest)))
        shutil.copy(symbols, dest)

  def make_dmg(self, bundle, volname, target):
    self.execute('rm -rf dmg_base'.split(' '), cwd=self.sapmachine_dir)
    self.execute('mkdir dmg_base'.split(' '), cwd=self.sapmachine_dir)
    self.execute('tar -xzf {0} -C dmg_base'.format(bundle).split(' '), cwd=self.sapmachine_dir)
    bundle_base_dir = path.basename(path.normpath(glob.glob(path.join(self.sapmachine_dir, 'dmg_base', '*'))[0]))
    self.execute('hdiutil create -srcfolder dmg_base -fs HFS+ -volname {0} {1}'.format(volname, target).split(' '), cwd=self.sapmachine_dir)
    self.sign_file(target)

  def sign_file(self, target, force=False, deep=False):
    if self.codesign_identity is not None:
        args = ['codesign', '-s', self.codesign_identity, '--timestamp']

        if force:
            args.append('--force')

        if deep:
            args.append('--deep')

        args.append(target)

        self.execute(args, cwd=self.sapmachine_dir)

  def determine_signing_settings(self):
    # dev/ent: SAP SE DeveloperID cert for internal distribution/testing
    # comp:    SAP AG DeveloperID cert for external distribution
    # none:    should be a developer build

    self.codesign_identity = None
    companybuild = False
    enterpriseBuild = False
    developmentbuild = False
    localBuild = False

    log.info('V_BUILD_RUNTIME="{}"'.format(os.environ['V_BUILD_RUNTIME']))
    log.info('V_TEMPLATE_TYPE="{}"'.format(os.environ['V_TEMPLATE_TYPE']))

    if 'V_BUILD_RUNTIME' in os.environ and 'V_TEMPLATE_TYPE' in os.environ and os.environ['V_TEMPLATE_TYPE'] != 'OD-common-staging':
        if re.match("darwinintel64_comp.*",os.environ['V_BUILD_RUNTIME']):
            companybuild = True
        if re.match("darwinintel64_ent.*",os.environ['V_BUILD_RUNTIME']):
            enterpriseBuild = True
        if re.match("darwinintel64_dev.*",os.environ['V_BUILD_RUNTIME']):
            developmentbuild = True
    else:
        localBuild = True

    if localBuild:
        raise XmakeException("Could not determine code sign settings")

    if companybuild:
        self.codesign_identity = "Developer ID Application: SAP SE"

    if self.codesign_identity is not None:
        self.common.unlock_ios_keychain(isExecutingCompanybuild=companybuild, isExecutingDevelopmentbuild=developmentbuild)
        self.execute(['rm', '-f', 'sapmachine_codesign_testfile'], cwd=self.sapmachine_dir)
        self.execute(['touch', 'sapmachine_codesign_testfile'], cwd=self.sapmachine_dir)
        self.execute(['codesign', '-s', self.codesign_identity, 'sapmachine_codesign_testfile'], cwd=self.sapmachine_dir)
