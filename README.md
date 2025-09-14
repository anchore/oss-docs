# Anchore Open Source Documentation

This repository contains the source code for the Anchore open source documentation website, which is deployed to [https://oss.anchore.com/](https://oss.anchore.com/).

The website is built using [Hugo](https://gohugo.io/) and the [Docsy](https://www.docsy.dev/) theme.

## Getting Started

To get started, you will need to have Hugo installed. You can find installation instructions in the [Hugo documentation](https://gohugo.io/getting-started/installing/).

Once you have Hugo installed, you can clone this repository and run the following command to start the local development server:

```bash
hugo server
```

This will start a local development server at `http://localhost:1313/`.

## Contributing

We welcome contributions to the Anchore open source documentation. If you would like to contribute, please fork this repository and submit a pull request.

When you submit a pull request, Cloudflare will automatically deploy a preview of your changes so that you can see what they will look like on the live website.

## Repository Structure

The repository is structured as follows:

*   `content/`: This directory contains the content of the website, which is written in Markdown.
*   `themes/docsy/`: This directory contains the Docsy theme, which is used to style the website.
*   `static/`: This directory contains static assets, such as images and CSS files.
*   `hugo.toml`: This file contains the configuration for the website.
*   `scripts`: Helper scripts to generate/update some content such as the "OSS Adopters" and "Releases" pages.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more information.
