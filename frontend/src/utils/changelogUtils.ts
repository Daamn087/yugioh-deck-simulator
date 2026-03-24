/**
 * Extracts the latest version string from the changelog markdown content.
 * Expected format: ## [v.v.v] - YYYY-MM-DD
 * @param content The raw markdown content of CHANGELOG.md
 * @returns The version string (e.g., "0.6.0") or null if not found.
 */
export const getLatestChangelogVersion = (content: string): string | null => {
  // Matches the first occurrence of "## [version]"
  const match = content.match(/^## \[(.*?)\]/m);
  return match ? (match[1] ?? null) : null;
};
