use anyhow::{Context, Result};
use git_web_client::FixtureStore;

fn main() -> Result<()> {
    let root = std::env::current_dir().context("cwd")?;
    let store = FixtureStore::generated(&root);
    let summary = store.load_summary().context("load generated summary")?;
    println!(
        "{} repos={} public={} private={} commits={} avg/month={}",
        summary.owner,
        summary.repos,
        summary.public_repos,
        summary.private_repos,
        summary.commits,
        summary.avg_repos_per_month
    );
    Ok(())
}
