#!/usr/bin/env python3

import os
import subprocess

# Define compilation flags
exclusive_flags = ['-O0', '-O1', '-O2', '-O3', '-Os', '-Ofast']
independent_flags = [
    '-mtune=native', '-fpic', '-fPIC', '-Os',
    '-march=native', '-fdata-sections', '-ffunction-sections',
    '-funroll-loops', '-ftree-loop-optimize', '-floop-parallelize-all',
    '-ftree-partial-pre', '-funsafe-math-optimizations',
    '-fgcse-sm', '-fgcse-las=all', '-fsched-spec-load', '-fsplit-loops',
    '-fsched-pressure', '-fipa-pta', '-floop-nest-optimize', '-fsection-anchors',
    '-ftree-loop-im', '-fivopts', '-ftree-parallelize-loops=4',
    '-ffinite-math-only', '-fno-signed-zeros', '-fno-signaling-nans -fno-trapping-math'
]

# Number of processors to use
nproc = str(os.cpu_count())


def run_command(command, env):
    # Improved command execution with subprocess.run
    result = subprocess.run(
        ["/usr/bin/time", "-f", "%U", "bash", "-c", command],
        text=True,
        env=env,
        capture_output=True
    )

    try:
        user_time = float(result.stderr.strip())
    except ValueError:
        user_time = float('inf')

    return user_time


def compile_and_test(flags):
    # Set the environment variables for compilation flags
    env = {'CFLAGS': ' '.join(flags), 'CXXFLAGS': ' '.join(flags)}

    try:
        # Run the configure script
        subprocess.run(['./configure'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, check=True)

        # Run make clean and parallel make
        subprocess.run(['make', 'clean'],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        subprocess.run(['make', '-j', nproc],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        # Run 'make check' four times and average the last three runs
        times = [run_command('make check', env) for _ in range(4)]
        avg_time = sum(times[1:]) / 3  # Average of the last three runs
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing: {e.cmd}")
        print(f"Error message: {e.stderr if e.stderr else 'No stderr output available.'}")
        avg_time = float('inf')

    return avg_time


def final_build(flags):
    env = {'CFLAGS': ' '.join(flags), 'CXXFLAGS': ' '.join(flags)}
    
    # Run the configure and final parallel make build
    subprocess.run(['./configure'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, check=True)
    subprocess.run(['make', 'clean'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(['make', '-j', nproc], check=True)
    
    print("Final build complete with optimal flags. You can now run 'make install' to install the optimized binary.")

    
def main():
    best_time = float('inf')
    best_flags = []

    for flag in exclusive_flags:
        print(f"Testing exclusive flag: {flag}")
        exec_time = compile_and_test([flag])
        print(f"Execution time with {flag}: {exec_time}s")

        if exec_time < best_time:
            best_time = exec_time
            best_flags = [flag]
            print(f"*** Best exclusive flag so far: {best_flags} with time: {best_time}s")

    for flag in independent_flags:
        current_flags = best_flags + [flag]
        print(f"Testing with flags: {current_flags}")
        exec_time = compile_and_test(current_flags)
        print(f"Execution time with {flag}: {exec_time}s")

        if exec_time < best_time:
            best_time = exec_time
            best_flags.append(flag)
            print(f"*** New optimal flags found: {best_flags} with execution time: {best_time}s")

    final_build(best_flags)

if __name__ == "__main__":
    main()
