import re

def style_tables(output_content, page, config):
    output_content = re.sub(r'<table>', '<div class="responsive-table"><table class="pure-table pure-table-striped">', output_content)
    output_content = re.sub(r'</table>', '</table></div>', output_content)
    return output_content