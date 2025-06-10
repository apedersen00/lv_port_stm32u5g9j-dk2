cmake_minimum_required(VERSION 3.22)

# Setup compiler settings
set(CMAKE_C_STANDARD            11)
set(CMAKE_C_STANDARD_REQUIRED   ON)
set(CMAKE_C_EXTENSIONS          ON)

# Define the build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Debug")
endif()
message("Build type: " ${CMAKE_BUILD_TYPE})

# Set paths
set(CORE_DIR            ${CMAKE_SOURCE_DIR}/Core)
set(HAL_DIR             ${CMAKE_SOURCE_DIR}/Drivers/STM32U5xx_HAL_Driver)
set(LVGL_DIR            ${CMAKE_SOURCE_DIR}/lvgl)
set(CMSIS_DIR           ${CMAKE_SOURCE_DIR}/Drivers/CMSIS)
set(NEMA_DIR            ${CMAKE_SOURCE_DIR}/lvgl/libs/nema_gfx)

# Enable compile command to ease indexing with e.g. clangd
set(CMAKE_EXPORT_COMPILE_COMMANDS TRUE)

# Compiler options
set(STM32_MCU_FLAGS  "-mcpu=cortex-m33 -mfpu=fpv4-sp-d16 -mfloat-abi=hard" )

# Set linker script
set(STM32_LINKER_SCRIPT "STM32U5G9ZJTXQ_FLASH.ld")

## Include toolchain file
include("${CMAKE_SOURCE_DIR}/cmake/gcc-arm-none-eabi.cmake")

# Set the project name
set(CMAKE_PROJECT_NAME STM32U5G9J-DK2_LVGL)
project(${CMAKE_PROJECT_NAME})

# Create an executable object type
add_executable(${CMAKE_PROJECT_NAME})

# Enable CMake support for ASM and C languages
enable_language(C ASM)

# In order to use CMake for cross-compiling
set(CMAKE_CXX_COMPILER_FORCED "true") 

# Add project symbols (macros)
target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE
    DEBUG
    USE_HAL_DRIVER
    STM32U5G9xx
)

# Add include paths
target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE
    ${CMAKE_SOURCE_DIR}
    ${CMSIS_DIR}/Include
    ${CMSIS_DIR}/Device/ST/STM32U5xx/Include
    ${CORE_DIR}/Inc
    ${HAL_DIR}/Inc
    ${LVGL_DIR}
    ${NEMA_DIR}/include
)

# Add compiler specific sources
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ${CORE_DIR}/Startup/startup_stm32u5g9zjtxq.s
)

# Core
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ${CORE_DIR}/Src/lvgl_port.c
    ${CORE_DIR}/Src/main.c
    ${CORE_DIR}/Src/stm32u5xx_hal_msp.c
    ${CORE_DIR}/Src/stm32u5xx_hal_timebase_tim.c
    ${CORE_DIR}/Src/stm32u5xx_it.c
    ${CORE_DIR}/Src/syscalls.c
    ${CORE_DIR}/Src/sysmem.c
    ${CORE_DIR}/Src/system_stm32u5xx.c
)

# HAL
file(GLOB_RECURSE HAL_SOURCES "${HAL_DIR}/Src/*.c")
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ${HAL_SOURCES}
)

# LVGL core sources
file(GLOB_RECURSE LVGL_SOURCES "${LVGL_DIR}/src/*.c")
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ${LVGL_SOURCES}
)

file(GLOB_RECURSE EXAMPLES_SOURCES "${LVGL_DIR}/demos/widgets/*.c")
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ${EXAMPLES_SOURCES}
)

file(GLOB_RECURSE EXAMPLES_SOURCES "${LVGL_DIR}/demos/benchmark/*.c")
target_sources(${CMAKE_PROJECT_NAME} PRIVATE
    ${EXAMPLES_SOURCES}
)

target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE
    ${NEMA_DIR}/lib/core/cortex_m33_revC/gcc/libnemagfx-float-abi-hard.a
)

# Validate that STM32CubeMX code is compatible with C standard
if(CMAKE_C_STANDARD LESS 11)
    message(ERROR "Generated code requires C11 or higher")
endif()
