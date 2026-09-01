//! hexa-sec-parse — fast scanner-report parsing shadows.
//!
//! The port never changes; only the adapter gets faster. pyo3 binds these
//! behind the driven ports. Phase 5 implements the real JSON/SARIF/XML/APK
//! parsers (serde ~10x faster than Python).

use std::collections::BTreeSet;

/// Return the distinct string keys whose value follows in a JSON snippet
/// (placeholder for the Phase 5 serde parsers).
pub fn json_keys(input: &str) -> Vec<String> {
    let chars: Vec<char> = input.chars().collect();
    let mut keys: BTreeSet<String> = BTreeSet::new();
    let mut index = 0;

    while index < chars.len() {
        if chars[index] != '"' {
            index += 1;
            continue;
        }
        let start = index + 1;
        let mut end = start;
        while end < chars.len() && chars[end] != '"' {
            end += 1;
        }
        let mut cursor = end + 1;
        while cursor < chars.len() && chars[cursor].is_whitespace() {
            cursor += 1;
        }
        if cursor < chars.len() && chars[cursor] == ':' && end > start {
            let key: String = chars[start..end].iter().collect();
            keys.insert(key);
        }
        index = end + 1;
    }

    keys.into_iter().collect()
}

#[cfg(test)]
mod tests {
    use super::json_keys;

    #[test]
    fn extracts_unique_keys() {
        let keys = json_keys(r#"{"name":"a","score":1,"name":"b"}"#);
        assert_eq!(keys, vec!["name", "score"]);
    }
}
