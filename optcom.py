import subprocess
import re
import os

# Define the set of mutually exclusive optimization flags
optimization_levels = [
    "-O0",
    "-O1",
    "-O2",
    "-O3",
    "-Ofast",
    "-Os",
    "-Og"
]

# Define the set of other independent optimization flags
independent_flags = [
    "-ffast-math",
    "-funroll-loops",
    "-march=native",
    "-flto",
    "-fomit-frame-pointer"
]

# Get the number of CPUs available
num_cpus = os.cpu_count()

# Function to run a shell command with given environment variables and return the user time
def run_command(command, env=None):
    print(f"Running command: {command}")
    result = subprocess.run(f"/usr/bin/time -f '%U' {command}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    user_time_match = re.search(r'(\d+\.\d+)', result.stderr.decode())
    user_time = float(user_time_match.group(1)) if user_time_match else float('inf')
    return result.returncode, user_time

# Function to configure, build, and check the program with given CFLAGS and CXXFLAGS
def build_and_check(flags):
    env = os.environ.copy()
    env["CFLAGS"] = " ".join(flags)
    env["CXXFLAGS"] = " ".join(flags)
    commands = [
        "./configure",
        "make clean",  # Ensure a clean build environment
        f"make -j{num_cpus}"
    ]
    
    print("Starting configuration and build process.")
    for command in commands:
        returncode, _ = run_command(command, env)
        if returncode != 0:
            return False, float('inf')
    
    # Run "make check" four times and take the average of the last three
    check_times = []
    print("Starting 'make check' runs.")
    for i in range(4):
        print(f"Running 'make check' (iteration {i + 1})")
        returncode, user_time = run_command("make check", env)
        if returncode != 0:
            return False, float('inf')
        check_times.append(user_time)
    
    avg_user_time = sum(check_times[1:]) / 3
    return True, avg_user_time

# Function to find the best -O optimization level
def find_best_optimization_level():
    best_flag = None
    best_time = float('inf')
    for flag in optimization_levels:
        print(f"Testing optimization level: {flag}")
        success, user_time = build_and_check([flag])
        if success:
            print(f"Optimization level {flag} user time: {user_time:.2f} seconds")
            if user_time < best_time:
                best_flag = flag
                best_time = user_time
        else:
            print(f"Optimization level {flag} caused failure")
    return best_flag, best_time

# Main function to find the optimal set of flags
def find_optimal_flags():
    # Determine the best -O optimization level
    best_optimization_level, best_time = find_best_optimization_level()
    print(f"Best optimization level: {best_optimization_level} with time {best_time:.2f} seconds")

    # Start with the best -O optimization level
    optimal_flags = [best_optimization_level]
    
    # Test the independent flags cumulatively
    for flag in independent_flags:
        print(f"Testing flag: {flag}")
        test_flags = optimal_flags + [flag]
        success, user_time = build_and_check(test_flags)
        if success:
            print(f"Flag {flag} user time: {user_time:.2f} seconds")
            if user_time < best_time:
                print(f"Flag {flag} improved performance.")
                best_time = user_time
                optimal_flags.append(flag)
            else:
                print(f"Flag {flag} did not improve performance.")
        else:
            print(f"Flag {flag} caused failure")

    return optimal_flags

if __name__ == "__main__":
    optimal_flags = find_optimal_flags()
    print("Optimal flags:", " ".join(optimal_flags))
    
    # Run final make with optimal flags
    print("Running final make with optimal flags...")
    build_and_check(optimal_flags)
    
    print("Final build complete. To install the optimized binary, run 'make install'.")
