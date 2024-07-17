from typing import Optional
import sys

argc = len(sys.argv)

project_name = None
project_path = None

def get_next_arg(current_pos: int) -> Optional[str]:
    if argc - 1 >= current_pos + 1:
        return sys.argv[current_pos + 1]
    return None


for i, arg in enumerate(sys.argv):
    if arg == "--name":
        project_name = get_next_arg(i)
    elif arg == "--path":
        project_path = get_next_arg(i)

if project_name is None and project_path is None:
    print("Usage: generator.py --name <your-project-name> --path <your-project-path>")
    exit()
elif project_name is None:
    print("You need to provide project name with --name <your-project-name>")
    exit()
elif project_path is None:
    print("You need to project your project path with --path <your-project-path>")
    exit()

import os, subprocess

if not os.path.exists(project_path):
    os.mkdir(project_path)

if len(os.listdir(project_path)) != 0:
    print("The project path must be empty")
    exit()

os.mkdir(os.path.join(project_path, project_name))

with open(os.path.join(project_path, "CMakeLists.txt"), "w") as f:
    f.write(f"""
# CMakeList.txt : Top-level CMake project file, do global configuration
# and include sub-projects here.
#
cmake_minimum_required (VERSION 3.8)

# Enable Hot Reload for MSVC compilers if supported.
if (POLICY CMP0141)
  cmake_policy(SET CMP0141 NEW)
  set(CMAKE_MSVC_DEBUG_INFORMATION_FORMAT "$<IF:$<AND:$<C_COMPILER_ID:MSVC>,$<CXX_COMPILER_ID:MSVC>>,$<$<CONFIG:Debug,RelWithDebInfo>:EditAndContinue>,$<$<CONFIG:Debug,RelWithDebInfo>:ProgramDatabase>>")
endif()

project ("{project_name}")

# Include sub-projects.
add_subdirectory ("{project_name}")

# Include all 3rdparty libraries
include("cmake/botcraft.cmake")

set_target_properties(${{PROJECT_NAME}} PROPERTIES DEBUG_POSTFIX "_d")
set_target_properties(${{PROJECT_NAME}} PROPERTIES RELWITHDEBINFO_POSTFIX "_rd")


if(MSVC)
    # To avoid having one subfolder per configuration when building with Visual
    set_target_properties(${{PROJECT_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_DEBUG "${{BOTCRAFT_OUTPUT_DIR}}/bin")
    set_target_properties(${{PROJECT_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELEASE "${{BOTCRAFT_OUTPUT_DIR}}/bin")
    set_target_properties(${{PROJECT_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${{BOTCRAFT_OUTPUT_DIR}}/bin")
    set_target_properties(${{PROJECT_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${{BOTCRAFT_OUTPUT_DIR}}/bin")
    
    set_property(TARGET ${{PROJECT_NAME}} PROPERTY VS_DEBUGGER_WORKING_DIRECTORY "${{BOTCRAFT_OUTPUT_DIR}}/bin")
else()
    set_target_properties(${{PROJECT_NAME}} PROPERTIES RUNTIME_OUTPUT_DIRECTORY "${{BOTCRAFT_OUTPUT_DIR}}/bin")
endif(MSVC)
""")

with open(os.path.join(project_path, project_name, "CMakeLists.txt"), "w") as f:
    f.write(
        f"""
# CMakeList.txt : CMake project for BurgerBot, include source and define
# project specific logic here.
#

# Add source to this project's executable.
add_executable ({project_name} "main.cpp")

if (CMAKE_VERSION VERSION_GREATER 3.12)
  set_property(TARGET {project_name} PROPERTY CXX_STANDARD 20)
endif()


# Link libraries
target_link_libraries(${{PROJECT_NAME}} botcraft)

# TODO: Add tests and install targets if needed.

"""
)

with open(os.path.join(project_path, project_name, "main.cpp"), "w") as f:
    f.write("""int main(int argc, char* argv[]) {}""")

os.mkdir(os.path.join(project_name, "3rdparty"))

subprocess.Popen(
    ["git", "init"],
    cwd=project_path,
).wait()

subprocess.Popen(
    ["git", "submodule", "add", "https://github.com/adepierre/Botcraft", "3rdparty/Botcraft"],
    cwd=project_path
).wait()