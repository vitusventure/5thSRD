import os
import glob
import markdown
import codecs
import logging
import shutil


class SRDIndexBuilder:
    def __init__(self, offline_mode=False, clean_output_directories=True):
        self.logger = logging.getLogger(__name__)

        if offline_mode:
            self.logger.info('Generating in offline mode...')

        self.offline_mode = offline_mode

        self.clean_output_directories = clean_output_directories

    def build_indexes_from_config(self, build_config):
        """
        Build indexes defined in config

        :param build_config: Configuration used to build indexes
        :type build_config: dict
        :return: None
        """
        # First, build all our regular indexes
        for index_type in build_config['indexes']:
            self.logger.info('Starting to build indexes of type: {0}'.format(index_type))
            index_type_config = build_config['indexes'][index_type]

            # First, clean if requested
            if self.clean_output_directories:
                self._clean_index_directory(index_type_config['index_path'])

            # Determine which fields to extract
            additional_fields = index_type_config['indexes_to_generate'].keys()
            self.logger.info('Extracting metadata with additional fields: {0}'.format(additional_fields))

            # Get the metadata to start building indexes with
            metadata = self.get_metadata(index_type_config['source_directory'],
                                         additional_fields,
                                         index_type_config['link_prefix'])

            # Now, build out each index page for this type
            for index_category in index_type_config['indexes_to_generate']:
                category_config = index_type_config['indexes_to_generate'][index_category]

                categorized_keys = self.categorize_metadata_keys(metadata, index_category)
                index_page = self.create_index_page(
                    metadata, 
                    categorized_keys, 
                    category_config['page_title'],
                    description=category_config.get('description')
                    )

                self.write_page_to_file(index_page, index_type_config['index_path'] + category_config['output_file_name'])

        # After building the indexes, also build the class spell lists if requested
        if build_config['class_spell_lists']:
            if not os.path.exists(build_config['class_spell_lists']['index_path']):
                os.makedirs(build_config['class_spell_lists']['index_path'])

            self.build_class_spell_lists(build_config['indexes']['spells'], build_config['class_spell_lists'])

    def _clean_index_directory(self, directory):
        """
        Clean all files from a directory by deleting then recreating it

        :param directory: Directory to clean
        :type directory: str
        :return: None
        """
        self.logger.info('Cleaning directory: {0}'.format(directory))
        # Delete everything other than the static index.md in each directory

        for item in glob.glob(f"{directory}/*.md"):
            if not item.endswith('index.md'):
                print(item)


    def build_class_spell_lists(self, spells_config, class_spell_lists_config):
        """
        In addition to regular indexes, we also build spell lists, using the classes metadata attribute.

        These spell lists require a bit of extra handling, since one spell can belong to many lists, and the
        final form for the list looks like a spells by level index page (just only showing the spells for a specific
        class).

        :param spells_config: Spells portion of build configuration file
        :type spells_config: dict
        :param class_spell_lists_config: config for building class spell lists
        :type class_spell_lists_config: dict
        :return: None
        """
        metadata = self.get_metadata(spells_config['source_directory'],
                                     ['level', 'classes', 'school'],
                                     spells_config['link_prefix'])

        # Generate a list of all the classes we have spells for
        classes = []
        for item in metadata.values():
            if isinstance(item['classes'], str):
                # If only one class has a spell, we will get a plain str, rather than a list
                item['classes'] = [item['classes']]

            for class_name in item['classes']:
                if class_name not in classes:
                    classes.append(class_name)

        for class_name in classes:
            self.logger.info('Generating class spell list for class: {0}'.format(class_name))

            # Generate a metadata dictionary with only the spells for this class
            class_spells_metadata = {}
            for item in metadata:
                if class_name in metadata[item]['classes']:
                    class_spells_metadata[item] = metadata[item]

            # After making our list of spells, we can build the index
            categorized_keys = self.categorize_metadata_keys(class_spells_metadata, 'level')
            index_page = self.create_spell_list_table_page(class_spells_metadata,
                                                categorized_keys,
                                                '{0} Spell List'.format(class_name.capitalize()),
                                                use_spell_titles=True,
                                                description=f'5th Edition (5e) {class_name.capitalize()} spell list, organized by level.')
            self.write_page_to_file(index_page, '{base}{class_name}_spells.md'.format(
                base=class_spell_lists_config['index_path'],
                class_name=class_name
            ))

    def _convert_name_to_link_format(self, name):
        """
        Names contain several unsafe characters for generating links. Replace or remove them here

        :param name: Name to convert
        :type name: str
        :return: converted name
        :rtype: str
        """
        # First, characters to remove
        name = name.replace("'", "").replace("/", "").replace(",", "").replace("+", "").replace("(", "").replace(")",
                                                                                                                 "")

        # Next, characters to substitute
        name = name.replace("-", "_").replace(" ", "_")

        # Finally, return the lowered name
        name = name.lower()

        # If we are generating in offline mode, append the index.html section
        if self.offline_mode:
            name = '{0}/index.html'.format(name)
        else:
            name = '{0}/'.format(name)
        return name

    def _convert_category_to_markdown(self, category, use_spell_titles=False):
        """
        Given a category, convert to markdown

        :param category: Category to convert
        :type category: str
        :return: Markdown formatted category
        :rtype: str
        """
        if use_spell_titles:
            if category == '0':
                return '## Cantrips (0 level)'
            if category == '1':
                return '## 1st Level'
            if category == '2':
                return '## 2nd level'
            if category == '3':
                return '## 3rd level'
            else:
                return '## {0}th level'.format(category)
        return '## {0}'.format(str(category).capitalize())

    def get_metadata(self, source_directory, additional_fields, link_prefix):
        """
        This function extracts specific metadata fields from all files in a directory, then constructs a dict
        of the metadata, so we can generate index pages.

        The name metadata field is always included, because that is what we use to generate the links. Any other
        fields can be passed in via additional_fields, and will be appended to the minimal metadata below, using
        the same names as the metadata fields.

        The metadata should look like:

        {'Acid Splash': {'name_category': 'A', 'relative_link': '/spellcasting/spells/acid_splash'}, ... }

        If we included ['level'] as additional_fields, an entry would look like:

        {'Acid Splash': {'name_category': 'A', 'relative_link': '/spellcasting/spells/acid_splash', 'level': '0'}, ... }

        :param source_directory: Directory of markdown files to scan for metadata
        :param additional_fields: List of additional metadata fields to extract from each file
        :param link_prefix: URL prefix for generating relative links
        :return: Metadata for directory
        :rtype: dict
        :raises RuntimeError: If there is missing metadata (unless allow_missing_metadata)
        """
        source_files_to_scan = os.listdir(source_directory)

        metadata_map = {}

        for filename in source_files_to_scan:
            # Generate a detail map for every file in the directory
            md = markdown.Markdown(extensions=['markdown.extensions.meta'])
            md.convert(codecs.open(os.path.join(source_directory, filename), mode='r', encoding='utf-8').read())
            try:
                name = md.Meta['name'][0]
                name_category = name[0].capitalize()
                rel_link = '{prefix}/{name}'.format(prefix=link_prefix, name=self._convert_name_to_link_format(name))

                metadata_map[name] = {'name_category': name_category, 'relative_link': rel_link}
            except KeyError:
                if filename == 'index.md':
                    self.logger.info('Skipping index file')
                    continue
                else:
                    raise RuntimeError('File {0} missing name metadata attribute!'.format(filename))

            # After getting the default field, get any additional fields
            for field_name in additional_fields:
                # If name_category was requested, skip it, because we always do it by default
                if field_name == 'name_category':
                    continue

                try:
                    field_value = md.Meta[field_name]

                    # If the field is just one item, collapse the list
                    if len(field_value) == 1:
                        field_value = field_value[0]

                    metadata_map[name][field_name] = field_value
                except KeyError:
                    raise RuntimeError('Additional field {field} missing from {file}'.format(
                        field=field_name,
                        file=filename
                    ))

        return metadata_map

    def categorize_metadata_keys(self, metadata, category_field):
        """
        From a metadata map, generate a new dictionary, with a top key for each unique category_field, with the details
        entry for each item underneath

        :param metadata: Metadata for directory
        :type metadata: dict
        :param category_field: Field to categorize with (should be on each item in metadata)
        :type category_field: str
        :return: Categorized metadata keys (ex: { 'A': ['Awakened Shrub', ...], 'B': ['Badger'...]})
        """

        categorized_metadata_keys_dict = {}

        for item in metadata:
            item_category = metadata[item][category_field].capitalize()

            try:
                categorized_metadata_keys_dict[item_category].append(item)
            except KeyError:
                categorized_metadata_keys_dict[item_category] = [item]

        return categorized_metadata_keys_dict

    def create_index_page(self, metadata, categorized_metadata_keys, page_title, use_spell_titles=False, description=None):
        """
        Create a markdown index page, using metadata and categorized metadata keys

        The page follows a basic format:

        description: <description>

        # <page_title>
        ## <category1>
        [item1](/link/prefix/item1)
        [item2](/link/prefix/item2)

        ## <category2>
        [item3](/link/prefix/item3)
        [item4](/link/prefix/item4)

        :param metadata: Metadata for a directory of files
        :type metadata: dict
        :param categorized_metadata_keys: Keys to metadata items sorted into categories (see self.categorize_metadata_keys)
        :type categorized_metadata_keys: dict
        :param page_title: Title of page to generate
        :type page_title: str
        :return: List of lines representing a page of markdown
        """
        # First, the page title
        if description:
             output = [f'description: {description}', '',  f'# {page_title}']
        else:
             output = ['# {0}'.format(page_title)]

        # Generate sorted metadata category lists
        try:
            # Try to cast as float first, for things like CR (with values like .125
            sorted_categories = sorted(categorized_metadata_keys, key=float)
        except ValueError:
            # Otherwise, just treat as strings
            sorted_categories = sorted(categorized_metadata_keys)

        # Figure out if we are generating spell lists by level
        if 'spells by level' in page_title.lower():
            use_spell_titles = True

        # Assemble the page
        for metadata_category in sorted_categories:
            # First, the category title
            output.append(self._convert_category_to_markdown(metadata_category, use_spell_titles=use_spell_titles))

            # Next, all the items
            for item in sorted(categorized_metadata_keys[metadata_category]):
                output.append("* [{item}]({rel_link})".format(
                    item=item,
                    rel_link=metadata[item]['relative_link']
                ))

            # Finally, a blank line after all the items
            output.append('')

        return output

    def create_spell_list_table_page(self, metadata, categorized_metadata_keys, page_title, use_spell_titles=False, description=None):
        """
        Create a markdown index page, using metadata and categorized metadata keys

        The page follows a basic format:

        description: <description>

        # <page_title>
        ## <category1>
        [item1](/link/prefix/item1)
        [item2](/link/prefix/item2)

        ## <category2>
        [item3](/link/prefix/item3)
        [item4](/link/prefix/item4)

        :param metadata: Metadata for a directory of files
        :type metadata: dict
        :param categorized_metadata_keys: Keys to metadata items sorted into categories (see self.categorize_metadata_keys)
        :type categorized_metadata_keys: dict
        :param page_title: Title of page to generate
        :type page_title: str
        :return: List of lines representing a page of markdown
        """
        # First, the page title
        if description:
            output = [f'description: {description}', '',  f'# {page_title}']
        else:
            output = ['# {0}'.format(page_title)]

        # Generate sorted metadata category lists
        try:
            # Try to cast as float first, for things like CR (with values like .125
            sorted_categories = sorted(categorized_metadata_keys, key=float)
        except ValueError:
            # Otherwise, just treat as strings
            sorted_categories = sorted(categorized_metadata_keys)

        # Assemble the page
        output.append('|Spell Level|Name|School|')
        output.append('|-|-|-|')
        for metadata_category in sorted_categories:
            # Next, all the items
            for item in sorted(categorized_metadata_keys[metadata_category]):
                spell_metadata = metadata[item]
                if spell_metadata["level"] == '0':
                    spell_metadata["level"] = '0 (Cantrip)'
                output.append(f'|{spell_metadata["level"]}|[{item}]({spell_metadata["relative_link"]})|{spell_metadata["school"].capitalize()}')

        return output

    def write_page_to_file(self, page, path):
        """
        Take a list of lines, and write it to a file at path

        :param page: List of lines representing a page to write
        :type page: list
        :param path: Path to write to
        :type path: str
        :return: None
        """
        self.logger.info('Writing to file at: {0}'.format(path))

        with open(path, "w") as out_file:
            for line in page:
                out_file.write(line + "\n")
