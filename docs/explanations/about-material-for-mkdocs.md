# About Material for MkDocs

[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) is a documentation framework based on [MkDocs](https://www.mkdocs.org/).

It has a better looking interface than plain MkDocs and offers various features to help organize your documentation with Markdown.

## How and why do we use Material for MkDocs

We use Material for MkDocs to generate the documentation website.

## Install Material for MkDocs

Install Material for MkDocs with the following commands.

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

=== ":simple-docker: Docker"

You can use the dev container to develop within. You can read more [here](https://code.visualstudio.com/docs/devcontainers/containers).

Once in the dev container you can run the following commands:

```sh title="In a terminal, execute the following command(s)."
# Activate the virtual environment
poetry shell
# Install the dependencies
poetry install
```

## Configuration

The configuration for Material for MkDocs is located in the `mkdocs.yml` configuration file.

## Common tasks

### Start the website for development

```sh title="In a terminal, execute the following command(s)."
mkdocs serve --dev-addr 0.0.0.0:8000
```

### Build the website for production

```sh title="In a terminal, execute the following command(s)."
mkdocs build --strict --site-dir public
```

### Add a new page

Add a new page by creating a new file/directory in the `docs` directory. All pages must have a `.md` file extension.

### Add a new navigation entry

Add a new entry to the navigation in the `mkdocs.yml` file under the `nav` property.

### Add a new glossary entry

Add a new entry to the glossary in the `docs/glossary.md` file.

The format must be as follow.

``` markdown
*[Abbr]: The full definition of the abbreviation
```

Each word that Material for MkDocs will find in the documentation will have a tooltip with the definition for the word.

## Resources and alternatives

These resources and alternatives are related to the current item (in alphabetical order).

- [Docsify](https://docsify.js.org/)
- [Docusaurus](https://docusaurus.io/)
- [GitBook](https://www.gitbook.com/)
- [Hugo](https://gohugo.io/)
- [Material for MkDocs - Icons, Emojis](https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/)
- [PyMdown Extensions Documentation - Keys](https://facelessuser.github.io/pymdown-extensions/extensions/keys/)
- [VuePress](https://vuepress.vuejs.org/)
