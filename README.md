# Robina Li's Book Reading Notes

A Jekyll blog for book reading notes — summaries, reflections, and takeaways. Powered by Jekyll and GitHub Pages.

## Features

- Clean, responsive design (Morandi theme)
- Markdown-based notes with table of contents
- Search and filter on the All Notes page
- Automatic GitHub Pages deployment
- RSS feed support
- Google Translate sidebar

## Getting Started

### Prerequisites

- Ruby (version 3.1 or higher)
- Bundler gem

### Local Development

1. Clone this repository:
   ```bash
   git clone https://github.com/robinali34/blog_book_notes.git
   cd blog_book_notes
   ```

2. Install dependencies:
   ```bash
   bundle install
   ```

3. Serve the site locally:
   ```bash
   ./serve.sh
   ```
   Or with the full test script:
   ```bash
   ./local-test.sh
   ```

4. Open your browser to:
   - Local: `http://localhost:4000/blog_book_notes/` (with `local-test.sh`)
   - Or: `http://localhost:4002/` (with `serve.sh`, empty baseurl)

### Adding New Notes

1. Create a new file in `_posts/` named `YYYY-MM-DD-book-title.md`
2. Add front matter:
   ```yaml
   ---
   layout: post
   title: "Book Title — Chapter or Topic"
   date: YYYY-MM-DD HH:MM:SS -0000
   categories: non-fiction
   tags: [author-name, topic]
   ---
   ```
3. Write your notes in Markdown below the front matter

### Deployment

Push to the `main` branch to deploy via GitHub Actions.

**Repository**: `blog_book_notes`  
**Live URL**: `https://robinali34.github.io/blog_book_notes/`

## Site Structure

| Path | Purpose |
|------|---------|
| `_posts/` | Book note posts |
| `_config.yml` | Site configuration |
| `reading-list.md` | Track books read and want to read |
| `about.md` | About page |
| `all-posts.html` | Searchable archive of all notes |

## License

MIT License
