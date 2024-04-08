import os
import sys




def create_module(module_name, inherit_flag, inherit_module_name):
    """
    Creates an Odoo module directory structure with necessary files, including a model
    and a security folder with a CSV for access rights.
    """
    base_path = os.getcwd()
    module_path = os.path.join(base_path, module_name)

    # Module structure paths
    models_path = os.path.join(module_path, 'models')
    views_path = os.path.join(module_path, 'views')
    if not inherit_flag:
        security_path = os.path.join(module_path, 'security')

    # Create directories
    os.makedirs(models_path, exist_ok=True)
    os.makedirs(views_path, exist_ok=True)
    if not inherit_flag:
        os.makedirs(security_path, exist_ok=True)

    # __init__.py in the module directory
    with open(os.path.join(module_path, '__init__.py'), 'w') as f:
        f.write('from . import models\n')

    # __init__.py in the models directory
    with open(os.path.join(models_path, '__init__.py'), 'w') as f:
        f.write('from . import model\n')

    # model.py with the specified content
    model_py_content = f"""from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ClassName(models.Model):
    _name = "module_name"
    _description = "module_description"
"""
    inherit_model_py_content = f"""from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Inherit_{inherit_module_name.replace(".", "_")}(models.Model):
    _inherit = "{inherit_module_name}"
    _description = "module_description"
"""
    with open(os.path.join(models_path, 'model.py'), 'w') as f:
        f.write(model_py_content if not inherit_flag else inherit_model_py_content)

    # Create the views directory and an XML file within it
    with open(os.path.join(views_path, 'module_view.xml'), 'w') as f:
        f.write('<!-- Add your views here -->\n')
        f.write("""<odoo>
    <data>
          <!-- your views here -->      
    </data>
</odoo>
""")

    # Security folder and ir.model.access.csv
    if not inherit_flag:
        with open(os.path.join(security_path, 'ir.model.access.csv'), 'w') as f:
            f.write('id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n')
            f.write(f'access_module_name,access.module.name,{module_name}.model_module_name,,1,1,1,1\n')

    # Create the manifest file
    with open(os.path.join(module_path, '__manifest__.py'), 'w') as f:
        manifest_content = f"""{{
    'name': '{module_name}',
    'description': 'Description for {module_name}',
    'application': True,
    'author': 'Your Name',
    'website': 'Your Website',
    'category': 'Your Category',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/module_view.xml',
    ],
}}
"""
        inherited_manifest_content = f"""{{
    'name': '{module_name}',
    'description': 'Description for {module_name}',
    'application': True,
    'author': 'Your Name',
    'website': 'Your Website',
    'category': 'Your Category',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'views/module_view.xml',
    ],
}}
"""
        f.write(manifest_content if not inherit_flag else inherited_manifest_content)
    print(f"{module_name} module created successfully!")

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ["create", "inherit"]:
        # First, check if a valid command is provided
        print("Invalid command. Usage:")
        print("  odooer create <module_name>")
        print("  odooer inherit <module_name to be inherited> <your module_name>")
        sys.exit(1)
    elif sys.argv[1] == "create":
        # Specific check for "create" command
        if len(sys.argv) != 3:
            print("Usage: odooer create <module_name>")
            sys.exit(1)
    elif sys.argv[1] == "inherit":
        # Specific check for "inherit" command
        if len(sys.argv) != 4:
            print("Usage: odooer inherit <module_name to be inherited> <your module_name>")
            sys.exit(1)

    
    inherit_flag = sys.argv[1] == "inherit"
    
    if not inherit_flag:
        module_name = sys.argv[2]
        create_module(module_name, inherit_flag, "")
    elif inherit_flag:
        inherit_module_name = sys.argv[2]
        module_name = sys.argv[3]
        create_module(module_name, inherit_flag, inherit_module_name)

if __name__ == "__main__":
    main()
