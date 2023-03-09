# How to use Material for MkDocs

## Installation

Install [Material for MkDocs](../explanations/about-material-for-mkdocs.md) with the following commands.

=== ":simple-linux: Linux"

	```sh title="In a terminal, execute the following command(s)."
	# Install Material for MkDocs and all its extensions
	pip install --user \
		cairosvg \
		mkdocs-git-revision-date-localized-plugin \
		mkdocs-glightbox \
		mkdocs-material \
		mkdocs-minify-plugin
	```

=== ":simple-apple: macOS"

	```sh title="In a terminal, execute the following command(s)."
	# Install Material for MkDocs and all its extensions
	pip3 install \
		cairosvg \
		mkdocs-git-revision-date-localized-plugin \
		mkdocs-glightbox \
		mkdocs-material \
		mkdocs-minify-plugin \
		pillow

	# Install Material for MkDocs dependencies
	brew install \
		cairo \
		freetype \
		libffi \
		libjpeg \
		libpng \
		zlib
	```

=== ":simple-windows: Windows"

	```sh title="In a terminal, execute the following command(s)."
	TODO
	```

## Start the website for development

```sh title="In a terminal, execute the following command(s)."
mkdocs serve
```

## Build the website for production

```sh title="In a terminal, execute the following command(s)."
mkdocs build --strict --site-dir public
```

## Configuration

The configuration for Material for MkDocs is located in the `mkdocs.yml` configuration file.

## Common tasks

### Add a new page

Add a new page by creating a new file/directory in the `docs` directory. All pages must have a `.md` file extension.

### Add a new navigation entry

Add a new entry to the navigation in the `mkdocs.yml` file under the `nav` property.

### Add a new glossary entry

Add a new entry to the glossary in the `docs/glossary.md` file.

The format must be as follow.

```
*[Abbr]: The full definition of the abbreviation
```

Each word that Material for MkDocs will find in the documentation will have a tooltip with the definition for the word.

## Related explanations

These explanations are related to the current item (in alphabetical order).

- [About Material for MkDocs](../explanations/about-material-for-mkdocs.md)

## Resources

These resources are related to the current item (in alphabetical order).

- [Material for MkDocs - Icons, Emojis](https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/)
- [PyMdown Extensions Documentation - Keys](https://facelessuser.github.io/pymdown-extensions/extensions/keys/)
