import os
import inflect
from jinja2 import Environment, FileSystemLoader


"""
Controller Generator
"""
class LaravelGenerator:
    def __init__(self):
        self.template_processor = TemplateProcessor()
        self.controller_template = ""
        
    def set_template_controller(self, path):
        self.controller_template = path

    def make_controller(self, data):
        output_path = os.path.join('app', 'Http', 'Controllers', f"{data['name'].capitalize()}Controller.php")
        self.template_processor.render(self.controller_template, output_path, data)


"""
Views Generator
https://github.com/rizmulya/reactalara
"""
class ReactaLaraGenerator:
    def __init__(self):
        self.template_processor = TemplateProcessor()
        self.templates = {
            "index": "",
            "create": "",
            "edit": "",
            "show": ""
        }

    def set_template(self, template_type, path):
        if template_type in self.templates:
            self.templates[template_type] = path
        else:
            raise ValueError(f"Invalid template type: {template_type}")

    def make_page(self, page_type, data):
        if page_type not in self.templates or not self.templates[page_type]:
            raise ValueError(f"Template for {page_type} is not set")
        
        template_path = self.templates[page_type]
        output_path = os.path.join('resources', 'js', 'Pages', data['name'].capitalize(), f"{page_type.capitalize()}.jsx")
        self.template_processor.render(template_path, output_path, data)


"""
Main Program
"""
class TemplateProcessor:
    @staticmethod
    def ensure_dir(file_path):
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def render(self, input_file, output_file, context = {}):
        # set env
        if not input_file.endswith('.rism'):
            raise ValueError("Input file must have a '.rism' extension")
        file_loader = FileSystemLoader(os.path.dirname(input_file))
        env = Environment(loader=file_loader)

        # add customize filter
        p = inflect.engine()
        env.filters.update({
            'pluralize': lambda word, count=2: p.plural(word) if count != 1 else word,
            'singularize': lambda word: p.singular_noun(word) or word,
            'capitalize': lambda word: word.capitalize()
        })

        # load and render
        template = env.get_template(os.path.basename(input_file))
        output = template.render(context)

        self.ensure_dir(output_file)
        with open(output_file, 'w') as file:
            file.write(output)
        print(f"{output_file} created!")

