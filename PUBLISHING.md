# Publication and verification

1. Build the source and run `python scripts/check_public_release.py --execute` before a release.
2. Review the exact release file list. Exclude .git, .openai, virtual environments, caches, private data, prior releases and local QA files.
3. Push only the reviewed new public edition to kochiuyu/data-to-decisions, preserving any intervening owner changes.
4. Select GitHub Actions as the Pages source in repository Settings → Pages.
5. Verify the expected commit is on main and the **Validate and deploy public course** workflow succeeded for that commit.
6. Verify the returned deployment URL, lesson pages, downloads and navigation before calling the public site live.

The workflow installs the pinned dependencies, recalculates the course from source, and runs structural, saved-result and full lab reproducibility checks before deployment. Full numerical reproduction is also performed before release. GitHub Pages publication does not modify the owner-private course.
