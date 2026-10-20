"""Recipe settings and the effective cargo-pgrx feature selection."""
import re

# Settings refer to the visible upstream commands, not a replacement build system.
RECIPES = {
    'pg-durable': {'manifest':'Cargo.toml','defaults':False,'installed':False},
    'pg-graphql': {'manifest':'Cargo.toml','defaults':True,'installed':True},
    'pg-jsonschema': {'manifest':'Cargo.toml','defaults':False,'installed':False},
    'pg-parquet': {'manifest':'Cargo.toml','defaults':False,'installed':False},
    'pg-search': {'manifest':'pg_search/Cargo.toml','defaults':True,'installed':False},
    'pg-session-jwt': {'manifest':'Cargo.toml','defaults':True,'installed':True},
}


def effective_features(manifest, recipe, pg_major):
    # cargo-pgrx manifest::modify_features_for_version makes non-PG defaults
    # explicit and disables default features before invoking cargo build.
    defaults = manifest.get('features',{}).get('default',[])
    features = [flag for flag in defaults if not re.fullmatch(r'pg\d+',flag)] if recipe['defaults'] else []
    return sorted(set(features+['pg'+str(pg_major)]))
