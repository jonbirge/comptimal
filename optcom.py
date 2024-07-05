import subprocess

# Define compilation flags
exclusive_flags = ['-O0', '-O1', '-O2', '-O3', '-Os', '-Ofast']
independent_flags = [
    '-mtune=native', '-fpic', '-fPIC',
    '-march=native', '-fdata-sections', '-ffunction-sections',
    '-finline-functions', '-ftree-loop-optimize',
    '-ftree-partial-pre', '-funsafe-math-optimizations',
    '-fgcse-sm', '-fgcse-las', '-fgcse-las=all', '-fsched-spec-load',
    '-fsched-pressure', '-fipa-pta', '--with-isl -floop-nest-optimize',
    '-ftree-loop-im', '-fivopts', '-ftree-parallelize-loops=4'
]

def run_command(command, env):
    # Using the 'time' command to measure user time
    process = subprocess.Popen(
        f"/usr/bin/time -f '%U' {command}",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=env
    )
    _, stderr = process.communicate()

    # Extracting user time from the output
    try:
        user_time = float(stderr.strip().decode())
    except ValueError:
        user_time = float('inf')
    
    return user_time

def compile_and_test(flags):
    # Set the environment variables for compilation flags
    env = {'CFLAGS': ' '.join(flags), 'CXXFLAGS': ' '.join(flags)}
    
    # Run the configure script
    subprocess.run(['./configure'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, check=True)
    
    # Run make clean and parallel make
    subprocess.run(['make', 'clean'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(['make', '-j', str(subprocess.check_output(['nproc'], stderr=subprocess.DEVNULL).strip().decode())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
 
    # Run 'make check' four times and average the last three runs
    times = [run_command('make check', env) for _ in range(4)]
    avg_time = sum(times[1:]) / 3  # Average of the last three runs

    return avg_time

def final_build(flags):
    env = {'CFLAGS': ' '.join(flags), 'CXXFLAGS': ' '.join(flags)}
    
    # Run the configure and final parallel make build
    subprocess.run(['./configure'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, check=True)
    subprocess.run(['make', 'clean'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(['make', '-j', str(subprocess.check_output(['nproc'], stderr=subprocess.DEVNULL).strip().decode())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
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
            print(f"Best exclusive flag so far: {best_flags} with time: {best_time}s")

    for flag in independent_flags:
        current_flags = best_flags + [flag]
        print(f"Testing with flags: {current_flags}")
        exec_time = compile_and_test(current_flags)
        print(f"Execution time with {flag}: {exec_time}s")

        if exec_time < best_time:
            best_time = exec_time
            best_flags.append(flag)
            print(f"New optimal flags found: {best_flags} with execution time: {best_time}s")

    final_build(best_flags)

if __name__ == "__main__":
    main()

