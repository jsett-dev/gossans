# gossanadvisory.com

The Gossan Advisory website. One static page, no build step, no dependencies.

```
index.html      the site: markup, styles and one small script, all inline
404.html        not-found page, styled to match
favicon.svg     the rust square mark
robots.txt      crawler policy
sitemap.xml     one URL, update if pages are added
CNAME           custom domain, read by GitHub Pages only
.nojekyll       stops GitHub Pages running Jekyll over the files
```

Everything is deliberately in one file. There is no framework, no bundler and
nothing to install, so the site cannot break because a dependency moved. The
only external requests are three fonts from Google Fonts.

## Preview it locally

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`. Opening `index.html` directly as a file also
works, but the absolute paths for the favicon and the 404 page only resolve when
it is served.

## Editing

Everything the reader sees is in `index.html`, and the sections are marked with
comment rules in the order they appear on the page.

| To change | Look for |
|---|---|
| Colours | The `:root` block at the top, then the two dark-theme blocks below it |
| Fonts | The `--f-display`, `--f-body` and `--f-data` variables |
| Header and title block | `<header class="plate">` |
| The opening statement | `<section class="thesis">` |
| Services and prices | The `<div class="ledger">` block, one `.svc` per service |
| Data request lists | The block with `Data` in its rail label |
| Worked example | The `<div class="case">` block |
| The eight findings | The `<div class="redlines">` block |
| Contact address | The `mailto:` link in `<a class="btn">` |

Three colour tokens carry the identity and are worth understanding before
changing them. `--draft` is the drafting-ink blue used for structure and
labels. `--redline` is the iron-oxide rust that gives the firm its name, and it
is reserved for the logo mark and the eight findings, which is what keeps it
meaning something. `--ink` and the `--paper` series are the neutrals.

Every colour is defined three times: once in `:root` for light, once under
`prefers-color-scheme: dark`, and once under `[data-theme="dark"]` for the
manual toggle. Change a colour in all three or the theme will fall apart.

## Deploying

The site is static, so anything that serves files will host it. Two good
options, both free at this size.

**Cloudflare Pages.** Connect the repository, leave the build command empty and
set the output directory to `/`. Add the custom domain in the Pages project and
Cloudflare writes the DNS records itself. If the domain is registered at
Cloudflare too, this is the least moving parts of any option.

**GitHub Pages.** Push to GitHub, then in Settings, Pages, deploy from the
`main` branch, root folder. The `CNAME` and `.nojekyll` files here are already
set up for it. Point the domain with these records at your registrar:

```
A     @    185.199.108.153
A     @    185.199.109.153
A     @    185.199.110.153
A     @    185.199.111.153
CNAME www  <your-github-username>.github.io
```

Tick "Enforce HTTPS" once the certificate is issued, which takes up to an hour.

## Before launch

- [ ] Register `gossanadvisory.com`, and `gossanpartners.com` alongside it
- [ ] Create the `hello@gossanadvisory.com` mailbox the contact button points to
- [ ] Run a USPTO wordmark search for Gossan, as Gossan Resources trades in Canada
- [ ] Add `og-image.png` at 1200x630 and reference it in the head, or social
      shares will render as a bare link
- [ ] Add `favicon.ico` at 32x32 and `apple-touch-icon.png` at 180x180, which
      the head already links to
- [ ] Decide whether to name yourself on the page, since a single-principal
      advisory converts better with a named person and a credential line
- [ ] Replace the worked example with a real engagement once a client agrees to
      be cited, and keep it labelled as illustrative until then

## A note on the figures

The pricing is real and the method is real. The worked example is modelled
output used to demonstrate the method, and it is labelled as such on the page.
Keep that label until a client agrees to be named, because a case study that
implies a client who does not exist is the one mistake in this business that is
not recoverable.
