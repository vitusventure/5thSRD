import os
import glob
import argparse

src_directory = "./src"
output_directory = "./docs/spellcasting/spell_lists"
spells_relative_link = "/spellcasting/spells"

def create_output_directory():
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

def convert_filename_to_title(filename):
    list_level = filename.split(".")[0]
    if list_level == "0":
        return "## Cantrips (0 level)"
    if list_level == "1":
        return "## 1st Level"
    if list_level == "2":
        return "## 2nd level"
    if list_level == "3":
        return "## 3rd level"
    else:
        return "## %sth level" % list_level

def convert_to_linkable_spell_name(spell):
    return spell.replace(" ", "_").replace("'", "").replace("/", "").lower()

def save_md(md, class_name):
    with open("%s/%s_spells.md" % (output_directory, class_name), "w") as f:
        for line in md:
            f.write(line + "\n")
    

def generate_md_for_class(class_name, class_files_path):
    md = []
    # Insert the overall header
    md.append("# %s Spells" % class_name.capitalize())
    files = sorted(os.listdir(class_files_path))
    for file in files:
        # Insert the section header
        md.append(convert_filename_to_title(file))
        with open("%s/%s" % (class_files_path, file)) as f:
            # Loop over each line, should be one spell name per line
            for line in f.readlines():
                spell_name = line.strip()
                spell_name_link = convert_to_linkable_spell_name(spell_name)
                if args.offline:
                    formatted_line = "[%s](%s/%s/index.html)   " % (spell_name, spells_relative_link, spell_name_link)
                else:
                    formatted_line = "[%s](%s/%s)   " % (spell_name, spells_relative_link, spell_name_link)
                md.append(formatted_line)
            md.append(" ")
    return md

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", default=False)
    args = parser.parse_args()
    if args.offline:
        print "Generating in offline mode..."
    create_output_directory()
    for root, directories, files in os.walk(src_directory):
        if not directories:
            class_name = root.split("/")[-1]
            class_files_path = root
            save_md(generate_md_for_class(class_name, class_files_path), class_name)