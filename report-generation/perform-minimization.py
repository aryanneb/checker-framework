import os
import subprocess
import shutil
import platform
import config

#update these absolute paths for your environment
JDK_REPO_PATH = config.JDK_REPO_PATH
CHECKER_FRAMEWORK_REPO_PATH = config.CHECKER_FRAMEWORK_REPO_PATH
script_dir = os.path.dirname(os.path.realpath(__file__))
RESULTS_BASE_DIR = os.path.join(script_dir, "results")
os.makedirs(RESULTS_BASE_DIR, exist_ok=True)

if platform.system() == "Windows":
    gradle_task_cmd  = ["cmd", "/c", "gradlew.bat", "copyAndMinimizeAnnotatedJdkFiles"]
else:
    gradle_task_cmd  = ["sh", "./gradlew", "copyAndMinimizeAnnotatedJdkFiles"]

#error messages for missing directories
if not os.path.isdir(JDK_REPO_PATH):
    print(f"'{JDK_REPO_PATH}' not found. Please ensure you have the JDK repo on your local machine")
    exit(1)

if not os.path.isdir(CHECKER_FRAMEWORK_REPO_PATH):
    print(f"'{CHECKER_FRAMEWORK_REPO_PATH}' not found. Please ensure you have the Checker Framework repo on your local machine")
    exit(1)

if not os.path.isdir(RESULTS_BASE_DIR):
    print(f"'{RESULTS_BASE_DIR}' not found. Please create this directory in the report-generation directory.")
    exit(1)


#move into JDK repository
os.chdir(JDK_REPO_PATH)

initial_branch_result = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    capture_output=True, text=True, check=True
)
initial_branch = initial_branch_result.stdout.strip()

#stash local changes before we fetch the remote branches (needed for config)
print("Stashing local changes...")
subprocess.run(["git", "stash"], check=True)

#fetch remote branches
subprocess.run(["git", "fetch", "--all", "--prune"], check=True)

#get list of remote branches using ls-remote
result = subprocess.run(["git", "ls-remote", "--heads", "origin"],
                        capture_output=True, text=True)
branches = [line.split("\t")[1].replace("refs/heads/", "")
            for line in result.stdout.splitlines() if line.strip()]

#processing
for jdk_version in branches[::-1]:
    print(f"\nprocessing version: {jdk_version}")

    # Checkout the branch and reset to the remote version
    try:
        subprocess.run(["git", "checkout", jdk_version], check=True)
        subprocess.run(["git", "reset", "--hard", f"origin/{jdk_version}"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error checking out branch {jdk_version}: {e.stderr}")
        continue

    print(f"Checked out JDK version: {jdk_version}")

    #move into checker-framework to run minimization
    try:
        os.chdir(CHECKER_FRAMEWORK_REPO_PATH)
    except FileNotFoundError:
        print(f"Could not find {CHECKER_FRAMEWORK_REPO_PATH}")
        exit(1)

    # Run the minimization Gradle task
    print(f"Running Gradle task for {jdk_version}...")
    try:
        subprocess.run(gradle_task_cmd, check=True)
        print(f"Gradle task done for {jdk_version}!")
    except subprocess.CalledProcessError as e:
        print(f"Error running for {jdk_version}: {e.stderr}")
        exit(1)

    # get output directory of the gradle task
    OUTPUT_DIR = os.path.join(CHECKER_FRAMEWORK_REPO_PATH, "framework", "build", "generated", "resources", "annotated-jdk")
    if not os.path.exists(OUTPUT_DIR):
        print("error finding otuput directory")
        os.chdir(JDK_REPO_PATH)
        continue

    # Define the final results directory for this branch
    result_dir = os.path.join(RESULTS_BASE_DIR, jdk_version)
    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
    os.makedirs(result_dir, exist_ok=True)

    #move the output directory into results directory
    shutil.move(OUTPUT_DIR, result_dir)
    print(f"Result stored in: {result_dir}")

    #switch back to JDK repo to process next version
    os.chdir(JDK_REPO_PATH)

print("\nAll minimizations completed!")

try:
    #move into the jdk
    os.chdir(JDK_REPO_PATH)
    #run git checkout on the initial branch
    subprocess.run(["git", "checkout", initial_branch], check=True)
    print(f"\nMoved back into the initial branch {initial_branch}")
except Exception as e:
    #output error in switching back to initial branch
    print(f"Error switching back to the initial branch '{initial_branch}'. Error: {e}")
