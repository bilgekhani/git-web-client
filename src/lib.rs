//! Fixture-backed models for the git web client.
//!
//! The first slice reads the generated GitHub-shaped JSON under
//! `fixtures/github/` so the UI can be built without a live forge.

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, thiserror::Error)]
pub enum FixtureError {
    #[error("io error for {path}: {source}")]
    Io {
        path: PathBuf,
        #[source]
        source: std::io::Error,
    },
    #[error("json error for {path}: {source}")]
    Json {
        path: PathBuf,
        #[source]
        source: serde_json::Error,
    },
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
pub struct Owner {
    pub login: String,
    pub id: u64,
    #[serde(rename = "type")]
    pub kind: Option<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq, Eq)]
pub struct License {
    pub key: String,
    pub name: String,
    pub spdx_id: Option<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq)]
pub struct RepoFixtureMeta {
    pub phase: String,
    pub kind: String,
    pub synthetic: bool,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq)]
pub struct Repository {
    pub id: u64,
    pub name: String,
    pub full_name: String,
    pub private: bool,
    pub visibility: String,
    pub description: Option<String>,
    pub language: Option<String>,
    pub html_url: String,
    pub created_at: String,
    pub pushed_at: String,
    pub stargazers_count: u64,
    pub fork: bool,
    pub archived: bool,
    pub fixture: Option<RepoFixtureMeta>,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq)]
pub struct Profile {
    pub login: String,
    pub name: Option<String>,
    pub bio: Option<String>,
    pub blog: Option<String>,
    pub company: Option<String>,
    pub location: Option<String>,
    pub html_url: String,
    pub public_repos: u64,
    pub total_private_repos: Option<u64>,
}

#[derive(Debug, Clone, Deserialize, Serialize, PartialEq)]
pub struct FixtureSummary {
    pub owner: String,
    pub repos: usize,
    pub public_repos: usize,
    pub private_repos: usize,
    pub commits: usize,
    pub avg_repos_per_month: f64,
}

#[derive(Debug, Clone)]
pub struct FixtureStore {
    root: PathBuf,
}

impl FixtureStore {
    pub fn new(root: impl Into<PathBuf>) -> Self {
        Self { root: root.into() }
    }

    pub fn generated(root: impl AsRef<Path>) -> Self {
        Self::new(root.as_ref().join("fixtures/github/generated"))
    }

    pub fn load_profile(&self) -> Result<Profile, FixtureError> {
        read_json(self.root.join("profile.json"))
    }

    pub fn load_summary(&self) -> Result<FixtureSummary, FixtureError> {
        read_json(self.root.join("summary.json"))
    }

    pub fn load_repos(&self) -> Result<Vec<Repository>, FixtureError> {
        read_json(self.root.join("repos.json"))
    }
}

fn read_json<T: serde::de::DeserializeOwned>(path: PathBuf) -> Result<T, FixtureError> {
    let bytes = fs::read(&path).map_err(|source| FixtureError::Io {
        path: path.clone(),
        source,
    })?;
    serde_json::from_slice(&bytes).map_err(|source| FixtureError::Json { path, source })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn repo_root() -> PathBuf {
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
    }

    #[test]
    fn generated_corpus_matches_summary() {
        let store = FixtureStore::generated(repo_root());
        let summary = store.load_summary().expect("summary");
        let repos = store.load_repos().expect("repos");
        let profile = store.load_profile().expect("profile");

        assert_eq!(summary.owner, "bilgekhani");
        assert_eq!(summary.repos, repos.len());
        assert_eq!(
            summary.public_repos,
            repos.iter().filter(|r| r.visibility == "public").count()
        );
        assert_eq!(
            summary.private_repos,
            repos.iter().filter(|r| r.visibility == "private").count()
        );
        assert!(summary.avg_repos_per_month > 4.0);
        assert!(summary.avg_repos_per_month < 7.0);
        assert_eq!(profile.login, "bilgekhani");
        assert!(repos.iter().any(|r| r.language.as_deref() == Some("Rust")));
        assert!(repos.iter().any(|r| r.language.as_deref() == Some("C++")));
        assert!(repos.iter().any(|r| r.language.as_deref() == Some("Python")));
    }
}
