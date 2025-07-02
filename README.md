# better-page-layouts

## Goal

Create a better way of managing page layouts on TerminalFour, specifically catered for Santa Clara University (homepage: [scu.edu](https://www.scu.edu))

The current biggest downfall is that it's hard to keep them all synchronized, as the current approach is to update them one at a time. However, many of them of have repeated components, such as the `<head>` and `<nav>`, which begs for a simpler, more programmable approach.

## Usage

Move into the site builder directory

  cd site-specific-builder

Then, run the `builder.py` script

  python builder.py

Follow the prompts in the command line. The pages should be generated into the
`build/` folder.
  
