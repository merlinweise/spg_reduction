import os
import subprocess

from path_conversion import windows_to_linux_path
from error_handling import print_error

USE_EXACT_ARITHMETIC = False  # If True, replaces floats with exact arithmetic (fractions), default is True
MAX_DENOMINATOR = 2_147_483_647  # 2,147,483,647 is the optimal value for PRISM-games
SSG_TO_SMG_VERSION = 1  # 1: Performant alternating version, 2: Older alternating version, 3: Synchronous version, default is 1

GLOBAL_IN_OUT_PATH_LINUX = ""  # only assign if the OS is Linux, otherwise it will be set to GLOBAL_IN_OUT_PATH_WINDOWS
GLOBAL_IN_OUT_PATH_WINDOWS = "C:\\Uni_Zeug\\6.Semester\\Bachelorarbeit\\PRISMgames_testing\\program_in_and_out"  # only assign if the OS is Windows, otherwise it will be set to GLOBAL_IN_OUT_PATH_LINUX

GLOBAL_DEBUG = False  # If True, prints debug information, default is False
PRINT_VERTEX_CREATION_WARNINGS = False  # If True, prints warnings about deadlock vertices and vertices with no outgoing transitions, default is False

ENSURE_EVE_AND_ADAM_VERTICES = False  # If True, ensures that every SPG and SSG has at least one Eve and one Adam vertex, if False, the algorithm will not ensure this, default is True
PRISM_EPSILON = 1e-6  # Epsilon for PRISM, used for numerical stability in value iteration algorithms, default is 1e-6
MAX_ITERS = 1_000_000_000  # Maximum number of iterations for PRISM algorithms, default is 10000
PRISM_PATH = "/mnt/c/Uni_Zeug/6.Semester/Bachelorarbeit/prism_extension/Algorithms-For-Stochastic-Games/prism-games-3.0.beta-src/prism/bin/prism"  # Path to the PRISM executable, needs to be in Linux format
PRISM_SOLVING_ALGORITHM = "POLICY_ITERATION"  # "VALUE_ITERATION" or "GAUSS_SEIDEL_VALUE_ITERATION" or "POLICY_ITERATION" or "MODIFIED_POLICY_ITERATION" or "INTERVAL_ITERATION" or "SOUND_VALUE_ITERATION" or "TOPOLOGICAL VALUE_ITERATION" or "SOUND_TOPOLOGICAL_VALUE_ITERATION" or "SOUND_POLICY_ITERATION" or "SOUND_MODIFIED_POLICY_ITERATION"


# ---------------------------------------------Automatic Settings-------------------------------------------------------

if GLOBAL_IN_OUT_PATH_LINUX == "" and GLOBAL_IN_OUT_PATH_WINDOWS == "":
    print_error("Global input/output path is not set. Please set GLOBAL_IN_OUT_PATH_LINUX or GLOBAL_IN_OUT_PATH_WINDOWS.")
if GLOBAL_IN_OUT_PATH_LINUX == "":
    GLOBAL_IN_OUT_PATH_LINUX = windows_to_linux_path(GLOBAL_IN_OUT_PATH_WINDOWS)

GLOBAL_IN_OUT_PATH = GLOBAL_IN_OUT_PATH_LINUX if os.name == 'posix' else GLOBAL_IN_OUT_PATH_WINDOWS

IS_OS_LINUX = os.name == 'posix'  # Check if the OS is Linux
if not IS_OS_LINUX:
    # Test if WSL is installed
    result = subprocess.run(["wsl", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    IS_WSL_INSTALLED = result.returncode == 0
else:
    IS_WSL_INSTALLED = False
if not IS_OS_LINUX and not IS_WSL_INSTALLED:
    print("Error: The current OS is not Linux nor is WSL installed. Please run this script on a Linux system or install WSL.")
match PRISM_SOLVING_ALGORITHM:  # Set the PRISM solving algorithm, used for property checking
    case "VALUE_ITERATION":
        PRISM_SOLVING_ALGORITHM = "-valiter"
    case "GAUSS_SEIDEL_VALUE_ITERATION":
        PRISM_SOLVING_ALGORITHM = "-gaussseidel"
    case "POLICY_ITERATION":
        PRISM_SOLVING_ALGORITHM = "-politer"
    case "MODIFIED_POLICY_ITERATION":
        PRISM_SOLVING_ALGORITHM = "-modpoliter"
    case "INTERVAL_ITERATION":
        PRISM_SOLVING_ALGORITHM = "-intervaliter"
    case "SOUND_VALUE_ITERATION":
        PRISM_SOLVING_ALGORITHM = "-soundvaliter"
    case "TOPOLOGICAL_VALUE_ITERATION":
        PRISM_SOLVING_ALGORITHM = "-topological"
    case _:
        PRISM_SOLVING_ALGORITHM = ""  # PRISM default algorithm, which is "VALUE_ITERATION"
