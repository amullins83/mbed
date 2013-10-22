import sys
from os.path import join, abspath, dirname
from shutil import copy
from time import sleep

# Be sure that the tools directory is in the search path
ROOT = abspath(join(dirname(__file__), ".."))
sys.path.append(ROOT)

from workspace_tools.options import get_default_options_parser
from workspace_tools.build_api import build_project
from workspace_tools.tests import TESTS, Test, TEST_MAP
from workspace_tools.paths import BUILD_DIR, RTOS_LIBRARIES
from workspace_tools.targets import TARGET_MAP
from workspace_tools.utils import args_error
try:
    import workspace_tools.private_settings as ps
except:
    ps = object()


if __name__ == '__main__':
    # Parse Options
    parser = get_default_options_parser()
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False, help="Verbose diagnostic output")
    parser.add_option("-D", "", action="append", dest="macros",
                      help="Add a macro definition")

    # Local run
    parser.add_option("--automated", action="store_true", dest="automated",
                      default=False, help="Automated test")
    parser.add_option("--host", dest="host_test",
                      default=None, help="Host test")
    parser.add_option("--extra", dest="extra",
                      default=None, help="Extra files")
    parser.add_option("--peripherals", dest="peripherals",
                      default=None, help="Required peripherals")
    parser.add_option("--dep", dest="dependencies",
                      default=None, help="Dependencies")
    parser.add_option("--source", dest="source_dir",
                      default=None, help="The source (input) directory")
    parser.add_option("--duration", type="int", dest="duration",
                      default=None, help="Duration of the test")
    parser.add_option("--build", dest="build_dir",
                      default=None, help="The build (output) directory")
    parser.add_option("-d", "--disk", dest="disk",
                      default=None, help="The mbed disk")
    parser.add_option("-s", "--serial", dest="serial",
                      default=None, help="The mbed serial port")
    parser.add_option("-b", "--baud", type="int", dest="baud",
                      default=None, help="The mbed serial baud rate")

    # Ideally, all the tests with a single "main" thread can be run with, or
    # without the rtos
    parser.add_option("--rtos", action="store_true", dest="rtos",
                      default=False, help="Link to the rtos")

    # Specify a different linker script
    parser.add_option("-l", "--linker", dest="linker_script",
                      default=None, help="use the specified linker script")

    (options, args) = parser.parse_args()

    # Target
    if options.mcu is None :
        args_error(parser, "[ERROR] You should specify an MCU")
    mcu = options.mcu

    # Toolchain
    if options.tool is None:
        args_error(parser, "[ERROR] You should specify a TOOLCHAIN")
    toolchain = options.tool

    target = TARGET_MAP[mcu]

    passed_tests = []
    failed_tests = []

    try:
        for p in range(len(TEST_MAP)):
        # Test
            test = Test(p)
    
            if test.is_supported(mcu, toolchain):
                if options.automated is not None:
                    test.automated = options.automated
                if options.dependencies is not None:
                    test.dependencies = options.dependencies
                if options.host_test is not None:
                    test.host_test = options.host_test;
                if options.peripherals is not None:
                    test.peripherals = options.peripherals;
                if options.duration is not None:
                    test.duration = options.duration;
                if options.extra is not None:
                    test.extra_files = options.extra
    
                # RTOS
                if options.rtos:
                    test.dependencies.append(RTOS_LIBRARIES)
    
                build_dir = join(BUILD_DIR, "test", mcu, toolchain, test.id)
                if options.source_dir is not None: 
                    test.source_dir = options.source_dir
                    build_dir = options.source_dir
    
                if options.build_dir is not None: 
                    build_dir = options.build_dir

                try:
                    bin = build_project(test.source_dir, build_dir, target, toolchain,
                                        test.dependencies, options.options,
                                        linker_script=options.linker_script,
                                        clean=options.clean, verbose=options.verbose,
                                        macros=options.macros)
                    print 'Image: %s' % bin
                    passed_tests.append(test)
                except Exception,e:
                    print "[ERROR] %s" % str(e)
                    failed_tests.append(test)
    except KeyboardInterrupt, e:
        print "\n[CTRL+c] exit"

    print "\n\nSummary:\n"

    print "Passed:\n"
    for test in passed_tests:
        print(test)
    print "\nTotal passed: %d\n", len(passed_tests)

    print "Failed:\n"
    for test in failed_tests:
        print(test)
    print "\nTotal failed: %d\n", len(failed_tests)
