# TuniHack 12.0 CTFd theme

This is a presentation layer for the CTFd 3.x core-beta theme. The existing CTFd routes,
Jinja blocks, APIs, challenge interactions, notifications, and plugin hooks remain in place.

## Structure

- `templates/` contains the core-beta Jinja templates. `page.html` adds the event hero to the
  root page; `components/navbar.html` keeps the existing menu and changes its positioning.
- `assets/scss/main.scss` loads Bootstrap and the theme styles.
- `assets/scss/includes/theme/` contains the palette, base styles, shared components, and page
  layouts.
- `assets/img/logo/` contains the supplied TuniHack marks and mascot. Vite copies optimized
  variants into `static/img/logo/`; oversized poster and emblem PNG originals stay source-only.
- `static/` contains the built files served by CTFd. Run `npm run build` after changing SCSS.

## Changing the colors

Edit the custom properties in `assets/scss/includes/theme/_tokens.scss`. The page and component
styles refer to these variables, so changing the palette there updates the whole theme. Rebuild
the assets with `npm run build` before deploying.

## Swapping the logo or mascot

Set the CTFd logo in Admin → Config → Appearance; the navbar uses the configured logo and falls
back to the CTF name. To replace the home illustration, put the new transparent PNG, WebP, or SVG
in `assets/img/logo/` and update the image path in `templates/page.html`. Keep the image close to
the current 425 × 544 px mascot dimensions, or use a similarly proportioned transparent asset.
Run the Vite build to copy it to `static/`.

## Pages and template overrides

The shared styles cover the core-beta templates for the home page, challenges and challenge
modal, scoreboard, login, registration, reset password, notifications, settings, teams, users,
profiles, and error pages. The markup changes in this pass are the home hero in
`templates/page.html` and sticky positioning in `templates/components/navbar.html`. The
scoreboard chart color palette and axis styling are set in
`assets/js/utils/graphs/echarts/scoreboard.js`; chart data and behavior are unchanged.

The bundled theme has a general neutral mascot, but no dedicated hologram/Tux projection image.
For the reference look, provide a transparent 800 × 1000 px WebP or PNG Tux hologram. The cube
accent and base rings are drawn with CSS, so separate wireframe assets are optional.
Inter, Barlow Condensed, and JetBrains Mono font files were also not present, so the styles use
system fallbacks and the bundled local Lato font where available. Add self-hosted WOFF2 files to
`static/fonts/` and declare them with `font-display: swap` to match the requested typography.

## Build and verification

Run `npm run build` from this directory to produce the deployable `static/` assets. This checkout
does not include `node_modules` or a Docker Compose file, so a local CTFd run and browser-based
page verification have not been performed here.
