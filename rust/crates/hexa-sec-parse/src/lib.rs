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
    let quote_indexes: Vec<usize> = chars
        .iter()
        .enumerate()
        .filter_map(|(index, &character)| (character == '"').then_some(index))
        .collect();
    let mut keys: BTreeSet<String> = BTreeSet::new();

    for pair in quote_indexes.chunks(2) {
        if pair.len() < 2 {
            break;
        }
        let key_start = pair[0] + 1;
        let key_end = pair[1];
        if key_end <= key_start {
            continue;
        }
        let tail = &chars[key_end + 1..];
        let Some(value_offset) = tail.iter().position(|character| !character.is_whitespace())
        else {
            continue;
        };
        if tail[value_offset] != ':' {
            continue;
        }
        let key: String = chars[key_start..key_end].iter().collect();
        keys.insert(key);
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

    #[test]
    fn empty_input_yields_no_keys() {
        assert!(json_keys("").is_empty());
    }

    #[test]
    fn no_quotes_yields_no_keys() {
        assert!(json_keys(r#"{name: a}"#).is_empty());
        assert!(json_keys("12345").is_empty());
    }

    #[test]
    fn ignores_whitespace_around_colon() {
        let keys = json_keys(r#"{ "a" : 1 ,  "b"   :  2 }"#);
        assert_eq!(keys, vec!["a", "b"]);
    }

    #[test]
    fn quoted_value_is_not_a_key() {
        let keys = json_keys(r#"{"k":"quoted"}"#);
        assert_eq!(keys, vec!["k"]);
    }

    #[test]
    fn empty_string_key_is_excluded() {
        // A key with no characters (end == start) is not a real key.
        let keys = json_keys(r#"{"":1}"#);
        assert!(keys.is_empty());
    }

    #[test]
    fn key_without_colon_is_not_a_key() {
        let keys = json_keys(r#"{"title"}"#);
        assert!(keys.is_empty());
    }

    #[test]
    fn unterminated_quoted_key_is_ignored() {
        // No closing quote: scanning reaches end-of-input without panicking.
        let keys = json_keys(r#"{"open"#);
        assert!(keys.is_empty());
    }

    #[test]
    fn trailing_text_after_object_is_ignored() {
        let keys = json_keys(r#"{"a":1} trailing : not "json""#);
        assert_eq!(keys, vec!["a"]);
    }

    #[test]
    fn nested_and_repeated_keys_are_flattened() {
        let keys = json_keys(r#"{"a":{"b":{"a":1}}}"#);
        assert_eq!(keys, vec!["a", "b"]);
    }

    #[test]
    fn unicode_keys_are_preserved() {
        let keys = json_keys(r#"{"clé":"v","ключ":2}"#);
        assert_eq!(keys, vec!["clé", "ключ"]);
    }

    #[test]
    fn escaped_quote_confuses_scanner_without_hanging() {
        // Documented placeholder quirk: the naive scanner splits on an escaped
        // quote. It must terminate and must never fabricate keys from the
        // mangled remainder.
        let keys = json_keys(r#"{"a\"b":1,"c":2}"#);
        assert!(!keys.iter().any(|k| k == "a\\b"));
        assert!(!keys.iter().any(|k| k == "a"));
        assert!(!keys.iter().any(|k| k == "c"));
    }
}
