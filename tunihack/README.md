# TuniHack CTFd theme

The visual source is the repository root `tunihack.css`. Its theme rules are compiled through
`assets/scss/includes/theme/_design.scss` and included by `assets/scss/main.scss`. Bootstrap stays
available for the existing CTFd layout and controls. Custom navigation rules are scoped so they
do not restyle CTFd tabs.

## Files

- `templates/` contains the CTFd Jinja templates. Theme classes are added alongside CTFd's
  existing hooks, IDs, and JavaScript classes.
- `assets/scss/main.scss` builds the stylesheet from Bootstrap, CTFd helpers, icons, and the
  theme design.
- `assets/scss/includes/theme/_design.scss` is the compiled theme stylesheet source.
- `static/` contains the deployable Vite output. Run `npm run build` after changing styles.

## Fonts and preview

The reference CSS asks for local Unbounded, Manrope, and JetBrains Mono WOFF2 files, but those
files are not present in this checkout. The theme uses bundled local Raleway and Lato as
fallbacks, then system fonts. It makes no font requests to a CDN. `preview.html` was also not
present, so the supplied CSS was the only available visual reference.

## Verification

`npm run build` compiles the theme and `npm run lint` checks the asset formatting. There is no
Docker Compose configuration in this repository, so a local CTFd browser preview is unavailable.
