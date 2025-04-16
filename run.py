import os
import sys
import importlib.util
import ast

def get_file_type(script_path):
    """
    Analyze the Python file to determine its type:
    1. Has main() function
    2. Has if __name__ == "__main__" block
    3. Runs code directly
    """
    with open(script_path, 'r') as file:
        tree = ast.parse(file.read())
        
    has_main = False
    has_name_main = False
    has_direct_code = False
    
    # Check for main() function and if __name__ == "__main__" block
    for node in ast.walk(tree):
        # Check for main() function
        if isinstance(node, ast.FunctionDef) and node.name == 'main':
            has_main = True
        
        # Check for if __name__ == "__main__" block
        if isinstance(node, ast.If):
            if (isinstance(node.test, ast.Compare) and 
                isinstance(node.test.left, ast.Name) and 
                node.test.left.id == '__name__' and
                isinstance(node.test.ops[0], ast.Eq) and
                isinstance(node.test.comparators[0], ast.Str) and
                node.test.comparators[0].s == '__main__'):
                has_name_main = True
    
    # Check for direct code by looking at the module body
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom)):
            has_direct_code = True
            break
    
    return has_main, has_name_main, has_direct_code

def run_script(script_path):
    """
    Run a Python script with the project root in the Python path.
    script_path should be relative to the project root, e.g., 'src/data/database/populate_database.py'
    """
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Convert the script path to module path
    module_path = script_path.replace('/', '.').replace('.py', '')
    
    try:
        # Analyze the file to determine its type
        has_main, has_name_main, has_direct_code = get_file_type(script_path)
        
        # Import the module
        module = importlib.import_module(module_path)
        
        if has_main:
            print(f"Running main() function from {script_path}")
            module.main()
        elif has_name_main:
            print(f"Running {script_path} as main module")
            # When we import the module, __name__ will be the module name, not "__main__"
            # So we need to execute the file directly
            with open(script_path, 'r') as file:
                exec(file.read(), {'__name__': '__main__'})
        elif has_direct_code:
            print(f"Running {script_path} directly")
            # The module will execute its top-level code when imported
        else:
            print(f"No executable code found in {script_path}")
            
    except ImportError as e:
        print(f"Error importing {script_path}: {e}")
        print("Make sure you're using the correct path relative to the project root")
        sys.exit(1)
    except Exception as e:
        print(f"Error running {script_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <script_path>")
        print("Example: python run.py src/data/database/populate_database.py")
        sys.exit(1)
    
    script_path = sys.argv[1]
    run_script(script_path) 