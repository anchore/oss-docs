# Anchore OSS Docs Scripts

Scripts used to update and maintain the docs.

## Update OSS Adopters page

The `/oss/about/adopters/` (in `content/about/adopters.md`) can be generated periodically.

```
pip install requests packaging
./scripts/generate-adopters-info.sh
```

## Generate release notes

`generate-release-notes.sh` - a helper script around `release-to-hugo.py` that pulls release notes for all our open source repos.

e.g. 

`scripts/generate-release-notes.sh`

`github-releases-to-hugo.py` - generate release notes in Hugo format, from the ones in the repos. Also generates a truncated `_index.md` which  Run once per repo specifying the Anchore repo name, the output directory, and weight. 

`--weight` controls the position of the item in the releases menu, with lower numbers at the top. I have put them in the order, syft (10), grype (20), grant (30), grype-db (40), vunnel (50), sbom-action (60), scan-action (70), stereoscope (80) (see `generate-release-notes.sh`, above). It won't generate a release notes file if one already exists. To re-generate them all, just delete all the `content/oss/releases/v*.md` files, and run again.

e.g. 

`python scripts/github-releases-to-hugo.py --repo syft --output-dir content/oss/releases/syft --weight 10`
