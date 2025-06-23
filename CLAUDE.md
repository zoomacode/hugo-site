# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a personal blog built with Hugo static site generator, deployed at https://chaotic.land/. The blog is multilingual (English/Russian) and covers topics ranging from software engineering to random thoughts. The site uses the Hugo Flex theme and has custom layouts for enhanced functionality.

## Architecture

- **Static Site Generator**: Hugo with multilingual support (en/ru)
- **Theme**: Currently using `hugo-flex` (also has `hugo-bearcub` available in themes/)
- **Content Structure**: Organized by content type and date hierarchy
  - `/content/posts/YYYY/MM/` - Blog posts with both .md and folders with index.md
  - `/content/book-reviews/` - Book review articles
  - `/content/jobs-to-be-done-47/` - JTBD course content
  - `/content/about/` - About pages
- **Multilingual**: Each content piece can have `.md` (English) and `.ru.md` (Russian) versions

## Key Directories

- `content/` - All markdown content organized by type and date
- `layouts/` - Custom Hugo layouts and partials (banner, social-follow, audio shortcode)
- `static/` - Static assets (favicon.png, logo.webp)
- `themes/` - Contains hugo-flex (active) and hugo-bearcub themes
- `public/` - Generated site output (don't edit directly)
- `resources/` - Hugo's resource cache

## Common Commands

Since this is a standard Hugo site with no package.json or build scripts:

```bash
# Serve the site locally with drafts and live reload
hugo server -D

# Build the production site
hugo

# Create a new post
hugo new posts/YYYY/MM/post-name/index.md

# Create a new book review
hugo new book-reviews/YYYY/book-name.md
```

## Content Creation Patterns

1. **Blog Posts**: Use bundle format in `content/posts/YYYY/MM/post-name/index.md` for posts with assets
2. **Simple Posts**: Use single files like `content/posts/YYYY/MM/post-name.md` 
3. **Multilingual**: Add `.ru.md` extension for Russian versions
4. **Front Matter**: Follow the archetype pattern with title, date, draft, author, summary, tags
5. **Media Files**: Store audio files (.mp3, .wav) and images directly in post bundles

## Site Configuration

- Base URL: https://chaotic.land/
- Default language: English (en)
- Supported languages: English (en), Russian (ru)
- Google Analytics: G-96GHV7J9Q8
- Comments: Utterances integration with GitHub repo
- RSS: Custom feed.xml endpoint
- Author: Anton Golubtsov

## Custom Features

- Custom banner navigation with language switching
- Audio shortcode for embedding audio files
- Social follow links (Twitter, GitHub, LinkedIn, Keybase, Mastodon)
- Utterances comments system
- Custom CSS for syntax highlighting
- Social cards and SEO optimization

## Theme Notes

The site currently uses `hugo-flex` theme but also has `hugo-bearcub` available. Both themes support:
- Multilingual content
- Dark mode
- Responsive design
- SEO optimization
- No JavaScript dependency (except for comments)

When switching themes, update the `theme` field in `config.yaml` and check for any custom layout compatibility.