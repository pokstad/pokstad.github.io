# pokstad.github.io

My static site hosted on GitHub Pages, built with [Hugo](https://gohugo.io).

## Install Hugo

```
brew install hugo
```

## Local development

```
./run.sh
```

Serves the site at `http://localhost:1313` with drafts included. Live-reloads on file changes.

## Deployment

Pushing to `master` triggers a GitHub Actions workflow that builds and deploys the site automatically.
