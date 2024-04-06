# Contributing
Thank you for your interest in contributing! This guide should help you get started.

<br>

## General guidance
We want folks at all points in their professional and personal journies to feel welcome contributing to the project. If you are unsure if you've followed these guidelines correctly or aren't sure how to do something, please engage with us. We would love to help. Just getting a few logistical things out of the way first...

### Code of Conduct
All contributors are expected to abide by the Code of Conduct (see `CONDUCT.md`).

### Open source
By contributing you agree:

 - You release your contribution to the project under the BSD License (see `LICENSE.md`).
 - By contributing to the project you affirm that your contribution is original and you have legal rights to submit the contribution.
 - Except by resolution of the planning group, you understand that contributors will be acknowledged as "Sketchingpy Contributors" in the `LICENSE.md` file.

For more information on the planning group, see `GOVERNANCE.md`.

### Generative AI
If AI tools (like generative AI) were used to make your contribution, please disclose it prior to its adoption. Currently the project is not accepting most generative AI contributions due to an evolving legal landscape.

<br>

## Non-code contributions
Anyone can help the project no matter their programming background. This document first starts off with options for community members to help out, potentially without writing any code.

### Reporting a problem
This section refers to unexpected behavior in existing documented functionality. Please report these bugs and other problems by [opening an issue](https://codeberg.org/sketchingpy/Sketchingpy/issues). Please include what you can from the following:

 - Brief description of the behavior expected and the behavior experienced.
 - Your operating system version and, if using Sketch2DWeb, your browser version.
 - Code snippets to reproduce the bug.

Any code snippets included in the problem are to be treated as code contributions subject to the BSD license. Please add the "Bug" label. If you are unable to open an issue or the problem is security related, please email us at hello@sketchingpy.org.

### Offering a proposal or enhancement
Changes to the expected behavior of existing functionality are covered in "enhancements" and suggestions for new functionality are "proposals" in our project language. Please open an issue in our [tracker](https://codeberg.org/sketchingpy/Sketchingpy/issues) with the following information:

 - Short single sentence description of the functionality.
 - Rationale and/or detailed description of the new feature.
 - Recommendations for design (in terms of API or implementation) if available.
 - Questions for the community if applicable.
 - Example code if applicable.

Please add the "enhancement" or "proposal" label to your issue. A member of the planning group will review your request!

<br>

## Documentation
This next section looks at contributions which may involve code that is not part of the Sketchingpy library distribution or supporting code itself.

### Adding your work to the showcase
The showcase is an important way to give both Sketchingpy and its community members important visibility. These detailed examples motivate the development of the library and inspire others. That said, submissions need to meet all of the criteria:

 - Publicly available under an OSI approved license.
 - Is original work with permission of all authors to submit.
 - Does not violate our code of conduct (see `CONDUCT.md`).
 - Is not substantively identical to a prior submission.

The following criteria also typically need to be met:

 - Due to the evolving legal landscape of AI-generated work, generally we cannot currently accept submissions with AI generated code or assets.
 - Generally code will need to be posted to a public repository.

Inclusion is up to discretion of the planning group (see `GOVERNANCE.md`). We may not be able to accomodate all requests but encourage you to share your work even if it does not quite fit here. Anyway, when you are ready to submit, please [open an issue](https://codeberg.org/sketchingpy/Sketchingpy/issues) with the following:

 - Authors
 - Description of the showcase item.
 - Link to public repository with the code.
 - Screenshot of the contribution (for non-visual contributions, this can be excluded).
 - Open source license details.

If you need help submitting, please reach out to hello@sketchingpy.org.

### Translation
We invite translators to migrate existing documentation to new languages for which a prior translation is not available. Please [open an issue](https://codeberg.org/sketchingpy/Sketchingpy/issues) and indicate the following:

 - What section of documentation you are hoping to volunteer.
 - What language you are offering to provide translation.
 - Confirm that you have prior skill in this language and will not use machine translation.

Be sure to add the tag "Documentation" to your issue. 

### Writing examples or other documentation
Short examples for specific Sketchingpy functionality and carefully crafted documentation contributions help developers of all skill levels use our open source tools. There are multiple ways to contribute. First, you may respond to an open issue asking for an example or documentation within [our tracker](https://codeberg.org/sketchingpy/Sketchingpy/issues?labels=175452) to indicate you are volunteering. Second, you may submit an example you've made even though a prior issue was not open by [opening an issue](https://codeberg.org/sketchingpy/Sketchingpy/issues) with the following:

 - Description of the functionality for which the example or documentation is being provided.
 - The code for the example (if applicable).
 - Draft of accompanying text.
 - Suggestion on where within Sketchingpy's website or repository the documentation should go.

Finally, you may report an issue with existing documentation by [opening an issue](https://codeberg.org/sketchingpy/Sketchingpy/issues) with the URL of the problem along with a description of the problem. Thank you very much!

<br>

## Contributing code
Thank you so much for volunteering! Code contributions are the lifeblood of projects like Sketchingpy. This section looks at how to get started in providing code to Sketchingpy itself that is included in the library distribution or in supporting code like CI / CD and testing.

### Background knowledge
There are some basic skills that most code contributors will need to know:

 - [Python](https://python.swaroopch.com/)
 - [Git](https://www.baeldung.com/git-guide)
 - [Google Style Guide](https://google.github.io/styleguide/pyguide.html)
 - [Unit Testing](https://www.freecodecamp.org/news/an-introduction-to-testing-in-python/)
 - [Python Type Hints](https://www.pythonstacks.com/blog/post/type-hints-python/)
 - [Python Packaging](https://docs.python-guide.org/shipping/packaging/)

Some contributions may also require knowledge of:

 - [Basic bash scripting](https://www.freecodecamp.org/news/shell-scripting-crash-course-how-to-write-bash-scripts-in-linux/)
 - [HTML and JavaScript](https://developer.mozilla.org/en-US/docs/Learn)
 - [YAML](https://www.tutorialspoint.com/yaml/index.htm)
 - [Docker](https://www.docker.com/101-tutorial/)

If you need help getting started, please email us at hello@sketchingpy.org. A maintainer may be available to work with you!

### Open a fork
Please fork the project and make pull requests from your fork to [sketchingpy/Sketchingpy](https://codeberg.org/sketchingpy/Sketchingpy).

### Getting ready to contribute
We recommend checking out your newly made fork and doing the following prior to first contribution:

 - Install a dev build (`pip install .[dev]`)
 - Run unit tests (`nose2`)
 - Execute code checks like mypy (`mypy sketchingpy/*.py`)

All of these actions are described in the `README.md`. If you are interested in mentorship, please also reach out to hello@sketchingpy.org to see if there are maintainers avialable to help you get started.

### Finding issues
Except for maintainers, contributors are generally only allowed to suggest changes to code (open pull requests) to resolve open issues. You have two options:

 - [Find an already open issue](https://codeberg.org/sketchingpy/Sketchingpy/issues) in need of help. We recommend staying away from things which still have the "Proposal" tag. You may also want to look for issues with the "Beginner Friendly" tag!
 - If there isn't an issue open for what you want to do, make an issue first (see above) to describe what you want to do.

When you have some code ready, see below for opening a pull request.

### Pull request
Whenever you have something ready to share, open a [pull request](https://codeberg.org/sketchingpy/Sketchingpy/pulls) with the "draft" tag included. Removing draft lets the maintainers know that you have code ready to merge. Before removing the "draft" tag please ensure the following:

 - Unit tests pass.
 - Pyflakes passes.
 - Pycodestyle passes.
 - Mypy passes.
 - The contribution adheres as best as possible to the development standards listed in the `README.md`.

Note that CI / CD may run automated checks for your contribution.

<br>

## Conflict resolution
You agree that the planning group (`GOVERNANCE.md`) will have final say on any contributions.
