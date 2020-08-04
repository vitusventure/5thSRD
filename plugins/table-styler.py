import re

def style_tables(output_content, page, config):
    output_content = re.sub(r'<table>', '<table class="pure-table pure-table-striped">', output_content)
    return output_content