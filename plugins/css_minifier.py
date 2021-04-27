import os
from csscompressor import compress


CSS_SOURCE = './purecss_theme/css/site.css'
OUTPUT_TARGET = './purecss_theme/inline_styles.html'

def generate_inline_css(*args, **kwargs):
    # Read in the source
    with open(CSS_SOURCE, 'r') as src:
        css_source = src.read()
    
    # Compress
    compressed = compress(css_source)

    # Write to the output
    output_text = '''{{% raw %}}
<style>
{}
</style>
{{% endraw %}}'''.format(compressed)

    with open(OUTPUT_TARGET, 'w') as f:
        f.write(output_text)
