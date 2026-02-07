// build_check.rs - Compile-time Python version gate for ChromaDB Rust bindings
//
// Add to build.rs in the chromadb-rust workspace to emit warnings/errors
// when building against unsupported Python versions.
//
// This is a reference snippet, not a standalone binary.

use std::env;

/// Check Python version compatibility at build time.
/// Call this from the crate's build.rs.
pub fn check_python_version_compat() {
    // pyo3 sets these environment variables during build
    let version = env::var("PYO3_PYTHON_VERSION").unwrap_or_default();

    if version.is_empty() {
        println!("cargo:warning=PYO3_PYTHON_VERSION not set; skipping version check");
        return;
    }

    let parts: Vec<u32> = version
        .split('.')
        .filter_map(|s| s.parse().ok())
        .collect();

    if parts.len() >= 2 {
        let (major, minor) = (parts[0], parts[1]);

        // Python 3.14+ requires pyo3 >= 0.22 for stable ABI support
        if major == 3 && minor >= 14 {
            println!(
                "cargo:warning=Building for Python {}.{}. Ensure pyo3 >= 0.22 is used.",
                major, minor
            );

            // Check if we're building for free-threaded Python (3.13t / 3.14t)
            if env::var("PYO3_GIL_DISABLED").unwrap_or_default() == "1" {
                println!(
                    "cargo:warning=Free-threaded Python detected. \
                     abi3 feature must be disabled for cp{}{}t wheels.",
                    major, minor
                );
            }
        }

        if major < 3 || (major == 3 && minor < 9) {
            panic!(
                "ChromaDB requires Python >= 3.9, found {}.{}",
                major, minor
            );
        }
    }
}
